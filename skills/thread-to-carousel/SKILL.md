---
name: thread-to-carousel
description: >
  Convert a Twitter/X thread into Instagram carousel slides styled as tweet/X post mockups.
  Each slide renders a clean tweet card with profile picture, display name, handle, and tweet text.
  Supports embedded images and combining short tweets 2-per-slide.
---

# Thread-to-Carousel Generator

## Process

### Step 1: Gather the Thread

Get the thread content from the user. They may:
- Paste a thread of text directly
- Provide a topic and ask you to write the thread
- Share screenshots or existing tweets to recreate

If writing the thread, use the voice and tone from `CLAUDE.md`. Each tweet in the thread should be a self-contained thought that flows into the next.

### Step 2: Gather Profile Info

The default profile is already configured:
- **Display name**: HEXA AI AGENCY
- **Handle**: @hexa_aiagency
- **Verified**: false
- **Headshot**: `skills/thread-to-carousel/assets/headshot.png`

If a different profile is needed, ask the user. Otherwise use defaults from `skills/thread-to-carousel/config_template.json`.

### Step 3: Break the Thread into Slides

Rules for slide layout:

**One tweet per slide (default):**
- Any tweet with an embedded image gets its own slide
- Tweets longer than ~200 characters get their own slide
- The first tweet (hook) always gets its own slide
- **The title slide (slide 1) should ALWAYS have an image.** A strong image on the first slide is critical for stopping the scroll.

**Two tweets per slide:**
- Combine consecutive short tweets (under ~150 characters each, no images) onto one slide
- This keeps the carousel compact and scannable
- A light gray divider line separates the two tweets

Walk through the thread and decide the slide breakdown. Present it to the user before generating:

```
Slide 1: Tweet 1 (hook) - own slide, with image
Slide 2: Tweet 2 + Tweet 3 - combined (both short)
Slide 3: Tweet 4 - own slide (has image)
Slide 4: Tweet 5 + Tweet 6 - combined (both short)
Slide 5: Tweet 7 (CTA) - own slide
```

### Step 4: Handle Images

Image pipelines in priority order:
1. **User-provided images** — always highest priority. If the user pastes or references an image, save it to the `reference/` folder.
2. **Web search** — use your web search tool to find relevant images. Search for the topic + "screenshot", "logo", "product", etc. When you find a good image URL, download it:
   ```bash
   python3 execution/download_image.py --url "https://example.com/image.png" --output "workspace/carousels/YYYY-MM-DD-slug/reference/hero.png"
   ```
3. **Live screenshots** — if discussing a specific website/tool, take a screenshot of their homepage or product page (future: `execution/carousel_screenshot.py`)
4. **AI-generated** — generate illustrations or diagrams if needed (future)

**Rules:**
- The hook slide (slide 1) MUST have an image. If the user didn't provide one, search for one.
- Aim for at least 50% of slides to have images — carousels with more visuals perform better.
- Save all images to `workspace/carousels/YYYY-MM-DD-slug/reference/` before building config.json.
- Use descriptive filenames: `hero.png`, `screenshot_product.png`, `logo_company.png`, etc.

### Step 5: Build config.json

Create the workspace folder and config:

```
workspace/carousels/YYYY-MM-DD-topic-slug/
├── config.json
├── reference/          # All source images go here
```

Copy the template from `skills/thread-to-carousel/config_template.json` and populate:
- Set `output_dir` to the workspace path
- Set theme (default: "light")
- Build the `slides` array based on the breakdown from Step 3
- For each slide, set `tweets` array (1 or 2 tweets)
- For images, save them to the `reference/` folder and set relative paths

Image paths in config should be relative to the project root (e.g., `workspace/carousels/2026-03-19-topic/reference/hero.png`).

### Step 6: Generate the Carousel

Run the rendering script:

```bash
python3 execution/render_carousel.py --config workspace/carousels/YYYY-MM-DD-topic-slug/config.json
```

This generates PNG slides at 1080x1350px (Instagram standard).

### Step 7: Present Results

After generation:
1. Show number of slides generated
2. Show the output folder path
3. Offer to adjust and re-run if needed (swap images, edit text, change theme)

To regenerate after changes, update the config.json and re-run the script.

## Theme Options

- **light** (default): White background, dark text
- **dark**: Black background, white text (v2)

## Edge Cases

- If a tweet has only emojis, it still gets rendered normally
- Very long tweets (400+ chars) may need the font size adjusted — the script handles this
- If headshot.png is missing, the script will render without a profile picture and warn
- Always use `\n` for explicit line breaks in tweet text
