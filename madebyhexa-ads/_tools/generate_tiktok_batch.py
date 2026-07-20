#!/usr/bin/env python3
"""
Generate the 21-piece TikTok week-1 batch:
  1. Write 21 config.json files with slides + VO scripts + footage
  2. Run gen_voice_natural.py per piece (caller does this in a loop)
  3. After VOs exist, run compute-end-indices + sync_manual.py
  4. Render via the existing pipeline

Output folders: madebyhexa-ads/tt-NN-{slug}/  (under the existing ads namespace
so the public/ symlink works without changes)
"""
import json
import os
import re
import shutil
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADS_DIR = os.path.join(PROJECT_ROOT, "madebyhexa-ads")
PUBLIC_DIR = os.path.join(ADS_DIR, "public")
VIDEO_PREFIX = "madebyhexa-ads/videos"  # relative path in config.json

# Voice (same natural settings as p/q/r batch)
VOICE_ID = "tnSpp4vdxKPjI9w0GnoV"

PIECES = [
    # ---------- AM (realism-reveal) — keyword SAMPLE ----------
    {
        "slug": "tt-01-mon-am-photo-vs-hexa-split",
        "vo": "[firm]This is your product photo. [punchy]This is your product photo plus Hexa. [deliberate]Same product. One photo. Forty-eight hours. [warm]Comment SAMPLE and we'll send you yours free.",
        "slides": [
            {"text": "Your product photo.", "emphasis": "photo", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-23-showreel.mp4", "end": "photo."},
            {"text": "Your product photo + Hexa.", "emphasis": "Hexa", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "Hexa."},
            {"text": "Same product. One photo.", "emphasis": "One photo", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "photo."},
            {"text": "48 hours.", "emphasis": "48", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "hours."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "free."},
        ],
        "bg_music": "sfx/bg-upbeat.mp3",
        "keyword": "SAMPLE",
    },
    {
        "slug": "tt-04-tue-am-spot-the-ai-challenge",
        "vo": "[curious]One of these is real. Three are AI. Which one? [deliberate]The answer is in the comments. [punchy]All three AI ones cost fifty-nine dollars each. [warm]Comment SAMPLE for yours.",
        "slides": [
            {"text": "One is real. Three are AI.", "emphasis": "Which one", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "one?"},
            {"text": "Which one?", "emphasis": "Which", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "comments."},
            {"text": "All AI. All $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "each."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "yours."},
        ],
        "bg_music": "sfx/bg-energetic.mp3",
        "keyword": "SAMPLE",
    },
    {
        "slug": "tt-07-wed-am-ai-2024-2025-2026",
        "vo": "[firm]AI video in 2024. AI video in 2025. AI video in 2026. [deliberate]Same product. One photo. [punchy]Fifty-nine dollars. Forty-eight hours. [warm]Comment SAMPLE for yours.",
        "slides": [
            {"text": "AI in 2024.", "emphasis": "2024", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-23-showreel.mp4", "end": "2024."},
            {"text": "AI in 2025.", "emphasis": "2025", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "2025."},
            {"text": "AI in 2026.", "emphasis": "2026", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "2026."},
            {"text": "Same product. One photo.", "emphasis": "One photo", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "photo."},
            {"text": "$59. 48 hours.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "hours."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "yours."},
        ],
        "bg_music": "sfx/bg-dramatic.mp3",
        "keyword": "SAMPLE",
    },
    {
        "slug": "tt-10-thu-am-client-reaction",
        "vo": "[curious]She sent us one photo. This is what she got back. [warm]Watch her reaction. [deliberate]Forty-eight hours from photo to this. Fifty-nine dollars. [punchy]Comment SAMPLE for yours.",
        "slides": [
            {"text": "She sent one photo.", "emphasis": "one photo", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "back."},
            {"text": "This is what she got back.", "emphasis": "this", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-30-lip-sync.mp4", "end": "reaction."},
            {"text": "48 hours. $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "dollars."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "yours."},
        ],
        "bg_music": "sfx/bg-chill.mp3",
        "keyword": "SAMPLE",
    },
    {
        "slug": "tt-13-fri-am-5-videos-0-to-film",
        "vo": "[firm]Five product videos. Zero filmed. Fifty-nine dollars each. [punchy]All five from one product photo. [deliberate]Forty-eight hours. [warm]Comment SAMPLE for yours.",
        "slides": [
            {"text": "5 videos. $0 filmed.", "emphasis": "$0", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "each."},
            {"text": "All from one photo.", "emphasis": "one photo", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "photo."},
            {"text": "48 hours.", "emphasis": "48", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "hours."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "yours."},
        ],
        "bg_music": "sfx/bg-upbeat-2.mp3",
        "keyword": "SAMPLE",
    },
    {
        "slug": "tt-16-sat-am-which-is-real-challenge",
        "vo": "[curious]Which one is real? [deliberate]Take a guess. Drop your answer below. [punchy]Two of these were made from one photo. Forty-eight hours. Fifty-nine dollars. [warm]Comment SAMPLE for yours.",
        "slides": [
            {"text": "Which is real?", "emphasis": "real", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "real?"},
            {"text": "Guess below ↓", "emphasis": "Guess", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "below."},
            {"text": "Two were AI. From one photo.", "emphasis": "one photo", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "photo."},
            {"text": "48 hours. $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "dollars."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "yours."},
        ],
        "bg_music": "sfx/bg-dramatic-2.mp3",
        "keyword": "SAMPLE",
    },
    {
        "slug": "tt-19-sun-am-same-product-5-hooks",
        "vo": "[firm]One product. Five ads. Five hooks. All AI. [punchy]Same photo. Five variants. [deliberate]Forty-eight hours. Fifty-nine dollars each. [warm]Comment SAMPLE for yours.",
        "slides": [
            {"text": "1 product. 5 ads.", "emphasis": "5 ads", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "AI."},
            {"text": "Same photo. 5 variants.", "emphasis": "5 variants", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "variants."},
            {"text": "48 hours. $59 each.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "each."},
            {"text": "Comment SAMPLE ↓", "emphasis": "SAMPLE", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "yours."},
        ],
        "bg_music": "sfx/bg-energetic-2.mp3",
        "keyword": "SAMPLE",
    },
    # ---------- Mid (process / BTS) — keyword HOW ----------
    {
        "slug": "tt-02-mon-mid-photo-to-ad-speedrun",
        "vo": "[firm]I made an eight thousand dollar product video for fifty-nine dollars. Here's the full process. [deliberate]Step one: drop your product photo. [punchy]Step two: pick the scene you want. [building]Step three: hit generate. Forty-five seconds later, this is what you get. [warm]Want to see it for your product? Comment HOW.",
        "slides": [
            {"text": "$8K video for $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "process."},
            {"text": "Step 1: drop the photo.", "emphasis": "Step 1", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "photo."},
            {"text": "Step 2: pick the scene.", "emphasis": "Step 2", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "want."},
            {"text": "Step 3: generate.", "emphasis": "Step 3", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "get."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "HOW."},
        ],
        "bg_music": "sfx/bg-corporate.mp3",
        "keyword": "HOW",
    },
    {
        "slug": "tt-05-tue-mid-1-photo-50-variants",
        "vo": "[firm]One photo plus one day equals fifty ad variants. Here's the math. [deliberate]Five hooks times five scenes times two voices equals fifty unique ads. [punchy]At fifty-nine dollars each, that's two thousand nine hundred and fifty dollars total. [building]Your studio shoot was twenty thousand. [warm]Comment HOW for the workflow.",
        "slides": [
            {"text": "1 photo + 1 day = 50 ads.", "emphasis": "50 ads", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "math."},
            {"text": "5 hooks × 5 scenes × 2 voices.", "emphasis": "5 × 5 × 2", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "ads."},
            {"text": "50 × $59 = $2,950.", "emphasis": "$2,950", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "total."},
            {"text": "vs $20,000 studio.", "emphasis": "$20,000", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "thousand."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "workflow."},
        ],
        "bg_music": "sfx/bg-corporate-2.mp3",
        "keyword": "HOW",
    },
    {
        "slug": "tt-08-wed-mid-behind-the-canvas",
        "vo": "[firm]This is how we turn this photo into a sixty-second cinematic ad. In two minutes. [deliberate]The photo is one of your existing product shots. [punchy]The canvas is our custom layer over Seedance two-point-oh. [building]The output is what your customer sees. [grounded]Forty-eight hours total, sixty seconds of footage, fifty-nine dollars. [warm]Comment HOW to see it for your product.",
        "slides": [
            {"text": "Photo → 60-sec ad. 2 min.", "emphasis": "2 min", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "minutes."},
            {"text": "Your existing photo.", "emphasis": "Your", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-21-showreel.mp4", "end": "shots."},
            {"text": "Our canvas. Seedance 2.0.", "emphasis": "Seedance", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "two-point-oh."},
            {"text": "48 hrs. 60 sec. $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "dollars."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "product."},
        ],
        "bg_music": "sfx/bg-corporate-3.mp3",
        "keyword": "HOW",
    },
    {
        "slug": "tt-11-thu-mid-9pm-ad-due-monday",
        "vo": "[curious]It's nine PM. Your ad is due Monday. Your shoot got cancelled. [firm]Open Hexa. Drop your product photo. Pick a scene. Hit generate. [punchy]Forty-eight hours later, you have your ad. Fifty-nine dollars. [warm]No crew. No studio. No panic. Comment HOW.",
        "slides": [
            {"text": "9 PM. Ad due Monday.", "emphasis": "9 PM", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "cancelled."},
            {"text": "Open Hexa. Drop photo.", "emphasis": "Open", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "generate."},
            {"text": "48 hours later → done.", "emphasis": "done", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "dollars."},
            {"text": "No crew. No studio.", "emphasis": "No", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-10-showreel.mp4", "end": "panic."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "HOW."},
        ],
        "bg_music": "sfx/bg-dramatic-3.mp3",
        "keyword": "HOW",
    },
    {
        "slug": "tt-14-fri-mid-real-time-speedrun",
        "vo": "[firm]Speedrun. From photo to cinematic ad. Real time. Watch the clock. [punchy]Drop the photo. Pick the scene. Hit generate. [building]Forty-five seconds for the model. [deliberate]Two minutes for the human pass. [warm]Total time: under three minutes. Fifty-nine dollars. Comment HOW.",
        "slides": [
            {"text": "Speedrun: photo → ad.", "emphasis": "Speedrun", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-34-hyper-motion.mp4", "end": "clock."},
            {"text": "Drop. Pick. Generate.", "emphasis": "Generate", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "generate."},
            {"text": "45 sec for the model.", "emphasis": "45", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "model."},
            {"text": "2 min human pass.", "emphasis": "2 min", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-21-showreel.mp4", "end": "pass."},
            {"text": "Total: <3 min. $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "dollars."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "HOW."},
        ],
        "bg_music": "sfx/bg-energetic-3.mp3",
        "keyword": "HOW",
    },
    {
        "slug": "tt-17-sat-mid-one-prompt-changes-everything",
        "vo": "[curious]One prompt. Changes the entire output. Here's the one we always use. [deliberate]Cinematic product hero, soft rim light, shallow depth of field, kitchen lifestyle backdrop. [punchy]That's it. That's the secret. [warm]Apply it to your photo? Comment HOW.",
        "slides": [
            {"text": "The 1 prompt we always use.", "emphasis": "1 prompt", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "use."},
            {"text": "Cinematic hero. Soft rim light.", "emphasis": "Cinematic", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "field,"},
            {"text": "Kitchen lifestyle backdrop.", "emphasis": "Kitchen", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "backdrop."},
            {"text": "That's the secret.", "emphasis": "secret", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-21-showreel.mp4", "end": "secret."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "HOW."},
        ],
        "bg_music": "sfx/bg-chill-2.mp3",
        "keyword": "HOW",
    },
    {
        "slug": "tt-20-sun-mid-competitor-doing-this",
        "vo": "[firm]Your competitor is running ten ad variants a week. You're running one. Here's why. [deliberate]They figured out AI product video. [punchy]Each variant costs them fifty-nine dollars. Forty-eight hours. [building]You're paying eight thousand for one. [grounded]The math is brutal. [warm]Comment HOW for the workflow.",
        "slides": [
            {"text": "10 ads/week vs 1 ad/month.", "emphasis": "10 vs 1", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "why."},
            {"text": "They figured out AI.", "emphasis": "AI", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "video."},
            {"text": "$59 × 10 = $590.", "emphasis": "$590", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "hours."},
            {"text": "$8,000 × 1 = $8,000.", "emphasis": "$8,000", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "one."},
            {"text": "Comment HOW ↓", "emphasis": "HOW", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "workflow."},
        ],
        "bg_music": "sfx/bg-dramatic.mp3",
        "keyword": "HOW",
    },
    # ---------- PM (founder POV) — keyword $59 ----------
    {
        "slug": "tt-03-mon-pm-almost-charged-499",
        "vo": "[curious]We almost charged four hundred and ninety-nine dollars per ad. Here's why we didn't. [deliberate]Our cost per ad is around eight dollars. The agency markup is what brands hate. [punchy]So we cut it. Fifty-nine dollars, forty-eight hours, free sample. [warm]Comment fifty-nine to see one for your product.",
        "slides": [
            {"text": "We almost charged $499.", "emphasis": "$499", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "didn't."},
            {"text": "Our cost: ~$8.", "emphasis": "$8", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "hate."},
            {"text": "We cut the markup.", "emphasis": "cut", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "sample."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "product."},
        ],
        "bg_music": "sfx/bg-corporate.mp3",
        "keyword": "$59",
    },
    {
        "slug": "tt-06-tue-pm-dtc-8k-scam",
        "vo": "[firm]DTC founders are paying eight thousand dollars for one product ad. I'll tell you why that's a scam. [deliberate]Studio. Crew. Edit. Color grade. All in. That used to be the only way. [punchy]Now AI does the same thing for fifty-nine dollars. Forty-eight hours. [grounded]I'm not saying agencies are useless. I'm saying eight thousand for one ad isn't sustainable. [warm]Comment fifty-nine for proof.",
        "slides": [
            {"text": "$8,000 for one ad = scam.", "emphasis": "scam", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "scam."},
            {"text": "Studio. Crew. Edit. Color.", "emphasis": "Studio", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "way."},
            {"text": "Now AI does it. $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "hours."},
            {"text": "$8K for one ad isn't sustainable.", "emphasis": "sustainable", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "sustainable."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "proof."},
        ],
        "bg_music": "sfx/bg-dramatic-2.mp3",
        "keyword": "$59",
    },
    {
        "slug": "tt-09-wed-pm-what-59-buys-you",
        "vo": "[curious]What does fifty-nine dollars actually buy you? Be honest with yourself before you watch this. [deliberate]Sixty seconds of cinematic product video. From one of your photos. Forty-eight hours. [firm]Same realism as an eight thousand dollar studio shoot. [grounded]We're not making this up. Free sample, no card. [warm]Comment fifty-nine to see it.",
        "slides": [
            {"text": "What $59 buys you.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "this."},
            {"text": "60-sec cinematic ad.", "emphasis": "60-sec", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "hours."},
            {"text": "Same realism as $8K shoot.", "emphasis": "Same", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "shoot."},
            {"text": "Free sample. No card.", "emphasis": "Free", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "card."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "it."},
        ],
        "bg_music": "sfx/bg-corporate-2.mp3",
        "keyword": "$59",
    },
    {
        "slug": "tt-12-thu-pm-stop-hiring-agencies",
        "vo": "[firm]Stop hiring agencies for product video. Here's what they're not telling you. [deliberate]Most of them are using the same AI tools you have access to. [punchy]They're marking it up forty to fifty times. [building]I worked with three agencies before building this. All three were running AI workflows. None of them told the clients. [grounded]We charge fifty-nine dollars. They charge eight thousand. [warm]Comment fifty-nine for proof.",
        "slides": [
            {"text": "Stop hiring agencies.", "emphasis": "Stop", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "you."},
            {"text": "They use AI. Marked up 40-50×.", "emphasis": "40-50×", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "times."},
            {"text": "3 agencies. All used AI.", "emphasis": "3 agencies", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "clients."},
            {"text": "Hexa $59. They $8K.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "thousand."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "proof."},
        ],
        "bg_music": "sfx/bg-dramatic-3.mp3",
        "keyword": "$59",
    },
    {
        "slug": "tt-15-fri-pm-meta-ads-not-converting",
        "vo": "[firm]Your Meta ads aren't converting. It's not the targeting. It's the creative. Here's why. [deliberate]Meta's algorithm rewards new creative every five to seven days. [punchy]You can't ship one ad and scale it. You need ten variants minimum to find the winner. [building]At eight thousand dollars per variant, you're spending eighty thousand to find one winner. [grounded]At fifty-nine dollars, you spend five hundred and ninety. [warm]Same answer. Different cost. Comment fifty-nine.",
        "slides": [
            {"text": "Meta ads not converting?", "emphasis": "not converting", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "why."},
            {"text": "Algo wants new creative every 5-7 days.", "emphasis": "5-7", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "days."},
            {"text": "10 variants minimum.", "emphasis": "10", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "winner."},
            {"text": "$80K studio. $590 Hexa.", "emphasis": "$590", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "ninety."},
            {"text": "Same answer. Different cost.", "emphasis": "Different", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "cost."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "fifty-nine."},
        ],
        "bg_music": "sfx/bg-corporate-3.mp3",
        "keyword": "$59",
    },
    {
        "slug": "tt-18-sat-pm-ai-ads-dont-convert-myth",
        "vo": "[firm]Everyone says AI ads don't convert. Here's our highest performer's actual stats. [deliberate]Four point eight percent click-through rate. Two point one dollars cost per click. One hundred and forty-three percent return on ad spend. [punchy]All from a fifty-nine dollar Hexa ad. [grounded]I'm not saying every AI ad will hit these numbers. I'm saying the ones that do exist. [warm]Comment fifty-nine to test it.",
        "slides": [
            {"text": "\"AI ads don't convert.\"", "emphasis": "convert", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "stats."},
            {"text": "4.8% CTR. $2.10 CPC.", "emphasis": "4.8%", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "click."},
            {"text": "143% ROAS.", "emphasis": "143%", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-01-showreel.mp4", "end": "spend."},
            {"text": "All from one $59 ad.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-08-showreel.mp4", "end": "ad."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "it."},
        ],
        "bg_music": "sfx/bg-energetic.mp3",
        "keyword": "$59",
    },
    {
        "slug": "tt-21-sun-pm-watch-before-5k-shoot",
        "vo": "[firm]Watch this before you spend five thousand dollars on your next product video. [deliberate]I'm not saying don't hire a studio. Some products need it. [punchy]But if your product is on a flat background, a model holding it, or a lifestyle scene — AI can do it for fifty-nine dollars. Forty-eight hours. [building]Test the cheap option first. If it doesn't work, you've lost fifty-nine dollars. [grounded]If it works, you've saved five thousand. [warm]Comment fifty-nine to test it free.",
        "slides": [
            {"text": "Wait. Watch this first.", "emphasis": "Wait", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-25-lip-sync.mp4", "end": "video."},
            {"text": "Some products need a studio.", "emphasis": "Some", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-22-showreel.mp4", "end": "it."},
            {"text": "Flat-bg, model, lifestyle: $59.", "emphasis": "$59", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-07-showreel.mp4", "end": "hours."},
            {"text": "Lose $59 or save $5K.", "emphasis": "$5K", "type": "broll", "footage": f"{VIDEO_PREFIX}/portfolio-15-showreel.mp4", "end": "thousand."},
            {"text": "Comment $59 ↓", "emphasis": "$59", "type": "cta", "footage": f"{VIDEO_PREFIX}/portfolio-06-showreel.mp4", "end": "free."},
        ],
        "bg_music": "sfx/bg-dramatic.mp3",
        "keyword": "$59",
    },
]


KNOWN_TAGS = {"firm", "punchy", "deliberate", "building", "warm", "curious",
              "grounded", "soft", "pause", "stern", "serious"}


def strip_tags(s):
    """Strip prosody tags and normalize whitespace, matching what ElevenLabs returns."""
    for t in KNOWN_TAGS:
        s = s.replace(f"[{t}]", "")
    return re.sub(r"\s+", " ", s).strip()


def vo_words(vo):
    """Word tokens as ElevenLabs returns them (whitespace-split, tag-stripped)."""
    return strip_tags(vo).split()


def find_end_idx(words, end_phrase, start_from=0):
    """Find the index of the LAST word matching end_phrase, looking from start_from forward.
    end_phrase may be a single word ('photo.') or multi-word ('this product.')."""
    target = end_phrase.split()[-1]
    # Match case-sensitive, exact-word (Eleven returns punctuation attached to words like 'photo.')
    for i in range(start_from, len(words)):
        if words[i] == target:
            return i
    # Fallback: case-insensitive
    for i in range(start_from, len(words)):
        if words[i].lower() == target.lower():
            return i
    raise ValueError(f"End word {target!r} not found from index {start_from}. Words from there: {words[start_from:]}")


def compute_end_indices(vo, slides):
    words = vo_words(vo)
    out = []
    cursor = 0
    for s in slides:
        idx = find_end_idx(words, s["end"], cursor)
        out.append(idx)
        cursor = idx + 1
    return out


def write_config(piece):
    folder = os.path.join(ADS_DIR, piece["slug"])
    public_folder = os.path.join(PUBLIC_DIR, piece["slug"])
    os.makedirs(folder, exist_ok=True)
    os.makedirs(public_folder, exist_ok=True)

    end_indices = compute_end_indices(piece["vo"], piece["slides"])

    cfg = {
        "_comment": f"TikTok organic week-1 piece. Slug: {piece['slug']}. Voice = same natural settings as p/q/r batch.",
        "_tiktok_meta": {
            "slot": piece["slug"].split("-")[3],  # am / mid / pm
            "comment_keyword": piece["keyword"],
            "week": "2026-06-22",
            "script_source": f"workspace/tiktok/2026-06-22-week-batch/{piece['slug'].replace('tt-', '')}.md",
        },
        "slides": [
            {
                "text": s["text"],
                "emphasis": s["emphasis"],
                "type": s["type"],
                "footage": s["footage"],
                "durationFrames": 90,  # placeholder, overwritten by sync_manual
            }
            for s in piece["slides"]
        ],
        "voiceover_script": piece["vo"],
        "accent_color": "#00B8FF",
        "seconds_per_slide": 4,
        "cta_keyword": piece["keyword"].replace("$", "").replace("FIFTYNINE", "$59"),
        "handle": "madebyhexa.co/offer",
        "bg_music": piece["bg_music"],
        "bg_music_volume": 0.1,
        "voiceover": f"madebyhexa-ads/{piece['slug']}/voiceover.mp3",
        "_end_word_indices": end_indices,  # consumed by sync step
    }

    cfg_path = os.path.join(folder, "config.json")
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return cfg_path, end_indices


def main():
    print(f"Generating {len(PIECES)} TikTok configs...")
    for p in PIECES:
        path, idxs = write_config(p)
        words = vo_words(p["vo"])
        print(f"  ✓ {p['slug']}  ({len(p['slides'])} slides, {len(words)} VO words, end_indices={idxs})")
    print(f"\nDone. {len(PIECES)} configs written to madebyhexa-ads/tt-*/")
    print(f"Next: run gen_voice_natural for each, then sync_manual with the _end_word_indices field, then render.")


if __name__ == "__main__":
    main()
