#!/usr/bin/env python3
"""
ScriptEvaluator (Agent 1): Pre-render gate that scores a reel script across 9
lead-gen dimensions and decides pass / regenerate / hard-fail.

Reads:
  - The generated script JSON (from generate_reel_script.py — slides[], voiceover_script, cta_keyword, ig_caption_draft)
  - The research brief JSON (from research_topic.py — used to verify the script's
    stats are actually from the brief and not hallucinated)

Emits a script_eval.json that the orchestrator (run_daily_reels.py) uses to
decide whether to proceed to Pexels + ElevenLabs spend, or regenerate.

Usage:
    python3 execution/evaluate_reel_script.py \\
      --script workspace/reels/<slug>/script.json \\
      --research-brief workspace/reels/<slug>/research_brief.json \\
      --niche dental --reel-type pas --topic "dental no-shows" \\
      --output workspace/reels/<slug>/script_eval.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed. Run: pip3 install anthropic", file=sys.stderr)
    sys.exit(1)


# Threshold defaults (overridable via env vars)
MIN_AVG = float(os.getenv("SCRIPT_EVAL_MIN_AVG", "3.8"))
MIN_DIM = int(os.getenv("SCRIPT_EVAL_MIN_DIM", "3"))
HARD_FAIL_AVG = float(os.getenv("SCRIPT_EVAL_HARD_FAIL_AVG", "2.5"))
RESEARCH_MIN = int(os.getenv("SCRIPT_EVAL_RESEARCH_MIN", "4"))


SYSTEM_PROMPT = """You are a skeptical performance marketer who has reviewed thousands of short-form lead-gen reels for B2B service businesses. You score scripts strictly on a 9-dimension rubric. You DO NOT rewrite the script.

You will be given:
  - The generated script JSON (slides, voiceover_script, cta_keyword)
  - The research brief JSON the script was supposed to be grounded in (key_stats with source_urls, recommended_hook_angles, cta_deliverable_ideas)

Score each dimension on a 1-5 integer scale. For any dimension scoring <= 3, include a one-sentence critique with a concrete fix. The aggregate `critique` field is what the regeneration step will see — make it actionable.

RUBRIC (1-5 each, integer):

1. hook_strength
   Slide 1 stops the scroll in 1.5s. Use stat shock, contrarian claim, callout, or curiosity gap. BANNED openers: "Did you know", "Most people", "Imagine if", "Have you ever". Bonus for a dollar amount or time amount in the first 6 words.

2. lead_gen_intent
   Reel sells a service-business outcome a viewer can BUY from Hexa AI Agency. Not thought-leadership, not AI-trend commentary, not generic Twitter takes. The reel implies "this person should call Hexa", not "this person should retweet".

3. retention_pacing
   A new tension/payoff/twist every ~3s of voiceover. No flat middle. Reading rate ~2.5 wps. If voiceover is over 30s, it must have at least 3 distinct beats.

4. specificity
   Real numbers, real tool names, real workflows. No "leverage AI to drive results" mush. Reels that say "$1,500/month" beat reels that say "thousands".

5. cta_clarity
   "Comment <KEYWORD> for <SPECIFIC DELIVERABLE>". Keyword is a natural typeable word. Deliverable is a concrete noun (the calculator, the checklist, the 7-prompt workflow), not "more info" or vague "the playbook".

6. voiceover_naturalness
   Reads like one person talking to one person. Short sentences. Breath-friendly. No corporate copy. Sanity-check: total VO word_count divided by 2.5 should yield expected reel length (15-30s for short, 60-90s for deep).

7. footage_concreteness
   Every footage_query depicts a SPECIFIC SCENE, not a topic. BANNED cliches: "business handshake", "abstract data viz", "AI future technology", "business growth", "happy team celebrating".

8. format_compliance
   - NO em dashes or en dashes anywhere
   - Last slide type == "cta"
   - Emphasis word appears verbatim in slide text
   - Slide text and voiceover_script align (same beat order)

9. research_fidelity   [HARD GATE: this must be >= 4]
   - Every numerical claim in the script traces back to a stat in the research brief's key_stats
   - CTA deliverable is from the brief's cta_deliverable_ideas OR is something Hexa can plausibly produce
   - Hook borrows from recommended_hook_angles, not copied verbatim from competitor_hook_patterns_seen
   - NO invented numbers
   If any number in the script cannot be matched to a key_stat in the brief, score this dimension <= 2 and call it out.

OUTPUT — respond with ONLY valid JSON, no markdown wrapping:

{
  "dimensions": {
    "hook_strength":         {"score": 4, "note": "..."},
    "lead_gen_intent":       {"score": 5, "note": "..."},
    "retention_pacing":      {"score": 4, "note": "..."},
    "specificity":           {"score": 4, "note": "..."},
    "cta_clarity":           {"score": 5, "note": "..."},
    "voiceover_naturalness": {"score": 4, "note": "..."},
    "footage_concreteness":  {"score": 3, "note": "Slide 3 query 'business success' too generic"},
    "format_compliance":     {"score": 5, "note": "..."},
    "research_fidelity":     {"score": 4, "note": "..."}
  },
  "critique": "Single paragraph in plain English. List the concrete fixes the regenerator should apply. Reference specific slide numbers and exact text to change."
}

Be strict on hook_strength and cta_clarity — those drive 80% of performance.
Be lenient on accent_color and font choices.
NEVER use em or en dashes anywhere.
"""


# Deterministic pre-check: find every number in the script, check if a similar
# number appears in the brief's key_stats. If a script number has no match in
# the brief, that's a hallucination signal.
NUMBER_PATTERN = re.compile(r"\$?\d[\d,]*(\.\d+)?%?")


def script_numbers(script: dict) -> set:
    """Extract every numeric token from the script (slides + voiceover)."""
    text_blobs = [script.get("voiceover_script", "")]
    for s in script.get("slides", []):
        text_blobs.append(s.get("text", ""))
    found = set()
    for t in text_blobs:
        for m in NUMBER_PATTERN.findall(t):
            # findall returns the inner group when present; re.finditer is more reliable
            pass
        for m in NUMBER_PATTERN.finditer(t):
            tok = m.group(0).strip(",.")
            if tok and not tok.startswith("0."):  # skip trivial decimals
                found.add(tok)
    return found


def brief_numbers(brief: dict) -> set:
    """Extract every numeric token from the brief's key_stats."""
    found = set()
    for stat in brief.get("key_stats", []):
        for m in NUMBER_PATTERN.finditer(stat.get("stat", "")):
            tok = m.group(0).strip(",.")
            if tok and not tok.startswith("0."):
                found.add(tok)
    return found


def deterministic_research_check(script: dict, brief: dict) -> list:
    """Return a list of numeric tokens that appear in the script but not the brief."""
    s_nums = script_numbers(script)
    b_nums = brief_numbers(brief)
    suspicious = []
    for n in s_nums:
        if n in b_nums:
            continue
        # Allow common reel numbers that don't need brief-backing (slide counts, percentages
        # like "100%" that are rhetorical not factual). Heuristic: small ints under 10 are
        # usually rhetorical.
        try:
            v = float(n.replace("$", "").replace("%", "").replace(",", ""))
            if 0 < v < 10:
                continue
        except ValueError:
            pass
        suspicious.append(n)
    return suspicious


def deterministic_format_check(script: dict) -> list:
    """Check for em/en dashes and last-slide-cta. Returns list of issues."""
    issues = []
    blobs = [script.get("voiceover_script", "")]
    for s in script.get("slides", []):
        blobs.append(s.get("text", ""))
        blobs.append(s.get("footage_query", ""))
    for t in blobs:
        if "—" in t or "–" in t:
            issues.append("em/en dash found")
            break
    slides = script.get("slides", [])
    if slides and slides[-1].get("type") != "cta":
        issues.append(f"last slide type is '{slides[-1].get('type')}', expected 'cta'")
    for i, s in enumerate(slides):
        emphasis = s.get("emphasis", "")
        text = s.get("text", "")
        if emphasis and emphasis.lower() not in text.lower():
            issues.append(f"slide {i+1} emphasis '{emphasis}' not in slide text")
    return issues


def evaluate(anthropic_client, model: str, script: dict, brief: dict,
             niche: str, topic: str, reel_type: str) -> dict:
    """Call Claude to score the script. Returns the dimensions+critique dict."""
    user_prompt = f"""Niche: {niche}
Topic: {topic}
Reel type: {reel_type}

SCRIPT TO EVALUATE:
{json.dumps(script, indent=2)}

RESEARCH BRIEF (the script should be grounded in this):
{json.dumps(brief, indent=2)}

Score per the rubric. Be strict on hook_strength, cta_clarity, and research_fidelity.
"""

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    result = json.loads(text)
    result["_tokens_used"] = getattr(response.usage, "input_tokens", 0) + getattr(response.usage, "output_tokens", 0)
    return result


def apply_pass_logic(eval_result: dict) -> dict:
    """Compute passed/regenerate/hard-fail booleans + summary stats."""
    dims = eval_result.get("dimensions", {})
    scores = [d.get("score", 0) for d in dims.values()]
    if not scores:
        return {
            **eval_result,
            "passed": False,
            "regenerate": False,
            "overall_score": 0.0,
            "min_dimension_score": 0,
        }
    avg = sum(scores) / len(scores)
    min_dim = min(scores)
    research = dims.get("research_fidelity", {}).get("score", 0)

    passed = (avg >= MIN_AVG) and (min_dim >= MIN_DIM) and (research >= RESEARCH_MIN)
    regenerate = (not passed) and (avg >= HARD_FAIL_AVG)
    # research_fidelity is ALWAYS regenerate-eligible — the fix is mechanical
    if not passed and research < RESEARCH_MIN:
        regenerate = True

    eval_result["overall_score"] = round(avg, 2)
    eval_result["min_dimension_score"] = min_dim
    eval_result["passed"] = passed
    eval_result["regenerate"] = regenerate
    return eval_result


def main():
    parser = argparse.ArgumentParser(description="Evaluate a reel script for lead-gen quality.")
    parser.add_argument("--script", required=True, help="Path to script JSON from generate_reel_script.py")
    parser.add_argument("--research-brief", required=True, help="Path to research_brief.json from research_topic.py")
    parser.add_argument("--niche", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--reel-type", default="pas")
    parser.add_argument("--output", required=True, help="Output path for script_eval.json (use '-' for stdout)")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        err = {"passed": False, "regenerate": False, "error": "ANTHROPIC_API_KEY not set"}
        print(json.dumps(err, indent=2))
        sys.exit(2)

    with open(args.script) as f:
        script = json.load(f)
    with open(args.research_brief) as f:
        brief = json.load(f)

    # Deterministic pre-checks (cheap, no API calls)
    suspicious_nums = deterministic_research_check(script, brief)
    format_issues = deterministic_format_check(script)

    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    anth = anthropic.Anthropic()

    print(f"  Evaluating script: {args.topic} ({args.niche}, {args.reel_type})")
    if suspicious_nums:
        print(f"  [pre-check] suspicious numbers not in brief: {sorted(suspicious_nums)}")
    if format_issues:
        print(f"  [pre-check] format issues: {format_issues}")

    try:
        eval_result = evaluate(anth, model, script, brief, args.niche, args.topic, args.reel_type)
    except anthropic.AuthenticationError as e:
        err = {"passed": False, "regenerate": False, "error": f"anthropic_auth: {str(e)[:200]}"}
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(err, f, indent=2)
        print(f"  Anthropic auth failed. Wrote error to {args.output}")
        sys.exit(2)
    except anthropic.APIError as e:
        err = {"passed": False, "regenerate": False, "error": f"anthropic_api: {str(e)[:200]}"}
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(err, f, indent=2)
        print(f"  Anthropic API error. Wrote error to {args.output}")
        sys.exit(2)

    # Inject deterministic findings into the result so the regenerator sees them
    deterministic = {}
    if suspicious_nums:
        deterministic["suspicious_numbers_not_in_brief"] = sorted(suspicious_nums)
    if format_issues:
        deterministic["format_issues"] = format_issues
    if deterministic:
        eval_result["deterministic_findings"] = deterministic

    eval_result = apply_pass_logic(eval_result)
    eval_result["model"] = model
    eval_result["tokens_used"] = eval_result.pop("_tokens_used", 0)
    eval_result["thresholds_used"] = {
        "min_avg": MIN_AVG,
        "min_dim": MIN_DIM,
        "hard_fail_avg": HARD_FAIL_AVG,
        "research_min": RESEARCH_MIN,
    }

    out_text = json.dumps(eval_result, indent=2)
    if args.output == "-":
        print(out_text)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(out_text)
        print(f"  Output: {args.output}")
        print(f"  passed={eval_result['passed']} regenerate={eval_result['regenerate']} "
              f"avg={eval_result['overall_score']} min_dim={eval_result['min_dimension_score']}")
        if not eval_result["passed"]:
            print(f"  critique: {eval_result.get('critique', '')[:200]}...")

    sys.exit(0 if eval_result["passed"] else 1)


if __name__ == "__main__":
    main()
