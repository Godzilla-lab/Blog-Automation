#!/usr/bin/env python3
"""
Search for images using Tavily API and download them.
Used by the thread-to-carousel skill to find relevant images for slides.

Usage:
    python3 execution/search_images.py --query "OpenClaw AI logo" --output "workspace/carousels/2026-03-19-topic/reference/" --count 3
    python3 execution/search_images.py --query "Gemini 3.1 Pro screenshot" --output "workspace/carousels/2026-03-19-topic/reference/" --count 1 --download
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


def search_images(query, count=5):
    """Search for images using Tavily API. Returns list of image URLs with context."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY not set in .env")
        sys.exit(1)

    from tavily import TavilyClient
    client = TavilyClient(api_key=api_key)

    results = client.search(
        query=query,
        search_depth="basic",
        include_images=True,
        max_results=count,
    )

    images = []

    # Tavily returns images as a list of URLs
    for i, img_url in enumerate(results.get("images", [])):
        images.append({
            "index": i + 1,
            "url": img_url,
        })

    # Also check results for images in the content
    for result in results.get("results", []):
        if result.get("url", "").endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            images.append({
                "index": len(images) + 1,
                "url": result["url"],
                "title": result.get("title", ""),
            })

    return images[:count]


def download_image(url, output_path):
    """Download a single image."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        size = os.path.getsize(output_path)
        print(f"  Downloaded: {output_path} ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"  Failed to download {url}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Search for images using Tavily")
    parser.add_argument("--query", required=True, help="Search query for images")
    parser.add_argument("--output", default=".", help="Output directory for downloaded images")
    parser.add_argument("--count", type=int, default=5, help="Number of images to find")
    parser.add_argument("--download", action="store_true", help="Download images (otherwise just list URLs)")
    args = parser.parse_args()

    print(f"Searching for: {args.query}")
    images = search_images(args.query, args.count)

    if not images:
        print("No images found.")
        sys.exit(1)

    print(f"Found {len(images)} image(s):\n")

    for img in images:
        print(f"  [{img['index']}] {img['url']}")
        if img.get("title"):
            print(f"      {img['title']}")

    if args.download:
        os.makedirs(args.output, exist_ok=True)
        print(f"\nDownloading to {args.output}...")

        for img in images:
            url = img["url"]
            # Determine file extension
            ext = ".png"
            for e in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                if e in url.lower():
                    ext = e
                    break
            filename = f"image_{img['index']}{ext}"
            output_path = os.path.join(args.output, filename)
            download_image(url, output_path)

    # Also output JSON for programmatic use
    print(f"\n{json.dumps(images, indent=2)}")


if __name__ == "__main__":
    main()
