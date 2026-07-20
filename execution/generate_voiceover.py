#!/usr/bin/env python3
"""
Generate voiceover audio from text.

Two engines:
  - elevenlabs (default if ELEVENLABS_API_KEY is set): high-quality cloned voices
  - edge       (free fallback): Microsoft Azure neural voices via Edge TTS

Both write:
  - MP3 audio file
  - <output>_timestamps.json (word-level timing)

Usage:
    # Auto: ElevenLabs if key present, else Edge TTS
    python3 execution/generate_voiceover.py --text "..." --output vo.mp3

    # Force ElevenLabs with explicit voice
    python3 execution/generate_voiceover.py --text "..." --output vo.mp3 --engine elevenlabs --voice-id VxWMVg3KARt7z2UFxY5M

    # Force Edge TTS (free, robotic-ish)
    python3 execution/generate_voiceover.py --text "..." --output vo.mp3 --engine edge --voice en-US-EmmaNeural
"""

import argparse
import asyncio
import base64
import json
import os
import sys

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))


EDGE_VOICES = {
    "emma": "en-US-EmmaNeural",
    "guy": "en-US-GuyNeural",
    "jenny": "en-US-JennyNeural",
    "aria": "en-US-AriaNeural",
    "ava": "en-US-AvaNeural",
    "davis": "en-US-DavisNeural",
}
EDGE_DEFAULT_VOICE = EDGE_VOICES["emma"]

ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"
ELEVENLABS_DEFAULT_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_v3")
ELEVENLABS_FALLBACK_MODEL = "eleven_multilingual_v2"
ELEVENLABS_VOICE_SETTINGS = {
    "stability": 0.30,
    "similarity_boost": 0.75,
    "style": 0.65,
    "use_speaker_boost": True,
}

# Inline audio tags consumed by ElevenLabs v3 for prosody control. If any of
# these leak into the word-timestamps response (different v3 versions behave
# differently here), they get filtered out before saving — otherwise they
# would render as visible captions and break slide-to-voice sync.
KNOWN_AUDIO_TAGS = {
    "serious", "whispers", "shouting", "excited", "pause",
    "sigh", "laughs", "stern", "gentle", "playful", "warm",
    "low", "deliberate", "matter-of-fact", "building", "grounded",
    "firm", "soft", "loud", "punchy", "dramatic", "slow",
    "fast", "curious", "hesitant", "emphasis", "calm",
}


def generate_elevenlabs(text: str, output_path: str, voice_id: str, api_key: str,
                        model_id: str = None) -> list:
    """Call ElevenLabs /text-to-speech/{voice_id}/with-timestamps and return word timestamps.

    If `model_id` is None, uses ELEVENLABS_DEFAULT_MODEL. On HTTP 400 indicating
    an unknown model (typical when v3 is not yet available on the account),
    automatically retries once with ELEVENLABS_FALLBACK_MODEL and logs loudly.
    """
    import requests

    url = f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}/with-timestamps"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    use_model = model_id or ELEVENLABS_DEFAULT_MODEL
    body = {
        "text": text,
        "model_id": use_model,
        "voice_settings": ELEVENLABS_VOICE_SETTINGS,
    }
    params = {"output_format": "mp3_44100_128"}

    resp = requests.post(url, headers=headers, json=body, params=params, timeout=120)

    # Graceful fallback when the configured model isn't available on this account.
    if resp.status_code == 400:
        body_text = resp.text.lower()
        if ("model_id" in body_text or "model not found" in body_text or "invalid model" in body_text) \
                and use_model != ELEVENLABS_FALLBACK_MODEL:
            print(f"  [voiceover] model '{use_model}' rejected (400). Falling back to '{ELEVENLABS_FALLBACK_MODEL}'.")
            body["model_id"] = ELEVENLABS_FALLBACK_MODEL
            use_model = ELEVENLABS_FALLBACK_MODEL
            resp = requests.post(url, headers=headers, json=body, params=params, timeout=120)

    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs {resp.status_code} (model={use_model}): {resp.text[:400]}")

    payload = resp.json()
    audio_b64 = payload.get("audio_base64")
    alignment = payload.get("alignment") or payload.get("normalized_alignment")
    if not audio_b64 or not alignment:
        raise RuntimeError(f"ElevenLabs response missing audio or alignment keys: {list(payload.keys())}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(audio_b64))

    words = _chars_to_words(alignment)
    words = _filter_audio_tag_words(words)
    return words


def _filter_audio_tag_words(words: list) -> list:
    """Drop word entries that look like leaked ElevenLabs v3 audio tags.

    Three patterns are filtered:
      1. Word is literally bracketed:  "[serious]"  or  "[matter-of-fact]"
      2. Word is in KNOWN_AUDIO_TAGS and has duration < 50 ms (real spoken
         words almost never go that short; near-zero-duration entries are how
         v3 acknowledges a tag without speaking it).
      3. Word is an empty string after stripping non-alphanumerics
         (occasional artifact when brackets are stripped by the API).
    """
    filtered = []
    for w in words:
        raw = w.get("word", "")
        text = raw.strip().lower()
        if not text:
            continue
        if text.startswith("[") and text.endswith("]"):
            continue
        # Strip surrounding punctuation for tag-lookup but keep the original token
        stripped = "".join(ch for ch in text if ch.isalnum() or ch == "-")
        if stripped in KNOWN_AUDIO_TAGS and (w.get("endMs", 0) - w.get("startMs", 0)) < 50:
            continue
        filtered.append(w)
    return filtered


def _chars_to_words(alignment: dict) -> list:
    """Convert ElevenLabs character-level alignment to word-level timestamps."""
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    words = []
    current_chars = []
    current_start = None

    for ch, start_s, end_s in zip(chars, starts, ends):
        if ch.isspace():
            if current_chars:
                words.append({
                    "word": "".join(current_chars),
                    "startMs": int(round(current_start * 1000)),
                    "endMs": int(round(current_end * 1000)),
                })
                current_chars = []
                current_start = None
        else:
            if current_start is None:
                current_start = start_s
            current_chars.append(ch)
            current_end = end_s

    if current_chars:
        words.append({
            "word": "".join(current_chars),
            "startMs": int(round(current_start * 1000)),
            "endMs": int(round(current_end * 1000)),
        })

    return words


async def generate_edge(text: str, output_path: str, voice: str) -> list:
    """Generate Edge TTS audio and return word timestamps estimated from sentence boundaries."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    sentences = []
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                sentences.append({
                    "text": chunk["text"],
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                })

    TICKS_PER_MS = 10_000
    words = []
    for sentence in sentences:
        sentence_words = sentence["text"].split()
        if not sentence_words:
            continue
        char_lengths = [len(w) + 1 for w in sentence_words]
        total = sum(char_lengths)
        offset = sentence["offset"]
        for i, word in enumerate(sentence_words):
            dur = int(sentence["duration"] * char_lengths[i] / total)
            words.append({
                "word": word,
                "startMs": round(offset / TICKS_PER_MS),
                "endMs": round((offset + dur) / TICKS_PER_MS),
            })
            offset += dur
    return words


def main():
    parser = argparse.ArgumentParser(description="Generate voiceover (ElevenLabs or Edge TTS)")
    parser.add_argument("--text", help="Text to speak")
    parser.add_argument("--file", help="Read text from file")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--engine", default="auto", choices=["auto", "elevenlabs", "edge"],
                        help="auto picks ElevenLabs if ELEVENLABS_API_KEY is set, else Edge TTS")
    parser.add_argument("--voice-id", help="ElevenLabs voice ID (overrides ELEVENLABS_VOICE_ID)")
    parser.add_argument("--model", help="ElevenLabs model_id override (default: ELEVENLABS_MODEL env or 'eleven_v3'). Falls back to 'eleven_multilingual_v2' if rejected.")
    parser.add_argument("--voice", default=EDGE_DEFAULT_VOICE,
                        help=f"Edge TTS voice (default {EDGE_DEFAULT_VOICE}). Shortcuts: {', '.join(EDGE_VOICES)}")
    parser.add_argument("--list-voices", action="store_true", help="List Edge TTS voices and exit")
    args = parser.parse_args()

    if args.list_voices:
        import edge_tts
        async def _list():
            for v in await edge_tts.list_voices():
                if v["Locale"].startswith("en-"):
                    print(f"  {v['ShortName']:30s}  {v['Gender']:8s}  {v['Locale']}")
        asyncio.run(_list())
        return

    if args.file:
        with open(args.file, "r") as f:
            text = f.read().strip()
    elif args.text:
        text = args.text
    else:
        print("Error: Provide --text or --file")
        sys.exit(1)
    if not text:
        print("Error: Empty text")
        sys.exit(1)

    el_key = os.getenv("ELEVENLABS_API_KEY")
    el_voice = args.voice_id or os.getenv("ELEVENLABS_VOICE_ID")

    engine = args.engine
    if engine == "auto":
        engine = "elevenlabs" if (el_key and el_voice) else "edge"

    if engine == "elevenlabs":
        if not el_key:
            print("Error: ELEVENLABS_API_KEY not set in .env")
            sys.exit(1)
        if not el_voice:
            print("Error: ELEVENLABS_VOICE_ID not set in .env and --voice-id not provided")
            sys.exit(1)
        model_to_use = args.model or ELEVENLABS_DEFAULT_MODEL
        print(f"Generating voiceover ({len(text)} chars, engine: ElevenLabs, voice_id: {el_voice}, model: {model_to_use})")
        try:
            words = generate_elevenlabs(text, args.output, el_voice, el_key, model_id=model_to_use)
        except Exception as e:
            print(f"ElevenLabs failed: {e}")
            if args.engine == "elevenlabs":
                sys.exit(1)
            print("Falling back to Edge TTS...")
            voice = EDGE_VOICES.get(args.voice, args.voice)
            words = asyncio.run(generate_edge(text, args.output, voice))
    else:
        voice = EDGE_VOICES.get(args.voice, args.voice)
        print(f"Generating voiceover ({len(text)} chars, engine: Edge TTS, voice: {voice})")
        words = asyncio.run(generate_edge(text, args.output, voice))

    if not os.path.exists(args.output) or os.path.getsize(args.output) == 0:
        print("Error: Audio file not created or empty")
        sys.exit(1)

    size_kb = os.path.getsize(args.output) / 1024
    print(f"  Audio: {args.output} ({size_kb:.0f} KB)")

    timestamps_path = os.path.splitext(args.output)[0] + "_timestamps.json"
    with open(timestamps_path, "w") as f:
        json.dump(words, f, indent=2)
    print(f"  Timestamps: {timestamps_path} ({len(words)} words)")

    if words:
        print(f"  Duration: {words[-1]['endMs'] / 1000:.1f}s")


if __name__ == "__main__":
    main()
