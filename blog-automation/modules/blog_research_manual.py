#!/usr/bin/env python3
"""
BlogResearcher in manual mode: Tavily-only, no Anthropic synthesis.

When ANTHROPIC_API_KEY is dead, we can still gather sourced material via Tavily
and hand it to the chat-Claude (or operator) to digest. This module produces a
`research_raw.json` file that the writer can pick citations from directly, with
no LLM synthesis step in between.

Use blog_research.research_blog_topic() when Anthropic is alive.
Use this module when it isn't.
"""

import json
import os
import sys
from datetime import date

try:
    from tavily import TavilyClient
except ImportError:
    print("Error: tavily-python not installed. Run: pip3 install tavily-python", file=sys.stderr)
    raise


def _build_queries(topic: str, niche: str) -> list:
    year = date.today().year
    queries = [
        f"{topic} statistics {year}",
        f"{topic} cost ROI {niche}",
        f"{topic} case study {niche} business",
        f"{topic} benchmarks {year}",
        f"{topic} survey report {year}",
        f"{topic} failure rate research",
    ]
    if niche and niche != "general":
        queries.append(f"{niche} {topic} industry data {year}")
    return queries


def _tavily_search(client: TavilyClient, query: str, max_results: int = 5) -> list:
    try:
        resp = client.search(query=query, search_depth="advanced", max_results=max_results)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": (r.get("content", "") or "")[:600],
                "query": query,
            }
            for r in resp.get("results", [])
        ]
    except Exception as e:
        print(f"  Tavily search failed for '{query}': {e}", file=sys.stderr)
        return []


def research_blog_topic_manual(topic: str, niche: str = "general") -> dict:
    """
    Tavily-only research. Returns a dict the orchestrator writes to
    research_raw.json. Mirrors the shape of the Anthropic-synthesized
    brief but without the synthesized key_stats / pain_points - the
    chat-Claude (or operator) picks those from sources directly.
    """
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY not set in environment")

    tav = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    queries = _build_queries(topic, niche)
    print(f"  [manual research] {topic} ({niche})")

    all_results, seen = [], set()
    for q in queries:
        print(f"    [tavily] {q}")
        for r in _tavily_search(tav, q):
            if r["url"] and r["url"] not in seen:
                seen.add(r["url"])
                all_results.append(r)

    # Light heuristic: prefer credible orgs at the top (.gov, .edu, well-known publishers)
    CREDIBLE_HOSTS = (
        "gartner.com", "mckinsey.com", "bcg.com", "rand.org", "forrester.com",
        "ibm.com", "anthropic.com", "openai.com", "developers.google.com",
        "support.google.com", "hubspot.com", "salesforce.com", "stripe.com",
        "make.com", "mitsloan.mit.edu", "sloanreview.mit.edu", "nanda.media.mit.edu",
        "harvardbusiness.org", "hbr.org", "techrepublic.com", "wired.com",
        "wsj.com", "ft.com", "nytimes.com", "bloomberg.com",
        ".gov", ".edu", "europa.eu",
    )

    def credibility(r):
        url = (r.get("url") or "").lower()
        for host in CREDIBLE_HOSTS:
            if host in url:
                return 0  # top
        if "linkedin.com" in url or "facebook.com" in url or "reddit.com" in url:
            return 2  # social, deprioritize
        return 1

    all_results.sort(key=credibility)

    return {
        "topic": topic,
        "niche": niche,
        "research_date": date.today().isoformat(),
        "mode": "manual_tavily_only",
        "tavily_queries_run": len(queries),
        "tavily_results_returned": len(all_results),
        "sources": all_results,
        "notes_for_writer": (
            "These are raw Tavily search results, deduplicated and ranked with "
            "credible publishers (gartner.com, mckinsey.com, rand.org, etc.) "
            "floated to the top. There is NO LLM-synthesized brief - the writer "
            "(chat-Claude or operator) must read these sources and pick 6-12 "
            "citation URLs + 3-5 buyer pain points + first-hand-experience context "
            "directly. The shape mirrors what blog_research.py would emit if "
            "Anthropic were alive."
        ),
    }


# ---------- CLI ----------

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(here))
    load_dotenv(os.path.join(project_root, ".env"))
    load_dotenv(os.path.join(os.path.dirname(here), ".env"))

    parser = argparse.ArgumentParser(description="Tavily-only blog research (manual mode).")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--niche", default="general")
    parser.add_argument("--output", required=True, help="Path for research_raw.json")
    args = parser.parse_args()

    try:
        brief = research_blog_topic_manual(args.topic, args.niche)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(2)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(brief, f, indent=2)
    print(f"  Output: {args.output}")
    print(f"  Sources: {len(brief['sources'])} unique URLs from {brief['tavily_queries_run']} queries")
