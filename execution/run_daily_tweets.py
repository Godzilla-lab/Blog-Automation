"""
Run the complete daily tweet generation pipeline
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    return True

def main():
    print("Starting daily tweet generation pipeline...\n")

    # Step 1: Scrape trends
    if not run_command(
        "python execution/scrape_ai_trends.py",
        "STEP 1: Scraping AI trends"
    ):
        print("Warning: Trend scraping failed, will use evergreen topics")

    # Step 2: Generate tweets
    if not run_command(
        "python execution/generate_tweets.py --count 5",
        "STEP 2: Generating human-sounding tweets"
    ):
        print("Error generating tweets")
        sys.exit(1)

    # Step 3: View queue
    run_command(
        "python execution/view_tweet_queue.py",
        "STEP 3: Tweet queue preview"
    )

    print("\n" + "="*60)
    print("[OK] Pipeline complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review tweets in .tmp/tweet_queue.json")
    print("2. Edit any tweets you want to adjust")
    print("3. Copy to your scheduler or post manually")
    print("\nRegenerate anytime with: python execution/run_daily_tweets.py")

if __name__ == "__main__":
    main()
