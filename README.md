# Blog & Content Automation

AI-powered content engine for [Hexa AI Agency](https://twitter.com/hexa_aiagency). Generates blog posts, viral tweets, and Instagram carousels using a 3-layer architecture that separates human intent from deterministic execution.

## How It Works

```
Directives (what to do)  →  Orchestration (AI decides)  →  Execution (Python scripts do it)
```

**Directives** are SOPs written in Markdown. **Orchestration** is handled by Claude, which reads the directives and calls the right scripts. **Execution** scripts are deterministic Python — they handle API calls, image processing, and file operations reliably.

This keeps AI focused on decision-making while pushing repeatable work into testable code.

## Features

### Thread-to-Carousel
Converts Twitter/X threads into Instagram carousel slides (1080x1350 PNG). Each slide renders a tweet card with profile picture, display name, handle, and text.

- Automatic slide breakdown (short tweets get combined, long ones get their own slide)
- Image sourcing via Tavily search + download
- Emoji rendering with Apple Color Emoji
- Light and dark theme support

```bash
python3 execution/render_carousel.py --config workspace/carousels/2026-03-19-topic/config.json
```

### Tweet Generation
Generates human-sounding tweets using trend scraping and Claude Opus.

- Scrapes Reddit for trending AI/niche topics
- Generates 5 daily tweets with varied structure and personality
- Bulk tweet library (300+ pre-written tweets by category)
- Daily queue management

```bash
python3 execution/run_daily_tweets.py
```

### Blog Post Generation
Generates SEO blog posts with matching social media content for niche service businesses.

- Blog posts with internal linking via sitemap analysis
- LinkedIn, Twitter thread, and Threads post variants
- Question bank with 200+ topics across niches (dental, property management, commercial cleaning, etc.)

```bash
cd blog-automation && python3 main.py
```

## Project Structure

```
├── directives/          # SOPs in Markdown (the instruction set)
├── execution/           # Python scripts (the tools)
│   ├── render_carousel.py      # Instagram carousel renderer
│   ├── search_images.py        # Tavily image search
│   ├── download_image.py       # Image downloader
│   ├── generate_tweets.py      # Daily tweet generator
│   ├── scrape_ai_trends.py     # Reddit trend scraper
│   ├── generate_bulk_tweets.py # Bulk tweet library
│   ├── pick_daily_tweets.py    # Daily tweet picker
│   ├── run_daily_tweets.py     # Full pipeline orchestrator
│   └── requirements.txt
├── skills/              # Reusable Claude Code skills
│   └── thread-to-carousel/
│       ├── SKILL.md             # Skill definition
│       ├── config_template.json # Config schema
│       └── assets/              # Profile pic, etc.
├── blog-automation/     # Blog post generation system
│   ├── main.py
│   ├── modules/                 # Claude client, sitemap, social gen
│   ├── templates/               # Prompt templates
│   └── output/                  # Generated posts
├── workspace/           # Generated carousel output
├── .tmp/                # Intermediate files (gitignored)
├── CLAUDE.md            # Architecture instructions for AI
└── .env                 # API keys (gitignored)
```

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip3 install -r execution/requirements.txt
   pip3 install pilmoji tavily-python
   ```
3. Create `.env` with your API keys:
   ```
   ANTHROPIC_API_KEY=your-key
   TAVILY_API_KEY=your-key
   ```
4. Add your profile picture to `skills/thread-to-carousel/assets/headshot.png`

## Requirements

- Python 3.9+
- macOS (uses system fonts for carousel rendering)
- [Claude Code](https://claude.com/claude-code) for orchestration
