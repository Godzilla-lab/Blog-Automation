# Tweet Library - How to Use

You now have **300 human-sounding tweets** ready to use. They're all saved and organized for you.

## Quick Start (2 commands)

### Get 5 tweets for today
```bash
python execution/pick_daily_tweets.py
```
This picks 5 varied tweets and saves them to `.tmp/tweet_queue.json`

### Browse by category
```bash
python execution/browse_tweets.py <category> <number>
```

Examples:
```bash
python execution/browse_tweets.py hot_take 10
python execution/browse_tweets.py before_after 5
python execution/browse_tweets.py tip 20
```

## What You Have

### Categories (300 tweets total)

1. **hot_take** (60 tweets) - Bold opinions, controversial takes
2. **before_after** (50 tweets) - Client results, case studies with numbers
3. **value_bomb** (30 tweets) - Educational tips, frameworks
4. **question** (30 tweets) - Engagement tweets, polls
5. **contrarian** (40 tweets) - Thought leadership, unpopular opinions
6. **story** (40 tweets) - Personal lessons, experiences
7. **tip** (50 tweets) - Quick tactical advice, how-tos

## Daily Workflow

### Option 1: Random Pick (Recommended)
```bash
# Every morning
python execution/pick_daily_tweets.py
```

This gives you 5 varied tweets:
- 8:00 AM - Opinion/thought leadership
- 12:00 PM - Results/case study
- 3:00 PM - Educational content
- 6:00 PM - Engagement question
- 9:00 PM - Mix

### Option 2: Browse and Choose
```bash
# Browse categories
python execution/browse_tweets.py hot_take 20

# Find one you like, note the ID
# Open .tmp/tweet_library.json and search for that ID
```

### Option 3: Direct from File
Open [.tmp/tweet_library.json](.tmp/tweet_library.json) and copy any tweet you want.

## File Structure

```
.tmp/
├── tweet_library.json      # All 300 tweets
└── tweet_queue.json        # Today's 5 picks

execution/
├── generate_bulk_tweets.py  # Generated the 300 (already done)
├── pick_daily_tweets.py     # Pick 5 random for today
└── browse_tweets.py         # Browse by category
```

## Example Tweets

### Hot Take
> "spent $40k testing AI tools last year — learned that the free tier of Claude beats most $500/mo enterprise solutions if you know what you're doing"

### Before/After
> "automated compliance checking\n\nbefore: legal team manually reviewing every doc for compliance\nafter: AI flags potential issues\n\n70% fewer escalations"

### Value Bomb
> "5 signs your business is ready for AI:\n\n1. you have repetitive tasks\n2. you have consistent processes\n3. you have data to work with\n4. you have budget for tools\n5. you're willing to iterate\n\nthat's it"

### Question
> "small business owners: what's the task you're doing manually that you KNOW could be automated?"

## Pro Tips

1. **Mix it up** - Don't post all hot takes. Use the random picker for variety
2. **Test timing** - The suggested times (8am, 12pm, 3pm, 6pm, 9pm) work for most audiences
3. **Track what works** - Note which tweet types get best engagement
4. **Regenerate anytime** - Run `pick_daily_tweets.py` multiple times until you like the selection
5. **Edit freely** - These are templates. Personalize with your specific numbers/experiences

## Browsing All Categories

```bash
# See all categories
python execution/browse_tweets.py

# Then browse any
python execution/browse_tweets.py hot_take 10
python execution/browse_tweets.py before_after 10
python execution/browse_tweets.py value_bomb 10
python execution/browse_tweets.py question 10
python execution/browse_tweets.py contrarian 10
python execution/browse_tweets.py story 10
python execution/browse_tweets.py tip 10
```

## Posting Strategy

### Week 1-2: High Engagement
Post hot takes, questions, contrarian views. Get people talking.

### Week 3-4: Value Delivery
Post tips, value bombs, educational content. Build authority.

### Week 5+: Results
Post before/after case studies. Show social proof.

Mix in personal stories throughout.

## Need More?

You have 300 tweets = 60 days of content (5/day).

After that:
1. Run `python execution/generate_bulk_tweets.py` again (generates new set)
2. Or regenerate with slight variations
3. Or use these as templates and personalize

## JSON Format

Each tweet in `tweet_library.json`:
```json
{
  "id": 1,
  "content": "the actual tweet text",
  "type": "hot_take",
  "viral_potential": "high",
  "category": "thought_leadership"
}
```

Search by ID to find specific tweets.

## Character Counts

All tweets are under 280 characters. Safe to copy and paste directly to Twitter/X.

---

You're set for 2 months of daily posting. No one will know these came from AI - they're written to sound completely human.

Post consistently, track what works, and adjust. You got this.
