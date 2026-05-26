# Directive: Generate Video

## Goal
Create animated video content using Remotion. Currently supports Instagram Story highlight covers for Hexa AI Agency (hexaiagency.com). Each video is a 6-second looping MP4 at 1080x1920.

## Inputs
- Composition name (Results, Services, HowItWorks, FAQ, BookACall) or "all"
- Optional: custom output directory

## Tools / Scripts
- `execution/render_video.py` — Python wrapper that calls Remotion CLI
- `skills/remotion-video/SKILL.md` — full process documentation
- `skills/remotion-video/config_template.json` — config schema reference
- `skills/remotion-video/remotion/renderAll.sh` — batch render all 5

## Process

1. **Identify composition(s)** — which highlight(s) to render
2. **Check prerequisites** — Node.js, ffmpeg, npm deps installed
3. **Render** — run `python3 execution/render_video.py --composition <id>` or `bash renderAll.sh`
4. **Verify output** — check MP4 files exist in `out/` directory
5. **Present to user** — report file paths and sizes

## Outputs
- MP4 video files in `skills/remotion-video/remotion/out/`
- Or in `workspace/videos/YYYY-MM-DD-slug/` when using config workflow

## Edge Cases
- If node/ffmpeg not found: print install instructions and exit
- If npm deps missing: auto-install before rendering
- First render is slower due to bundling
- AVIF images must be converted to PNG for Remotion

## Learnings
- Node.js installed at ~/.local/node-v22.22.2-darwin-arm64/bin (not via brew/nvm)
- ffmpeg 7.0 ARM64 static binary installed alongside Node.js
- Pillow can convert AVIF to PNG for Remotion compatibility
- Remotion's bundled ffmpeg requires libSDL2 (Homebrew dependency). Fix: replace bundled ffmpeg at `node_modules/@remotion/compositor-darwin-arm64/ffmpeg/remotion/bin/ffmpeg` with the system static ffmpeg binary. Must redo after every `npm install`.
- Each 6-second 1080x1920 video renders to ~450-675KB H.264 MP4
