# Directive: Write a Blog Post for hexaaiagency.com

## Goal
Produce ONE blog post that Google will index on the first crawl. The site has many posts stuck in "Crawled - currently not indexed" because they read as AI mass-production. Every new post must clear three QA gates (research, deterministic validator, LLM evaluator) before it's considered shippable. The operator copies the output into the rich-text admin and publishes.

## When to invoke
User says: "write a blog post", "new blog", "blog post about X", "create a blog", "post for the site", or asks to use a niche runner (HVAC, roofing, self-storage, AI failure, etc.).

If the user says "rewrite an existing post" or "fix an unindexed post", this directive does NOT cover that workflow yet — flag it and ask before improvising.

## Inputs
- **topic** (required) — the buyer question the post answers. Phrase as a question or task ("How does AI roofing estimating software cut sales cycles?"). Push back if the topic is too broad ("the future of AI"), too generic ("top 50 AI tools"), or doesn't map to a service/industry from `blog-automation/hexa_urls.json`.
- **niche** (optional, defaults to `general`) — hints the research + the industry link choice. Use one of: `finance`, `property-management`, `healthcare`, `retail`, `real-estate`, `hvac`, `roofing`, `self-storage`, `ai-strategy`, `general`.
- **user_answers** (optional dict) — operator first-hand context. Without these, the post can still draft from research alone, but EEAT-experience scoring will be weaker. Niche runners already bake these in.
- **slug** (optional) — override the auto-derived slug.

## Tools / Scripts
| Script | Purpose |
|---|---|
| `blog-automation/modules/blog_research.py` | **[Agent 0]** Tavily web search + Claude synthesis → `research_brief.json` (6-12 sourced stats with URLs, pain points, CTA ideas, citation candidates) |
| `blog-automation/modules/blog_validator.py` | **[deterministic gate]** Wordcount, TL;DR, internal-link allowlist, external-link count, banned phrases, em/en dashes, brand spelling, first-hand-experience regex |
| `blog-automation/modules/blog_evaluator.py` | **[Agent 1]** 9-dimension LLM rubric (EEAT, citation_quality, internal_linking, voice_no_ai_tells, etc.). Returns critique that feeds into retry loop |
| `blog-automation/modules/claude_client.py` | Claude wrapper, defaults to Opus 4.7. `generate_blog_post()` takes the topic + answers + research brief + URL allowlist + optional critique |
| `blog-automation/run_blog_post.py` | **Master orchestrator** — chains research → draft → validate → evaluate → retry loop → social repurpose → save |
| `blog-automation/templates/blog_prompt.txt` | The binding writer system prompt. Encodes both the HEXA writer guide and the Google indexing guide. Edit ONLY if a rule actually changes |
| `blog-automation/hexa_urls.json` | Canonical list of internal URLs the writer is allowed to link to. **Update this file when a new service / industry / case-study page ships on the site** |
| `blog-automation/run_*_post.py` | Niche runners (HVAC, roofing, self-storage, AI failure). Pre-baked EXPERT_ANSWERS playbooks + topic. Each just calls `generate_one_post()` |
| `blog-automation/main.py` | Interactive entry point — pick a question from the bank, answer 5 qualifying questions, run the pipeline |
| `blog-automation/auto_generate.py` | Non-interactive demo. Useful for smoke-testing after a code change |
| `blog-automation/modules/social_generator.py` | LinkedIn / Twitter / Threads repurposing from the rendered BODY (unchanged) |

## Quick Start

### When the Anthropic API key works (full pipeline)
```bash
# Interactive: walks operator through topic + answers
cd blog-automation && python main.py

# One-shot CLI: pass topic + niche
cd blog-automation && python run_blog_post.py \
  --topic "AI invoice processing in QuickBooks" \
  --niche finance

# Niche runner with pre-baked operator playbook
cd blog-automation && python run_hvac_post.py
cd blog-automation && python run_roofing_post.py
cd blog-automation && python run_storage_post.py
cd blog-automation && python run_ai_failure_post.py

# Smoke test
cd blog-automation && python auto_generate.py
```

### When the Anthropic API key is dead (manual mode)
The orchestrator auto-detects auth failures and recommends `--manual`. The flow is:
```bash
# Step 1: prepare the post dir (uses Tavily for research, NO Anthropic)
cd blog-automation && python run_blog_post.py \
  --topic "AI invoice processing in QuickBooks" \
  --niche finance \
  --manual

# This writes:
#   output/<date>-<slug>/research_raw.json   (Tavily sources, no synthesis)
#   output/<date>-<slug>/prompt_packet.md    (full writer prompt, interpolated)
#   output/<date>-<slug>/MANUAL_README.md    (step-by-step protocol)

# Step 2: the chat-Claude (or operator) reads prompt_packet.md and produces
# the 8-section output. Save the BODY (HTML) as article.html in the post dir.

# Step 3: re-run the deterministic validator (NO API calls)
cd blog-automation && python run_blog_post.py \
  --validate-only \
  --post-dir output/<date>-<slug>

# If validator fails, a critique is saved to next_critique.md - paste it back
# into the chat session with the article and ask for a revision. Iterate.
```

## Pipeline Flow

The orchestrator runs in two modes:
- **Full mode** (default): Anthropic + Tavily. Research → draft → validate → evaluate → retry → save. Used when the API key is alive.
- **Manual mode** (`--manual`): Tavily only, no Anthropic. The orchestrator prepares a self-contained prompt packet that a chat-Claude (or operator) fulfills by hand. Used when the API key is dead OR for higher-quality drafts where you want a human-in-the-loop writer.

### Full mode flow
```
0. blog_research.research_blog_topic(topic, niche)
     → research_brief.json (6-12 stats with source URLs, citation candidates)
     hard-fail if 0 stats returned (no point drafting without facts)

1. Draft loop (max 2 retries):
   a. claude.generate_blog_post(topic, user_answers, niche,
                                 research_brief, hexa_urls,
                                 critique=last_failure_critique)
       → raw output with 8 labelled sections (TITLE/SLUG/EXCERPT/BODY/...)

   b. parse_sections() → dict of named sections

   c. blog_validator.validate_blog(body, hexa_urls)
       checks: wordcount in [1800, 2200], TL;DR present,
               internal links 3-5 all from hexa_urls, external links 6-12,
               banned phrases, em/en dashes, brand spelling,
               first-hand-experience regex, paste sections present
       on fail → critique = critique_from_failures(); retry

   d. blog_evaluator.evaluate_blog(body, research_brief, topic, niche)
       9-dim rubric scored by Claude (only runs if validator passed)
       on fail with regenerate=True → critique = result.critique; retry
       on hard fail → save draft + flag, don't loop

2. social_generator.generate_all_posts(body)
     → LinkedIn / Twitter / Threads copies (existing flow, unchanged)

3. Save to blog-automation/output/<YYYY-MM-DD>-<slug>/
```

### Manual mode flow (no Anthropic)
```
0. blog_research_manual.research_blog_topic_manual(topic, niche)
     → research_raw.json (Tavily sources, deduped, ranked by publisher credibility)
     no LLM synthesis - the writer picks citations directly

1. build_writer_prompt() interpolates templates/blog_prompt.txt with:
     topic + niche + user_answers + hexa_urls + research_raw_as_citation_candidates
     → prompt_packet.md (one self-contained file the chat-Claude / operator pastes
                          into a chat session)

2. Chat-Claude (or operator by hand) produces the 8 labelled sections in chat.
   Operator saves the BODY (HTML) as article.html in the post dir.
   Operator saves the full output as paste_sections.md.

3. validate_post_dir() reruns the deterministic validator on the saved article.html
     → updates draft_eval.json with pass/fail + stats
     → if fail, writes next_critique.md the operator pastes back into the chat
       to get a revision
     no API calls in this step

4. Operator iterates step 2-3 until the validator passes.
```

The LLM evaluator (Agent 1) is skipped in manual mode. The deterministic validator
catches the structural failures (word count, internal-link allowlist, banned phrases,
em dashes, brand spelling, first-hand signal, citation count) which are the bulk of
what Google penalizes. The subjective EEAT / voice scoring that Agent 1 does
remains the operator's eyeball check.

## Layered QA
Three gates, cheap to expensive:

1. **Research (Agent 0)** — runs before any drafting. Hard-fails on 0 stats. Soft-warns on fewer than 6 stats.
2. **Deterministic validator** — runs after every draft attempt, before the LLM evaluator. Catches the structural failures the model keeps making (no TL;DR, internal links not in allowlist, too few external citations). 100% reliable, no token cost. Drives the critique-feedback retry loop.
3. **LLM evaluator (Agent 1)** — runs only if validator passes. Scores EEAT, citation_quality, internal_linking, voice_no_ai_tells, conversion_clarity on a 9-dim rubric. Catches the subjective "this reads like AI" failures the deterministic check can't see.

All three must pass for `qa_passed: true` in `metadata.json`. A post that ships with `qa_passed: false` should be reviewed in `draft_eval.json` before publishing — the operator decides whether the failures are minor (publish anyway) or fundamental (don't publish).

## Output schema (per post)
`blog-automation/output/<YYYY-MM-DD>-<slug>/`:
```
article.html            # The §7 BODY HTML, ready to paste into admin's rich-text editor
paste_sections.md       # All 8 labelled sections for per-field paste:
                        #   TITLE / SLUG / EXCERPT / BODY / COVER IMAGE BRIEF /
                        #   INLINE IMAGE BRIEFS / INTERNAL LINKS USED /
                        #   EXTERNAL CITATIONS USED
blog_post.md            # Markdown copy of the body (backward compat - reels read this)
research_brief.json     # Agent 0 output: stats, pain points, CTA ideas, citation URLs
draft_eval.json         # validator stats + evaluator scores + retry history
linkedin_post.md
twitter_thread.md
threads_post.md
metadata.json           # title, slug, qa_passed, word_count, internal_links_used,
                        # external_links_used, evaluator_score, retry_count, model, ...
```

## What the writer MUST produce (enforced by the validator)
- 1,800-2,200 words of body (NOT MORE, NOT LESS)
- `<div class="tldr">` block with 3-5 bullets directly under the intro
- 4-7 H2 sections, mixed phrasing (not every H2 a "How to X")
- At least one paragraph of plausible first-hand experience (specific scene, specific number)
- Exactly 3-5 contextual internal links in the body, every URL from `hexa_urls.json`
- 6-12 external citations, each from research_brief.external_citation_candidates
- FAQ block with 3-5 real buyer questions
- Closing: ONE paragraph + ONE concrete next step. NO "Conclusion" heading.
- NO em dashes, NO en dashes (brand rule, hard-fail)
- "Hexa AI Agency" / "hexaaiagency.com" spelled correctly (hard-fail)
- Zero banned phrases ("delve", "leverage" as verb, "in today's fast-paced", "robust", "seamless", etc.)

## Edge cases
- **ANTHROPIC_API_KEY missing or revoked**: research, drafting, and evaluator all hard-fail. Surface the auth error and stop — no point burning Tavily credits with no LLM to synthesize. Memory entry [project_anthropic_key_status.md] tracks past revocation incidents.
- **TAVILY_API_KEY missing**: research stage hard-fails. Without sourced stats the post will have nothing real to cite and Google will ignore it.
- **Research returns 0 stats**: hard-fail. Either the topic is too niche for web research or Tavily is throttled. Try a broader query or add `--no-cache` flag.
- **Validator fails after MAX_RETRIES (default 2)**: the draft is saved anyway with `qa_passed: false`. Operator reviews `draft_eval.json` to decide whether the failures are cosmetic (publish with manual fixes) or structural (regenerate from scratch).
- **Internal link allowlist missing a URL**: writer will be told only to link to URLs in `hexa_urls.json` and the validator rejects anything else. If the operator needs a link to a brand-new service/case-study page, add it to `hexa_urls.json` first.
- **Topic doesn't map to a service**: the writer is instructed to refuse (writer guide §12). If the model returns a refusal instead of a post, surface the message and ask the operator to either pick a different topic or extend `hexa_urls.json`.
- **Operator pastes an HTML body with images**: the rich-text admin auto-uploads inline images to Supabase storage. Inline image placeholders (`<!-- IMAGE N: ... -->`) in the BODY are spec'd in `INLINE IMAGE BRIEFS` so the operator knows what to find/generate.

## Learnings
- The previous prompt described the rules but did not enforce them; 5/6 audited posts had 0 internal body links and 0 TL;DR despite the prompt asking for both. **The validator is what forces compliance, not the prompt language.**
- First-hand experience signal is the dominant 2026 EEAT factor. Without "we built this for…" / "when we shipped…", the post reads as textbook summary and gets de-prioritized.
- Word count of 2k is the sweet spot. The existing 6k-12k posts are over-padded and trigger AI-content suspicion.
- 6-12 external citations is the indexing-friendly density. Below 6 = "where did these claims come from?", above 12 = link stuffing.
- The niche-runner pattern (pre-baked EXPERT_ANSWERS) is the most reliable path to a great post — operator playbook content is the strongest first-hand signal. Use a niche runner whenever a niche runner exists for the topic.
- The research brief is REQUIRED for citation quality. Drafting from `user_answers` alone produces vague claims with no source URLs to cite.
- TODO: cross-check `EXPERT_ANSWERS` stats against the research brief and flag unverifiable claims. Currently the writer trusts EXPERT_ANSWERS as ground truth.
