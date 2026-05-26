#!/usr/bin/env python3
"""
TopicResearcher (Agent 0): Tavily web search + Claude synthesis.

Produces a research brief (real stats with source URLs, pain points, hook angles,
CTA deliverable ideas) for a reel topic, so script generation runs against real
data instead of training-set guesses.

Usage:
    python3 execution/research_topic.py \\
      --niche dental --reel-type pas --topic "dental no-shows" \\
      --output workspace/reels/2026-05-26-dental-no-shows/research_brief.json

    python3 execution/research_topic.py \\
      --niche general --topic "AI agency ROI" \\
      --output -            # write JSON to stdout
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
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

try:
    from tavily import TavilyClient
except ImportError:
    print("Error: tavily-python not installed. Run: pip3 install tavily-python", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None


CACHE_DIR = Path(project_root) / "workspace" / ".research_cache"

SYSTEM_PROMPT = """You are a skeptical B2B research analyst building a brief for a 15-30 second Instagram Reel that needs to generate leads for an AI automation agency.

You will be given:
  - A niche (e.g. dental, property management, cleaning, HVAC, general SMB)
  - A topic (e.g. "dental no-shows")
  - A reel type (pas, before_after, lead_magnet, trend)
  - Raw web search results from Tavily (titles, URLs, content snippets)

Your job: extract from the sources ONLY information that is credible, specific, and recent. You are NOT allowed to invent numbers. If a stat lacks a credible source in the search results, exclude it.

OUTPUT — respond with ONLY valid JSON, no markdown wrapping, matching this schema:

{
  "key_stats": [
    {
      "stat": "Concrete one-sentence statement with a number",
      "source_url": "https://exact-url-from-the-search-results",
      "source_name": "Publisher or report name as shown in the source",
      "confidence": "high" | "medium" | "low"
    }
  ],
  "pain_points": [
    "One acute pain point in the viewer's daily reality (not abstract)",
    "..."
  ],
  "current_solutions_in_market": [
    {"name": "Vendor or method name", "approach": "what it does in one line", "limitation": "why it falls short"}
  ],
  "competitor_hook_patterns_seen": [
    "Hook patterns observed in this space (for inspiration, never copy verbatim)"
  ],
  "recommended_hook_angles": [
    {
      "angle": "money-on-the-table | identity-attack | inside-the-room | counter-conventional | one-question-diagnostic",
      "example": "A specific hook line for THIS topic in the angle style",
      "uses_stats": ["stat_key_or_excerpt"]
    }
  ],
  "cta_deliverable_ideas": [
    {"name": "Specific deliverable name (calculator, checklist, template)", "deliverability": "PDF | Notion doc | Sheet | web tool"}
  ]
}

RULES:
- 3-7 key_stats. Every stat MUST include source_url copied EXACTLY from the search results (do not paraphrase URLs).
- 2-5 pain_points, written from the viewer's POV ("Front desk spends 4 hours/week on...", not "Practices suffer from...").
- 2-4 recommended_hook_angles. The "example" field must be a usable hook line, not a description.
- 2-4 cta_deliverable_ideas. Each must be something a single person could plausibly produce (no enterprise platforms).
- If a search result is from a forum, blog, or unsourced claim, mark confidence "low".
- If you cannot find 3 credible stats with source URLs, return what you have anyway — the validation step downstream will catch it.

NEVER use em or en dashes anywhere. Use hyphens or commas.
"""


def cache_key(niche: str, topic: str) -> Path:
    """Cache file path for a niche+topic+day combo."""
    today = date.today().isoformat()
    slug_niche = niche.lower().replace(" ", "-")
    slug_topic = topic.lower().replace(" ", "-")[:60]
    safe = "".join(c for c in f"{slug_niche}--{slug_topic}--{today}" if c.isalnum() or c in "-_")
    return CACHE_DIR / f"{safe}.json"


def tavily_search(client: TavilyClient, query: str, max_results: int = 5) -> list:
    """Run one Tavily search, return list of {title, url, content} dicts."""
    try:
        resp = client.search(query=query, search_depth="advanced", max_results=max_results)
        results = []
        for r in resp.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": (r.get("content", "") or "")[:800],
            })
        return results
    except Exception as e:
        print(f"  Tavily search failed for '{query}': {e}", file=sys.stderr)
        return []


def build_queries(niche: str, topic: str, reel_type: str) -> list:
    """Build the search queries for this niche+topic+reel-type."""
    year = date.today().year
    queries = [
        f"{topic} {niche} statistics {year}",
        f"{topic} cost to {niche} business",
        f"{niche} {topic} automation case study",
    ]
    if reel_type == "trend":
        queries.append(f"{topic} {niche} recent news")
    return queries


def validate_source_urls(brief: dict) -> tuple:
    """HEAD-check every source_url; drop stats whose URL 404s. Returns (validated_brief, dropped_count)."""
    if not requests:
        return brief, 0
    dropped = 0
    kept = []
    for stat in brief.get("key_stats", []):
        url = stat.get("source_url", "")
        if not url:
            dropped += 1
            continue
        try:
            r = requests.head(url, timeout=8, allow_redirects=True)
            if r.status_code < 400:
                kept.append(stat)
            else:
                dropped += 1
        except Exception:
            # Network/timeout — be lenient and keep it; the user can spot-check.
            kept.append(stat)
    brief["key_stats"] = kept
    return brief, dropped


def synthesize(anthropic_client, model: str, niche: str, topic: str, reel_type: str, raw_results: list) -> dict:
    """Feed Tavily results to Claude and parse a research brief."""
    sources_block = "\n\n".join(
        f"### Source [{i+1}]: {r['title']}\nURL: {r['url']}\n{r['content']}"
        for i, r in enumerate(raw_results)
    )

    user_prompt = f"""Niche: {niche}
Topic: {topic}
Reel type: {reel_type}

Raw search results below. Extract a research brief per the schema. Cite source_url exactly from these results.

{sources_block}
"""

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    brief = json.loads(text)
    brief["_tokens_used"] = getattr(response.usage, "input_tokens", 0) + getattr(response.usage, "output_tokens", 0)
    return brief


def evaluate_brief(brief: dict) -> tuple:
    """Apply pass/fail logic from the plan. Returns (passed, warnings)."""
    warnings = []
    stats = brief.get("key_stats", [])
    if len(stats) < 3:
        warnings.append(f"only {len(stats)} key_stats (need >= 3)")
    missing_url = [i for i, s in enumerate(stats) if not s.get("source_url")]
    if missing_url:
        warnings.append(f"stats missing source_url at indexes {missing_url}")
    if len(brief.get("pain_points", [])) < 2:
        warnings.append("fewer than 2 pain_points")
    if len(brief.get("recommended_hook_angles", [])) < 2:
        warnings.append("fewer than 2 recommended_hook_angles")
    passed = len(warnings) == 0
    return passed, warnings


def main():
    parser = argparse.ArgumentParser(description="Research a reel topic and emit a brief.")
    parser.add_argument("--niche", required=True, help="dental, property, cleaning, hvac, general, etc.")
    parser.add_argument("--topic", required=True, help="What the reel is about, e.g. 'dental no-shows'")
    parser.add_argument("--reel-type", default="pas", choices=["pas", "before_after", "lead_magnet", "trend"])
    parser.add_argument("--output", required=True, help="Output path for research_brief.json (use '-' for stdout)")
    parser.add_argument("--no-cache", action="store_true", help="Bypass the 24h cache")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Cache check
    cf = cache_key(args.niche, args.topic)
    if cf.exists() and not args.no_cache:
        print(f"  [cache hit] {cf.name}")
        with open(cf) as f:
            brief = json.load(f)
    else:
        # Anthropic precondition
        if not os.getenv("ANTHROPIC_API_KEY"):
            err = {"passed": False, "warnings": ["ANTHROPIC_API_KEY not set"], "error": "missing_anthropic_key"}
            print(json.dumps(err, indent=2))
            sys.exit(2)
        if not os.getenv("TAVILY_API_KEY"):
            err = {"passed": False, "warnings": ["TAVILY_API_KEY not set"], "error": "missing_tavily_key"}
            print(json.dumps(err, indent=2))
            sys.exit(2)

        # Tavily
        tav = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        queries = build_queries(args.niche, args.topic, args.reel_type)
        print(f"  Researching: {args.topic} ({args.niche}, {args.reel_type})")
        all_results = []
        seen_urls = set()
        for q in queries:
            print(f"    [tavily] {q}")
            for r in tavily_search(tav, q):
                if r["url"] and r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_results.append(r)

        if not all_results:
            err = {
                "niche": args.niche,
                "topic": args.topic,
                "reel_type": args.reel_type,
                "research_date": date.today().isoformat(),
                "key_stats": [],
                "pain_points": [],
                "recommended_hook_angles": [],
                "cta_deliverable_ideas": [],
                "passed": False,
                "warnings": ["no web research available"],
                "tavily_queries_run": len(queries),
                "tavily_results_returned": 0,
            }
            print(json.dumps(err, indent=2))
            sys.exit(3)

        print(f"  Synthesizing brief from {len(all_results)} unique sources")
        model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
        anth = anthropic.Anthropic()
        try:
            brief = synthesize(anth, model, args.niche, args.topic, args.reel_type, all_results)
        except anthropic.AuthenticationError as e:
            err = {
                "passed": False,
                "warnings": ["Anthropic API rejected the key (401)"],
                "error": f"anthropic_auth: {str(e)[:200]}",
            }
            if args.output == "-":
                print(json.dumps(err, indent=2))
            else:
                os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
                with open(args.output, "w") as f:
                    json.dump(err, f, indent=2)
                print(f"  Anthropic auth failed. Wrote error to {args.output}")
            sys.exit(2)
        except anthropic.APIError as e:
            err = {
                "passed": False,
                "warnings": [f"Anthropic API error: {str(e)[:200]}"],
                "error": "anthropic_api",
            }
            if args.output == "-":
                print(json.dumps(err, indent=2))
            else:
                os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
                with open(args.output, "w") as f:
                    json.dump(err, f, indent=2)
                print(f"  Anthropic API error. Wrote error to {args.output}")
            sys.exit(2)

        # Validate URLs
        brief, dropped = validate_source_urls(brief)
        if dropped:
            print(f"  Dropped {dropped} stats with 404/missing source_url")

        # Annotate metadata
        brief["niche"] = args.niche
        brief["topic"] = args.topic
        brief["reel_type"] = args.reel_type
        brief["research_date"] = date.today().isoformat()
        brief["model"] = model
        brief["tavily_queries_run"] = len(queries)
        brief["tavily_results_returned"] = len(all_results)
        brief["tokens_used"] = brief.pop("_tokens_used", 0)

        # Cache
        with open(cf, "w") as f:
            json.dump(brief, f, indent=2)

    # Evaluate
    passed, warnings = evaluate_brief(brief)
    brief["passed"] = passed
    brief["warnings"] = warnings

    # Emit
    out_text = json.dumps(brief, indent=2)
    if args.output == "-":
        print(out_text)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(out_text)
        print(f"  Output: {args.output}")
        print(f"  passed: {passed}, key_stats: {len(brief.get('key_stats', []))}, hook_angles: {len(brief.get('recommended_hook_angles', []))}")
        if warnings:
            print(f"  warnings: {warnings}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
