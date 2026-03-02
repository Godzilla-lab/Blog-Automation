"""
Pick 5 random tweets from library for today
Ensures variety by picking from different categories
"""

import json
import random
from pathlib import Path
from datetime import datetime

def load_library():
    """Load tweet library"""
    library_file = Path('.tmp/tweet_library.json')
    with open(library_file, encoding='utf-8') as f:
        return json.load(f)

def pick_daily_tweets():
    """Pick 5 varied tweets for today"""
    library = load_library()
    tweets = library['tweets']

    # Group by type
    by_type = {}
    for tweet in tweets:
        tweet_type = tweet['type']
        if tweet_type not in by_type:
            by_type[tweet_type] = []
        by_type[tweet_type].append(tweet)

    # Pick distribution for variety
    daily_picks = []
    times = ["8:00", "12:00", "15:00", "18:00", "21:00"]

    # Pick one from each major category for variety
    pick_from = [
        ('hot_take', 'contrarian', 'story'),  # Opinion/thought leadership
        ('before_after',),  # Results
        ('value_bomb', 'tip'),  # Educational
        ('question',),  # Engagement
        ('hot_take', 'contrarian', 'value_bomb')  # Wild card
    ]

    for i, categories in enumerate(pick_from):
        available = []
        for cat in categories:
            if cat in by_type:
                available.extend(by_type[cat])

        if available:
            picked = random.choice(available)
            daily_picks.append({
                "time": times[i],
                "content": picked['content'],
                "type": picked['type'],
                "viral_potential": picked.get('viral_potential', 'medium'),
                "id": picked['id']
            })

    return daily_picks

def save_daily_queue(tweets):
    """Save today's picks"""
    output = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'tweets': tweets
    }

    with open(Path('.tmp/tweet_queue.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Picked 5 tweets for today")
    print(f"[OK] Saved to .tmp/tweet_queue.json\n")

    for i, tweet in enumerate(tweets, 1):
        print(f"{i}. [{tweet['time']}] ({tweet['type']}) [ID: {tweet['id']}]")
        print(f"   {tweet['content'][:80]}...")
        print(f"   Viral potential: {tweet['viral_potential']}\n")

def main():
    print("Picking 5 tweets from library...\n")
    tweets = pick_daily_tweets()
    save_daily_queue(tweets)

if __name__ == "__main__":
    main()
