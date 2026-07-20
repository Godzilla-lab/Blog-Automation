# Directive: Generate Daily Instagram Reels

## Goal
Produce 3 Instagram Reels per day for Hexa AI Agency (@hexa_aiagency). Each reel has stock b-roll footage, AI voiceover, synced captions, kinetic text, and an engagement-optimized CTA. Content attracts potential clients in niche service verticals.

## Inputs
- Optional: specific niche (dental, property, cleaning, general)
- Optional: specific topic or blog post to repurpose
- Optional: reel count (default 3)

## Tools / Scripts
| Script | Purpose |
|--------|---------|
| `execution/scrape_ai_trends.py` | Scrape trending topics from Reddit + Tavily |
| `execution/research_topic.py` | **[Agent 0]** Web-research the topic → research_brief.json. See [research_topic.md](research_topic.md) |
| `execution/generate_reel_script.py` | Generate reel config (slides, voiceover, footage queries) via Claude — now takes `--research-brief` |
| `execution/evaluate_reel_script.py` | **[Agent 1]** Pre-render eval (9-dim rubric, 2 auto-retries on soft fail). See [evaluate_reel_script.md](evaluate_reel_script.md) |
| `execution/download_pexels_video.py` | Download stock footage from Pexels API |
| `execution/generate_voiceover.py` | Generate TTS voiceover + word timestamps (ElevenLabs default) |
| `execution/generate_reel.py` | Render video via Remotion DailyReel composition |
| `execution/generate_ig_caption.py` | Generate Instagram caption + hashtags |
| `execution/review_reel.py` | Deterministic QA (file checks, em-dash, audio sync, watermark config). See [review_reel_output.md](review_reel_output.md) |
| `execution/reality_qa_reel.py` | **[Agent 2]** Post-render vision QA (clipped captions, wrong CTA on final frame, artifacts). One auto-rerender on footage fail. See [reality_qa_reel.md](reality_qa_reel.md) |
| `execution/run_daily_reels.py` | **Master orchestrator** — chains all steps below |

## Quick Start
```bash
# Generate 3 reels (auto-picks topics from trends + blog posts)
python3 execution/run_daily_reels.py --count 3

# Generate 1 reel for a specific niche
python3 execution/run_daily_reels.py --count 1 --niche dental

# Generate 1 reel on a specific topic
python3 execution/run_daily_reels.py --count 1 --topic "dental no-shows" --niche dental

# Dry run (plan topics without generating)
python3 execution/run_daily_reels.py --count 3 --dry-run
```

## Pipeline Flow
```
0.  research_topic.py            →  workspace/reels/slug/research_brief.json    [Agent 0]
       hard-fail on empty research; no further spend

1.  generate_reel_script.py      →  workspace/reels/slug/config.json
       takes --research-brief; uses ONLY brief's stats

1b. evaluate_reel_script.py      →  workspace/reels/slug/script_eval.json       [Agent 1]
       soft-fail → regenerate with --critique (up to 2 retries)
       hard-fail → stop (no Pexels/ElevenLabs spend)

2.  download_pexels_video.py     →  skills/remotion-video/remotion/public/reels/slug/clip-N.mp4
3.  generate_voiceover.py        →  .../public/reels/slug/voiceover.mp3 + timestamps
4.  generate_reel.py             →  workspace/reels/slug/reel.mp4
5.  generate_ig_caption.py       →  workspace/reels/slug/caption.txt

6.  review_reel.py               (deterministic — em-dash, audio sync, handle config)
6b. reality_qa_reel.py           →  workspace/reels/slug/reality_qa.json        [Agent 2]
       on fail with footage hints → re-download flagged clips, re-render once, re-QA
       on fail with config hints  → surface to user (no auto-rerender)

Final qa_passed = review_passed AND reality_qa_passed (both required to ship)
```

## Layered QA
The pipeline now has THREE quality gates, layered from cheap to expensive:

1. **Script eval (Agent 1)** — runs before any paid stock/TTS API spend. 9-dimension rubric scored by Claude. 2 auto-retries with critique fed back. See [evaluate_reel_script.md](evaluate_reel_script.md).
2. **Deterministic QA (existing)** — file-level checks, no AI. Em-dashes, audio sync, watermark in config, hook quality regex. See [review_reel_output.md](review_reel_output.md). Stays exactly as-is; not replaced.
3. **Reality QA (Agent 2)** — vision check on 6 sampled frames of the rendered MP4. Catches clipped captions, wrong CTA in the final frame, stripe artifacts, off-topic b-roll. Auto-rerenders once on footage-level fail. See [reality_qa_reel.md](reality_qa_reel.md).

All gates must pass for a reel to be shippable. Each gate writes its own JSON to the reel's directory for post-hoc review.

## Content Strategy

### Reel Types (daily mix)
| Type | % | Description |
|------|---|-------------|
| Problem-Agitation-Solution (pas) | 40% | Hook with pain point → stats → solution → CTA |
| Before/After (before_after) | 25% | Show painful "before" → contrast with "after" results |
| Free Value + CTA (lead_magnet) | 20% | Offer insight → "Comment [KEYWORD] for free [resource]" |
| Trend Reaction (trend) | 15% | React to industry news with hot take |

### Hook Formulas (first slide — determines 90% of performance)
- **Stat Shock**: "$15K/month. That's what dental practices lose to no-shows."
- **Contrarian**: "Stop sending appointment reminders. They don't work."
- **Question**: "Why are your tenants still emailing about broken faucets in 2026?"
- **Curiosity Gap**: "The #1 reason property managers burn out has nothing to do with tenants."
- **NEVER** start with "Did you know" or generic intros

### CTA Strategy
- Primary: "Comment [KEYWORD] and I'll DM you [free thing]" (for ManyChat)
- Secondary: "Link in bio for the full guide"
- Engagement: "Save this for later"

### Lead Magnets by Niche
| Niche | Lead Magnet | Keyword |
|-------|------------|---------|
| Dental | No-Show Cost Calculator (PDF) | DENTAL |
| Property Mgmt | Tenant Communication Automation Checklist | PROPERTY |
| Cleaning | Scheduling Efficiency Audit Template | CLEANING |
| General | AI Automation ROI Calculator | HEXA |

### Niche Rotation
Don't post 2+ reels for the same niche in a row. The orchestrator handles this automatically.

### Multi-Clip Slides (visual variety on long beats)
ElevenLabs v3 prosody pauses make voiceovers ~15% longer than v2, which pushes some slides past the **6-second threshold** where a single Pexels clip starts to feel frozen. The renderer (`skills/remotion-video/remotion/src/reels/scenes/FootageBackground.tsx`) supports an array of footage clips per slide and rotates between them evenly.

| Slide duration | Clips needed | Config field |
|---|---|---|
| ≤ 6.0s | 1 | `"footage": "clip-N.mp4"` (legacy) |
| 6.0s - 9.0s | 2 | `"footages": ["clip-Na.mp4", "clip-Nb.mp4"]` |
| > 9.0s | 2-3 | `"footages": ["clip-Na.mp4", "clip-Nb.mp4", "clip-Nc.mp4"]` |

`run_daily_reels.py` handles this automatically:
1. After `sync_slides_to_voice` computes per-slide `durationFrames`, identify slides with `durationFrames > 180` (6s @ 30fps).
2. For each: rename existing `clip-N.mp4` → `clip-Na.mp4`, download a 2nd clip (same `footage_query`, Pexels rotates results) as `clip-Nb.mp4`.
3. Set `slide.footages = [clip-Na.mp4, clip-Nb.mp4]`; drop `slide.footage`.
4. The renderer divides each slide's window evenly across the array.

The `<Video>` element in `FootageBackground.tsx` uses `loop` so even if a Pexels clip is shorter than its sub-window, it restarts cleanly instead of freezing.

If RealityQA flags a multi-clip slide's footage, the auto-rerender only re-downloads `clip-Na.mp4` (keeps the second clip, halves the Pexels spend on retries).

### Voiceover Prosody (ElevenLabs v3 inline tags)
The voiceover is rendered through ElevenLabs **v3** (`ELEVENLABS_MODEL=eleven_v3` in `.env`) with prosody-tuned settings. The script generator emits inline audio tags inside `voiceover_script` so the voice pauses, leans in, and shifts energy with the meaning. **Tags only ever appear in `voiceover_script` — slide `text` fields stay clean** (otherwise they'd render as visible captions).

Allowed tags:
| Tag | When to use |
|---|---|
| `[serious]` | Damning stats. Flat, grim weight. |
| `[firm]` | Rebuttals. Assertive but not angry. |
| `[matter-of-fact]` | Citing data ("Gartner says..."). |
| `[deliberate]` | Planting an insight. Slow, weighted. |
| `[building]` | Energy ramping into the payoff. |
| `[punchy]` | Punchlines. Short and sharp. |
| `[grounded]` | The resolve after a punchline. |
| `[warm]` | The CTA. Inviting, friendly. |
| `[curious]` | Questions. Leaning in. |
| `[pause]` | Explicit 0.5s beat. Cap at 4 per reel. |

Plus: `...` (three dots) for short hesitation, ALL-CAPS on the emphasis word for volume. `execution/generate_voiceover.py` strips any tag tokens that leak into `word_timestamps.json` before save, so SyncedCaptions never displays them. If v3 isn't available on the account, the script falls back to `eleven_multilingual_v2` and the audio sounds like the old monotone Ellen.

## Content Sources (in priority order)
1. **Trending topics** — from `scrape_ai_trends.py` (Reddit + Tavily web search)
2. **Blog post repurposing** — from `blog-automation/output/` (16K+ word articles → 4-6 slide reels)
3. **Evergreen topics** — hardcoded fallback list in `scrape_ai_trends.py`

## Video Specs
- **Format**: 1080x1920 (9:16 portrait)
- **Duration**: No fixed default. Let the content and Instagram algorithm performance dictate the length. Size each reel to maximize watch-through rate and engagement — a hot take might be 20s, a process breakdown might be 75s. Never pad, never rush.
- **FPS**: 30
- **Codec**: H.264
- **Font**: Bebas Neue (kinetic text), Montserrat (synced captions)
- **Accent**: Configurable per reel (default #FFD700 gold)

## Voiceover
- **Engine**: ElevenLabs (realistic neural voices via API). Edge TTS is the automatic fallback only when `ELEVENLABS_API_KEY` / `ELEVENLABS_VOICE_ID` are unset.
- **Default voice**: Ellen — voice_id `BIvP0GN1cAtSRTxNHnWS` (serious, direct, confident female). Configured in `.env` as `ELEVENLABS_VOICE_ID`.
- **Model**: `eleven_multilingual_v2` (set via `ELEVENLABS_MODEL`)
- **Output**: MP3 + word-level timestamps JSON (character-aligned, exact) for synced captions
- **Fallback voice**: en-US-EmmaNeural (Edge TTS) if ElevenLabs fails or is unavailable

## Outputs
Each reel produces a directory at `workspace/reels/YYYY-MM-DD-slug/`:
```
workspace/reels/2026-03-30-dental-no-shows/
├── config.json       (full config with slides, footage paths, voiceover, timestamps)
├── reel.mp4          (final rendered video)
└── caption.txt       (Instagram post caption with hashtags)
```

Stock footage and voiceover audio are stored in Remotion's public directory:
```
skills/remotion-video/remotion/public/reels/2026-03-30-dental-no-shows/
├── clip-1.mp4 ... clip-N.mp4    (Pexels stock footage)
├── voiceover.mp3                 (TTS audio)
└── voiceover_timestamps.json     (word-level timing)
```

## Edge Cases
- If Pexels returns no results for a footage query, the script uses the slide text as a broader fallback search
- If voiceover generation fails, the reel still renders with kinetic text only (no audio)
- If a trend source (Reddit, Tavily) is down, the pipeline falls back to evergreen topics
- `PEXELS_API_KEY` and `ANTHROPIC_API_KEY` must be set in `.env`
- First render after `npm install` takes longer (Remotion bundles the project)
- **Pexels CDN flake**: `videos.pexels.com` sometimes resets or read-times-out mid-download, leaving a 0-byte to ~2MB partial file. After every download, validate file size (`stat -f%z` > 500KB) before treating it as success. If still bad after one retry, fall back to `workspace/footage-library/<niche>/` — a tag-matched curated clip beats a broken render.
- **Anthropic API failures**: if `generate_reel_script.py` or `generate_ig_caption.py` return 401/credit errors, the rest of the pipeline (download, voiceover, render) is fully deterministic. Hand-write the `config.json` (slides + voiceover_script + emphasis + footage_query, see schema in `workspace/reels/2026-04-22-self-storage-after-hours-occupancy/config.json`) and `caption.txt`, then run the remaining scripts directly.

## Learnings
- 4 seconds per slide is the sweet spot for readability
- Yellow (#FFD700) accent on dark backgrounds gets the most engagement
- Hard cuts between slides (no transitions) matches the viral reel style
- Word-by-word synced captions (SyncedCaptions.tsx) dramatically increase watch time
- Voiceover + captions together outperform either alone
- Footage must be in Remotion's `public/` directory for `staticFile()` to work
- **Remotion font fetch timeout**: Google Fonts (`@remotion/google-fonts/*`) defaults to a 28s `delayRender` timeout, which is too tight on slow networks and causes "delayRender() was called but not cleared" errors. `skills/remotion-video/remotion/remotion.config.ts` raises it to 120s via `Config.setDelayRenderTimeoutInMilliseconds(120000)` — keep this file in place.
- **Per-slide temp dirs**: `download_pexels_video.py` always writes to `clip-1.mp4` inside its `--output` dir, so calling it sequentially against the same dir overwrites prior clips. Always download into a per-slide temp dir, then move into `clip-N.mp4`. The orchestrator and `.tmp/download_reel_footage.sh` both follow this pattern.
