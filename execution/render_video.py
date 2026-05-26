#!/usr/bin/env python3
"""
Render video using Remotion.

Usage:
    python3 execution/render_video.py --config workspace/videos/YYYY-MM-DD-slug/config.json

Or render a specific composition directly:
    python3 execution/render_video.py --composition Results --output out/results.mp4

Config JSON format:
{
    "template": "Results",
    "output_dir": "workspace/videos/2026-03-26-highlights",
    "output_filename": "results.mp4"
}
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Find project root (directory containing CLAUDE.md)
def find_project_root():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

PROJECT_ROOT = find_project_root()
REMOTION_DIR = PROJECT_ROOT / "skills" / "remotion-video" / "remotion"
NODE_BIN = Path.home() / ".local" / "node-v22.22.2-darwin-arm64" / "bin"


def check_prerequisites():
    """Verify node, npm, ffmpeg are available."""
    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:{env.get('PATH', '')}"

    for cmd, install_hint in [
        ("node", "Install Node.js: nvm install 22 or download from nodejs.org"),
        ("npm", "npm comes with Node.js"),
        ("ffmpeg", "Download from https://www.osxexperts.net or brew install ffmpeg"),
    ]:
        if not shutil.which(cmd, path=env.get("PATH")):
            print(f"ERROR: {cmd} not found. {install_hint}")
            sys.exit(1)

    # Check node_modules
    if not (REMOTION_DIR / "node_modules").exists():
        print("Installing Remotion dependencies...")
        subprocess.run(["npm", "install"], cwd=REMOTION_DIR, env=env, check=True)
        print("Dependencies installed.")


def render_composition(composition: str, output_path: str, env: dict):
    """Render a single Remotion composition to MP4."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "npx", "remotion", "render",
        "src/index.ts", composition, str(output),
        "--codec=h264",
    ]

    print(f"Rendering {composition} -> {output}")
    result = subprocess.run(
        cmd,
        cwd=REMOTION_DIR,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR rendering {composition}:")
        print(result.stderr)
        return False

    if output.exists():
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  Done: {output} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ERROR: Output file not created")
        return False


def main():
    parser = argparse.ArgumentParser(description="Render Remotion video")
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--composition", help="Composition ID to render directly")
    parser.add_argument("--output", help="Output file path (used with --composition)")
    args = parser.parse_args()

    check_prerequisites()

    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:{env.get('PATH', '')}"

    if args.config:
        config_path = PROJECT_ROOT / args.config
        with open(config_path) as f:
            config = json.load(f)

        composition = config["template"]
        output_dir = PROJECT_ROOT / config.get("output_dir", "out")
        output_filename = config.get("output_filename", "video.mp4")
        output_path = output_dir / output_filename

        success = render_composition(composition, str(output_path), env)
        sys.exit(0 if success else 1)

    elif args.composition:
        output = args.output or f"out/{args.composition.lower()}.mp4"
        output_path = REMOTION_DIR / output
        success = render_composition(args.composition, str(output_path), env)
        sys.exit(0 if success else 1)

    else:
        print("Usage: render_video.py --config <config.json> or --composition <id>")
        sys.exit(1)


if __name__ == "__main__":
    main()
