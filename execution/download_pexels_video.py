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
PIXABAY_API_URL = "https://pixabay.com/api/videos/"


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

        # The reel renders at 1080x1920. Pick the SMALLEST file that's >= 1080p
        # tall — 4K source files are 3-5x bigger, download slower, and are more
        # likely to fail mid-stream or have decode artifacts in the H.264 chunks.
        video_files = sorted(
            video.get("video_files", []),
            key=lambda f: f.get("height", 0),
        )

        chosen_file = None
        for vf in video_files:
            h = vf.get("height", 0)
            if h >= 1080 and vf.get("link"):
                chosen_file = vf
                break

        # Fallback: any file >= 720p (still acceptable, will scale up)
        if not chosen_file:
            for vf in video_files:
                h = vf.get("height", 0)
                if h >= 720 and vf.get("link"):
                    chosen_file = vf
                    break

        # Last resort: largest available
        if not chosen_file and video_files:
            chosen_file = video_files[-1]  # largest

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


def search_pixabay(query, count=5, orientation="vertical", min_duration=3):
    """Search for videos on Pixabay as fallback source."""
    api_key = os.getenv("PIXABAY_API_KEY")
    if not api_key:
        return []  # silently skip if no key

    params = {
        "key": api_key,
        "q": query,
        "video_type": "film",
        "orientation": orientation,
        "per_page": count * 3,
        "safesearch": "true",
    }

    try:
        response = requests.get(PIXABAY_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"  Pixabay search failed: {e}")
        return []

    videos = []
    for hit in data.get("hits", []):
        duration = hit.get("duration", 0)
        if duration < min_duration:
            continue

        # Pixabay provides videos in multiple sizes
        video_data = hit.get("videos", {})
        # Prefer large > medium > small
        chosen = None
        for size_key in ["large", "medium", "small"]:
            vf = video_data.get(size_key, {})
            if vf.get("url") and vf.get("height", 0) >= 720:
                chosen = vf
                break
        if not chosen:
            chosen = video_data.get("medium", video_data.get("small", {}))
        if not chosen or not chosen.get("url"):
            continue

        videos.append({
            "id": hit.get("id", 0),
            "duration": duration,
            "width": chosen.get("width", 0),
            "height": chosen.get("height", 0),
            "url": chosen["url"],
            "quality": "pixabay",
            "photographer": hit.get("user", "Unknown"),
        })

        if len(videos) >= count * 3:
            break

    return videos


def search_all_sources(query, count=5, orientation="portrait", min_duration=3):
    """Search Pexels + Pixabay, merge results sorted by resolution."""
    pexels_results = search_videos(query, count, orientation, min_duration)
    pixabay_orientation = "vertical" if orientation == "portrait" else "horizontal"
    pixabay_results = search_pixabay(query, count, pixabay_orientation, min_duration)

    # Merge and sort by height (highest quality first)
    all_results = pexels_results + pixabay_results
    all_results.sort(key=lambda v: v.get("height", 0), reverse=True)
    return all_results


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


def _verify_video_decodes(path):
    """Run ffmpeg null-decode to check the file isn't truncated/corrupt.
    Returns (ok, message)."""
    import shutil
    import subprocess
    node_bin = os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin")
    ffmpeg = shutil.which("ffmpeg", path=f"{node_bin}:{os.environ.get('PATH', '')}") or shutil.which("ffmpeg")
    if not ffmpeg:
        return True, "ffmpeg not available, skipped"
    r = subprocess.run(
        [ffmpeg, "-v", "error", "-i", path, "-f", "null", "-"],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or "Invalid NAL" in r.stderr or "partial file" in r.stderr:
        first = r.stderr.strip().splitlines()[0] if r.stderr.strip() else "decode error"
        return False, first[:120]
    return True, "decodes cleanly"


def download_video(url, output_path, max_attempts=3):
    """Download a single video file. Verifies Content-Length match and ffmpeg-decodes
    cleanly; retries on truncation/corruption."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, headers=headers, timeout=(15, 60), stream=True)
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

            # Bytes check: Content-Length must match (when provided)
            if total > 0 and size != total:
                last_err = f"truncated: got {size}/{total} bytes ({size*100//total}%)"
                print(f"\n  Attempt {attempt}: {last_err}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                continue

            # Decode check: ffmpeg must read the whole file without errors
            ok, msg = _verify_video_decodes(output_path)
            if not ok:
                last_err = f"corrupt: {msg}"
                print(f"\n  Attempt {attempt}: {last_err}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                continue

            print(f"\r  Downloaded: {output_path} ({size / 1024 / 1024:.1f} MB, {msg})")
            return True
        except Exception as e:
            last_err = str(e)
            print(f"\n  Attempt {attempt} failed: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass

    print(f"  Giving up after {max_attempts} attempts: {last_err}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Search and download Pexels stock videos")
    parser.add_argument("--query", required=True, help="Search query for videos")
    parser.add_argument("--output", default=".", help="Output directory for downloaded videos")
    parser.add_argument("--count", type=int, default=4, help="Number of videos to download")
    parser.add_argument("--orientation", default="portrait", choices=["portrait", "landscape", "square"],
                        help="Video orientation (default: portrait)")
    parser.add_argument("--min-duration", type=int, default=6, help="Minimum video duration in seconds (default 6 — covers most slides without looping)")
    parser.add_argument("--list-only", action="store_true", help="List results without downloading")
    parser.add_argument("--filename", help="Explicit output filename (e.g. clip-3.mp4). When set, --count is forced to 1 and the file goes directly to <output>/<filename>. Use this when downloading per-slide to avoid clip-1 collisions.")
    args = parser.parse_args()

    if args.filename:
        args.count = 1

    print(f"Searching Pexels for: '{args.query}' ({args.orientation})")
    videos = search_all_sources(args.query, args.count, args.orientation, args.min_duration)

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
        if args.filename:
            filename = args.filename
            frame_filename = os.path.splitext(args.filename)[0] + ".jpg"
        else:
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
