"""
Browse tweet library by category
"""

import json
import sys
from pathlib import Path

def load_library():
    """Load tweet library"""
    library_file = Path('.tmp/tweet_library.json')
    with open(library_file, encoding='utf-8') as f:
        return json.load(f)

def show_by_category(category=None, limit=10):
    """Show tweets by category"""
    library = load_library()

    if not category:
        print("\nAvailable categories:")
        print("="*60)
        for cat, count in library['by_category'].items():
            print(f"  {cat}: {count} tweets")
        print("\nUsage: python execution/browse_tweets.py <category> [limit]")
        print("Example: python execution/browse_tweets.py hot_take 5")
        return

    tweets = [t for t in library['tweets'] if t['type'] == category]

    if not tweets:
        print(f"No tweets found for category: {category}")
        return

    print(f"\n{category.upper()} ({len(tweets)} total, showing {min(limit, len(tweets))})")
    print("="*60)

    for i, tweet in enumerate(tweets[:limit], 1):
        print(f"\n{i}. [ID: {tweet['id']}] ({tweet.get('viral_potential', 'medium')} viral potential)")
        print(f"{tweet['content']}")
        print("-"*60)

def main():
    category = sys.argv[1] if len(sys.argv) > 1 else None
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    show_by_category(category, limit)

if __name__ == "__main__":
    main()
