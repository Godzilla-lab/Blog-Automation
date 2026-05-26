# Directive: Reality QA Reel (Agent 2)

## Goal
Post-render vision gate. Catch visual problems that `review_reel.py` (deterministic, file-level) can't see: clipped captions, off-topic b-roll, missing watermark on a sampled frame, wrong CTA keyword baked into the final frame, decode artifacts (stripes, tears, black flashes).

If a problem is footage-level, auto-rerender ONCE with a fresh Pexels clip on the flagged slide. If still fails, or if it's config-level, surface to the user.

## When to invoke
- Automatically: as Step 6b of `run_daily_reels.py`, immediately after `review_reel.py`.
- Manually: any time you want a vision QA pass on a rendered reel (e.g. spot-checking a shipped reel for retroactive issues).

## Inputs
- `--config` (the reel's config.json — provides ground truth for cta_keyword, handle, slide texts)
- `--reel` (the rendered reel.mp4)
- `--output` (path for `reality_qa.json`, default `<reel_dir>/reality_qa.json`)
- `--frames-only` (debugging — extract the 6 frames but skip the Claude vision call)

## Tools / Scripts
- `execution/reality_qa_reel.py` — entry point
- ffmpeg at `/Users/godzilla/.local/node-v22.22.2-darwin-arm64/bin/ffmpeg` — frame extraction
- ffprobe at `skills/remotion-video/remotion/node_modules/@ffprobe-installer/darwin-arm64/ffprobe` — duration probe
- Anthropic vision (`claude-opus-4-7`) — multimodal scoring

## Frame-sampling strategy

Probe reel duration `T`, extract 6 frames at fixed relative timestamps:

| # | Tag | Timestamp | Purpose |
|---|---|---|---|
| 1 | hook | 0.6s (or T×0.05 if T < 12s) | Hook frame, slide 1 mid-display |
| 2 | setup | T × 0.20 | Setup beat |
| 3 | insight1 | T × 0.45 | Mid-reel beat |
| 4 | insight2 | T × 0.70 | Late-mid beat |
| 5 | cta | T − 2.0s | Pre-final-fade CTA |
| 6 | final | T − 0.3s | The frame that must contain CTA keyword + handle |

Each frame is downscaled to 720×1280 JPG at quality 3 to keep vision-input tokens bounded (~50KB per frame). Saved to `<reel_dir>/.qa_frames/frame_NN_<tag>.jpg` for post-failure review.

## Vision rubric (8 dimensions, 1-5 integer)

| # | Dimension | Hard gate? |
|---|---|---|
| 1 | caption_legibility | no |
| 2 | hook_text_readability | no |
| 3 | watermark_present | **>= 3** |
| 4 | broll_on_topic | no |
| 5 | broll_quality | no |
| 6 | brand_color_consistency | no |
| 7 | **cta_frame_correct** | **>= 4** |
| 8 | **visual_artifacts** | **>= 4** |

Ground truth (`cta_keyword`, `handle`, `accent_color`, slide texts) is passed into the vision prompt so dimension 7 is a direct text-match check, not an open-ended guess.

## Pass logic
- `passed = (avg >= 4.0) AND (cta_frame_correct >= 4) AND (watermark_present >= 3) AND (visual_artifacts >= 4)`

Thresholds via env vars: `REALITY_QA_MIN_AVG=4.0`, `REALITY_QA_CTA_MIN=4`, `REALITY_QA_WATERMARK_MIN=3`, `REALITY_QA_ARTIFACTS_MIN=4`.

## Output schema (`reality_qa.json`)

```json
{
  "passed": false,
  "overall_score": 3.4,
  "frames_analyzed": [
    {"timestamp": "0.60s", "tag": "hook",    "path": ".qa_frames/frame_01_hook.jpg"},
    {"timestamp": "16.50s", "tag": "final",  "path": ".qa_frames/frame_06_final.jpg"}
  ],
  "dimensions": {
    "caption_legibility":      {"score": 4, "issues": []},
    "hook_text_readability":   {"score": 5, "issues": []},
    "watermark_present":       {"score": 2, "issues": ["@hexa_aiagency missing at 11.8s, 14.8s"]},
    "broll_on_topic":          {"score": 4, "issues": []},
    "broll_quality":           {"score": 5, "issues": []},
    "brand_color_consistency": {"score": 5, "issues": []},
    "cta_frame_correct":       {"score": 1, "issues": ["Final frame says 'AUDIT' but config says 'DENTAL'"]},
    "visual_artifacts":        {"score": 5, "issues": []}
  },
  "frame_issues": [
    {"timestamp": "11.8s", "issue": "Watermark missing"},
    {"timestamp": "16.5s", "issue": "Wrong CTA keyword"}
  ],
  "rerender_hints": {
    "swap_clips": [],
    "regen_voiceover": false,
    "fix_config": ["cta_keyword mismatch — check slide 6 text vs config.cta_keyword"]
  },
  "recommendation": "fail",
  "model": "claude-opus-4-7",
  "tokens_used": 8420,
  "reel_duration_s": 16.87,
  "thresholds_used": {...}
}
```

## Auto-rerender policy

When `passed=false`:
1. Read `rerender_hints.swap_clips` (1-indexed slide numbers) and `rerender_hints.fix_config`.
2. If `swap_clips` is non-empty AND `fix_config` is empty:
   - Re-run `download_pexels_video.py` for each flagged slide (Pexels rotates results, so fresh search picks a different clip)
   - Re-render with `generate_reel.py`
   - Re-run RealityQA ONCE more
   - If STILL fails: surface to user, do NOT retry again
3. If `fix_config` is non-empty: skip auto-rerender and surface immediately. Config-level issues (wrong cta_keyword, bad slide text) need a human or a config edit.

## Edge Cases
- **reel.mp4 missing or 0 bytes**: short-circuit with `error: "reel not found"`, exit code 2.
- **ffprobe returns 0 duration**: short-circuit with `error: "could not probe reel duration"`.
- **API key revoked**: hard fail with `error: "ANTHROPIC_API_KEY not set"`, exit code 2. Orchestrator marks `reality_qa_passed=false`.
- **Stripe artifacts return**: if `visual_artifacts <= 3`, the user has likely re-introduced the `<OffthreadVideo>` regression. Check `FootageBackground.tsx` per `feedback_offthread_video.md` memory.

## Tradeoffs
- **False positive on watermark**: vision can mistake handle visibility if the watermark is partially behind text or in a low-contrast region. Threshold is `>=3` (not `>=4`) and the .qa_frames JPGs are preserved on disk so the user can override in <10s.
- **broll_on_topic is subjective**: not a hard gate. Score reflects "does this scene plausibly match the slide claim", not "is this the best possible scene."
- **cta_frame_correct via vision**: can be fooled by fancy font rendering. Future v2 may add tesseract OCR backstop.

## Learnings (update as patterns emerge)
- 720×1280 JPG @ q:v 3 gives ~50KB frames — 6 frames totals ~300KB input, well under vision token budget.
- Frame sampling at T-0.3s consistently catches the final CTA frame even with the 15-frame fade-out.
- The `recommendation` field is just a human-readable echo of `passed` — useful when piping output through pretty-printers.
