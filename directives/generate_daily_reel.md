# Directive: Generate Daily Reel

> **Single-reel mode also benefits from the gates.** The full pipeline in [generate_daily_reels.md](generate_daily_reels.md) wires three AI gates: [research_topic.md](research_topic.md) (Agent 0), [evaluate_reel_script.md](evaluate_reel_script.md) (Agent 1), and [reality_qa_reel.md](reality_qa_reel.md) (Agent 2). If you're generating a single reel manually, you can run those three scripts in order around the existing render step to avoid the manual-review loop.

## Goal
Create a 15-30 second Instagram Reel from existing blog/thread content. Each Reel has stock b-roll footage with bold kinetic text captions — punchy, fast-paced, designed for saves and shares.

## Inputs
- A blog post from `blog-automation/output/` or a thread from its `twitter_thread.md`
- Optional: specific niche / topic
- Optional: talking head footage path

## Tools / Scripts
- `execution/download_pexels_video.py` — Search and download stock footage from Pexels
- `execution/generate_reel.py` — Render the Reel via Remotion
- Remotion composition: `DailyReel` (in `skills/remotion-video/remotion/src/reels/DailyReel.tsx`)

## Process

### 1. Extract Script from Content
Read the blog post or Twitter thread. Extract 4-6 punchy lines:
- **Slide 1 (Hook):** Contrarian or shocking statement. E.g., "Your dental reminders are broken."
- **Slides 2-4 (Data/Points):** Key stats or insights. E.g., "23% of appointments end in no-shows."
- **Slide 5 (Solution/Shift):** What works instead. E.g., "Here's what top practices do."
- **Slide 6 (CTA):** Call to action. E.g., "DM 'DENTAL' for a free audit."

For each line, identify the **emphasis word** (the most impactful word to highlight in yellow).

### 2. Source Stock Footage
For each slide, determine a stock footage search keyword:
```
"Your dental reminders are broken." → "dental office phone"
"23% of appointments end in no-shows." → "empty waiting room"
"Here's what top practices do." → "doctor using tablet"
"DM DENTAL for a free audit." → "business person phone"
```

Download footage:
```bash
python3 execution/download_pexels_video.py \
  --query "dental office" \
  --output workspace/reels/YYYY-MM-DD-slug/footage/ \
  --count 4 \
  --orientation portrait
```

**Important:** Footage files must be placed in the Remotion `public/` directory to be accessible via `staticFile()`. Either:
- Download directly to `skills/remotion-video/remotion/public/reels/YYYY-MM-DD-slug/`
- Or symlink the footage directory

### 3. Build Config
Create `workspace/reels/YYYY-MM-DD-slug/config.json`:
```json
{
  "slides": [
    {
      "text": "Your dental reminders are broken.",
      "emphasis": "broken",
      "footage": "reels/2026-03-28-dental/clip-1.mp4",
      "type": "broll"
    },
    {
      "text": "23% of appointments end in no-shows.",
      "emphasis": "no-shows",
      "footage": "reels/2026-03-28-dental/clip-2.mp4",
      "type": "broll"
    },
    {
      "text": "Here's what top practices do instead.",
      "emphasis": "instead",
      "footage": "reels/2026-03-28-dental/clip-3.mp4",
      "type": "broll"
    },
    {
      "text": "DM DENTAL for a free audit.",
      "emphasis": "DENTAL",
      "footage": "reels/2026-03-28-dental/clip-4.mp4",
      "type": "cta"
    }
  ],
  "seconds_per_slide": 4,
  "accent_color": "#FFD700",
  "handle": "@hexa_aiagency"
}
```

**Footage paths** are relative to the Remotion `public/` directory.

**Slide types:**
- `broll` — Stock footage background with centered text
- `talking_head` — User's camera footage with text banner above
- `cta` — Same as broll but used for the final call-to-action

### 4. Render
```bash
python3 execution/generate_reel.py --config workspace/reels/YYYY-MM-DD-slug/config.json
```

### 5. Preview (Optional)
```bash
cd skills/remotion-video/remotion && npx remotion studio
```
Select "DailyReel" from the sidebar.

## Outputs
- MP4 file at `workspace/reels/YYYY-MM-DD-slug/reel.mp4`
- Config JSON for reproducibility

## Edge Cases
- If Pexels returns no results, try broader keywords (e.g., "office" instead of "dental office reception")
- If footage is landscape, Remotion's `objectFit: 'cover'` will crop to fill portrait frame
- Talking head clips should ideally be 9:16 portrait, pre-recorded by user
- Max 8 slides recommended (32 seconds at 4s/slide)
- PEXELS_API_KEY must be set in `.env`

## Learnings
- Bebas Neue font used for Reel captions (bold, all-caps, high impact)
- Yellow (#FFD700) accent matches the reference video style
- 4 seconds per slide is the sweet spot for readability
- Footage must be in Remotion's `public/` directory or subdirectory for `staticFile()` to work
- Hard cuts between slides (no transitions) matches the reference style
- **Per-slide durations:** Each slide accepts an optional `durationFrames` field (30fps). Set this from `word_timestamps` so the slide is visible during its spoken segment — never rely on a fixed `seconds_per_slide` when there's a voiceover with bridge sentences. Formula: `durationFrames[i] = (V_start[i+1] - V_start[i]) * 30 + 15`. Last slide: `(V_end - V_start[last]) * 30 + 30` (1s CTA hold). Without this, the slide visuals desync from spoken captions and the reel runs past voiceover end.
