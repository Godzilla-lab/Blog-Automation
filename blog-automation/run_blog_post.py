#!/usr/bin/env python3
"""
Blog post orchestrator. Wires the full pipeline:

    research (Tavily + Claude)  -> research_brief.json
       |
    draft  (Claude, with hexa_urls.json + research_brief injected)
       |
    deterministic validate  (blog_validator)
       |       \\__ fail -> critique-feedback retry (up to MAX_RETRIES)
       |
    LLM evaluate  (blog_evaluator)
       |       \\__ regenerate=True -> critique-feedback retry
       |
    parse 8 sections (TITLE / SLUG / EXCERPT / BODY / COVER IMAGE BRIEF /
                      INLINE IMAGE BRIEFS / INTERNAL LINKS USED /
                      EXTERNAL CITATIONS USED)
       |
    social repurpose (LinkedIn / Twitter / Threads, existing flow)
       |
    save to blog-automation/output/<YYYY-MM-DD>-<slug>/

Designed to be called as:
  - A CLI:  python run_blog_post.py --topic "..." --niche finance
  - A function: from run_blog_post import generate_one_post
                generate_one_post(question, user_answers, niche, slug_override)

Replaces the legacy main.py + auto_generate.py flow. The niche runners
(run_hvac_post.py, run_roofing_post.py, etc.) call generate_one_post directly.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load BOTH the local blog-automation/.env AND the parent project's .env.
# The parent has TAVILY_API_KEY (and other shared keys); the local has the
# blog-specific Anthropic key. Local takes precedence on any overlap.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(SCRIPT_DIR / ".env", override=True)

sys.path.insert(0, str(SCRIPT_DIR))

from modules.claude_client import create_client
from modules.blog_research import research_blog_topic
from modules.blog_research_manual import research_blog_topic_manual
from modules.blog_validator import validate_blog, critique_from_failures
from modules.blog_evaluator import evaluate_blog
from modules.social_generator import create_generator


HEXA_URLS_PATH = SCRIPT_DIR / "hexa_urls.json"
TEMPLATE_PATH = SCRIPT_DIR / "templates" / "blog_prompt.txt"
OUTPUT_BASE = SCRIPT_DIR / "output"
MAX_DRAFT_RETRIES = int(os.getenv("BLOG_MAX_RETRIES", "2"))


# ---------- Section parser ----------

# The 8 labelled sections from blog_prompt.txt
SECTION_NAMES = [
    "TITLE",
    "SLUG",
    "EXCERPT",
    "BODY (HTML)",
    "COVER IMAGE BRIEF",
    "INLINE IMAGE BRIEFS",
    "INTERNAL LINKS USED",
    "EXTERNAL CITATIONS USED",
]


def parse_sections(raw_output: str) -> dict:
    """
    Split the writer's response into the 8 named sections.

    Accepts headers in any of these forms (the model is inconsistent):
        ### TITLE
        ## TITLE
        **TITLE**
        TITLE:
    The label is matched case-insensitively. Returns a dict keyed by the
    canonical section name (e.g. {"TITLE": "...", "BODY": "...", ...}).
    The BODY key drops the "(HTML)" suffix for ergonomics.
    """
    # Build alternation of acceptable section labels
    labels = [re.escape(name) for name in SECTION_NAMES]
    # Header forms: optional #/* prefix + the label + optional trailing :/\n
    header_re = re.compile(
        rf'^\s*(?:#{{1,4}}\s*|\*\*\s*)?({"|".join(labels)})\s*(?:\*\*)?\s*:?\s*$',
        re.IGNORECASE | re.MULTILINE,
    )

    sections = {}
    matches = list(header_re.finditer(raw_output))
    for i, m in enumerate(matches):
        name = m.group(1).upper().replace("(HTML)", "").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_output)
        sections[name] = raw_output[start:end].strip()

    return sections


def derive_slug(title: str, fallback: str = "blog-post") -> str:
    """Make a kebab-case slug from a title if the writer didn't supply one."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")[:60]
    return slug or fallback


def build_writer_prompt(template_path: Path, blog_question: str, user_answers: dict,
                        niche: str, research_brief: dict, hexa_urls: dict,
                        critique: str = None) -> str:
    """
    Interpolate the writer prompt template with all the context. Used by both
    the API-mode flow (passes result to messages.create) and the manual flow
    (writes result to prompt_packet.md for chat-Claude / operator).
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    formatted_answers = "\n\n".join(
        f"**Q: {q}**\nA: {a}" for q, a in (user_answers or {}).items()
    )
    critique_block = ""
    if critique:
        critique_block = (
            "================================================================================\n"
            "REGENERATION CRITIQUE (the previous draft failed - fix every item)\n"
            "================================================================================\n\n"
            + critique
            + "\n"
        )
    return template.format(
        question=blog_question,
        niche=niche or "general",
        user_answers=formatted_answers,
        research_brief=json.dumps(research_brief, indent=2),
        hexa_urls=json.dumps(hexa_urls, indent=2),
        critique_block=critique_block,
    )


# ---------- Manual mode (no Anthropic) ----------

def prepare_manual_post(question: str, user_answers: dict = None, niche: str = "general",
                        slug_override: str = None, output_base: Path = None) -> dict:
    """
    Prepare a post directory for hand-fulfillment when Anthropic is down.

    Produces:
      - research_raw.json  (Tavily-only, no LLM synthesis)
      - prompt_packet.md   (the full writer prompt with all context interpolated,
                            ready to paste into a chat session)
      - MANUAL_README.md   (the protocol for filling the rest)

    Does NOT call Anthropic. Returns a result dict.
    """
    output_base = output_base or OUTPUT_BASE
    user_answers = user_answers or {}

    print("\n" + "=" * 64)
    print("  BLOG POST PIPELINE (MANUAL MODE - no Anthropic)")
    print(f"  Topic: {question}")
    print(f"  Niche: {niche}")
    print("=" * 64)

    if not HEXA_URLS_PATH.exists():
        return {"success": False, "reason_if_failed": f"hexa_urls.json not found at {HEXA_URLS_PATH}"}
    with open(HEXA_URLS_PATH) as f:
        hexa_urls = json.load(f)

    # Slug + output dir
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slug_override or derive_slug(question)
    output_dir = output_base / f"{date_str}-{slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Step 1: Tavily-only research ----
    print("\n[1/3] Manual research (Tavily only) ...")
    try:
        research_raw = research_blog_topic_manual(topic=question, niche=niche)
    except RuntimeError as e:
        print(f"  ! Tavily research failed: {e}")
        print(f"  Continuing with empty research; operator must source citations by hand.")
        research_raw = {
            "topic": question, "niche": niche,
            "research_date": datetime.now().strftime("%Y-%m-%d"),
            "mode": "manual_tavily_unavailable",
            "sources": [],
            "warning": str(e),
        }
    (output_dir / "research_raw.json").write_text(json.dumps(research_raw, indent=2), encoding="utf-8")
    print(f"      sources: {len(research_raw.get('sources', []))}")

    # ---- Step 2: Build the prompt packet ----
    print("\n[2/3] Build prompt_packet.md ...")
    # Shape the raw research into something the writer-prompt template can interpolate.
    # The template expects {research_brief} as a JSON blob; manual mode just stuffs
    # the Tavily sources in there directly.
    research_brief_proxy = {
        "topic": research_raw.get("topic"),
        "niche": research_raw.get("niche"),
        "mode": "manual_tavily_only",
        "external_citation_candidates": [
            {"url": s.get("url"), "title": s.get("title"), "snippet": s.get("content")}
            for s in research_raw.get("sources", [])[:30]
        ],
        "notes_for_writer": research_raw.get("notes_for_writer", ""),
    }
    prompt = build_writer_prompt(
        template_path=TEMPLATE_PATH,
        blog_question=question,
        user_answers=user_answers,
        niche=niche,
        research_brief=research_brief_proxy,
        hexa_urls=hexa_urls,
    )
    (output_dir / "prompt_packet.md").write_text(prompt, encoding="utf-8")
    print(f"      written: {output_dir / 'prompt_packet.md'}")

    # ---- Step 3: Write the protocol README ----
    readme = f"""# Manual-mode protocol for {slug}

Anthropic API is unavailable, so the orchestrator stopped at the research step.
A chat-Claude session (or you, by hand) must complete the next steps. Tavily research
ran successfully and the candidate citations are in `research_raw.json`.

## Step 1 - Read the prompt packet

Open `prompt_packet.md`. It contains the full writer prompt with topic, niche,
user_answers, hexa_urls (the internal link allowlist), and research candidates
all interpolated. This is what an Anthropic-driven writer would receive.

## Step 2 - Produce the 8-section output

In your chat session, paste the contents of `prompt_packet.md` as the user message.
The chat-Claude will produce the 8 labelled sections (TITLE / SLUG / EXCERPT /
BODY (HTML) / COVER IMAGE BRIEF / INLINE IMAGE BRIEFS / INTERNAL LINKS USED /
EXTERNAL CITATIONS USED).

## Step 3 - Save the BODY as article.html

Save the HTML body (the content under `### BODY (HTML)`) as `article.html` in
this folder. Save the full 8-section output as `paste_sections.md`.

## Step 4 - Validate

Run the deterministic validator. This needs no API key:

    cd blog-automation
    python run_blog_post.py --validate-only --post-dir output/{date_str}-{slug}

If it passes, `draft_eval.json` and `metadata.json` will be updated. If it fails,
the failure list tells you what to fix; iterate the article and re-validate until
it passes.

## Step 5 - Publish

The operator pastes the sections from `paste_sections.md` into the admin's
per-field form, OR pastes `article.html` directly into the rich-text editor.
"""
    (output_dir / "MANUAL_README.md").write_text(readme, encoding="utf-8")

    print(f"\n[3/3] Done.")
    print(f"      output dir: {output_dir}")
    print(f"      next: open {output_dir / 'MANUAL_README.md'} and follow the protocol")
    return {
        "success": True,
        "output_dir": str(output_dir),
        "slug": slug,
        "mode": "manual_prepared",
        "next_step": f"Hand-fulfill prompt_packet.md, save article.html in this dir, then run: python run_blog_post.py --validate-only --post-dir {output_dir}",
    }


def validate_post_dir(post_dir: Path, hexa_urls: dict = None) -> dict:
    """
    Re-run the deterministic validator on a hand-written article.html in an
    existing post directory. No API calls. Updates draft_eval.json with the
    new pass/fail status. Used by --validate-only.
    """
    if hexa_urls is None:
        with open(HEXA_URLS_PATH) as f:
            hexa_urls = json.load(f)

    article_path = post_dir / "article.html"
    if not article_path.exists():
        return {"success": False, "reason_if_failed": f"article.html not found in {post_dir}"}

    text = article_path.read_text(encoding="utf-8")
    validator_result = validate_blog(text, hexa_urls)

    # Update or create draft_eval.json
    eval_path = post_dir / "draft_eval.json"
    existing = {}
    if eval_path.exists():
        try:
            existing = json.loads(eval_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    existing.update({
        "qa_passed": validator_result["passed"],
        "validator": validator_result,
        "evaluator": existing.get("evaluator", {"skipped": True, "reason": "LLM evaluator not run in --validate-only mode"}),
        "mode": existing.get("mode", "manual") + "_revalidated",
        "revalidated_at": datetime.now().isoformat(),
    })
    eval_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    print(f"  article.html: {article_path}")
    print(f"  passed={validator_result['passed']}")
    print(f"  words={validator_result['stats']['words']}, "
          f"internal={validator_result['stats']['internal_links']}, "
          f"external={validator_result['stats']['external_links']}")
    if not validator_result["passed"]:
        for f in validator_result["failures"]:
            print(f"  - [{f['check']}] {f['detail']}")
        critique = critique_from_failures(validator_result["failures"])
        (post_dir / "next_critique.md").write_text(critique, encoding="utf-8")
        print(f"\n  Critique saved to {post_dir / 'next_critique.md'} - paste into chat with the article to get a revision.")
    return {"success": validator_result["passed"], "output_dir": str(post_dir), "validator": validator_result}


# ---------- The pipeline ----------

def generate_one_post(question: str, user_answers: dict = None, niche: str = "general",
                       slug_override: str = None, output_base: Path = None,
                       skip_social: bool = False) -> dict:
    """
    Run the full pipeline for one post.

    Returns a result dict:
      {
        "success": bool,
        "output_dir": str,
        "title": str, "slug": str,
        "validator": {...}, "evaluator": {...},
        "retry_count": int,
        "reason_if_failed": str | None,
      }
    """
    output_base = output_base or OUTPUT_BASE
    user_answers = user_answers or {}

    print("\n" + "=" * 64)
    print(f"  BLOG POST PIPELINE")
    print(f"  Topic: {question}")
    print(f"  Niche: {niche}")
    print("=" * 64)

    # ---- Preflight ----
    if not HEXA_URLS_PATH.exists():
        return {"success": False, "reason_if_failed": f"hexa_urls.json not found at {HEXA_URLS_PATH}"}
    with open(HEXA_URLS_PATH) as f:
        hexa_urls = json.load(f)

    # ---- Stage 1: Research ----
    print("\n[1/5] Research (Tavily + Claude) ...")
    try:
        research_brief = research_blog_topic(topic=question, niche=niche)
    except RuntimeError as e:
        msg = str(e)
        hint = ""
        if "ANTHROPIC" in msg.upper():
            hint = " | Anthropic key down? Re-run with --manual to use Tavily-only research."
        return {"success": False, "reason_if_failed": f"research failed: {e}{hint}"}
    except Exception as e:
        # Anthropic SDK raises various subclasses on 401/quota/timeout. Catch
        # anything that smells like auth and recommend manual mode.
        err_str = str(e).lower()
        if "authentication" in err_str or "invalid x-api-key" in err_str or "401" in err_str:
            return {
                "success": False,
                "reason_if_failed": f"Anthropic auth failed: {e}",
                "suggestion": "Re-run with --manual to skip Anthropic stages and use Tavily-only research."
            }
        return {"success": False, "reason_if_failed": f"research crashed: {e}"}

    if not research_brief.get("key_stats"):
        return {
            "success": False,
            "reason_if_failed": "research returned 0 stats; cannot draft without sourced facts",
            "research_brief": research_brief,
        }
    print(f"      stats: {len(research_brief.get('key_stats', []))}, "
          f"citation candidates: {len(research_brief.get('external_citation_candidates', []))}, "
          f"pain points: {len(research_brief.get('pain_points', []))}")

    # ---- Stage 2-3: Draft loop (with validator + evaluator critique feedback) ----
    print("\n[2/5] Draft + validate loop ...")
    claude = create_client()
    critique = None
    retry_count = 0
    sections = {}
    raw_output = ""
    validator_result = {}
    evaluator_result = {}
    retry_history = []

    while retry_count <= MAX_DRAFT_RETRIES:
        attempt_label = "first draft" if retry_count == 0 else f"retry {retry_count}/{MAX_DRAFT_RETRIES}"
        print(f"      {attempt_label} ...")

        try:
            raw_output = claude.generate_blog_post(
                blog_question=question,
                user_answers=user_answers,
                niche=niche,
                research_brief=research_brief,
                hexa_urls=hexa_urls,
                template_path=str(TEMPLATE_PATH),
                critique=critique,
            )
        except Exception as e:
            return {"success": False, "reason_if_failed": f"draft generation crashed: {e}",
                    "research_brief": research_brief}

        sections = parse_sections(raw_output)
        body = sections.get("BODY", "")
        if not body:
            critique = "Previous output was missing the '### BODY (HTML)' section. You MUST produce all 8 labelled sections, BODY (HTML) included."
            retry_history.append({"attempt": retry_count, "outcome": "no_body_section"})
            retry_count += 1
            continue

        # Deterministic validator
        validator_result = validate_blog(body, hexa_urls)
        print(f"      validator: passed={validator_result['passed']}, "
              f"words={validator_result['stats']['words']}, "
              f"internal_links={validator_result['stats']['internal_links']}, "
              f"external_links={validator_result['stats']['external_links']}")

        if not validator_result["passed"]:
            retry_history.append({"attempt": retry_count, "outcome": "validator_failed",
                                  "failures": validator_result["failures"]})
            if retry_count >= MAX_DRAFT_RETRIES:
                break
            critique = critique_from_failures(validator_result["failures"])
            retry_count += 1
            continue

        # LLM evaluator (only if validator passed)
        print(f"      evaluator (Claude) ...")
        evaluator_result = evaluate_blog(
            article_text=body,
            research_brief=research_brief,
            topic=question,
            niche=niche,
        )
        if "error" in evaluator_result:
            print(f"      evaluator skipped: {evaluator_result['error']}")
            retry_history.append({"attempt": retry_count, "outcome": "evaluator_error",
                                  "error": evaluator_result["error"]})
            break  # validator passed, evaluator broken — ship the draft

        print(f"      evaluator: passed={evaluator_result.get('passed')}, "
              f"avg={evaluator_result.get('overall_score')}, "
              f"min_dim={evaluator_result.get('min_dimension_score')}")

        if evaluator_result.get("passed"):
            retry_history.append({"attempt": retry_count, "outcome": "passed"})
            break
        if evaluator_result.get("regenerate") and retry_count < MAX_DRAFT_RETRIES:
            critique = evaluator_result.get("critique", "Improve eeat_experience, citation_quality, and voice_no_ai_tells.")
            retry_history.append({"attempt": retry_count, "outcome": "evaluator_failed_retry",
                                  "critique": critique[:200]})
            retry_count += 1
            continue

        retry_history.append({"attempt": retry_count, "outcome": "evaluator_failed_terminal"})
        break

    qa_passed = bool(validator_result.get("passed") and evaluator_result.get("passed", True))

    # ---- Stage 4: Social repurpose ----
    body = sections.get("BODY", "")
    social_posts = {"linkedin": "", "twitter": "", "threads": ""}
    if body and not skip_social:
        print("\n[3/5] Social repurpose (LinkedIn / Twitter / Threads) ...")
        try:
            social_posts = create_generator(claude).generate_all_posts(body)
        except Exception as e:
            print(f"      social generation failed: {e}")

    # ---- Stage 5: Save ----
    title = sections.get("TITLE", question).strip().strip("`'\"")
    slug = slug_override or sections.get("SLUG", "").strip() or derive_slug(title)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = output_base / f"{date_str}-{slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[4/5] Save -> {output_dir}")

    # article.html: the BODY HTML, ready for the rich-text admin paste
    (output_dir / "article.html").write_text(body, encoding="utf-8")

    # paste_sections.md: the 8 sections labelled, one per admin form field
    paste_lines = []
    for key in ["TITLE", "SLUG", "EXCERPT", "BODY", "COVER IMAGE BRIEF",
                "INLINE IMAGE BRIEFS", "INTERNAL LINKS USED", "EXTERNAL CITATIONS USED"]:
        paste_lines.append(f"### {key}\n")
        paste_lines.append((sections.get(key, "") or "").strip() + "\n\n")
    (output_dir / "paste_sections.md").write_text("\n".join(paste_lines), encoding="utf-8")

    # blog_post.md: Markdown copy of the body (backward compat — reels read this)
    md_body = f"# {title}\n\n> {sections.get('EXCERPT', '').strip()}\n\n{body}\n"
    (output_dir / "blog_post.md").write_text(md_body, encoding="utf-8")

    # research_brief.json
    (output_dir / "research_brief.json").write_text(
        json.dumps(research_brief, indent=2), encoding="utf-8"
    )

    # draft_eval.json: full QA record
    (output_dir / "draft_eval.json").write_text(json.dumps({
        "qa_passed": qa_passed,
        "validator": validator_result,
        "evaluator": evaluator_result,
        "retry_count": retry_count,
        "retry_history": retry_history,
    }, indent=2), encoding="utf-8")

    # social posts (backward compat)
    (output_dir / "linkedin_post.md").write_text(social_posts.get("linkedin", ""), encoding="utf-8")
    (output_dir / "twitter_thread.md").write_text(social_posts.get("twitter", ""), encoding="utf-8")
    (output_dir / "threads_post.md").write_text(social_posts.get("threads", ""), encoding="utf-8")

    # metadata
    metadata = {
        "title": title,
        "slug": slug,
        "topic": question,
        "niche": niche,
        "qa_passed": qa_passed,
        "word_count": validator_result.get("stats", {}).get("words", 0),
        "internal_links_used": validator_result.get("stats", {}).get("internal_links", 0),
        "external_links_used": validator_result.get("stats", {}).get("external_links", 0),
        "evaluator_score": evaluator_result.get("overall_score"),
        "retry_count": retry_count,
        "model": os.getenv("CLAUDE_MODEL", "claude-opus-4-7"),
        "generated_at": datetime.now().isoformat(),
        "website": "hexaaiagency.com",
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"\n[5/5] Done.")
    print(f"      qa_passed: {qa_passed}")
    print(f"      output: {output_dir}")
    if not qa_passed:
        print(f"      ! draft did NOT pass all QA gates — review draft_eval.json before publishing")

    return {
        "success": qa_passed,
        "output_dir": str(output_dir),
        "title": title,
        "slug": slug,
        "validator": validator_result,
        "evaluator": evaluator_result,
        "retry_count": retry_count,
        "reason_if_failed": None if qa_passed else "draft did not pass all QA gates after retries",
    }


# ---------- CLI ----------

def _cli():
    parser = argparse.ArgumentParser(description="Generate one blog post for hexaaiagency.com.")
    parser.add_argument("--topic", default=None, help="The buyer question the post answers")
    parser.add_argument("--niche", default="general",
                        help="finance, property-management, healthcare, retail, real-estate, general")
    parser.add_argument("--slug", default=None, help="Override the generated slug")
    parser.add_argument("--answers-file", default=None,
                        help="Optional JSON file: {'q1 text': 'answer1', ...}")
    parser.add_argument("--skip-social", action="store_true",
                        help="Skip LinkedIn/Twitter/Threads repurposing")
    parser.add_argument("--manual", action="store_true",
                        help="Manual mode: skip Anthropic-dependent stages. Produces "
                             "research_raw.json + prompt_packet.md for chat-Claude / "
                             "operator to fulfill. Required when ANTHROPIC_API_KEY is dead.")
    parser.add_argument("--validate-only", action="store_true",
                        help="Re-run the deterministic validator on a hand-written "
                             "article.html in --post-dir. No API calls.")
    parser.add_argument("--post-dir", default=None,
                        help="Existing post directory (for --validate-only)")
    args = parser.parse_args()

    # --- validate-only mode ---
    if args.validate_only:
        if not args.post_dir:
            print("error: --validate-only requires --post-dir <existing-output-dir>", file=sys.stderr)
            sys.exit(2)
        result = validate_post_dir(Path(args.post_dir))
        sys.exit(0 if result["success"] else 1)

    # --- everything else requires --topic ---
    if not args.topic:
        print("error: --topic is required (unless using --validate-only)", file=sys.stderr)
        sys.exit(2)

    user_answers = {}
    if args.answers_file:
        with open(args.answers_file) as f:
            user_answers = json.load(f)

    # --- manual mode (no Anthropic) ---
    if args.manual:
        result = prepare_manual_post(
            question=args.topic,
            user_answers=user_answers,
            niche=args.niche,
            slug_override=args.slug,
        )
        sys.exit(0 if result["success"] else 1)

    # --- default: full Anthropic-driven pipeline ---
    result = generate_one_post(
        question=args.topic,
        user_answers=user_answers,
        niche=args.niche,
        slug_override=args.slug,
        skip_social=args.skip_social,
    )
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    _cli()
