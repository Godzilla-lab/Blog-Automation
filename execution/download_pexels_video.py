#!/usr/bin/env python3
"""
Search and download stock video clips from Pexels API.
Used by the daily Reel pipeline to source b-roll footage.

Usage:
    python3 execution/download_pexels_video.py --query "dental office" --output workspace/reels/footage/ --count 4
    python3 execution/download_pexels_video.py --query "business meeting" --output .tmp/footage/ --count 2 --orientation portrait
"""

import argparse
import json
import os
import sys
import requests
from dotenv import load_dotenv

# Load .env from project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

PEXELS_API_URL = "https://api.pexels.com/videos/search"


def search_videos(query, count=5, orientation="portrait", min_duration=3):
    """Search for videos on Pexels. Returns list of video metadata."""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("Error: PEXELS_API_KEY not set in .env")
        print("Get a free key at: https://www.pexels.com/api/new/")
        sys.exit(1)

    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": count * 3,  # fetch extra for QA fallbacks
        "orientation": orientation,
    }

    response = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    videos = []
    for video in data.get("videos", []):
        duration = video.get("duration", 0)
        if duration < min_duration:
            continue

        # Find the best video file: prefer HD portrait, largest adequate resolution
        # Sort descending by height so we pick the highest quality first
        video_files = sorted(
            video.get("video_files", []),
            key=lambda f: f.get("height", 0),
            reverse=True,
        )

        # Pick the largest file that's at least 1080p tall (for 1080x1920 output)
        chosen_file = None
        for vf in video_files:
            h = vf.get("height", 0)
            w = vf.get("width", 0)
            if h >= 1080 and vf.get("link"):
                chosen_file = vf
                break

        # Fallback: pick largest file >= 720p if no 1080p available
        if not chosen_file:
            for vf in video_files:
                h = vf.get("height", 0)
                if h >= 720 and vf.get("link"):
                    chosen_file = vf
                    break

        # Last resort: largest available
        if not chosen_file and video_files:
            chosen_file = video_files[0]  # already sorted descending

        if not chosen_file:
            continue

        videos.append({
            "id": video["id"],
            "duration": duration,
            "width": chosen_file.get("width", 0),
            "height": chosen_file.get("height", 0),
            "url": chosen_file["link"],
            "quality": chosen_file.get("quality", "unknown"),
            "photographer": video.get("user", {}).get("name", "Unknown"),
        })

        if len(videos) >= count * 3:
            break  # enough candidates for QA fallbacks

    return videos


def extract_frame(video_path, output_path, timestamp="00:00:01"):
    """Extract a still frame from a video using ffmpeg."""
    import shutil
    import subprocess

    # Find ffmpeg
    node_bin = os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin")
    ffmpeg = shutil.which("ffmpeg", path=f"{node_bin}:{os.environ.get('PATH', '')}")
    if not ffmpeg:
        ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("  Warning: ffmpeg not found, cannot extract frame")
        return False

    cmd = [ffmpeg, "-y", "-i", video_path, "-ss", timestamp, "-frames:v", "1", "-q:v", "2", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0 and os.path.exists(output_path)


def validate_frame(frame_path, min_brightness=30):
    """Check if an extracted frame meets quality standards."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return True, "skipped (Pillow/numpy not installed)"

    try:
        img = Image.open(frame_path)
        w, h = img.size
        if w < 480 or h < 480:
            return False, f"too small ({w}x{h})"

        arr = np.array(img.convert("L"))
        brightness = float(arr.mean())
        if brightness < min_brightness:
            return False, f"too dark (brightness={brightness:.0f})"

        file_size = os.path.getsize(frame_path)
        if file_size < 10000:
            return False, f"corrupt ({file_size // 1024}KB)"

        return True, f"ok (brightness={brightness:.0f}, {w}x{h})"
    except Exception as e:
        return False, f"error ({e})"


def download_video(url, output_path):
    """Download a single video file."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=120, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = (downloaded / total) * 100
                    print(f"\r  Downloading: {pct:.0f}%", end="", flush=True)

        size = os.path.getsize(output_path)
        print(f"\r  Downloaded: {output_path} ({size / 1024 / 1024:.1f} MB)")
        return True
    except Exception as e:
        print(f"\n  Failed to download: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Search and download Pexels stock videos")
    parser.add_argument("--query", required=True, help="Search query for videos")
    parser.add_argument("--output", default=".", help="Output directory for downloaded videos")
    parser.add_argument("--count", type=int, default=4, help="Number of videos to download")
    parser.add_argument("--orientation", default="portrait", choices=["portrait", "landscape", "square"],
                        help="Video orientation (default: portrait)")
    parser.add_argument("--min-duration", type=int, default=3, help="Minimum video duration in seconds")
    parser.add_argument("--list-only", action="store_true", help="List results without downloading")
    args = parser.parse_args()

    print(f"Searching Pexels for: '{args.query}' ({args.orientation})")
    videos = search_videos(args.query, args.count, args.orientation, args.min_duration)

    if not videos:
        print("No videos found.")
        sys.exit(1)

    print(f"Found {len(videos)} video(s):\n")
    for i, v in enumerate(videos):
        print(f"  [{i + 1}] {v['width']}x{v['height']} | {v['duration']}s | by {v['photographer']}")

    if args.list_only:
        print(f"\n{json.dumps(videos, indent=2)}")
        return

    os.makedirs(args.output, exist_ok=True)
    print(f"\nDownloading to {args.output}...")

    downloaded = []
    clip_num = 0
    for i, v in enumerate(videos):
        if clip_num >= args.count:
            break
        filename = f"clip-{clip_num + 1}.mp4"
        frame_filename = f"clip-{clip_num + 1}.jpg"
        output_path = os.path.join(args.output, filename)
        frame_path = os.path.join(args.output, frame_filename)
        if download_video(v["url"], output_path):
            if extract_frame(output_path, frame_path):
                print(f"  Extracted frame: {frame_path}")
                # Validate frame quality
                is_valid, reason = validate_frame(frame_path)
                if not is_valid:
                    print(f"  Frame failed QA: {reason}, trying next candidate...")
                    os.remove(output_path)
                    os.remove(frame_path)
                    continue
                print(f"  QA passed: {reason}")
            downloaded.append({
                "filename": filename,
                "frame": frame_filename,
                "path": output_path,
                "frame_path": frame_path,
                "duration": v["duration"],
                "width": v["width"],
                "height": v["height"],
                "photographer": v["photographer"],
                "pexels_id": v["id"],
            })
            clip_num += 1

    # Write metadata for the orchestrator
    meta_path = os.path.join(args.output, "footage_meta.json")
    with open(meta_path, "w") as f:
        json.dump(downloaded, f, indent=2)
    print(f"\nMetadata saved to {meta_path}")
    print(f"Downloaded {len(downloaded)}/{len(videos)} clips.")


if __name__ == "__main__":
    main()
