#!/usr/bin/env python3
"""
BlogEvaluator (Agent 1): LLM eval that scores a blog draft on a 9-dimension
rubric and returns a critique the orchestrator can feed back to the writer.

Runs AFTER blog_validator.py has already passed (no point burning tokens on a
draft that fails wordcount or has an em dash). Catches the subjective things
the deterministic check can't: E-E-A-T strength, citation quality, AI-tells in
the prose, search-intent fit, conversion clarity.

Mirrors execution/evaluate_reel_script.py — same interface, blog-tuned rubric.

Usage as a module:
    from modules.blog_evaluator import evaluate_blog
    eval_result = evaluate_blog(article_text, research_brief, topic, niche)
"""

import json
import os
import sys

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed. Run: pip3 install anthropic", file=sys.stderr)
    raise


# Thresholds (overridable via env)
MIN_AVG = float(os.getenv("BLOG_EVAL_MIN_AVG", "3.8"))
MIN_DIM = int(os.getenv("BLOG_EVAL_MIN_DIM", "3"))
HARD_FAIL_AVG = float(os.getenv("BLOG_EVAL_HARD_FAIL_AVG", "2.5"))
RESEARCH_MIN = int(os.getenv("BLOG_EVAL_RESEARCH_MIN", "4"))


SYSTEM_PROMPT = """You are a skeptical senior SEO + content strategist who has reviewed thousands of B2B service-business blog posts. You score drafts strictly on a 9-dimension rubric. You DO NOT rewrite the draft.

You will be given:
  - The blog draft (HTML + Markdown mixed is fine)
  - The research brief the draft was supposed to be grounded in
  - Topic + niche

Score each dimension on a 1-5 integer scale. For any dimension <= 3, include a one-sentence critique with a concrete fix. The aggregate `critique` field is what the writer will see on regeneration - make it actionable, reference specific paragraphs or claims to change.

RUBRIC (1-5 each, integer):

1. eeat_experience  [the dominant Google signal in 2026]
   At least one paragraph of plausible first-hand experience. Not "in our experience, AI helps..." (generic) but "when we shipped this for a 45-person commercial cleaning company in March 2026, the vendor name parsing on hand-typed PDFs broke at 3am..." (specific scene, specific number, specific failure). If the post reads like a textbook summary, this is a 2.

2. search_intent_fit
   The post answers ONE specific buyer query (informational, comparison, how-to). Title and H2s reflect that query and likely variants. If the post mixes top-of-funnel ("what is AI") with bottom-of-funnel ("AI invoice processing in QuickBooks"), this is a 3.

3. specificity
   Real tool names, real numbers, real industries. "$5K/month", "HubSpot Workflows + Claude 4.6", "47 minutes to 8" beats "many businesses save time". Generic ROI claims with no source = 2.

4. citation_quality  [HARD GATE: must be >= 4]
   - Every external link supports a load-bearing claim (not padding)
   - Numerical claims trace back to research brief stats
   - No invented stats
   - No links to competitor sales pages without commentary
   If you find a number in the post that doesn't match any stat in the brief, this is a 2.

5. internal_linking
   3-5 contextual body internal links. Anchor text describes the destination ("AI workflow automation services", not "click here"). All link targets must be from the hexa_urls.json allowlist that was injected into the writer prompt.

6. structure
   Clear H1 / TL;DR / 4-7 H2s / FAQ block / short closing. H2s phrased as real questions or sub-tasks. NOT every H2 a "How to X" — vary statement / question / noun phrase.

7. voice_no_ai_tells
   Senior practitioner voice. Short sentences mixed with longer. No four-bullet-section uniformity. No banned phrases (delve, leverage as verb, in today's fast-paced, robust, seamless, cutting-edge, navigate the complexities). If you'd be embarrassed to publish under your name, this is a 2.

8. conversion_clarity
   "You" language. 1-2 inline soft CTAs where natural. One concrete closing CTA (cal.com/hexaiagency or a service page) - not "contact us today!". No fake social proof.

9. completeness
   Reader can leave without needing another article. Trade-offs are honest (when NOT to use AI). Edge cases / failure modes mentioned. If the post reads as encyclopedic summary with no opinion, this is a 3.

OUTPUT - respond with ONLY valid JSON, no markdown wrapping:

{
  "dimensions": {
    "eeat_experience":      {"score": 4, "note": "..."},
    "search_intent_fit":    {"score": 5, "note": "..."},
    "specificity":          {"score": 4, "note": "..."},
    "citation_quality":     {"score": 4, "note": "..."},
    "internal_linking":     {"score": 5, "note": "..."},
    "structure":            {"score": 4, "note": "..."},
    "voice_no_ai_tells":    {"score": 4, "note": "..."},
    "conversion_clarity":   {"score": 5, "note": "..."},
    "completeness":         {"score": 4, "note": "..."}
  },
  "critique": "Single paragraph in plain English. List concrete fixes the writer should apply on the next pass. Reference specific paragraphs, claims, or H2s to change."
}

Be strict on eeat_experience and citation_quality - those drive 80% of whether Google indexes the post.
Be lenient on word-choice style if the content is strong.
NEVER use em or en dashes anywhere in your output.
"""


def evaluate_blog(article_text: str, research_brief: dict, topic: str, niche: str,
                  model: str = None) -> dict:
    """
    Score the blog draft. Returns the eval dict with pass/regenerate flags.
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"passed": False, "regenerate": False, "error": "ANTHROPIC_API_KEY not set"}

    model = model or os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    anth = anthropic.Anthropic()

    user_prompt = f"""Topic: {topic}
Niche: {niche}

DRAFT TO EVALUATE:
{article_text}

RESEARCH BRIEF (the draft should be grounded in this):
{json.dumps(research_brief, indent=2)}

Score per the rubric. Be strict on eeat_experience, citation_quality, internal_linking.
"""

    try:
        response = anth.messages.create(
            model=model,
            max_tokens=2500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.AuthenticationError as e:
        return {"passed": False, "regenerate": False, "error": f"anthropic_auth: {str(e)[:200]}"}
    except anthropic.APIError as e:
        return {"passed": False, "regenerate": False, "error": f"anthropic_api: {str(e)[:200]}"}

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        return {"passed": False, "regenerate": True, "error": f"eval response not valid JSON: {e}", "raw": text[:500]}

    # Compute pass / regenerate
    dims = result.get("dimensions", {})
    scores = [d.get("score", 0) for d in dims.values()]
    if not scores:
        result.update({"passed": False, "regenerate": False, "overall_score": 0.0, "min_dimension_score": 0})
        return result

    avg = sum(scores) / len(scores)
    min_dim = min(scores)
    citation = dims.get("citation_quality", {}).get("score", 0)

    passed = (avg >= MIN_AVG) and (min_dim >= MIN_DIM) and (citation >= RESEARCH_MIN)
    regenerate = (not passed) and (avg >= HARD_FAIL_AVG)
    # citation_quality fails are always worth a retry — the fix is mechanical (swap a number for a brief-stat)
    if not passed and citation < RESEARCH_MIN:
        regenerate = True

    result.update({
        "overall_score": round(avg, 2),
        "min_dimension_score": min_dim,
        "passed": passed,
        "regenerate": regenerate,
        "model": model,
        "tokens_used": getattr(response.usage, "input_tokens", 0) + getattr(response.usage, "output_tokens", 0),
        "thresholds_used": {
            "min_avg": MIN_AVG,
            "min_dim": MIN_DIM,
            "hard_fail_avg": HARD_FAIL_AVG,
            "citation_min": RESEARCH_MIN,
        },
    })
    return result
