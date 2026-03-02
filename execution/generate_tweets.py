"""
Generate human-sounding viral tweet ideas using Claude Opus 4.5.
Uses advanced prompting to ensure tweets sound authentic and natural.
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_trends():
    """Load scraped AI trends"""
    trends_file = Path('.tmp/ai_trends.json')
    if trends_file.exists():
        with open(trends_file) as f:
            return json.load(f)
    return {'trends': [], 'evergreen': []}

def generate_human_tweets(count=5):
    """Generate tweets that sound genuinely human"""

    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    trends_data = load_trends()

    # Extract trend topics
    trend_topics = [t.get('title', '') for t in trends_data.get('trends', [])][:10]
    evergreen = trends_data.get('evergreen', [])

    # Human-mimicking prompt (this is the secret sauce)
    prompt = f"""You're a founder of an AI agency tweeting from your personal experience. Generate {count} tweet ideas that sound COMPLETELY human and natural.

CURRENT AI TRENDS:
{chr(10).join(f"- {t}" for t in trend_topics) if trend_topics else "- AI automation\n- Custom AI agents\n- ChatGPT updates"}

EVERGREEN TOPICS:
{chr(10).join(f"- {t}" for t in evergreen[:5])}

CRITICAL: Make these sound like a REAL person wrote them, not AI:
- Use contractions (don't, can't, we've, here's)
- Vary sentence length (mix short punchy lines with longer ones)
- Use casual punctuation (em dashes —, ellipses..., no period endings sometimes)
- Add personality: "honestly", "real talk", "ngl", "lowkey"
- Use numbers when possible (8x faster, 3 mistakes, $50k saved)
- Ask questions occasionally
- Be conversational, like texting a colleague
- NO corporate speak, NO buzzwords, NO "delighted to announce"
- NO hashtags (look desperate)
- Make some slightly controversial or contrarian

TWEET TYPES TO MIX:
1. Value bomb: "3 AI mistakes costing you $$$"
2. Hot take: "Everyone's wrong about [X]. Here's why..."
3. Before/after: "We automated [X] — went from 8hrs to 8min"
4. Trend reaction: "[News] just dropped. My take:"
5. Question: "Which AI tool actually works for [X]?"

WRITE NATURALLY. Imagine you're tweeting between meetings, typing fast, being real.

Return ONLY valid JSON (no markdown, no explanation):
{{
  "tweets": [
    {{
      "content": "the actual tweet text under 280 chars",
      "type": "value_bomb|hot_take|before_after|trend_reaction|question",
      "time": "8:00|12:00|15:00|18:00|21:00",
      "viral_potential": "high|medium"
    }}
  ]
}}

Make each tweet FEEL different — different rhythm, different vibe. Not templated."""

    # Call Claude Opus 4.5
    response = client.messages.create(
        model="claude-opus-4-5-20251101",  # Opus 4.5
        max_tokens=2000,
        temperature=0.8,  # Higher temp = more creative/varied
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse response
    content = response.content[0].text.strip()

    # Remove markdown code blocks if present
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]
        content = content.strip()

    tweets_data = json.loads(content)
    return tweets_data['tweets']

def save_tweet_queue(tweets):
    """Save generated tweets to queue"""
    output_dir = Path('.tmp')
    output_dir.mkdir(exist_ok=True)

    queue_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'tweets': tweets
    }

    with open(output_dir / 'tweet_queue.json', 'w') as f:
        json.dump(queue_data, f, indent=2)

    print(f"\n[OK] Generated {len(tweets)} human-sounding tweets")
    print(f"[OK] Saved to .tmp/tweet_queue.json\n")

    # Display preview
    for i, tweet in enumerate(tweets, 1):
        print(f"{i}. [{tweet['time']}] ({tweet['type']})")
        print(f"   {tweet['content']}")
        print(f"   Viral potential: {tweet.get('viral_potential', 'medium')}\n")

def main():
    parser = argparse.ArgumentParser(description='Generate human-sounding tweets')
    parser.add_argument('--count', type=int, default=5, help='Number of tweets to generate')
    args = parser.parse_args()

    print(f"Generating {args.count} tweets using Opus 4.5...")

    tweets = generate_human_tweets(args.count)
    save_tweet_queue(tweets)

if __name__ == "__main__":
    main()
