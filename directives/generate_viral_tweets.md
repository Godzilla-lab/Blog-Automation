# Generate Viral Tweet Ideas

## Goal
Generate 5 authentic, human-sounding tweet ideas daily for an AI agency that have viral potential. Nobody should be able to tell these are AI-generated.

## Context
- Twitter/X account: @hexa_aiagency
- Industry: AI agency/automation
- Posting frequency: 5 times per day (8am, 12pm, 3pm, 6pm, 9pm)
- Tone: Knowledgeable but casual, sometimes contrarian, always valuable

## Inputs
- Current AI trends (scraped from AI Twitter)
- Recent viral AI tweets (for format/style analysis)
- Your existing content themes

## Process

### 1. Gather Trending Topics
Run: `python execution/scrape_ai_trends.py`
- Scrapes trending AI topics from Twitter
- Identifies viral tweet patterns
- Stores in `.tmp/ai_trends.json`

### 2. Generate Tweet Ideas
Run: `python execution/generate_tweets.py --count 5`
- Uses Opus 4.5 with human-mimicking prompts
- Applies randomization to avoid patterns
- Includes strategic "imperfections" (casual tone, varied punctuation)
- Outputs to `.tmp/tweet_queue.json`

### 3. Review Queue
Run: `python execution/view_tweet_queue.py`
- Displays today's queued tweets
- Shows scheduled posting times
- Allows editing/regeneration

## Output
JSON file at `.tmp/tweet_queue.json` with:
```json
{
  "date": "2026-01-08",
  "tweets": [
    {
      "time": "8:00",
      "content": "tweet text here",
      "type": "hot_take",
      "engagement_prediction": "high"
    }
  ]
}
```

## Human-Writing Techniques Applied
1. **Varied sentence structure** - short punchy sentences mixed with longer ones
2. **Casual language** - contractions, conversational phrases
3. **Strategic imperfection** - occasional em dashes, ellipses, informal punctuation
4. **Personal voice** - opinions, "we", "I've seen", anecdotes
5. **Natural transitions** - "here's the thing", "real talk", "honestly"
6. **Authentic examples** - specific numbers, real scenarios
7. **Format variety** - questions, statements, threads, hot takes

## Tweet Types Distribution
- 40% Value bombs (tips, insights, how-tos)
- 25% Trend reactions (hot takes on AI news)
- 20% Before/after results (social proof)
- 10% Contrarian takes (thought leadership)
- 5% Engagement bait (questions, polls)

## Edge Cases
- If API rate limited → cache results, retry in 15min
- If no trends found → use evergreen content templates
- If tweet too AI-sounding → regenerate with more "humanizing" constraints
- If controversial topic → flag for manual review

## Success Metrics
- Engagement rate > 2%
- At least 1 tweet per week > 100 likes
- Zero "sounds like AI" comments
- Growing follower count

## Continuous Improvement
- Track which tweet types perform best
- Update prompts based on engagement data
- Add successful formats to template library
