#!/usr/bin/env python3
"""
Compute per-slide durationFrames from voiceover word_timestamps.

Each slide's durationFrames is sized to cover the voiceover region that
introduces that slide's text. Slide N stays on screen until slide N+1's
first word starts; the last slide runs to the end of audio + a short tail.

Designed to be robust to mild divergence between slide text and the voiceover
script (e.g. "$1,500" on a slide vs "fifteen hundred" in voice). It finds the
first matchable non-stopword anchor in each slide and uses that as the slide
start.

Usage from another module:
    from sync_slides_to_voice import sync_slides_to_voice
    durations, total = sync_slides_to_voice(config['slides'], config['word_timestamps'])

CLI usage (rewrites config.json in place):
    python3 execution/sync_slides_to_voice.py workspace/reels/<slug>/config.json
"""
import json
import os
import re
import sys

FPS = 30
TRANSITION_FRAMES = 15  # must match TRANSITION_FRAMES in DailyReel.tsx
DEFAULT_TAIL_FRAMES = 12  # ~0.4s of fade-out room after last word; not padding

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "i", "im", "youre", "you", "he", "she",
    "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its",
    "our", "their", "this", "that", "these", "those", "of", "in", "on", "at", "to",
    "for", "with", "from", "by", "as", "if", "so", "ill",
}

WORD_RE = re.compile(r"[a-z0-9]+")


def _norm(word: str) -> str:
    return "".join(WORD_RE.findall(word.lower()))


def _anchor_words(slide_text: str) -> list:
    """First 1-3 non-stopword tokens from a slide's text. Used to locate
    the slide's start in the voiceover. Falls back to all tokens if every
    word is a stopword."""
    tokens = [_norm(w) for w in slide_text.split() if _norm(w)]
    non_stop = [t for t in tokens if t not in STOPWORDS]
    if non_stop:
        return non_stop[:3]
    return tokens[:3]


def _find_slide_start(anchors: list, word_timestamps: list, search_from: int) -> tuple:
    """Find the index in word_timestamps where this slide's anchors first appear
    in order (allowing arbitrary gaps). Returns (idx, startMs) or (None, None) if
    not found."""
    if not anchors:
        return search_from, word_timestamps[search_from]["startMs"] if search_from < len(word_timestamps) else 0

    # Try to match the full anchor sequence first; fall back to fewer anchors
    for depth in range(len(anchors), 0, -1):
        target = anchors[:depth]
        i = search_from
        while i < len(word_timestamps):
            # Try to match target starting at i (with up to 10-word slack between anchors)
            if _norm(word_timestamps[i]["word"]) == target[0]:
                start_idx = i
                hit = 1
                j = i + 1
                slack = 0
                while hit < len(target) and j < len(word_timestamps) and slack < 12:
                    if _norm(word_timestamps[j]["word"]) == target[hit]:
                        hit += 1
                        slack = 0
                    else:
                        slack += 1
                    j += 1
                if hit == len(target):
                    return start_idx, word_timestamps[start_idx]["startMs"]
            i += 1
    return None, None


def sync_slides_to_voice(
    slides: list,
    word_timestamps: list,
    fps: int = FPS,
    transition_frames: int = TRANSITION_FRAMES,
    tail_frames: int = DEFAULT_TAIL_FRAMES,
) -> tuple:
    """Compute durationFrames for each slide so visual timing follows the voiceover.

    Returns (durations, total_frames). Mutates nothing; caller writes back."""
    if not slides:
        return [], 0
    if not word_timestamps:
        # No voice -> can't sync. Return whatever the slides already have.
        return [s.get("durationFrames", fps * 4) for s in slides], 0

    # Find each slide's start position in the voiceover
    starts_ms = []
    search_from = 0
    for i, slide in enumerate(slides):
        anchors = _anchor_words(slide.get("text", ""))
        if i == 0:
            # Slide 1 always starts at frame 0
            starts_ms.append(0)
            idx, _ = _find_slide_start(anchors, word_timestamps, 0)
            search_from = (idx + 1) if idx is not None else search_from
            continue
        idx, start_ms = _find_slide_start(anchors, word_timestamps, search_from)
        if idx is None or start_ms is None:
            # No anchor match -> evenly distribute the remaining slides across the
            # remaining audio so we don't collapse to zero-duration slides.
            remaining_slides = len(slides) - i
            audio_end = word_timestamps[-1]["endMs"]
            spent = starts_ms[-1]
            chunk = max(int((audio_end - spent) / max(remaining_slides, 1)), 500)
            starts_ms.append(spent + chunk)
            continue
        # Don't allow a slide to start before the previous one
        starts_ms.append(max(start_ms, starts_ms[-1] + 200))
        search_from = idx + 1

    audio_end_ms = word_timestamps[-1]["endMs"]
    durations = []
    for i, start_ms in enumerate(starts_ms):
        if i < len(starts_ms) - 1:
            end_ms = max(starts_ms[i + 1], start_ms + 333)  # min ~10 frames visible
            frames = round((end_ms - start_ms) * fps / 1000) + transition_frames
        else:
            end_ms = max(audio_end_ms, start_ms + 333)
            frames = round((end_ms - start_ms) * fps / 1000) + tail_frames
        durations.append(max(frames, fps // 2))  # floor at 0.5s per slide

    total_frames = sum(durations) - (len(durations) - 1) * transition_frames
    return durations, total_frames


def main():
    if len(sys.argv) != 2:
        print("Usage: sync_slides_to_voice.py <config.json>")
        sys.exit(1)
    config_path = sys.argv[1]
    with open(config_path) as f:
        config = json.load(f)

    word_timestamps = config.get("word_timestamps") or []
    slides = config.get("slides") or []
    if not word_timestamps:
        print("Error: config has no word_timestamps; can't sync.")
        sys.exit(1)

    durations, total = sync_slides_to_voice(slides, word_timestamps)
    voice_end_s = word_timestamps[-1]["endMs"] / 1000

    print(f"Voiceover: {voice_end_s:.2f}s")
    print(f"Per-slide durations:")
    for i, (slide, frames) in enumerate(zip(slides, durations)):
        prev = slide.get("durationFrames")
        delta = f"  (was {prev})" if prev is not None else ""
        text = slide.get("text", "")[:50]
        print(f"  Slide {i+1}: {frames}f / {frames/FPS:.2f}s{delta}  '{text}'")
        slide["durationFrames"] = frames

    print(f"Total reel: {total}f / {total/FPS:.2f}s  (voiceover: {voice_end_s:.2f}s, tail: {(total/FPS - voice_end_s):.2f}s)")

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Wrote {config_path}")


if __name__ == "__main__":
    main()
