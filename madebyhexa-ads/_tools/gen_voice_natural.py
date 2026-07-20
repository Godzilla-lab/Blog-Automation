#!/usr/bin/env python3
"""
Custom voiceover gen for the MadeByHexa ad batch — tunes ElevenLabs voice
settings for a more natural, less actorly female read.

Differences from execution/generate_voiceover.py:
  - stability bumped 0.30 → 0.55  (reduces vibrato/wobble; voice less performative)
  - similarity_boost 0.75 → 0.85  (more faithful to source voice)
  - style 0.65 → 0.30             (less exaggerated style transfer; more conversational)
  - use_speaker_boost: still True

Same model (eleven_v3) so prosody tags ([firm], [punchy]) still work.

Usage:
    python3 madebyhexa-ads/_tools/gen_voice_natural.py \
        --text "..." --output path/voiceover.mp3 --voice-id <id>
"""
import argparse
import base64
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

NATURAL_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.85,
    "style": 0.30,
    "use_speaker_boost": True,
}

API_BASE = "https://api.elevenlabs.io/v1"
MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_v3")
FALLBACK_MODEL = "eleven_multilingual_v2"

KNOWN_TAGS = {
    "serious", "whispers", "shouting", "excited", "pause", "sigh", "laughs",
    "stern", "gentle", "playful", "warm", "low", "deliberate", "matter-of-fact",
    "building", "grounded", "firm", "soft", "loud", "punchy", "dramatic",
    "slow", "fast", "curious", "hesitant", "emphasis", "calm",
}


def chars_to_words(alignment):
    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])
    if not (chars and starts and ends):
        return []
    words = []
    cur = ""
    cur_start = None
    for i, c in enumerate(chars):
        if c == " ":
            if cur:
                words.append({"word": cur, "startMs": int(cur_start * 1000),
                              "endMs": int(ends[i - 1] * 1000)})
                cur = ""; cur_start = None
        else:
            if cur_start is None:
                cur_start = starts[i]
            cur += c
    if cur:
        words.append({"word": cur, "startMs": int(cur_start * 1000),
                      "endMs": int(ends[-1] * 1000)})
    # Strip any leaked tag tokens
    cleaned = []
    for w in words:
        wt = w["word"]
        for t in KNOWN_TAGS:
            wt = wt.replace(f"[{t}]", "")
        cleaned.append({**w, "word": wt})
    return cleaned


def generate(text, voice_id, output, model_id=None):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY not in env")

    use_model = model_id or MODEL
    url = f"{API_BASE}/text-to-speech/{voice_id}/with-timestamps"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json",
               "Accept": "application/json"}
    body = {"text": text, "model_id": use_model, "voice_settings": NATURAL_SETTINGS}
    params = {"output_format": "mp3_44100_128"}

    print(f"Generating (voice={voice_id}, model={use_model}, settings=natural):")
    print(f"  stability={NATURAL_SETTINGS['stability']}, "
          f"style={NATURAL_SETTINGS['style']}, "
          f"similarity={NATURAL_SETTINGS['similarity_boost']}")

    r = requests.post(url, headers=headers, json=body, params=params, timeout=120)
    if r.status_code == 400 and use_model != FALLBACK_MODEL:
        bt = r.text.lower()
        if "model" in bt:
            print(f"  Model {use_model} rejected, falling back to {FALLBACK_MODEL}")
            body["model_id"] = FALLBACK_MODEL
            r = requests.post(url, headers=headers, json=body, params=params, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"  ElevenLabs {r.status_code}: {r.text[:400]}")

    payload = r.json()
    audio_b64 = payload.get("audio_base64")
    alignment = payload.get("alignment") or payload.get("normalized_alignment")
    if not (audio_b64 and alignment):
        raise SystemExit(f"  Missing audio/alignment in response: {list(payload.keys())}")

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "wb") as f:
        f.write(base64.b64decode(audio_b64))

    words = chars_to_words(alignment)
    ts_path = output.replace(".mp3", "_timestamps.json")
    # Actually the project uses `voiceover_timestamps.json` next to the file
    ts_path = os.path.join(os.path.dirname(output), "voiceover_timestamps.json")
    with open(ts_path, "w") as f:
        json.dump(words, f, indent=2)

    print(f"  ✓ {output} ({os.path.getsize(output) // 1024} KB, {len(words)} words)")
    if words:
        dur = words[-1]["endMs"] / 1000
        print(f"  Duration: {dur:.1f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--voice-id", required=True)
    ap.add_argument("--model", default=None)
    args = ap.parse_args()
    generate(args.text, args.voice_id, args.output, args.model)
