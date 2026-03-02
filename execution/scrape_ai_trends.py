"""
Scrapes trending AI topics from Twitter and viral AI accounts.
Uses web scraping to gather current trends without Twitter API.
"""

import json
import requests
from datetime import datetime
from pathlib import Path

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
    "https://news.ycombinator.com/",  # HN often has AI news
    "https://www.reddit.com/r/MachineLearning/hot.json",
    "https://www.reddit.com/r/OpenAI/hot.json",
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
        "Building AI teams"
    ]

def main():
    print("Scraping AI trends...")

    # Try to get trends
    trends = scrape_reddit_ai_trends()

    # If no trends found, use evergreen topics
    if not trends:
        print("No trends found, using evergreen topics")
        trends = [{"title": topic, "score": 0, "source": "evergreen"}
                  for topic in get_evergreen_topics()]

    # Save to file
    output_dir = Path('.tmp')
    output_dir.mkdir(exist_ok=True)

    output = {
        'date': datetime.now().isoformat(),
        'trends': trends[:15],  # Keep top 15
        'evergreen': get_evergreen_topics()
    }

    with open(output_dir / 'ai_trends.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"[OK] Scraped {len(trends)} trends")
    print(f"[OK] Saved to .tmp/ai_trends.json")

if __name__ == "__main__":
    main()
