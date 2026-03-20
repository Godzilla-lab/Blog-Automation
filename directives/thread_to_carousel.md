# Directive: Thread to Instagram Carousel

## Goal
Turn a Twitter/X thread into a set of Instagram carousel slides (1080x1350 PNG images) that mimic the look of real tweets.

## Inputs
- A thread of tweets (pasted text, topic to write about, or screenshots)
- Optional: images to embed in specific slides

## Tools / Scripts
- `execution/render_carousel.py` — Pillow-based renderer, takes `--config path/to/config.json`
- `skills/thread-to-carousel/SKILL.md` — full process documentation
- `skills/thread-to-carousel/config_template.json` — config schema reference

## Process

### 1. Get the thread content
Ask the user or receive pasted text. If writing, use the voice/tone from CLAUDE.md.

### 2. Apply slide breakdown rules
- Hook tweet (first) → own slide, always has an image
- Tweets >200 chars or with images → own slide
- Two consecutive short tweets (<150 chars each, no images) → combine on one slide with gray divider
- Present the breakdown to the user for approval

### 3. Source images
Priority: user-provided > web search > live screenshot > AI-generated.
Save all images to `workspace/carousels/YYYY-MM-DD-slug/reference/`.

### 4. Build config.json
Copy from `skills/thread-to-carousel/config_template.json`. Populate profile info, theme, slides array.
Save to `workspace/carousels/YYYY-MM-DD-slug/config.json`.

### 5. Render
```bash
python3 execution/render_carousel.py --config workspace/carousels/YYYY-MM-DD-slug/config.json
```

### 6. Review and iterate
Show the user the output folder. Offer to swap images, edit text, or change theme and re-render.

## Outputs
- PNG slides at `workspace/carousels/YYYY-MM-DD-slug/slide_N.png`
- Config file at `workspace/carousels/YYYY-MM-DD-slug/config.json`

## Edge Cases
- If no headshot exists at `skills/thread-to-carousel/assets/headshot.png`, warn the user and render with placeholder
- If a tweet has only emojis, render normally
- For very long threads (10+ tweets), suggest splitting into two carousels
- Always use `\n` for explicit line breaks in tweet text within config.json

## Learnings
- `pilmoji` (not `pillmoji`) is the correct package name for emoji rendering
- Font sizes: name=30px bold, handle=26px, text=30px for 1080px canvas
- Avatar size: 80px circular
- macOS fonts: SF Pro at `/System/Library/Fonts/SFNS.ttf`, Helvetica Neue Bold at index 1 of `/System/Library/Fonts/HelveticaNeue.ttc`
