#!/usr/bin/env python3
"""
Search the Meta Ad Library (via ScrapeCreators) for advertisers matching a
keyword, list each page's ads, and rank them by days-active so the
longest-running (= proven-winner) ads surface to the top.

This is the missing "search" front-end to fetch_competitor_ad.py. Once you have
a ranked ad_archive_id, deep-pull it with:
    python3 execution/fetch_competitor_ad.py --ad-id <ad_archive_id>

Usage:
    python3 execution/search_winning_ads.py \
        --query "AI automation agency" --query "automation agency" \
        --min-days 30 --top-pages 3 --max-results 20

Cost: 1 credit per /search/companies call + 1 credit per page /company/ads call.
A 4-query x 3-page sweep = ~16 credits (~$0.16).

Output: .tmp/competitor_ads/_search/results.json  (full ranked list)
        + a printed table of the top winners.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

API_BASE = "https://api.scrapecreators.com/v1/facebook/adLibrary"
OUT_DIR = os.path.join(PROJECT_ROOT, ".tmp", "competitor_ads", "_search")
KEY = os.getenv("SCRAPECREATORS_API_KEY")


def api_get(path):
    if not KEY:
        sys.exit("SCRAPECREATORS_API_KEY missing from .env")
    req = urllib.request.Request(API_BASE + path, headers={"x-api-key": KEY})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ! {path.split('?')[0]} -> {e.code}: {e.read().decode()[:150]}")
        return None


def days_active(ad):
    start = ad.get("start_date")
    end = ad.get("end_date")
    today = datetime.datetime.now(datetime.timezone.utc).timestamp()
    if not start:
        return None
    end_eff = min(end, today) if end else today
    return int((end_eff - start) / 86400)


def snap_field(ad, *path, default=None):
    cur = ad.get("snapshot") or {}
    for p in path:
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return default
    return cur if cur not in (None, "") else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", action="append", required=True,
                    help="Search keyword (repeatable).")
    ap.add_argument("--min-days", type=int, default=30,
                    help="Only keep ads running at least this many days.")
    ap.add_argument("--top-pages", type=int, default=3,
                    help="How many advertiser pages per query to pull ads from.")
    ap.add_argument("--max-results", type=int, default=20,
                    help="How many ranked winners to print.")
    ap.add_argument("--active-only", action="store_true",
                    help="Only keep ads still running right now.")
    ap.add_argument("--image-only", action="store_true",
                    help="Only keep IMAGE display_format ads (for static swipes).")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    seen_pages = set()
    winners = []

    for q in args.query:
        print(f"\n[search] '{q}'")
        res = api_get(f"/search/companies?query={urllib.parse.quote(q)}")
        if not res or not res.get("success"):
            continue
        pages = res.get("searchResults", [])[: args.top_pages]
        print(f"  {len(pages)} pages (credits left: {res.get('credits_remaining')})")
        for pg in pages:
            pid = pg.get("page_id")
            if not pid or pid in seen_pages:
                continue
            seen_pages.add(pid)
            ads_res = api_get(f"/company/ads?pageId={pid}&trim=true")
            if not ads_res or not ads_res.get("success"):
                continue
            ads = ads_res.get("results", [])
            print(f"  - {pg.get('name')}: {len(ads)} ads "
                  f"(credits left: {ads_res.get('credits_remaining')})")
            for ad in ads:
                d = days_active(ad)
                if d is None or d < args.min_days:
                    continue
                if args.active_only and not ad.get("is_active"):
                    continue
                winners.append({
                    "page_name": ad.get("page_name") or pg.get("name"),
                    "ad_archive_id": ad.get("ad_archive_id"),
                    "days_active": d,
                    "is_active": ad.get("is_active"),
                    "cta_text": snap_field(ad, "cta_text"),
                    "title": snap_field(ad, "title"),
                    "body": (snap_field(ad, "body", "text") or "")[:240],
                    "link_url": snap_field(ad, "link_url"),
                    "matched_query": q,
                    "library_url": f"https://www.facebook.com/ads/library/?id={ad.get('ad_archive_id')}",
                })

    # Dedup by ad_archive_id, keep longest-running, rank desc.
    by_id = {}
    for w in winners:
        k = w["ad_archive_id"]
        if k not in by_id or w["days_active"] > by_id[k]["days_active"]:
            by_id[k] = w
    ranked = sorted(by_id.values(), key=lambda w: w["days_active"], reverse=True)

    out_path = os.path.join(OUT_DIR, "results.json")
    with open(out_path, "w") as f:
        json.dump(ranked, f, indent=2)

    print(f"\n=== TOP WINNERS (>= {args.min_days}d active), {len(ranked)} total ===")
    for w in ranked[: args.max_results]:
        active = "LIVE" if w["is_active"] else "off "
        print(f"{w['days_active']:>4}d [{active}] {w['page_name'][:28]:<28} "
              f"id={w['ad_archive_id']}  CTA={w['cta_text']}")
    print(f"\nsaved: {out_path}")


if __name__ == "__main__":
    main()
