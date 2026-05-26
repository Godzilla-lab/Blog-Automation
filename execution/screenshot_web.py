#!/usr/bin/env python3
"""
Screenshot fallback for image sourcing.
When Tavily can't find a matching image, this script searches the web
and takes a screenshot of the most relevant result.

Usage:
    # Search Google Images and screenshot the top result page
    python3 execution/screenshot_web.py --query "dental office empty chairs" --output workspace/carousels/slug/reference/screenshot_1.png

    # Screenshot a specific URL
    python3 execution/screenshot_web.py --url "https://example.com/page" --output workspace/carousels/slug/reference/screenshot_1.png

    # Search and take multiple screenshots
    python3 execution/screenshot_web.py --query "AI chatbot dashboard" --output workspace/carousels/slug/reference/ --count 3

    # Crop to a specific region (x, y, width, height)
    python3 execution/screenshot_web.py --url "https://example.com" --output shot.png --crop 0,100,1080,800
"""

import argparse
import os
import sys
import time
import urllib.parse

from playwright.sync_api import sync_playwright


def screenshot_url(page, url, output_path, crop=None, wait_seconds=2):
    """Navigate to a URL and take a screenshot."""
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(wait_seconds)  # let lazy-loaded content appear

        # Set viewport to a clean size for carousel images
        page.set_viewport_size({"width": 1280, "height": 900})
        time.sleep(0.5)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if crop:
            x, y, w, h = crop
            page.screenshot(
                path=output_path,
                clip={"x": x, "y": y, "width": w, "height": h},
            )
        else:
            page.screenshot(path=output_path, full_page=False)

        size = os.path.getsize(output_path)
        print(f"  Saved: {output_path} ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"  Failed to screenshot {url}: {e}")
        return False


def search_and_screenshot(page, query, output_dir, count=1, crop=None):
    """Search Google Images, visit top result pages, and screenshot them."""
    os.makedirs(output_dir, exist_ok=True)
    saved = []

    # Use DuckDuckGo image search (avoids Google bot detection)
    search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&iax=images&ia=images"
    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
    except Exception as e:
        print(f"  Image search failed: {e}")
        return saved

    # Get image result links (the actual source pages)
    # First, let's just screenshot the search results themselves - they contain
    # high-quality thumbnails that work well for carousel backgrounds
    for i in range(count):
        output_path = os.path.join(output_dir, f"screenshot_{i + 1}.png")

        if i == 0:
            # Screenshot the image search results grid
            screenshot_url(page, search_url, output_path, crop=crop)
            saved.append(output_path)
        else:
            # Click on individual images and screenshot the preview
            try:
                images = page.query_selector_all('div[data-ri] img')
                if i - 1 < len(images):
                    images[i - 1].click()
                    time.sleep(1.5)
                    page.screenshot(path=output_path, full_page=False)
                    print(f"  Saved: {output_path} ({os.path.getsize(output_path):,} bytes)")
                    saved.append(output_path)
                    # Close the preview
                    page.keyboard.press("Escape")
                    time.sleep(0.5)
            except Exception as e:
                print(f"  Failed on image {i}: {e}")

    return saved


def search_and_screenshot_pages(page, query, output_dir, count=1, crop=None):
    """Use Tavily API to find relevant URLs, then screenshot them with Playwright."""
    os.makedirs(output_dir, exist_ok=True)
    saved = []

    # Use Tavily to find relevant page URLs (avoids search engine bot detection)
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            load_dotenv(os.path.join(project_root, ".env"))
            api_key = os.environ.get("TAVILY_API_KEY")
        except ImportError:
            pass

    if not api_key:
        print("  Error: TAVILY_API_KEY not set — cannot search for pages to screenshot")
        return saved

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, search_depth="basic", max_results=count)
        result_urls = [r["url"] for r in results.get("results", [])[:count]]
    except Exception as e:
        print(f"  Tavily search failed: {e}")
        return saved

    print(f"  Found {len(result_urls)} page(s) to screenshot")

    for i, url in enumerate(result_urls):
        output_path = os.path.join(output_dir, f"screenshot_{i + 1}.png")
        print(f"  Visiting: {url}")
        success = screenshot_url(page, url, output_path, crop=crop)
        if success:
            saved.append(output_path)

    return saved


def main():
    parser = argparse.ArgumentParser(description="Screenshot web pages for carousel images")
    parser.add_argument("--query", help="Search query (will Google and screenshot results)")
    parser.add_argument("--url", help="Specific URL to screenshot")
    parser.add_argument("--output", required=True, help="Output path (file or directory)")
    parser.add_argument("--count", type=int, default=1, help="Number of screenshots to take")
    parser.add_argument("--crop", help="Crop region: x,y,width,height (e.g., 0,100,1080,800)")
    parser.add_argument("--pages", action="store_true",
                        help="Visit actual pages from search results instead of image search")
    args = parser.parse_args()

    if not args.query and not args.url:
        print("Error: provide --query or --url")
        sys.exit(1)

    crop = None
    if args.crop:
        parts = [int(x) for x in args.crop.split(",")]
        if len(parts) != 4:
            print("Error: --crop must be x,y,width,height")
            sys.exit(1)
        crop = tuple(parts)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        if args.url:
            output_path = args.output
            if os.path.isdir(args.output) or args.output.endswith("/"):
                os.makedirs(args.output, exist_ok=True)
                output_path = os.path.join(args.output, "screenshot_1.png")
            screenshot_url(page, args.url, output_path, crop=crop)
        elif args.query:
            output_dir = args.output
            if args.output.endswith(".png"):
                output_dir = os.path.dirname(args.output)

            if args.pages:
                search_and_screenshot_pages(page, args.query, output_dir, args.count, crop)
            else:
                search_and_screenshot(page, args.query, output_dir, args.count, crop)

        browser.close()

    print("\nDone!")


if __name__ == "__main__":
    main()
