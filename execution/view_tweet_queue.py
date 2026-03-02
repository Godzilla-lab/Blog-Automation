"""
View and manage tweet queue
"""

import json
from pathlib import Path
from datetime import datetime

def view_queue():
    """Display current tweet queue"""
    queue_file = Path('.tmp/tweet_queue.json')

    if not queue_file.exists():
        print("No tweet queue found. Run generate_tweets.py first.")
        return

    with open(queue_file) as f:
        data = json.load(f)

    print(f"\n=== Tweet Queue for {data['date']} ===")
    print(f"Generated: {data['generated_at']}\n")

    tweets = data['tweets']

    for i, tweet in enumerate(tweets, 1):
        print(f"Tweet #{i}")
        print(f"Time: {tweet['time']}")
        print(f"Type: {tweet['type']}")
        print(f"Content: {tweet['content']}")
        print(f"Characters: {len(tweet['content'])}/280")
        print(f"Viral potential: {tweet.get('viral_potential', 'medium')}")
        print("-" * 60)

    print(f"\nTotal tweets: {len(tweets)}")

if __name__ == "__main__":
    view_queue()
