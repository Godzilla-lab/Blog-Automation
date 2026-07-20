#!/usr/bin/env python3
"""
QA review script for generated Instagram Reels.

Checks a reel directory for completeness, audio/video sync,
branding consistency, caption quality, and footage integrity.

Usage:
    python3 execution/review_reel.py workspace/reels/2026-04-14-dental-practice-833-percent-roi
    python3 execution/review_reel.py workspace/reels/2026-04-14-*   # review multiple
    python3 execution/review_reel.py --all                          # review all reels from today
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REMOTION_PUBLIC = os.path.join(PROJECT_ROOT, "skills", "remotion-video", "remotion", "public")
FFMPEG_BIN = (
    shutil.which("ffmpeg")
    or os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin/ffmpeg")
)
# Mean Y-plane brightness floor (0-255). A pure-black background averages ~10
# even with overlay text + watermark. Real Pexels footage with dark overlay
# averages 40-90. Slide that drops to <BLACK_FRAME_BRIGHTNESS_FLOOR almost
# always means b-roll didn't paint (FootageBackground rendered null).
BLACK_FRAME_BRIGHTNESS_FLOOR = 18

# Thresholds
MIN_REEL_SIZE_MB = 3
MIN_CAPTION_LENGTH = 200
MAX_CAPTION_LENGTH = 2200
MIN_HASHTAGS = 10
MAX_HASHTAGS = 30
MIN_SLIDES = 4
MAX_SLIDES = 20
EXPECTED_HANDLE = "@hexa_aiagency"
# CTA keyword is now topic-driven, not niche-locked. We just check it looks
# like a real word a viewer would actually type.
CTA_KEYWORD_PATTERN = re.compile(r"^[A-Z]{3,15}$")
BAD_CHARS = ["\u2014", "\u2013"]  # em dash, en dash
BAD_OPENERS = ["did you know", "have you ever wondered"]


class ReelReview:
    def __init__(self, reel_dir):
        self.reel_dir = os.path.abspath(reel_dir)
        self.slug = os.path.basename(self.reel_dir)
        self.config = None
        self.errors = []    # critical - must fix
        self.warnings = []  # should fix

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def check_files_exist(self):
        """Check all expected output files exist."""
        config_path = os.path.join(self.reel_dir, "config.json")
        reel_path = os.path.join(self.reel_dir, "reel.mp4")
        caption_path = os.path.join(self.reel_dir, "caption.txt")

        if not os.path.exists(config_path):
            self.error("MISSING config.json")
            return False
        if not os.path.exists(reel_path):
            self.error("MISSING reel.mp4 - video not rendered")
        else:
            size_mb = os.path.getsize(reel_path) / 1024 / 1024
            if size_mb < MIN_REEL_SIZE_MB:
                self.error(f"reel.mp4 too small ({size_mb:.1f}MB) - likely corrupted")
        if not os.path.exists(caption_path):
            self.error("MISSING caption.txt - no Instagram caption")

        # Load config for subsequent checks
        with open(config_path) as f:
            self.config = json.load(f)
        return True

    def check_slides(self):
        """Validate slide structure and content."""
        slides = self.config.get("slides", [])
        if len(slides) < MIN_SLIDES:
            self.error(f"Only {len(slides)} slides (min {MIN_SLIDES})")
        if len(slides) > MAX_SLIDES:
            self.warn(f"{len(slides)} slides (max recommended {MAX_SLIDES})")

        for i, slide in enumerate(slides):
            num = i + 1
            text = slide.get("text", "")
            emphasis = slide.get("emphasis", "")
            footage = slide.get("footage", "")
            footages = slide.get("footages") or []

            if not text:
                self.error(f"Slide {num}: empty text")
            if not emphasis:
                self.warn(f"Slide {num}: no emphasis word set")
            elif emphasis.lower() not in text.lower():
                self.warn(f"Slide {num}: emphasis '{emphasis}' not found in text")
            if not footage and not footages:
                self.error(f"Slide {num}: no footage path")

            # Check for bad characters
            for char in BAD_CHARS:
                if char in text:
                    self.error(f"Slide {num}: contains em/en dash in text")
                    break

        # Last slide should be CTA
        if slides and slides[-1].get("type") != "cta":
            self.warn("Last slide is not type 'cta'")

        # First slide hook check
        if slides:
            first_text = slides[0].get("text", "").lower()
            for opener in BAD_OPENERS:
                if first_text.startswith(opener):
                    self.error(f"Hook starts with '{opener}' - weak opener")

    def check_footage_exists(self):
        """Verify all referenced footage files actually exist."""
        slides = self.config.get("slides", [])
        for i, slide in enumerate(slides):
            paths = []
            if slide.get("footage"):
                paths.append(slide["footage"])
            if slide.get("footages"):
                paths.extend(slide["footages"])
            for footage in paths:
                full_path = os.path.join(REMOTION_PUBLIC, footage)
                if not os.path.exists(full_path):
                    self.error(f"Slide {i+1}: footage missing at {footage}")
                elif os.path.getsize(full_path) < 10000:  # <10KB is suspicious
                    self.warn(f"Slide {i+1}: footage suspiciously small ({os.path.getsize(full_path)} bytes)")

    def check_voiceover_sync(self):
        """Critical: verify video duration >= voiceover duration."""
        voiceover = self.config.get("voiceover", "")
        timestamps = self.config.get("word_timestamps", [])
        slides = self.config.get("slides", [])
        sps = self.config.get("seconds_per_slide", 4)

        if not voiceover:
            self.warn("No voiceover configured")
            return

        vo_path = os.path.join(REMOTION_PUBLIC, voiceover)
        if not os.path.exists(vo_path):
            self.error(f"Voiceover file missing: {voiceover}")
            return
        if os.path.getsize(vo_path) < 1000:
            self.error("Voiceover file is empty/corrupt")
            return

        if not timestamps:
            self.warn("No word timestamps - synced captions won't work")
            return

        vo_duration_s = timestamps[-1]["endMs"] / 1000

        # Use real per-slide durationFrames when present (post-sync); fall back
        # to len(slides) * sps only for legacy configs that never ran the sync step.
        FPS = 30
        TRANSITION_FRAMES = 15
        frames_per_slide = sps * FPS
        sum_frames = sum(
            s.get("durationFrames", frames_per_slide) for s in slides
        )
        video_duration_s = (sum_frames - (len(slides) - 1) * TRANSITION_FRAMES) / FPS

        # Audio MUST fit in the video. Audio is what drives the content; if it
        # gets cut, the reel is broken. Anything past the last word is just tail
        # transition/breathing room.
        if video_duration_s + 0.05 < vo_duration_s:
            gap = vo_duration_s - video_duration_s
            self.error(
                f"AUDIO CUT OFF: voiceover is {vo_duration_s:.1f}s but video is only "
                f"{video_duration_s:.1f}s ({gap:.1f}s of audio gets cut). "
                f"Re-run the slide-to-voice sync (sync_slides_to_voice.py)."
            )

        # Check timestamps are ordered
        for i in range(1, len(timestamps)):
            if timestamps[i]["startMs"] < timestamps[i-1]["startMs"]:
                self.error(f"Word timestamps out of order at index {i}")
                break

    def check_branding(self):
        """Verify consistent branding."""
        handle = self.config.get("handle", "")
        if handle != EXPECTED_HANDLE:
            self.error(f"Handle is '{handle}', expected '{EXPECTED_HANDLE}'")

        cta = self.config.get("cta_keyword", "")
        if cta and not CTA_KEYWORD_PATTERN.match(cta):
            self.warn(f"CTA keyword '{cta}' doesn't look like a normal one-word call (3-15 uppercase letters)")

        color = self.config.get("accent_color", "")
        if color and not color.startswith("#"):
            self.warn(f"accent_color '{color}' doesn't look like a hex color")

    def check_caption(self):
        """Validate caption.txt quality."""
        caption_path = os.path.join(self.reel_dir, "caption.txt")
        if not os.path.exists(caption_path):
            return

        with open(caption_path) as f:
            caption = f.read()

        if len(caption) < MIN_CAPTION_LENGTH:
            self.warn(f"Caption too short ({len(caption)} chars, min {MIN_CAPTION_LENGTH})")
        if len(caption) > MAX_CAPTION_LENGTH:
            self.warn(f"Caption too long ({len(caption)} chars, max {MAX_CAPTION_LENGTH})")

        # Check for em/en dashes
        for char in BAD_CHARS:
            if char in caption:
                self.error("Caption contains em/en dash - use hyphens instead")
                break

        # Check hashtags
        hashtags = [w for w in caption.split() if w.startswith("#")]
        if len(hashtags) < MIN_HASHTAGS:
            self.warn(f"Only {len(hashtags)} hashtags (recommended {MIN_HASHTAGS}-{MAX_HASHTAGS})")
        if len(hashtags) > MAX_HASHTAGS:
            self.warn(f"{len(hashtags)} hashtags (max recommended {MAX_HASHTAGS})")

        # Check CTA keyword present
        cta = self.config.get("cta_keyword", "")
        if cta and cta not in caption:
            self.warn(f"CTA keyword '{cta}' not found in caption")

        # Check first line isn't too long (Instagram truncates around 125 chars)
        first_line = caption.split("\n")[0]
        if len(first_line) > 150:
            self.warn(f"First line is {len(first_line)} chars - may get truncated in feed")

    def check_rendered_frames(self):
        """Sample one frame per slide from reel.mp4 and confirm it has b-roll.

        This is the deterministic substitute for Agent 2 (reality_qa_reel.py)
        — it catches the failure mode where multi-clip or single-clip slides
        render with a pure-black background because the footage prop was
        silently dropped or the file resolved to nothing. Runs without any
        Anthropic dependency so it works when the API key is down.
        """
        reel_mp4 = os.path.join(self.reel_dir, "reel.mp4")
        if not os.path.exists(reel_mp4):
            return
        if not FFMPEG_BIN or not os.path.exists(FFMPEG_BIN):
            self.warn("ffmpeg not found — skipping rendered-frame brightness check")
            return

        slides = self.config.get("slides", [])
        if not slides:
            return

        FPS = 30
        TRANSITION_FRAMES = 15
        sps = self.config.get("seconds_per_slide", 4)
        frames_per_slide_fallback = sps * FPS

        # Compute each slide's visible window midpoint in seconds, matching
        # DailyReel's actual layout (transitions subtract 15f per gap).
        cursor_frames = 0
        slide_midpoints = []
        for i, slide in enumerate(slides):
            df = slide.get("durationFrames", frames_per_slide_fallback)
            mid_frames = cursor_frames + df // 2
            slide_midpoints.append(mid_frames / FPS)
            cursor_frames += df
            if i < len(slides) - 1:
                cursor_frames -= TRANSITION_FRAMES

        qa_dir = os.path.join(self.reel_dir, ".qa_frames")
        os.makedirs(qa_dir, exist_ok=True)
        for i, t in enumerate(slide_midpoints):
            slide = slides[i]
            has_footage = bool(slide.get("footage") or slide.get("footages"))
            if not has_footage:
                continue

            frame_path = os.path.join(qa_dir, f"slide-{i+1}.jpg")
            # signalstats writes YAVG (mean Y-plane brightness) to log via -f null
            cmd = [
                FFMPEG_BIN, "-hide_banner", "-loglevel", "info",
                "-ss", f"{t:.3f}", "-i", reel_mp4,
                "-vf", "select=eq(n\\,0),signalstats,metadata=print",
                "-frames:v", "1", "-y", frame_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            # YAVG appears in stderr as "lavfi.signalstats.YAVG=<float>"
            m = re.search(r"YAVG=([\d.]+)", proc.stderr or "")
            if not m:
                # Fall back: use ffmpeg's blackdetect on a 0.1s clip at midpoint
                bd_cmd = [
                    FFMPEG_BIN, "-hide_banner", "-loglevel", "info",
                    "-ss", f"{t:.3f}", "-t", "0.1", "-i", reel_mp4,
                    "-vf", "blackdetect=d=0.05:pic_th=0.95", "-f", "null", "-",
                ]
                bd = subprocess.run(bd_cmd, capture_output=True, text=True)
                if "black_start" in (bd.stderr or ""):
                    self.error(
                        f"Slide {i+1}: rendered frame at t={t:.1f}s is mostly black — "
                        f"b-roll did not paint. Check FootageBackground wiring."
                    )
                continue

            yavg = float(m.group(1))
            if yavg < BLACK_FRAME_BRIGHTNESS_FLOOR:
                self.error(
                    f"Slide {i+1}: rendered frame at t={t:.1f}s has mean brightness "
                    f"{yavg:.1f} (<{BLACK_FRAME_BRIGHTNESS_FLOOR}) — b-roll likely missing. "
                    f"Sample saved to {frame_path}."
                )

    def check_bg_music(self):
        """Verify background music is set and exists."""
        bg = self.config.get("bg_music", "")
        if not bg:
            self.warn("No background music configured")
            return
        bg_path = os.path.join(REMOTION_PUBLIC, bg)
        if not os.path.exists(bg_path):
            self.error(f"Background music file missing: {bg}")

        vol = self.config.get("bg_music_volume", 0)
        if vol > 0.2:
            self.warn(f"BG music volume is {vol} - may overpower voiceover (recommended 0.08-0.15)")

    def run(self):
        """Run all checks. Returns (errors, warnings)."""
        if not self.check_files_exist():
            return self.errors, self.warnings

        self.check_slides()
        self.check_footage_exists()
        self.check_voiceover_sync()
        self.check_branding()
        self.check_caption()
        self.check_bg_music()
        self.check_rendered_frames()

        return self.errors, self.warnings


def review_reel(reel_dir):
    """Review a single reel directory. Returns True if passed."""
    reviewer = ReelReview(reel_dir)
    errors, warnings = reviewer.run()

    slug = reviewer.slug
    passed = len(errors) == 0

    # Print results
    status = "PASS" if passed else "FAIL"
    print(f"\n{'='*60}")
    print(f"  [{status}] {slug}")
    print(f"{'='*60}")

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    [x] {e}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    [!] {w}")

    if not errors and not warnings:
        print("  All checks passed.")

    return passed


def main():
    parser = argparse.ArgumentParser(description="QA review for generated Instagram Reels")
    parser.add_argument("dirs", nargs="*", help="Reel directories to review")
    parser.add_argument("--all", action="store_true", help="Review all reels from today")
    parser.add_argument("--date", help="Review all reels from a specific date (YYYY-MM-DD)")
    args = parser.parse_args()

    reel_dirs = []

    if args.all or args.date:
        target_date = args.date or date.today().isoformat()
        reels_base = os.path.join(PROJECT_ROOT, "workspace", "reels")
        reel_dirs = sorted(glob.glob(os.path.join(reels_base, f"{target_date}-*")))
        if not reel_dirs:
            print(f"No reels found for {target_date}")
            sys.exit(1)
    elif args.dirs:
        for d in args.dirs:
            expanded = glob.glob(d)
            reel_dirs.extend(expanded if expanded else [d])
    else:
        parser.print_help()
        sys.exit(1)

    # Filter to only directories
    reel_dirs = [d for d in reel_dirs if os.path.isdir(d)]

    results = []
    for reel_dir in reel_dirs:
        passed = review_reel(reel_dir)
        results.append((os.path.basename(reel_dir), passed))

    # Summary
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed

    print(f"\n{'#'*60}")
    print(f"  REVIEW SUMMARY: {passed}/{total} passed, {failed} failed")
    print(f"{'#'*60}")

    for name, p in results:
        print(f"  {'PASS' if p else 'FAIL'}  {name}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
