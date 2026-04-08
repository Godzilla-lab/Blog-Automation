#!/usr/bin/env python3
"""
Master orchestrator: generate N Instagram Reels per day.

Full pipeline per reel:
  1. Pick topic (from trends, blog posts, or evergreen)
  2. Generate reel script (Claude → slides + voiceover + footage queries)
  3. Download stock footage (Pexels API)
  4. Generate voiceover audio (Edge TTS)
  5. Render video (Remotion DailyReel)
  6. Generate Instagram caption

Usage:
    python3 execution/run_daily_reels.py --count 3
    python3 execution/run_daily_reels.py --count 1 --niche dental
    python3 execution/run_daily_reels.py --count 3 --dry-run
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

REMOTION_PUBLIC = os.path.join(project_root, "skills", "remotion-video", "remotion", "public")
NODE_BIN = os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin")

# Content mix: how often each reel type should appear
REEL_TYPE_WEIGHTS = {
    "pas": 40,
    "before_after": 25,
    "lead_magnet": 20,
    "trend": 15,
}

NICHES = ["dental", "property", "cleaning", "general"]


def pick_reel_type() -> str:
    """Pick a reel type based on content mix weights."""
    types = list(REEL_TYPE_WEIGHTS.keys())
    weights = list(REEL_TYPE_WEIGHTS.values())
    return random.choices(types, weights=weights, k=1)[0]


def pick_niche(exclude: list = None) -> str:
    """Pick a niche, avoiding the ones we just used (rotation)."""
    available = [n for n in NICHES if n not in (exclude or [])]
    if not available:
        available = NICHES
    return random.choice(available)


def pick_topic(niche: str) -> str:
    """Pick a topic — from trends file, blog posts, or evergreen fallback."""
    # Try trend file first
    trends_file = os.path.join(project_root, ".tmp", "ai_trends.json")
    if os.path.exists(trends_file):
        with open(trends_file, "r") as f:
            trends_data = json.load(f)
        niche_trends = trends_data.get("niche_trends", [])
        if niche_trends:
            trend = random.choice(niche_trends)
            return trend["title"]

    # Try blog posts
    blog_output = os.path.join(project_root, "blog-automation", "output")
    if os.path.exists(blog_output):
        blog_dirs = [d for d in os.listdir(blog_output) if os.path.isdir(os.path.join(blog_output, d))]
        if blog_dirs:
            chosen = random.choice(blog_dirs)
            # Convert slug to topic: "2026-03-19-why-dental-appointment-reminders-dont-work"
            topic = chosen.split("-", 3)[-1].replace("-", " ") if len(chosen.split("-")) > 3 else chosen
            return topic

    # Evergreen fallback
    evergreen = {
        "dental": [
            "dental no-shows cost practices thousands",
            "why dental appointment reminders don't work",
            "how AI recall systems increase chair utilization",
        ],
        "property": [
            "why property managers are overwhelmed with tenant communications",
            "automating maintenance requests saves 10+ hours a week",
            "the hidden cost of manual rent collection",
        ],
        "cleaning": [
            "why cleaning companies lose contracts over communication",
            "employee scheduling kills cleaning business productivity",
            "automating client check-ins retains more contracts",
        ],
        "general": [
            "why most small businesses waste 20 hours a week on manual tasks",
            "AI automation ROI: what businesses actually see in 90 days",
            "the 3 workflows every service business should automate first",
        ],
    }
    topics = evergreen.get(niche, evergreen["general"])
    return random.choice(topics)


def run_step(description: str, cmd: list, env: dict = None, cwd: str = None) -> bool:
    """Run a pipeline step with logging."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")

    result = subprocess.run(
        cmd,
        env=env or os.environ.copy(),
        cwd=cwd or project_root,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode})")
        if result.stderr:
            print(result.stderr[:500])
        return False
    return True


def generate_one_reel(index: int, niche: str, reel_type: str, topic: str, output_base: str) -> dict:
    """Generate a single reel through the full pipeline. Returns result dict."""
    today = date.today().isoformat()
    slug = topic.lower().replace(" ", "-").replace("'", "")[:50]
    reel_dir = os.path.join(output_base, f"{today}-{slug}")
    os.makedirs(reel_dir, exist_ok=True)

    config_path = os.path.join(reel_dir, "config.json")
    footage_dir = os.path.join(REMOTION_PUBLIC, "reels", f"{today}-{slug}")
    voiceover_path = os.path.join(REMOTION_PUBLIC, "reels", f"{today}-{slug}", "voiceover.mp3")
    timestamps_path = os.path.join(REMOTION_PUBLIC, "reels", f"{today}-{slug}", "voiceover_timestamps.json")
    reel_output = os.path.join(reel_dir, "reel.mp4")

    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:{env.get('PATH', '')}"

    result = {
        "index": index,
        "niche": niche,
        "type": reel_type,
        "topic": topic,
        "dir": reel_dir,
        "success": False,
    }

    # Step 1: Generate script
    if not run_step(
        f"[Reel {index+1}] Generating script: {topic}",
        ["python3", os.path.join(script_dir, "generate_reel_script.py"),
         "--topic", topic, "--niche", niche, "--type", reel_type,
         "--output", config_path],
    ):
        return result

    # Load the generated config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Step 2: Download footage for each slide (downloads .mp4 + extracts .jpg frame)
    os.makedirs(footage_dir, exist_ok=True)
    slides = config.get("slides", [])
    for i, slide in enumerate(slides):
        query = slide.get("footage_query", slide.get("text", "business")[:30])
        clip_path = os.path.join(footage_dir, f"clip-{i+1}.mp4")
        frame_path = os.path.join(footage_dir, f"clip-{i+1}.jpg")

        if not run_step(
            f"[Reel {index+1}] Downloading footage {i+1}/{len(slides)}: '{query}'",
            ["python3", os.path.join(script_dir, "download_pexels_video.py"),
             "--query", query, "--output", footage_dir, "--count", "1",
             "--orientation", "portrait"],
        ):
            print(f"  Warning: Footage download failed for slide {i+1}, using fallback")

        # Rename the downloaded clip + frame to match expected path
        generic_clip = os.path.join(footage_dir, "clip-1.mp4")
        generic_frame = os.path.join(footage_dir, "clip-1.jpg")
        if os.path.exists(generic_clip) and generic_clip != clip_path:
            os.rename(generic_clip, clip_path)
        if os.path.exists(generic_frame) and generic_frame != frame_path:
            os.rename(generic_frame, frame_path)

        # Use .mp4 for Remotion (OffthreadVideo decodes via FFmpeg, not Chrome)
        slide["footage"] = f"reels/{today}-{slug}/clip-{i+1}.mp4"
        # Fall back to .jpg if .mp4 doesn't exist
        if not os.path.exists(clip_path) and os.path.exists(frame_path):
            slide["footage"] = f"reels/{today}-{slug}/clip-{i+1}.jpg"

    # Step 3: Generate voiceover
    voiceover_script = config.get("voiceover_script", "")
    if voiceover_script:
        os.makedirs(os.path.dirname(voiceover_path), exist_ok=True)
        if run_step(
            f"[Reel {index+1}] Generating voiceover",
            ["python3", os.path.join(script_dir, "generate_voiceover.py"),
             "--text", voiceover_script,
             "--output", voiceover_path],
        ):
            config["voiceover"] = f"reels/{today}-{slug}/voiceover.mp3"

            # Load word timestamps
            if os.path.exists(timestamps_path):
                with open(timestamps_path, "r") as f:
                    config["word_timestamps"] = json.load(f)

    # Pick background music based on reel type (randomly from available tracks per mood)
    BG_MUSIC_MAP = {
        "pas": "bg-dramatic",         # problem-agitation-solution: serious tone
        "before_after": "bg-upbeat",   # transformation: motivational
        "lead_magnet": "bg-corporate",  # free value + CTA: professional
        "trend": "bg-energetic",        # trend reaction: high energy
    }
    BG_MUSIC_FALLBACK = "bg-chill"
    mood_prefix = BG_MUSIC_MAP.get(reel_type, BG_MUSIC_FALLBACK)
    sfx_dir = os.path.join(REMOTION_PUBLIC, "sfx")
    mood_tracks = [
        f for f in os.listdir(sfx_dir)
        if f.startswith(mood_prefix) and f.endswith(".mp3")
    ] if os.path.exists(sfx_dir) else []
    if mood_tracks:
        bg_track = f"sfx/{random.choice(mood_tracks)}"
        config["bg_music"] = bg_track
        config["bg_music_volume"] = 0.12

    # Save updated config with footage paths and voiceover
    config["handle"] = "@hexa_aiagency"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Step 4: Render video
    if not run_step(
        f"[Reel {index+1}] Rendering video",
        ["python3", os.path.join(script_dir, "generate_reel.py"),
         "--config", config_path, "--output", reel_output],
        env=env,
    ):
        return result

    # Step 5: Generate Instagram caption
    run_step(
        f"[Reel {index+1}] Generating Instagram caption",
        ["python3", os.path.join(script_dir, "generate_ig_caption.py"),
         "--config", config_path],
    )

    if os.path.exists(reel_output):
        size_mb = os.path.getsize(reel_output) / 1024 / 1024
        result["success"] = True
        result["output"] = reel_output
        result["size_mb"] = round(size_mb, 1)
        print(f"\n  Reel {index+1} complete: {reel_output} ({size_mb:.1f} MB)")

    return result


def main():
    parser = argparse.ArgumentParser(description="Generate daily Instagram Reels")
    parser.add_argument("--count", type=int, default=3, help="Number of reels to generate (default: 3)")
    parser.add_argument("--niche", choices=NICHES, help="Force a specific niche (otherwise rotates)")
    parser.add_argument("--topic", help="Force a specific topic for all reels")
    parser.add_argument("--type", dest="reel_type", choices=list(REEL_TYPE_WEIGHTS.keys()),
                        help="Force a specific reel type")
    parser.add_argument("--output", default=os.path.join(project_root, "workspace", "reels"),
                        help="Output base directory")
    parser.add_argument("--dry-run", action="store_true", help="Plan the reels without generating")
    args = parser.parse_args()

    print(f"\n{'#'*60}")
    print(f"  DAILY REELS PIPELINE — {date.today().isoformat()}")
    print(f"  Generating {args.count} reel(s)")
    print(f"{'#'*60}")

    # Plan the reels
    recent_niches = []
    plans = []
    for i in range(args.count):
        niche = args.niche or pick_niche(exclude=recent_niches[-2:] if len(recent_niches) >= 2 else [])
        reel_type = args.reel_type or pick_reel_type()
        topic = args.topic or pick_topic(niche)

        plans.append({"niche": niche, "type": reel_type, "topic": topic})
        recent_niches.append(niche)

    print(f"\n  Planned reels:")
    for i, p in enumerate(plans):
        print(f"    {i+1}. [{p['niche']}] [{p['type']}] {p['topic']}")

    if args.dry_run:
        print("\n  Dry run — no reels generated.")
        return

    # Generate each reel
    results = []
    for i, plan in enumerate(plans):
        result = generate_one_reel(
            index=i,
            niche=plan["niche"],
            reel_type=plan["type"],
            topic=plan["topic"],
            output_base=args.output,
        )
        results.append(result)

    # Summary
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\n{'#'*60}")
    print(f"  SUMMARY")
    print(f"{'#'*60}")
    print(f"  Generated: {len(successful)}/{len(results)} reels")

    for r in successful:
        print(f"    {r['index']+1}. [{r['niche']}] {r['topic'][:50]} -> {r.get('output', '?')}")

    if failed:
        print(f"\n  Failed:")
        for r in failed:
            print(f"    {r['index']+1}. [{r['niche']}] {r['topic'][:50]}")

    # Save run log
    log_path = os.path.join(args.output, f"run-{date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump({"date": date.today().isoformat(), "results": results}, f, indent=2, default=str)
    print(f"\n  Run log: {log_path}")


if __name__ == "__main__":
    main()
