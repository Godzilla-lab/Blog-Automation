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
ELEVENLABS_DEFAULT_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVENLABS_VOICE_SETTINGS = {
    "stability": 0.45,
    "similarity_boost": 0.7,
    "style": 0.35,
    "use_speaker_boost": True,
}


def generate_elevenlabs(text: str, output_path: str, voice_id: str, api_key: str) -> list:
    """Call ElevenLabs /text-to-speech/{voice_id}/with-timestamps and return word timestamps."""
    import requests

    url = f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}/with-timestamps"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {
        "text": text,
        "model_id": ELEVENLABS_DEFAULT_MODEL,
        "voice_settings": ELEVENLABS_VOICE_SETTINGS,
    }
    params = {"output_format": "mp3_44100_128"}

    resp = requests.post(url, headers=headers, json=body, params=params, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs {resp.status_code}: {resp.text[:400]}")

    payload = resp.json()
    audio_b64 = payload.get("audio_base64")
    alignment = payload.get("alignment") or payload.get("normalized_alignment")
    if not audio_b64 or not alignment:
        raise RuntimeError(f"ElevenLabs response missing audio or alignment keys: {list(payload.keys())}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(audio_b64))

    return _chars_to_words(alignment)


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
        print(f"Generating voiceover ({len(text)} chars, engine: ElevenLabs, voice_id: {el_voice}, model: {ELEVENLABS_DEFAULT_MODEL})")
        try:
            words = generate_elevenlabs(text, args.output, el_voice, el_key)
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
