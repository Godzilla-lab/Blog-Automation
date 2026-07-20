#!/usr/bin/env python3
"""
Analyze a previously fetched competitor ad: extract frames, transcribe VO via
ElevenLabs Scribe, send everything to Claude (vision), and write a structured
"creative brief" we can clone.

Usage:
    python3 execution/analyze_competitor_ad.py --ad-id 1110229847960703

Reads: .tmp/competitor_ads/<ad_id>/{meta.json, creative.mp4 or creative.jpg, cover.jpg}
Writes: .tmp/competitor_ads/<ad_id>/{frames/, transcript.json, analysis.json}
"""
import argparse
import json
import os
import re
import subprocess
import sys

import requests
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "execution"))

from reality_qa_reel import extract_frame  # reuse

SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
MAX_FRAMES = 8

SYSTEM_PROMPT = """You analyze winning direct-response ads so the user can ethically clone the STRUCTURE (not the brand) for their own offer.

You will receive:
- METADATA: page_name, days_active, body_text, cta_text, title, link_description
- TRANSCRIPT: spoken VO with word timestamps (videos only)
- FRAMES: 6-8 sampled frames from 0s to end, each labeled with its timestamp

Return a STRICT JSON object (no markdown, no commentary). Keys, exactly:
{
  "hook_first_3s": {
    "visual": "what is visually on screen at 0-3s",
    "spoken": "the spoken hook line, exact",
    "on_screen_text": "any kinetic caption text visible at 0-3s"
  },
  "hook_archetype": "one of: realism-reveal | problem-callout | contrarian | founder-cred | volume-claim | curiosity-gap | social-proof | demonstration",
  "structure_beats": [
    {"ts_s": 0.0, "what_happens": "<short>", "why_it_works": "<short>"},
    ...
  ],
  "cta": {"text": "...", "visual": "...", "position": "lower-third | endcard | overlay | spoken-only"},
  "pacing": {"avg_shot_s": 1.2, "style": "fast-cut | single-take | mixed"},
  "proof_elements": ["specific numbers, credentials, logos, or claims used as proof"],
  "visual_style": "AI-avatar-talking-head | ugc-handheld | screen-rec | studio | product-demo | text-on-image | mixed",
  "restyle_ideas_for_hexa": [
    "2-3 ways MadeByHexa (AI-generated hyper-real product video service, madebyhexa.co/offer) could restyle this for its own offer"
  ],
  "clone_template_for_hexa": {
    "hook_line_to_clone": "rewrite the hook in Hexa's voice (product video, 48hr turnaround, free sample, no card, $59 vs $8K). Keep the ARCHETYPE; change brand specifics.",
    "slide_structure": [
      {"text": "<kinetic caption text for slide>", "visual": "<what footage shows>", "approx_s": 2.0},
      ...
    ],
    "cta_to_match": "Free Sample Below ↓"
  }
}

Rules:
- Be concrete. Reference the actual frames and transcript, not generic ad-school advice.
- structure_beats: 4-7 entries. ts_s in chronological order. Each beat is one clean creative decision.
- proof_elements: extract real numbers/names from transcript or visible text. If none, return [].
- clone_template_for_hexa.slide_structure: 4-6 slides total, last slide MUST be CTA. Total approx_s should roughly match the source ad length.
- Return JSON ONLY. No prose around it."""


def probe_duration(mp4_path):
    """ffprobe isn't installed on this box; parse Duration from ffmpeg -i stderr."""
    try:
        out = subprocess.run(
            ["ffmpeg", "-i", mp4_path, "-hide_banner"],
            capture_output=True, text=True,
        ).stderr
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", out)
        if not m:
            return 0.0
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    except Exception:
        return 0.0


def pick_timestamps(duration):
    """Hook-heavy + CTA. Capped at MAX_FRAMES."""
    base = [0.5, 1.0, 2.0, 3.0]  # hook coverage
    if duration > 6:
        base.append(duration / 2)
    if duration > 4:
        base.append(max(0.5, duration - 3.0))
        base.append(max(0.5, duration - 1.5))
        base.append(max(0.5, duration - 0.3))
    ts = sorted(set(t for t in base if t <= max(0.5, duration - 0.1)))
    return ts[:MAX_FRAMES]


def transcribe_scribe(mp4_path, out_path):
    """POST audio to ElevenLabs Scribe. Return parsed dict."""
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY missing")
    # Extract audio (mp3) to keep payload small
    audio_path = mp4_path.replace(".mp4", "_audio.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", mp4_path,
         "-vn", "-c:a", "libmp3lame", "-b:a", "64k", audio_path],
        check=True, capture_output=True,
    )
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {"model_id": "scribe_v1", "diarize": "false"}
        r = requests.post(SCRIBE_URL, headers={"xi-api-key": key},
                          files=files, data=data, timeout=180)
    os.remove(audio_path)
    if r.status_code != 200:
        return {"text": "", "words": [], "_error": f"scribe_{r.status_code}: {r.text[:300]}"}
    payload = r.json()
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    return payload


def write_brief_inputs(ad_dir, meta, transcript, frame_pairs):
    """Stage all inputs so the agent (in-session) can Read them and write analysis.json.

    The ANTHROPIC_API_KEY in .env is currently revoked (see memory), and the
    user explicitly wants the agent (multimodal) to do the synthesis — not a
    separate API call. So we stop at staging inputs; the agent does step 3
    via the Read + Write tools."""
    inputs = {
        "ad_id": meta["ad_id"],
        "meta": meta,
        "transcript_text": transcript.get("text", ""),
        "transcript_words": (transcript.get("words") or [])[:200],
        "frames": [{"ts_s": ts, "path": p} for ts, p in frame_pairs],
        "system_prompt_for_agent": SYSTEM_PROMPT,
    }
    with open(os.path.join(ad_dir, "brief_inputs.json"), "w") as f:
        json.dump(inputs, f, indent=2)


def analyze_one(ad_id):
    ad_dir = os.path.join(PROJECT_ROOT, ".tmp", "competitor_ads", ad_id)
    meta_p = os.path.join(ad_dir, "meta.json")
    if not os.path.exists(meta_p):
        sys.exit(f"meta.json missing in {ad_dir}. Run fetch_competitor_ad.py first.")
    meta = json.load(open(meta_p))
    print(f"[{ad_id}] {meta['page_name']} ({meta['days_active']}d, {meta['display_format']})")

    is_video = meta["display_format"] == "VIDEO"
    mp4_path = os.path.join(ad_dir, "creative.mp4")
    jpg_path = os.path.join(ad_dir, "creative.jpg")

    frames_dir = os.path.join(ad_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    frame_pairs = []

    if is_video and os.path.exists(mp4_path):
        duration = probe_duration(mp4_path)
        print(f"  duration: {duration:.1f}s  ->  picking timestamps")
        ts_list = pick_timestamps(duration)
        for ts in ts_list:
            out = os.path.join(frames_dir, f"f_{ts:.2f}.jpg")
            if extract_frame(mp4_path, ts, out):
                frame_pairs.append((ts, out))
        print(f"  extracted {len(frame_pairs)} frames")
        print(f"  transcribing via Scribe...")
        transcript = transcribe_scribe(mp4_path, os.path.join(ad_dir, "transcript.json"))
        spoken = transcript.get("text", "")
        print(f"  transcript: {spoken[:120]}{'...' if len(spoken) > 120 else ''}")
    elif os.path.exists(jpg_path):
        frame_pairs = [(0.0, jpg_path)]
        transcript = {"text": "", "words": [], "_note": "static image, no audio"}
    else:
        sys.exit(f"  No creative.mp4 or creative.jpg in {ad_dir}")

    write_brief_inputs(ad_dir, meta, transcript, frame_pairs)
    print(f"  ✓ inputs staged. Agent reads frames + transcript and writes analysis.json next.")
    print(f"    frames: {[p for _, p in frame_pairs]}")
    return {"ad_id": ad_id, "frames": frame_pairs, "transcript_text": transcript.get("text", "")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad-id", required=True)
    args = ap.parse_args()
    analyze_one(args.ad_id)


if __name__ == "__main__":
    main()
