# Directive: Review Reel Output

> **Layered QA note**: this is the *deterministic* QA layer (file-level checks, regex, em-dash detection, audio sync). The *vision* QA layer lives in [reality_qa_reel.md](reality_qa_reel.md) and runs immediately after this one. **Both must pass** for a reel to be considered shippable. This directive does NOT cover visual problems like clipped captions, missing watermark frames, or off-topic b-roll — those are RealityQA's job.

## Goal
Automatically QA every reel before it reaches the user. Catch the mistakes that keep slipping through: audio cutoff, missing files, bad formatting, branding gaps.

## When to Run
After every reel generation - either manually or as the final step in `run_daily_reels.py`.

## Tool
| Script | Purpose |
|--------|---------|
| `execution/review_reel.py` | Deterministic QA checks on reel directories |

## Usage
```bash
# Review a single reel
python3 execution/review_reel.py workspace/reels/2026-04-14-dental-practice-833-percent-roi

# Review all reels from today
python3 execution/review_reel.py --all

# Review all reels from a specific date
python3 execution/review_reel.py --date 2026-04-10
```

## What It Checks

### Critical (errors - blocks delivery)
- **File existence**: config.json, reel.mp4, caption.txt all present
- **Audio sync**: voiceover duration <= video duration (the #1 recurring bug)
- **Footage integrity**: every slide's footage file exists and isn't empty
- **Slide content**: no empty text, no em/en dashes
- **Branding**: handle is @hexa_aiagency
- **Hook quality**: no "Did you know" or weak openers

### Important (warnings - flag for review)
- Caption length (200-2200 chars), hashtag count (10-30)
- CTA keyword present in caption
- First caption line not truncated (under 150 chars)
- Emphasis word matches slide text
- Last slide is type "cta"
- BG music exists and volume isn't too loud
- Tight timing buffer between voiceover and video

## Exit Codes
- `0` - all reels passed
- `1` - at least one reel failed (has errors)

## Integration with Pipeline
The review runs as the final step in `run_daily_reels.py`. If a reel fails review, it's flagged in the run log but doesn't block other reels from generating.

## Learnings
- The voiceover/video duration mismatch is the most common failure. Always calculate `seconds_per_slide` from voiceover timestamps, not a fixed value.
- clip-1 gets overwritten when downloading footage in a loop. Use temp directories per slide to avoid collisions.
- Remotion port conflicts happen when rendering in parallel. Render sequentially.
