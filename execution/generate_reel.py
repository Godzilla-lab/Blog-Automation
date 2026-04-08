#!/usr/bin/env python3
"""
Render a Daily Reel from a config JSON file using Remotion.

Usage:
    python3 execution/generate_reel.py --config workspace/reels/2026-03-28-dental/config.json
    python3 execution/generate_reel.py --config workspace/reels/2026-03-28-dental/config.json --output out/dental-reel.mp4
"""

import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REMOTION_DIR = os.path.join(PROJECT_ROOT, "skills", "remotion-video", "remotion")
NODE_BIN = os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin")


def check_prerequisites():
    """Verify node, npm, and ffmpeg are available."""
    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:{env.get('PATH', '')}"

    for cmd in ["node", "npm"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True, env=env)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Error: {cmd} not found. Expected at {NODE_BIN}")
            sys.exit(1)

    # Check npm deps
    if not os.path.exists(os.path.join(REMOTION_DIR, "node_modules")):
        print("Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=REMOTION_DIR, check=True, env=env)


def render_reel(config_path, output_path=None):
    """Render a DailyReel composition from config."""
    with open(config_path, "r") as f:
        config = json.load(f)

    slides = config.get("slides", [])
    if not slides:
        print("Error: No slides in config.")
        sys.exit(1)

    seconds_per_slide = config.get("seconds_per_slide", 4)
    total_frames = len(slides) * seconds_per_slide * 30
    total_seconds = len(slides) * seconds_per_slide

    # Build props JSON for Remotion
    props = {
        "slides": slides,
        "secondsPerSlide": seconds_per_slide,
        "accentColor": config.get("accent_color", "#FFD700"),
        "handle": config.get("handle", "@hexa_aiagency"),
    }
    if config.get("voiceover"):
        props["voiceover"] = config["voiceover"]
    if config.get("word_timestamps"):
        props["wordTimestamps"] = config["word_timestamps"]
    if config.get("bg_music"):
        props["bgMusic"] = config["bg_music"]
    if config.get("bg_music_volume"):
        props["bgMusicVolume"] = config["bg_music_volume"]

    # Determine output path (must be absolute for Remotion since it runs from REMOTION_DIR)
    if not output_path:
        config_dir = os.path.dirname(os.path.abspath(config_path))
        output_path = os.path.join(config_dir, "reel.mp4")

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write props to temp file
    props_file = os.path.join(REMOTION_DIR, ".tmp-props.json")
    with open(props_file, "w") as f:
        json.dump(props, f)

    print(f"Rendering Daily Reel:")
    print(f"  Slides: {len(slides)}")
    print(f"  Duration: {total_seconds}s ({total_frames} frames)")
    print(f"  Output: {output_path}")
    print()

    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:{env.get('PATH', '')}"

    cmd = [
        "npx", "remotion", "render",
        "src/index.ts", "DailyReel",
        output_path,
        "--codec=h264",
        f"--props={props_file}",
    ]

    result = subprocess.run(
        cmd,
        cwd=REMOTION_DIR,
        env=env,
        capture_output=True,
        text=True,
    )

    # Cleanup props file
    if os.path.exists(props_file):
        os.remove(props_file)

    if result.returncode != 0:
        print(f"Render failed:\n{result.stderr}")
        sys.exit(1)

    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\nSuccess! Output: {output_path} ({size_mb:.1f} MB)")
    else:
        print("Error: Output file not created.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Render a Daily Reel from config")
    parser.add_argument("--config", required=True, help="Path to reel config JSON")
    parser.add_argument("--output", help="Output MP4 path (default: reel.mp4 in config dir)")
    args = parser.parse_args()

    check_prerequisites()
    render_reel(args.config, args.output)


if __name__ == "__main__":
    main()
