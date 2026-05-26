"""
Scrapes trending topics from Reddit, Tavily web search, and niche communities.
Feeds the daily Reels pipeline with fresh content ideas.

Usage:
    python3 execution/scrape_ai_trends.py
    python3 execution/scrape_ai_trends.py --niche dental
    python3 execution/scrape_ai_trends.py --niche property --tavily
"""

import argparse
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

# Top AI Twitter accounts to monitor
AI_INFLUENCERS = [
    "@sama",  # Sam Altman
    "@gdb",  # Greg Brockman
    "@AnthropicAI",
    "@OpenAI",
    "@ylecun",  # Yann LeCun
    "@karpathy",  # Andrej Karpathy
]

# AI news sources
AI_NEWS_SOURCES = [
    "https://www.reddit.com/r/MachineLearning/hot.json",
    "https://www.reddit.com/r/OpenAI/hot.json",
    "https://www.reddit.com/r/artificial/hot.json",
]

# Niche-specific subreddits for service-related trends
NICHE_SOURCES = [
    "https://www.reddit.com/r/propertymanagement/hot.json",
    "https://www.reddit.com/r/dentistry/hot.json",
    "https://www.reddit.com/r/medicalbilling/hot.json",
    "https://www.reddit.com/r/smallbusiness/hot.json",
]

def scrape_reddit_ai_trends():
    """Scrape trending AI topics from Reddit ML communities"""
    trends = []

    for url in AI_NEWS_SOURCES:
        if 'reddit.com' in url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=10)
                data = response.json()

                for post in data['data']['children'][:10]:
                    post_data = post['data']
                    trends.append({
                        'title': post_data['title'],
                        'score': post_data['score'],
                        'url': post_data['url'],
                        'source': 'reddit'
                    })
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

    return trends

def scrape_niche_trends():
    """Scrape trending topics from niche-specific subreddits"""
    trends = []
    for url in NICHE_SOURCES:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            for post in data['data']['children'][:5]:
                post_data = post['data']
                trends.append({
                    'title': post_data['title'],
                    'score': post_data['score'],
                    'url': post_data['url'],
                    'source': 'reddit_niche',
                    'subreddit': post_data.get('subreddit', '')
                })
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
    return trends

TAVILY_NICHE_QUERIES = {
    "dental": [
        "dental practice challenges 2026",
        "dental no-show solutions",
        "dental office automation AI",
    ],
    "property": [
        "property management automation 2026",
        "tenant communication challenges",
        "property management AI tools",
    ],
    "cleaning": [
        "commercial cleaning business challenges",
        "cleaning company scheduling problems",
        "janitorial business automation",
    ],
    "general": [
        "small business AI automation 2026",
        "service business operational challenges",
        "AI tools for small businesses",
    ],
}


def scrape_tavily_trends(niche: str = None) -> list:
    """Search Tavily for niche-specific trending content."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("  Tavily API key not set, skipping web search")
        return []

    queries = []
    if niche and niche in TAVILY_NICHE_QUERIES:
        queries = TAVILY_NICHE_QUERIES[niche]
    else:
        for q_list in TAVILY_NICHE_QUERIES.values():
            queries.extend(q_list[:1])  # one query per niche

    trends = []
    for query in queries:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 5,
                },
                timeout=15,
            )
            data = response.json()
            for result in data.get("results", []):
                trends.append({
                    "title": result.get("title", ""),
                    "score": result.get("score", 0),
                    "url": result.get("url", ""),
                    "source": "tavily",
                    "content_snippet": result.get("content", "")[:200],
                    "query": query,
                })
        except Exception as e:
            print(f"  Error searching Tavily for '{query}': {e}")
            continue

    return trends


def get_evergreen_topics():
    """Fallback evergreen AI topics if scraping fails"""
    return [
        "AI automation for businesses",
        "ChatGPT vs Claude comparison",
        "AI agent workflows",
        "Custom GPT development",
        "AI integration mistakes",
        "Prompt engineering tips",
        "AI cost optimization",
        "AI for customer service",
        "AI workflow automation",
        "Building AI teams",
        "Dental no-shows costing practices thousands",
        "Property managers drowning in tenant emails",
        "Medical billing claim denials",
        "Cleaning companies losing contracts",
        "Self-storage lead follow-up failures"
    ]

def main():
    parser = argparse.ArgumentParser(description="Scrape trending topics for content pipeline")
    parser.add_argument("--niche", choices=["dental", "property", "cleaning", "general"],
                        help="Focus on a specific niche")
    parser.add_argument("--tavily", action="store_true", help="Include Tavily web search results")
    args = parser.parse_args()

    print("Scraping trends...")

    # Get AI trends from Reddit
    ai_trends = scrape_reddit_ai_trends()
    print(f"  Found {len(ai_trends)} AI trends (Reddit)")

    # Get niche-specific trends from Reddit
    niche_trends = scrape_niche_trends()
    print(f"  Found {len(niche_trends)} niche trends (Reddit)")

    # Get Tavily web search trends
    tavily_trends = []
    if args.tavily or os.getenv("TAVILY_API_KEY"):
        tavily_trends = scrape_tavily_trends(args.niche)
        print(f"  Found {len(tavily_trends)} web trends (Tavily)")

    # Combine
    trends = ai_trends + niche_trends + tavily_trends

    # If no trends found, use evergreen topics
    if not trends:
        print("No trends found, using evergreen topics")
        trends = [{"title": topic, "score": 0, "source": "evergreen"}
                  for topic in get_evergreen_topics()]

    # Save to file
    output_dir = Path(project_root) / '.tmp'
    output_dir.mkdir(exist_ok=True)

    output = {
        'date': datetime.now().isoformat(),
        'niche_filter': args.niche,
        'ai_trends': ai_trends[:10],
        'niche_trends': niche_trends[:10],
        'tavily_trends': tavily_trends[:10],
        'trends': trends[:30],
        'evergreen': get_evergreen_topics()
    }

    with open(output_dir / 'ai_trends.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"[OK] Scraped {len(trends)} total trends")
    print(f"[OK] Saved to .tmp/ai_trends.json")

if __name__ == "__main__":
    main()
