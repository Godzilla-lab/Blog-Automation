# Content Engine

An AI-native content automation system that generates blog posts, Instagram carousels, daily Reels, and viral tweets from a single prompt. Built for [Hexa AI Agency](https://hexaaiagency.com) to produce multi-platform content for niche service businesses at scale.

## The Problem

Content marketing for service businesses (dental practices, property managers, cleaning companies) requires:
- 3-5 blog posts per week with SEO optimization and internal linking
- Daily social media across 4+ platforms (LinkedIn, X, Threads, Instagram)
- Instagram carousels and Reels with voiceover, stock footage, and captions
- Consistent brand voice, CTAs, and lead magnets across everything

Doing this manually takes 20-30 hours per week per client. LLMs can help, but they're probabilistic - 90% accuracy per step compounds to 59% over just 5 steps. You can't build reliable infrastructure on coin flips.

## The Solution: 3-Layer Architecture

This system separates **what to do** from **how to decide** from **how to execute**, so AI handles judgment while deterministic code handles everything else.

```
┌─────────────────────────────────────────────────────────┐
│  DIRECTIVES (Layer 1)                                   │
│  Markdown SOPs that define goals, inputs, outputs,      │
│  edge cases. Like instructions for a mid-level employee.│
├─────────────────────────────────────────────────────────┤
│  ORCHESTRATION (Layer 2)                                │
│  Claude reads directives, routes tasks, handles errors, │
│  and updates SOPs with learnings. Pure decision-making. │
├─────────────────────────────────────────────────────────┤
│  EXECUTION (Layer 3)                                    │
│  18 deterministic Python scripts. API calls, rendering, │
│  file ops, data processing. Testable and reliable.      │
└─────────────────────────────────────────────────────────┘
```

**Why this works:** AI stays focused on decisions it's good at (topic selection, content strategy, error recovery) while repeatable work runs in tested code that doesn't hallucinate. Each layer can be improved independently.

## Pipelines

### Blog Posts + Social Distribution

Generates a 2,000+ word SEO blog post with matching LinkedIn post, X thread, and Threads post from a curated question bank of 200+ topics.

**What it does:**
- Pulls from a question bank organized by niche, search intent, difficulty, and content type
- Analyzes the target site's sitemap for internal linking opportunities
- Generates the blog post with meta descriptions, H2/H3 structure, and CTAs
- Produces platform-specific social variants in a single run

```
Input:  "Why dental practices lose thousands monthly to no-shows"
Output: blog_post.md + linkedin_post.md + twitter_thread.md + threads_post.md + metadata.json
```

### Instagram Reels (Daily)

End-to-end pipeline that produces 3 Reels per day with AI voiceover, stock footage, and Instagram captions.

**Pipeline flow:**
1. Scrape trending topics from Reddit and web sources
2. Generate reel script with slide text, emphasis words, and footage queries
3. Download matching HD stock footage from Pexels
4. Generate voiceover with word-level timestamps (Edge TTS)
5. Render final MP4 via Remotion (1080p, H.264)
6. Generate Instagram caption with hook, CTA, and hashtags

**Content mix:**
- 40% Problem-Agitation-Solution (stat shock hooks)
- 25% Before/After transformations
- 20% Lead magnets with comment-to-get CTAs
- 15% Trend reactions with contrarian angles

### Instagram Carousels

Converts X threads or topic briefs into branded carousel slides (1080x1350 PNG).

**What it does:**
- Breaks content into slides with intelligent grouping (short tweets combine, long ones split)
- Sources images via Tavily web search
- Renders with profile picture, handle, emoji support, and light/dark themes
- Generates Instagram caption with hashtags

### Viral Tweets

Daily tweet generation pipeline with trend-aware topic selection and a bulk library of 300+ pre-written tweets.

## Self-Annealing

The system improves itself. When a script fails:

1. Claude reads the error and stack trace
2. Fixes the script
3. Re-runs to verify
4. Updates the directive with what it learned (API limits, edge cases, better approaches)
5. The system is now stronger than before the failure

This means the directives evolve from initial SOPs into battle-tested runbooks. Every failure makes the next run more reliable.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Orchestration | Claude (Opus) via Claude Code |
| Blog generation | Anthropic API + custom prompt templates |
| Image search | Tavily API |
| Stock footage | Pexels API |
| Voiceover | Edge TTS (Microsoft Azure, free tier) |
| Video rendering | Remotion (React-based video framework) |
| Carousel rendering | Pillow + Pilmoji (Python) |
| Trend scraping | Reddit API + Tavily |
| Webhooks | Modal (serverless, event-driven) |
| Notifications | Slack (real-time activity stream) |

## Project Structure

```
directives/              # 6 Markdown SOPs (the instruction set)
execution/               # 18 Python scripts (the tools)
  render_carousel.py       # Instagram carousel PNG renderer
  run_daily_reels.py       # Master Reels pipeline orchestrator
  generate_reel_script.py  # Claude-powered reel config builder
  generate_voiceover.py    # TTS with word-level timestamps
  generate_reel.py         # Remotion video renderer
  download_pexels_video.py # Stock footage downloader
  search_images.py         # Tavily image search
  generate_tweets.py       # Daily tweet generation
  scrape_ai_trends.py      # Reddit trend scraper
  generate_ig_caption.py   # Instagram caption generator
  ...and 8 more utilities
skills/                  # Reusable Claude Code skills
  thread-to-carousel/      # Full carousel generation skill
blog-automation/         # Blog post generation system
  main.py                  # Interactive CLI
  modules/                 # Claude client, sitemap analyzer, social gen
  templates/               # Prompt templates per platform
  questions_bank.json      # 200+ curated topics across niches
workspace/               # Generated output (carousels, reels)
CLAUDE.md                # Architecture instructions for AI orchestration
.env                     # API keys (gitignored)
```

## Niches Served

- **Dental practices** - no-shows, recall systems, patient communication
- **Property management** - tenant communication, maintenance automation, rent collection
- **Commercial cleaning** - contract retention, client communication, scheduling
- **General small business** - AI adoption, automation ROI, operational efficiency

Each niche has dedicated questions in the bank with targeted keywords, search intent mapping, and content type assignments.

## Results

- 200+ blog topics curated with SEO metadata across 4 niches
- Multi-platform distribution from a single content generation run
- 3 Instagram Reels per day with voiceover, footage, and captions
- Carousel generation from any X thread or topic brief in under 2 minutes
- Self-improving SOP system that gets more reliable with every run

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip3 install -r execution/requirements.txt
   pip3 install pilmoji tavily-python
   ```
3. Create `.env` with API keys:
   ```
   ANTHROPIC_API_KEY=
   TAVILY_API_KEY=
   PEXELS_API_KEY=
   ```
4. Install [Claude Code](https://claude.ai/download) for orchestration
5. Run any pipeline:
   ```bash
   # Blog post + social content
   cd blog-automation && python3 main.py

   # Daily reels
   python3 execution/run_daily_reels.py

   # Carousel from thread
   python3 execution/render_carousel.py --config workspace/carousels/<folder>/config.json
   ```

## Requirements

- Python 3.9+
- Node.js 18+ (for Remotion video rendering)
- macOS recommended (uses system fonts for carousel rendering)
- Claude Code CLI for orchestration layer

---

Built by [Hexa AI Agency](https://hexaaiagency.com)
