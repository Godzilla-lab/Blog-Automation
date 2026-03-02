# Human-Sounding Tweet Generator

Automatically generates 5 viral-worthy tweet ideas daily for your AI agency. Built to sound **completely human** — no one will know it's AI-generated.

## Quick Start

```bash
# Install dependencies
pip install -r execution/requirements.txt

# Generate today's tweets (one command does everything)
python execution/run_daily_tweets.py
```

That's it. You'll get 5 human-sounding tweets in `.tmp/tweet_queue.json`.

## What Makes This Human?

The system uses **Claude Opus 4.5** with advanced prompting that:
- Uses contractions and casual language
- Varies sentence rhythm (short + long mixed)
- Adds personality ("honestly", "real talk", "ngl")
- Includes real numbers and specifics
- Makes some tweets slightly controversial
- Avoids all corporate speak and buzzwords
- No hashtags (they look desperate)
- Different vibe for each tweet (not templated)

## How It Works

### 3-Step Pipeline

1. **Scrape AI Trends** (`scrape_ai_trends.py`)
   - Pulls trending AI topics from Reddit ML communities
   - Falls back to evergreen topics if scraping fails
   - Saves to `.tmp/ai_trends.json`

2. **Generate Tweets** (`generate_tweets.py`)
   - Uses Opus 4.5 with human-mimicking prompts
   - Creates 5 varied tweets (value bombs, hot takes, before/after, etc.)
   - Saves to `.tmp/tweet_queue.json`

3. **View Queue** (`view_tweet_queue.py`)
   - Shows your daily tweet queue
   - Character counts, viral potential, scheduling times

## Tweet Types (Auto-Mixed)

- **40% Value bombs**: "3 AI mistakes costing you money"
- **25% Trend reactions**: "Hot take on [latest AI news]"
- **20% Before/after**: "We automated X — 8hrs → 8min"
- **10% Contrarian takes**: "Everyone's wrong about AI agents"
- **5% Engagement**: Questions, polls

## Posting Times

System suggests optimal times:
- 8:00 AM - Morning catch-up crowd
- 12:00 PM - Lunch scroll
- 3:00 PM - Afternoon break
- 6:00 PM - After work
- 9:00 PM - Evening engagement

## Advanced Usage

### Generate custom count
```bash
python execution/generate_tweets.py --count 10
```

### Just scrape trends
```bash
python execution/scrape_ai_trends.py
```

### View queue
```bash
python execution/view_tweet_queue.py
```

### Regenerate if you don't like them
Just run it again:
```bash
python execution/run_daily_tweets.py
```

Higher temperature = more varied results each time.

## File Structure

```
.tmp/
├── ai_trends.json       # Scraped trends (regenerated daily)
└── tweet_queue.json     # Your tweet queue (edit if needed)

execution/
├── scrape_ai_trends.py  # Trend scraper
├── generate_tweets.py   # Tweet generator
├── view_tweet_queue.py  # Queue viewer
└── run_daily_tweets.py  # Run everything

directives/
└── generate_viral_tweets.md  # System instructions
```

## Editing Generated Tweets

1. Open `.tmp/tweet_queue.json`
2. Edit the `content` field for any tweet
3. Keep it under 280 characters
4. Save and post

## Pro Tips

1. **Run daily** - Fresh trends = better engagement
2. **Review before posting** - 95% are ready, but always check
3. **Track what works** - Note which tweets perform best
4. **Regenerate freely** - Don't like one? Just run it again
5. **Mix it up** - Vary between tweet types throughout day

## Why This Works

**The Problem:** Most AI tweets sound robotic (formal, corporate, buzzword-heavy)

**The Solution:** Advanced prompting that mimics human writing:
- Natural language patterns
- Conversational tone
- Strategic imperfection
- Personality injection
- Real examples

**The Result:** Tweets that feel like they came from a real founder, not a bot.

## Example Output

```json
{
  "tweets": [
    {
      "content": "spent 3 months building custom AI agents — biggest lesson? start simpler than you think. most companies need 2-3 good prompts, not a whole system",
      "type": "hot_take",
      "time": "8:00",
      "viral_potential": "high"
    },
    {
      "content": "real talk: if you're paying for ChatGPT Plus but not using Custom GPTs, you're leaving money on the table. here's what we built for clients that actually works...",
      "type": "value_bomb",
      "time": "12:00",
      "viral_potential": "high"
    }
  ]
}
```

## Automation (Optional)

To auto-post these:
1. Copy tweets to a scheduler (Buffer, Hootsuite, etc.)
2. Or build Twitter API integration (requires Twitter API access)
3. Or use Zapier to auto-post from the JSON file

## Support

If trends fail to scrape, system uses **evergreen AI topics** as fallback. You'll always get 5 tweets.

---

Built following the 3-layer architecture:
- **Directive**: [directives/generate_viral_tweets.md](directives/generate_viral_tweets.md)
- **Orchestration**: This is handled by Claude
- **Execution**: Python scripts in `execution/`
