#!/usr/bin/env python3
"""
Download an image from a URL and save it to a local path.
Used by the thread-to-carousel skill to fetch images for slides.

Usage:
    python3 execution/download_image.py --url "https://example.com/image.png" --output "workspace/carousels/2026-03-19-topic/reference/hero.png"
"""

import argparse
import os
import sys
import requests
from urllib.parse import urlparse


def download_image(url, output_path):
    """Download an image from a URL and save it locally."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers, timeout=30, stream=True)
    response.raise_for_status()

    # Verify it's actually an image
    content_type = response.headers.get("content-type", "")
    if not any(t in content_type for t in ["image", "octet-stream"]):
        print(f"Warning: content-type is '{content_type}', may not be an image")

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size = os.path.getsize(output_path)
    print(f"Downloaded: {output_path} ({file_size:,} bytes)")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download an image from a URL")
    parser.add_argument("--url", required=True, help="Image URL to download")
    parser.add_argument("--output", required=True, help="Local path to save the image")
    args = parser.parse_args()

    try:
        download_image(args.url, args.output)
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        sys.exit(1)
