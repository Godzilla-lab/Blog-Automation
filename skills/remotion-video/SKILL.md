---
name: remotion-video
description: >
  Generate animated videos using Remotion (React-based video framework).
  Currently includes 5 Instagram Story highlight cover compositions for Hexa AI Agency.
  Each renders as a 6-second looping H.264 MP4 at 1080x1920 (9:16 vertical).
---

# Remotion Video Generator

## Available Compositions

| ID | Description | Accent Color |
|---|---|---|
| Results | Animated bar chart + stats (80% Sales, 90%+ Attribution) | #00e5cc (teal) |
| Services | Hex gear + 3 orbiting service labels | #00b4ff (blue) |
| HowItWorks | 3-step flow with dashed connectors | #7b61ff (purple) |
| FAQ | Animated "?" with floating question bubbles | #ff6b6b (red) |
| BookACall | Calendar icon + CTA + teal shimmer | #00e5cc (teal) |

## Process

### Step 1: Determine What to Render

User may request:
- A specific highlight composition by name
- All 5 highlights at once
- A new composition (requires creating a new .tsx file)

### Step 2: Render

**Single composition:**
```bash
python3 execution/render_video.py --composition Results --output out/results.mp4
```

**All 5 at once:**
```bash
cd skills/remotion-video/remotion && bash renderAll.sh
```

**Via config (for workspace-based workflow):**
```bash
python3 execution/render_video.py --config workspace/videos/YYYY-MM-DD-slug/config.json
```

### Step 3: Preview (Interactive)

```bash
cd skills/remotion-video/remotion && npx remotion studio
```
Opens browser at localhost:3000 with live preview of all compositions.

### Step 4: Iterate

Edit the composition .tsx files in `skills/remotion-video/remotion/src/highlights/` and re-render. The studio hot-reloads.

## Brand Reference

All brand constants live in `skills/remotion-video/remotion/src/brand.ts`:
- Colors: background #07070f, primary #00e5cc, secondary #00b4ff, purple #7b61ff
- Fonts: Orbitron (headings), Syne (body) — loaded via @remotion/google-fonts
- Canvas: 1080x1920, 30fps, 180 frames (6 seconds)
- Motion: spring({mass: 1, damping: 18, stiffness: 80}), stagger 6 frames

## Prerequisites

- Node.js 22+ (installed at ~/.local/node-v22.22.2-darwin-arm64/)
- ffmpeg 7+ (installed alongside Node.js)
- npm dependencies: `cd skills/remotion-video/remotion && npm install`

## Adding New Compositions

1. Create `src/highlights/NewComp.tsx` using existing compositions as reference
2. Register in `src/Root.tsx` with a `<Composition>` wrapper
3. Add render command to `renderAll.sh`
4. Test with `npx remotion studio`

## Edge Cases

- If logo (hexa.png) is missing, LogoBadge will error. Re-download from hexaaiagency.com/hexa.avif and convert to PNG.
- First render after `npm install` takes longer (Remotion bundles the project).
- AVIF files need conversion to PNG for Remotion's `<Img>` component.
