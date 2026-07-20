#!/usr/bin/env python3
"""
Manual duration sync when prosody tags are stripped from word_timestamps
(e.g. when using gen_voice_natural.py). Matches slide.text against the word
stream and sets durationFrames based on segment endpoints.

Usage:
    python3 madebyhexa-ads/_tools/sync_manual.py <concept_dir> <segment-end-word-indices>

Example:
    python3 madebyhexa-ads/_tools/sync_manual.py madebyhexa-ads/m-opener-short 4 8 12 20 25 29
"""
import json
import os
import sys

TRANSITION = 15
HOLD = 24
FPS = 30


def sync(concept_dir, end_indices):
    cfg_p = os.path.join(concept_dir, "config.json")
    ts_p = os.path.join(concept_dir, "voiceover_timestamps.json")
    cfg = json.load(open(cfg_p))
    vo = json.load(open(ts_p))

    if len(end_indices) != len(cfg["slides"]):
        raise SystemExit(f"Need {len(cfg['slides'])} end-indices, got {len(end_indices)}")

    durations = []
    prev_end_ms = 0
    for i, end_idx in enumerate(end_indices):
        end_ms = vo[end_idx]["endMs"]
        seg_ms = end_ms - prev_end_ms
        frames = round(seg_ms / 1000 * FPS)
        if i < len(end_indices) - 1:
            frames += TRANSITION
        else:
            frames += HOLD
        durations.append(frames)
        prev_end_ms = end_ms

    for i, slide in enumerate(cfg["slides"]):
        slide["durationFrames"] = durations[i]
    cfg["word_timestamps"] = vo
    json.dump(cfg, open(cfg_p, "w"), indent=2)

    total = sum(durations) - (len(durations) - 1) * TRANSITION
    print(f"  {concept_dir}: durations={durations}, render={total} frames ({total/FPS:.1f}s)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    concept = sys.argv[1]
    ends = [int(x) for x in sys.argv[2:]]
    sync(concept, ends)
