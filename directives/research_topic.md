# Directive: Research Topic (Agent 0)

## Goal
Produce a research brief (real stats with source URLs, pain points, hook angles, CTA deliverables) for a reel topic BEFORE the script is generated. No script is allowed to be generated off the model's training data alone — every claim must be sourced.

## When to invoke
- Automatically: as Step 0 of `run_daily_reels.py` for every reel.
- Manually (single-reel mode): run before `generate_reel_script.py` and pass the brief in via `--research-brief`.

## Inputs
- `--niche` (dental, property, cleaning, hvac, general, etc.)
- `--topic` (what the reel is about, e.g. "dental no-shows")
- `--reel-type` (pas, before_after, lead_magnet, trend)
- `--output` (path for `research_brief.json`)

## Tools / Scripts
- `execution/research_topic.py` — the entry point
- Tavily (`TAVILY_API_KEY` in `.env`) — web search
- Anthropic (`ANTHROPIC_API_KEY` in `.env`) — synthesis (model: `claude-opus-4-7`)

## Process

1. **Search queries**: 3-4 Tavily searches per topic. Pattern:
   - `<topic> <niche> statistics <year>` → industry stats
   - `<topic> cost to <niche> business` → dollar amounts
   - `<niche> <topic> automation case study` → real outcomes
   - For `trend` reels: also `<topic> <niche> recent news`
2. **Dedupe** by URL across all query results.
3. **Synthesize** with Claude. The system prompt is strict: extract ONLY stats with a credible source URL from the search results. Never invent numbers.
4. **Validate URLs**: HEAD-check every `source_url`. Drop stats whose URL 404s.
5. **Pass logic**: brief passes iff (>=3 key_stats with source_url) AND (>=2 pain_points) AND (>=2 recommended_hook_angles).
6. **Cache**: results are cached by `(niche, topic, YYYY-MM-DD)` in `workspace/.research_cache/`. Re-running the same reel within 24h uses the cache.

## Output schema (`research_brief.json`)

```json
{
  "niche": "dental",
  "topic": "dental no-shows",
  "reel_type": "pas",
  "research_date": "2026-05-26",
  "key_stats": [
    {"stat": "...", "source_url": "...", "source_name": "...", "confidence": "high"}
  ],
  "pain_points": ["..."],
  "current_solutions_in_market": [{"name": "...", "approach": "...", "limitation": "..."}],
  "competitor_hook_patterns_seen": ["..."],
  "recommended_hook_angles": [{"angle": "...", "example": "...", "uses_stats": ["..."]}],
  "cta_deliverable_ideas": [{"name": "...", "deliverability": "..."}],
  "passed": true,
  "warnings": [],
  "model": "claude-opus-4-7",
  "tavily_queries_run": 3,
  "tavily_results_returned": 12,
  "tokens_used": 6200
}
```

## Edge Cases
- **No web results**: brief sets `passed=false, warnings=["no web research available"]`. The orchestrator returns early with `research_failed=true` — no script is generated, no Pexels spend.
- **API key revoked**: hard fail with `error: "missing_anthropic_key"`. Restore the key and re-run.
- **Tavily rate limit**: searches that fail individually are skipped; if ALL fail, the brief returns empty and the orchestrator stops.
- **Obscure topic**: if Tavily returns junk (low-relevance results), Claude will still try to extract what it can but most stats will be `confidence: "low"` or excluded. The pass-logic check on `len(key_stats) >= 3` is the safety net.

## Sources policy
- Prefer authoritative industry reports (Gartner, IBM, Forrester, ADA, trade associations) over blog opinion pieces.
- Stats must be ≤ 24 months old where possible. If a stat is older, it should still be flagged with `confidence: "medium"` or lower.
- If a single source URL produces 3+ stats, that's a sign the synthesis is being lazy — diversify sources.

## Learnings
- Tavily's `search_depth="advanced"` gives noticeably better source quality than `basic` (the default used elsewhere for image search).
- `max_results=5` per query is the sweet spot — more than that adds noise; fewer misses depth.
- HEAD-check validation drops ~5-15% of stats on average. Worth the time.
- Cache hits save the user $0.05-0.10 per re-run.
