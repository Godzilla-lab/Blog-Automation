#!/usr/bin/env python3
"""
BlogResearcher (Agent 0): Tavily web search + Claude synthesis.

Produces a research brief for a blog topic: 6-12 sourced stats with URLs, 3-5
buyer pain points, 2-4 angle hooks, 3-5 concrete CTA-deliverable ideas. The
writer then cites stats ONLY from this brief, so external links resolve and
numbers aren't hallucinated.

Mirrors execution/research_topic.py (the reel pipeline's Agent 0). The shape
is the same; the system prompt is tuned for long-form blog content (more stats,
deeper pain points, B2B service-business buyer persona).

Usage as a module:
    from modules.blog_research import research_blog_topic
    brief = research_blog_topic(topic="AI invoice processing in QuickBooks",
                                niche="finance")
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed. Run: pip3 install anthropic", file=sys.stderr)
    raise

try:
    from tavily import TavilyClient
except ImportError:
    print("Error: tavily-python not installed. Run: pip3 install tavily-python", file=sys.stderr)
    raise

try:
    import requests
except ImportError:
    requests = None


SYSTEM_PROMPT = """You are a skeptical B2B research analyst building a brief for a 1,800-2,200 word blog post for Hexa AI Agency, an AI automation agency for small-to-mid-size service businesses.

The blog post you are researching for needs to:
- Rank on Google (target a real buyer query)
- Convince a senior decision-maker (founder, COO, head of ops at 5-200 employee company)
- Cite real numbers with real sources (Google's E-E-A-T rewards this)
- Include 6-12 external citations to authoritative sources

You will be given:
  - A topic (e.g. "AI invoice processing in QuickBooks")
  - A niche (e.g. finance, property management, healthcare, retail, general SMB)
  - Raw web search results from Tavily (titles, URLs, content snippets)

Your job: extract from the sources ONLY information that is credible, specific, and recent. You are NOT allowed to invent numbers. If a stat lacks a credible source in the search results, exclude it.

OUTPUT - respond with ONLY valid JSON, no markdown wrapping, matching this schema:

{
  "key_stats": [
    {
      "stat": "Concrete one-sentence statement with a number, year, or specific claim",
      "source_url": "https://exact-url-from-the-search-results",
      "source_name": "Publisher or report name as shown in the source",
      "confidence": "high" | "medium" | "low"
    }
  ],
  "pain_points": [
    "One acute pain point in the buyer's daily reality (concrete moment, not abstract). e.g. 'AP runs out of time to code invoices before month-end close, so finance team works the weekend'"
  ],
  "current_solutions_in_market": [
    {"name": "Vendor or method name", "approach": "what it does in one line", "limitation": "why it falls short"}
  ],
  "recommended_angle_hooks": [
    {
      "angle": "money-on-the-table | identity-attack | inside-the-room | counter-conventional | one-question-diagnostic",
      "example": "A specific opening sentence for THIS topic in this angle's style"
    }
  ],
  "cta_deliverable_ideas": [
    {"name": "Specific deliverable name (calculator, checklist, template, audit)", "deliverability": "PDF | Notion doc | Sheet | web tool"}
  ],
  "external_citation_candidates": [
    {
      "url": "https://...",
      "title": "Page title",
      "claim_it_supports": "One-line summary of what this URL can be cited for in the post"
    }
  ]
}

RULES:
- 6-12 key_stats (the blog needs 6-12 external citations, so research must surface that many credible stats). Every stat MUST include source_url copied EXACTLY from the search results (do not paraphrase URLs).
- 3-5 pain_points, written from the buyer's POV (specific moments, not abstract problems).
- 2-3 current_solutions_in_market — what competitors / incumbents offer, and why a HEXA build beats them.
- 2-4 recommended_angle_hooks. The "example" field must be a usable opening sentence, not a description.
- 3-5 cta_deliverable_ideas. Each must be something a small agency could plausibly produce (no enterprise platforms).
- 6-12 external_citation_candidates — every URL the writer might link to. Prefer Google docs, vendor docs (HubSpot, Anthropic, OpenAI, Stripe, Make.com), and published research from credible firms (McKinsey, Forrester, Gartner, RAND). Avoid competitor sales pages.
- If a search result is from a forum, blog, or unsourced claim, mark confidence "low".
- If you cannot find 6 credible stats with source URLs, return what you have anyway - the validator downstream will catch it.

NEVER use em or en dashes anywhere. Use hyphens or commas.
"""


def _build_queries(topic: str, niche: str) -> list:
    year = date.today().year
    queries = [
        f"{topic} statistics {year}",
        f"{topic} cost ROI {niche}",
        f"{topic} case study {niche} business",
        f"{topic} benchmarks {year}",
    ]
    if niche and niche != "general":
        queries.append(f"{niche} {topic} survey {year}")
    return queries


def _tavily_search(client: TavilyClient, query: str, max_results: int = 5) -> list:
    try:
        resp = client.search(query=query, search_depth="advanced", max_results=max_results)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": (r.get("content", "") or "")[:800],
            }
            for r in resp.get("results", [])
        ]
    except Exception as e:
        print(f"  Tavily search failed for '{query}': {e}", file=sys.stderr)
        return []


def _validate_source_urls(brief: dict) -> tuple:
    """HEAD-check key_stats URLs; drop the ones that 404. Returns (brief, dropped_count)."""
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
            # Network flake — keep it; the writer can spot-check.
            kept.append(stat)
    brief["key_stats"] = kept
    return brief, dropped


def _synthesize(anth, model: str, topic: str, niche: str, raw_results: list) -> dict:
    sources_block = "\n\n".join(
        f"### Source [{i+1}]: {r['title']}\nURL: {r['url']}\n{r['content']}"
        for i, r in enumerate(raw_results)
    )
    user_prompt = f"""Topic: {topic}
Niche: {niche}

Raw search results below. Extract a research brief per the schema. Cite source_url exactly from these results.

{sources_block}
"""
    response = anth.messages.create(
        model=model,
        max_tokens=4000,
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


def research_blog_topic(topic: str, niche: str = "general") -> dict:
    """
    Main entry point. Returns the research_brief dict. Raises on missing API keys.
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY not set in environment")

    tav = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    queries = _build_queries(topic, niche)
    print(f"  Researching blog topic: {topic} ({niche})")
    all_results, seen = [], set()
    for q in queries:
        print(f"    [tavily] {q}")
        for r in _tavily_search(tav, q):
            if r["url"] and r["url"] not in seen:
                seen.add(r["url"])
                all_results.append(r)

    if not all_results:
        return {
            "topic": topic,
            "niche": niche,
            "research_date": date.today().isoformat(),
            "key_stats": [],
            "pain_points": [],
            "recommended_angle_hooks": [],
            "cta_deliverable_ideas": [],
            "external_citation_candidates": [],
            "passed": False,
            "warnings": ["no web research available"],
        }

    print(f"  Synthesizing brief from {len(all_results)} unique sources")
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    anth = anthropic.Anthropic()
    brief = _synthesize(anth, model, topic, niche, all_results)

    brief, dropped = _validate_source_urls(brief)
    if dropped:
        print(f"  Dropped {dropped} stats with 404/missing source_url")

    brief.update({
        "topic": topic,
        "niche": niche,
        "research_date": date.today().isoformat(),
        "model": model,
        "tavily_queries_run": len(queries),
        "tavily_results_returned": len(all_results),
        "tokens_used": brief.pop("_tokens_used", 0),
    })

    # Soft pass/fail (orchestrator decides what to do)
    warnings = []
    if len(brief.get("key_stats", [])) < 6:
        warnings.append(f"only {len(brief.get('key_stats', []))} key_stats (writer needs 6-12 external citations)")
    if len(brief.get("pain_points", [])) < 3:
        warnings.append("fewer than 3 pain_points")
    brief["warnings"] = warnings
    brief["passed"] = len(warnings) == 0

    return brief


# ---------- CLI ----------

def _cli():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--niche", default="general")
    parser.add_argument("--output", required=True, help="Path for research_brief.json (or '-' for stdout)")
    args = parser.parse_args()

    try:
        brief = research_blog_topic(args.topic, args.niche)
    except RuntimeError as e:
        print(json.dumps({"passed": False, "error": str(e)}, indent=2))
        sys.exit(2)

    out = json.dumps(brief, indent=2)
    if args.output == "-":
        print(out)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(out)
        print(f"  Output: {args.output}")
        print(f"  passed={brief['passed']} stats={len(brief.get('key_stats', []))} citations={len(brief.get('external_citation_candidates', []))}")
    sys.exit(0 if brief["passed"] else 1)


if __name__ == "__main__":
    _cli()
