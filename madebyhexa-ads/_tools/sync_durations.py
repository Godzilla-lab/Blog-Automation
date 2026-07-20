#!/usr/bin/env python3
"""
Sync per-slide durationFrames in a Concept's config.json to the
voiceover_timestamps.json. Slide boundaries are marked by prosody tags
"[curious]", "[deliberate]", etc. at the start of a word in the VO.

Formula:
  durationFrames[i] = (vo_start[i+1] - vo_start[i]) * 30 + TRANSITION
  durationFrames[last] = (vo_end - vo_start[last]) * 30 + HOLD

TRANSITION matches DailyReel.tsx's 15-frame crossfade overlap.
HOLD adds breathing room at the end for the CTA card.

Usage:
    python3 madebyhexa-ads/_tools/sync_durations.py madebyhexa-ads/a-isnt-real
"""
import json
import os
import re
import sys

TRANSITION = 15
HOLD = 24  # ~0.8s breath at end
FPS = 30


def sync(concept_dir: str) -> None:
    cfg_p = os.path.join(concept_dir, "config.json")
    vo_p = os.path.join(concept_dir, "voiceover_timestamps.json")
    with open(cfg_p) as f:
        cfg = json.load(f)
    with open(vo_p) as f:
        vo = json.load(f)

    tag_re = re.compile(r"^\[([a-z_]+)\]")
    boundaries_ms = []
    for w in vo:
        if tag_re.match(w["word"]):
            boundaries_ms.append(w["startMs"])
    last_end_ms = vo[-1]["endMs"]

    n_slides = len(cfg["slides"])
    if len(boundaries_ms) != n_slides:
        raise SystemExit(
            f"Tag count {len(boundaries_ms)} != slides {n_slides} in {concept_dir}"
        )

    durations = []
    for i in range(n_slides):
        start = boundaries_ms[i]
        if i < n_slides - 1:
            end = boundaries_ms[i + 1]
            frames = round((end - start) / 1000 * FPS) + TRANSITION
        else:
            frames = round((last_end_ms - start) / 1000 * FPS) + HOLD
        durations.append(frames)

    for i, slide in enumerate(cfg["slides"]):
        slide["durationFrames"] = durations[i]

    # Also embed word_timestamps so DailyReel SyncedCaptions can render them.
    cfg["word_timestamps"] = [
        {"word": w["word"].replace(f"[{m.group(1)}]", ""), "startMs": w["startMs"], "endMs": w["endMs"]}
        for w in vo
        for m in [tag_re.match(w["word"])] if True
    ] if False else [
        {
            "word": tag_re.sub("", w["word"]),
            "startMs": w["startMs"],
            "endMs": w["endMs"],
        }
        for w in vo
    ]

    with open(cfg_p, "w") as f:
        json.dump(cfg, f, indent=2)

    total = sum(durations) - (n_slides - 1) * TRANSITION
    print(f"  {concept_dir}: {n_slides} slides, durations={durations}, render={total} frames ({total/FPS:.1f}s)")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        sync(d)
