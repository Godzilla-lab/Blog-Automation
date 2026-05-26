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
Priority: user-provided > web search (Tavily) > live screenshot > AI-generated.

**Step A: Try Tavily first**
Use `execution/search_images.py` to search and download images via Tavily API:
```bash
python3 execution/search_images.py --query "dental office empty chair" --output workspace/carousels/YYYY-MM-DD-slug/reference/ --count 3 --download
```

**Step B: Screenshot fallback (if Tavily images don't match)**
If Tavily returns no results or the images don't match the slide content, use `execution/screenshot_web.py` to take screenshots from the web:
```bash
# Screenshot a specific URL
python3 execution/screenshot_web.py --url "https://example.com/relevant-page" --output workspace/carousels/YYYY-MM-DD-slug/reference/screenshot_1.png

# Search and screenshot top results
python3 execution/screenshot_web.py --query "dental office scheduling software dashboard" --output workspace/carousels/YYYY-MM-DD-slug/reference/ --count 2

# Visit actual pages (not image search) and screenshot them
python3 execution/screenshot_web.py --query "AI chatbot for property management" --output workspace/carousels/YYYY-MM-DD-slug/reference/ --count 2 --pages

# Crop to a specific region
python3 execution/screenshot_web.py --url "https://example.com" --output shot.png --crop 0,100,1080,800
```

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

### 7. Generate caption.txt
Always generate an Instagram caption for the carousel. Include a hook line, value summary, CTA with keyword trigger, and 15-25 hashtags. Save to `workspace/carousels/YYYY-MM-DD-slug/caption.txt`.

## Outputs
- PNG slides at `workspace/carousels/YYYY-MM-DD-slug/slide_N.png`
- Config file at `workspace/carousels/YYYY-MM-DD-slug/config.json`
- Caption at `workspace/carousels/YYYY-MM-DD-slug/caption.txt`

## Edge Cases
- If no headshot exists at `skills/thread-to-carousel/assets/headshot.png`, warn the user and render with placeholder
- If a tweet has only emojis, render normally
- For very long threads (10+ tweets), suggest splitting into two carousels
- Always use `\n` for explicit line breaks in tweet text within config.json

## Learnings
- `pilmoji` (not `pillmoji`) is the correct package name for emoji rendering
- Bundled font: Inter (Regular, Medium, SemiBold, Bold) at `skills/thread-to-carousel/assets/fonts/`
- Font sizes: name=34px bold, handle=28px, text=38px, line spacing=1.45x for 1080px canvas
- Avatar size: 80px circular
- **Bold text support**: Use `**bold**` markers in tweet text to render key phrases in SemiBold weight. Renderer handles inline bold across `\n\n` breaks and word-wrap — bold positions are resolved by walking `plain_text` with a pointer per wrapped char (not by counting `len(line)`), so bold lands in the right place even when word-wrap drops whitespace/newlines
- Optional font size override in config.json: `"fonts": {"text_size": 42}` (backward compatible, omit for defaults)
- Falls back to macOS system fonts (SF Pro, Helvetica) if bundled fonts missing
