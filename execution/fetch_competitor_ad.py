#!/usr/bin/env python3
"""
Fetch a Meta/Facebook ad by ID via ScrapeCreators API, download the creative,
and save normalized metadata so the analyzer can pick it up.

Usage:
    python3 execution/fetch_competitor_ad.py --ad-id 1110229847960703

Output: .tmp/competitor_ads/<ad_id>/
    meta.json     — normalized record (page_name, days_active, body, cta, etc.)
    raw.json      — full ScrapeCreators response (for re-analysis)
    creative.mp4  — downloaded mp4 (for VIDEO display_format)
    creative.jpg  — downloaded image (for IMAGE display_format)
    cover.jpg     — frame at 1.5s for video; same as creative.jpg for image
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.request

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

API_BASE = "https://api.scrapecreators.com/v1/facebook/adLibrary"
OUT_ROOT = os.path.join(PROJECT_ROOT, ".tmp", "competitor_ads")


def fetch_ad(ad_id):
    key = os.getenv("SCRAPECREATORS_API_KEY")
    if not key:
        sys.exit("SCRAPECREATORS_API_KEY missing from .env")
    url = f"{API_BASE}/ad?id={ad_id}"
    req = urllib.request.Request(url, headers={"x-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ScrapeCreators {e.code}: {e.read().decode()[:400]}")
    if not data.get("success"):
        sys.exit(f"ScrapeCreators success=False: {data}")
    return data


def download(url, out_path):
    if not url:
        return False
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(out_path, "wb") as f:
        f.write(r.read())
    return os.path.getsize(out_path) > 0


def extract_cover(mp4_path, jpg_path, ts=1.5):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(ts), "-i", mp4_path,
         "-frames:v", "1", "-q:v", "2", jpg_path],
        capture_output=True, check=False,
    )


def normalize(data):
    snap = data.get("snapshot", {})
    start = data.get("startDate")
    end = data.get("endDate")
    today = datetime.datetime.now(datetime.timezone.utc).timestamp()
    days_active = None
    if start:
        end_effective = min(end, today) if end else today
        days_active = int((end_effective - start) / 86400)
    body = snap.get("body") or {}
    return {
        "ad_id": str(data.get("adArchiveID")),
        "page_id": data.get("pageID"),
        "page_name": snap.get("page_name"),
        "is_active": data.get("isActive"),
        "days_active": days_active,
        "start_date": data.get("startDateString"),
        "end_date": data.get("endDateString"),
        "display_format": snap.get("display_format"),
        "title": snap.get("title"),
        "body_text": body.get("text") if isinstance(body, dict) else body,
        "cta_text": snap.get("cta_text"),
        "cta_type": snap.get("cta_type"),
        "link_url": snap.get("link_url"),
        "link_description": snap.get("link_description"),
        "library_url": f"https://www.facebook.com/ads/library/?id={data.get('adArchiveID')}",
        "credits_remaining": data.get("credits_remaining"),
        "collation_count": data.get("collationCount"),
        "video_hd_url": (snap.get("videos") or [{}])[0].get("video_hd_url"),
        "image_url": (snap.get("images") or [{}])[0].get("original_image_url"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad-id", required=True)
    args = ap.parse_args()

    out_dir = os.path.join(OUT_ROOT, args.ad_id)
    os.makedirs(out_dir, exist_ok=True)

    print(f"[{args.ad_id}] fetching via ScrapeCreators...")
    data = fetch_ad(args.ad_id)

    with open(os.path.join(out_dir, "raw.json"), "w") as f:
        json.dump(data, f, indent=2)

    meta = normalize(data)
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  page: {meta['page_name']}  |  days_active: {meta['days_active']}  |  format: {meta['display_format']}")
    print(f"  credits_remaining: {meta['credits_remaining']}")

    fmt = meta["display_format"]
    if fmt == "VIDEO" and meta["video_hd_url"]:
        mp4_path = os.path.join(out_dir, "creative.mp4")
        print(f"  downloading mp4 -> {mp4_path}")
        download(meta["video_hd_url"], mp4_path)
        size_mb = os.path.getsize(mp4_path) / 1024 / 1024
        print(f"  ✓ {size_mb:.1f} MB")
        extract_cover(mp4_path, os.path.join(out_dir, "cover.jpg"))
    elif fmt == "IMAGE" and meta["image_url"]:
        jpg_path = os.path.join(out_dir, "creative.jpg")
        print(f"  downloading image -> {jpg_path}")
        download(meta["image_url"], jpg_path)
        subprocess.run(["cp", jpg_path, os.path.join(out_dir, "cover.jpg")], check=False)
        print(f"  ✓ {os.path.getsize(jpg_path) // 1024} KB")
    else:
        print(f"  WARN: unhandled display_format={fmt} (no media downloaded)")

    print(f"  saved: {out_dir}")


if __name__ == "__main__":
    main()
