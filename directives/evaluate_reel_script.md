# Directive: Evaluate Reel Script (Agent 1)

## Goal
Pre-render gate. Score a generated reel script across 9 lead-gen dimensions BEFORE we burn Pexels and ElevenLabs credits. If the script is weak, regenerate (with critique fed back) up to 2 times. If still weak, surface to user without spending another dollar.

## When to invoke
- Automatically: as Step 1b of `run_daily_reels.py`, immediately after `generate_reel_script.py` and before Pexels downloads.
- Manually: any time you want to score an existing config without re-rendering.

## Inputs
- `--script` (the generated config.json with slides, voiceover_script, cta_keyword)
- `--research-brief` (the brief from Agent 0 — used to verify the script's stats are sourced, not hallucinated)
- `--niche`, `--topic`, `--reel-type` (for context)
- `--output` (path for `script_eval.json`)

## Tools / Scripts
- `execution/evaluate_reel_script.py` — entry point
- Anthropic (`ANTHROPIC_API_KEY` in `.env`, model `claude-opus-4-7`)

## Rubric (9 dimensions, 1-5 integer each)

| # | Dimension | Notes |
|---|---|---|
| 1 | hook_strength | Scroll-stop in 1.5s. Stat shock, contrarian, callout, or curiosity gap. Banned: "Did you know", "Most people", "Imagine if". Bonus for $ or time amount in first 6 words. |
| 2 | lead_gen_intent | Sells a service-business outcome a viewer can BUY. Not thought-leadership. |
| 3 | retention_pacing | A new beat every ~3s. No flat middle. |
| 4 | specificity | Real numbers, real tool names. No "leverage AI" mush. |
| 5 | cta_clarity | "Comment <KEYWORD> for <SPECIFIC DELIVERABLE>". Concrete deliverable, not "more info". |
| 6 | voiceover_naturalness | Conversational, breath-friendly, ~2.5 wps. |
| 7 | footage_concreteness | Scenes, not topics. Banned cliches: handshake, abstract data viz, "AI future technology". |
| 8 | format_compliance | No em/en dashes. Last slide is `cta`. Emphasis word in slide text. |
| 9 | **research_fidelity [HARD GATE >= 4]** | Every number traces to brief's `key_stats`. CTA deliverable from brief. No invented numbers. |

## Pass logic
- `passed = (avg >= 3.8) AND (min_dim >= 3) AND (research_fidelity >= 4)` — all three.
- `regenerate = (not passed) AND (avg >= 2.5)` — soft fail, eligible for retry.
- `research_fidelity < 4` always sets `regenerate=true` (fix is mechanical).
- `passed=false AND regenerate=false` — hard fail. Surface to user.

Thresholds via env vars: `SCRIPT_EVAL_MIN_AVG=3.8`, `SCRIPT_EVAL_MIN_DIM=3`, `SCRIPT_EVAL_HARD_FAIL_AVG=2.5`, `SCRIPT_EVAL_RESEARCH_MIN=4`.

## Deterministic pre-checks (cheap, run before the Claude call)
1. **Numbers-in-brief check**: extract every number from the script (voiceover + slide text). Any number not in the brief's `key_stats` and not a small rhetorical integer (1-9) is flagged as `suspicious_numbers_not_in_brief`.
2. **Format check**: em/en dashes, last-slide-cta, emphasis-in-text.

Findings from these are injected into the eval JSON as `deterministic_findings` so the regenerator sees them in the critique.

## Output schema (`script_eval.json`)

```json
{
  "dimensions": {
    "hook_strength":         {"score": 4, "note": "..."},
    "lead_gen_intent":       {"score": 5, "note": "..."},
    "retention_pacing":      {"score": 4, "note": "..."},
    "specificity":           {"score": 4, "note": "..."},
    "cta_clarity":           {"score": 5, "note": "..."},
    "voiceover_naturalness": {"score": 4, "note": "..."},
    "footage_concreteness":  {"score": 3, "note": "Slide 3 too generic"},
    "format_compliance":     {"score": 5, "note": "..."},
    "research_fidelity":     {"score": 4, "note": "..."}
  },
  "critique": "Plain English. Reference specific slides. Tell the regenerator exactly what to change.",
  "deterministic_findings": {"suspicious_numbers_not_in_brief": ["..."], "format_issues": ["..."]},
  "passed": false,
  "regenerate": true,
  "overall_score": 4.0,
  "min_dimension_score": 3,
  "model": "claude-opus-4-7",
  "tokens_used": 1240,
  "thresholds_used": {...}
}
```

## Retry-with-critique loop (in `run_daily_reels.py`)
```
for attempt in 0..MAX_SCRIPT_RETRIES:
    generate_reel_script.py (with --critique=<prev critique> if attempt > 0)
    evaluate_reel_script.py
    if eval.passed: break
    if not eval.regenerate: HARD FAIL, return
    critique = eval.critique
else:
    EXHAUSTED RETRIES, return
```

`MAX_SCRIPT_RETRIES = 2` by default (overridable via `SCRIPT_EVAL_MAX_RETRIES` env var). Cost ceiling: 3 generations + 3 evals = ~6 Opus calls per reel before we touch a paid stock API.

## Edge Cases
- **Generator returns malformed JSON**: the generator script itself dies; orchestrator returns `script_generation_failed`.
- **Evaluator returns malformed JSON**: subprocess returns non-zero; orchestrator detects missing output file and surfaces `script_eval_failed`.
- **Brief missing or empty**: evaluator still runs, but `research_fidelity` will score low. Orchestrator should have already short-circuited via the Step 0 brief-pass check.

## Tradeoffs
- **Generator and evaluator are both Claude** — they share blind spots. The deterministic number-check is the backstop; if Claude misses a hallucinated stat, the regex usually catches it.
- **Over-strict on `research_fidelity`**: if the brief has 3 stats and the script uses 1, that's fine. The check fires only when the script invents NEW numbers.
- **Adversarial system prompt**: evaluator is told "you are a skeptical performance marketer who has seen a thousand of these" to push it away from rubber-stamping.

## Learnings (update as patterns emerge)
- Hooks that include a dollar amount in the first 6 words consistently score 4-5 on hook_strength.
- CTAs that name the deliverable ("the no-show calculator") score 5; CTAs that say "the playbook" score 3.
- Banned footage cliches catch ~30% of first-attempt scripts; regeneration with the critique fixes them.
