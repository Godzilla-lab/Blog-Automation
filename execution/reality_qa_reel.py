#!/usr/bin/env python3
"""
RealityQA (Agent 2): Post-render vision gate.

Samples 6 frames from reel.mp4 at fixed timestamps, sends them to Claude with
vision, scores 8 dimensions of visual correctness. Catches what review_reel.py
can't see: clipped captions, off-topic b-roll, missing watermark, wrong CTA
keyword in the final frame, decode artifacts.

Reads: config.json (for ground-truth cta_keyword, handle, slide texts)
Reads: reel.mp4
Writes: reality_qa.json
Writes: <reel_dir>/.qa_frames/frame_NN_<tag>.jpg

Usage:
    python3 execution/reality_qa_reel.py \\
      --config workspace/reels/<slug>/config.json \\
      --reel workspace/reels/<slug>/reel.mp4 \\
      --output workspace/reels/<slug>/reality_qa.json

    python3 execution/reality_qa_reel.py --config ... --reel ... --frames-only
        Just extract the 6 frames, do not call Claude. Useful for testing.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed. Run: pip3 install anthropic", file=sys.stderr)
    sys.exit(1)


FFMPEG = "/Users/godzilla/.local/node-v22.22.2-darwin-arm64/bin/ffmpeg"
FFPROBE = os.path.join(
    project_root,
    "skills/remotion-video/remotion/node_modules/@ffprobe-installer/darwin-arm64/ffprobe",
)

# Threshold defaults (overridable via env vars)
MIN_AVG = float(os.getenv("REALITY_QA_MIN_AVG", "4.0"))
CTA_MIN = int(os.getenv("REALITY_QA_CTA_MIN", "4"))
WATERMARK_MIN = int(os.getenv("REALITY_QA_WATERMARK_MIN", "3"))
ARTIFACTS_MIN = int(os.getenv("REALITY_QA_ARTIFACTS_MIN", "4"))


SYSTEM_PROMPT = """You are a strict QA reviewer for short-form Instagram Reels rendered by a Remotion pipeline. You are given 6 sampled frames from a rendered reel and the config that produced it. Your job is to score the rendered output across 8 visual-correctness dimensions on a 1-5 integer scale.

You receive ground truth from the config:
  - cta_keyword: the exact word/phrase that must appear on the final frame
  - handle: the watermark text expected in the bottom-right of every frame
  - slide texts and emphasis words
  - accent_color hex

You are NOT evaluating whether the script is good. You are evaluating whether the rendered video matches the config.

RUBRIC (1-5 each, integer):

1. caption_legibility
   The synced caption text at the bottom of each frame is fully visible (not clipped at left/right edges), reads clearly against the b-roll, contrast is acceptable.

2. hook_text_readability
   The hook slide text (frame 1) is fully legible at-a-glance. No stripe artifacts. No overlapping with other text. Big enough to read on a phone.

3. watermark_present   [HARD GATE: must be >= 3]
   The handle text (e.g. "@hexa_aiagency") appears in the bottom-right area of every sampled frame. If it is missing on more than 1 frame out of 6, score <= 2.

4. broll_on_topic
   The b-roll scene under the text on each frame visually matches what the slide is about. Generic stockphoto handshakes, abstract data viz, or scenes completely unrelated to the slide topic flag here.

5. broll_quality
   The b-roll is not visibly pixelated, not zoom-cropped to be unreadable, not watermarked by a stock site, not corrupted.

6. brand_color_consistency
   The accent color (provided in the config) appears on emphasis words and the CTA highlight. Wrong colors or no highlight at all = low score.

7. cta_frame_correct   [HARD GATE: must be >= 4]
   The final frame (frame 6) text contains the cta_keyword EXACTLY as configured (case-insensitive match acceptable). Also contains the handle. If the keyword in the frame differs from the configured cta_keyword, score <= 2.

8. visual_artifacts   [HARD GATE: must be >= 4]
   No compositing stripes (horizontal banding from bad video decoders), no frame tears, no half-rendered frames, no unexpected black flashes mid-clip.

For any dimension scoring <= 3, write a `issues` array entry naming the specific frame timestamp where the issue was visible.

OUTPUT — respond with ONLY valid JSON, no markdown wrapping:

{
  "dimensions": {
    "caption_legibility":      {"score": 4, "issues": []},
    "hook_text_readability":   {"score": 5, "issues": []},
    "watermark_present":       {"score": 5, "issues": []},
    "broll_on_topic":          {"score": 4, "issues": []},
    "broll_quality":           {"score": 5, "issues": []},
    "brand_color_consistency": {"score": 5, "issues": []},
    "cta_frame_correct":       {"score": 5, "issues": []},
    "visual_artifacts":        {"score": 5, "issues": []}
  },
  "frame_issues": [
    {"timestamp": "11.8s", "issue": "Concrete one-line description"}
  ],
  "rerender_hints": {
    "swap_clips": [list of 1-indexed slide numbers whose footage should be re-downloaded],
    "regen_voiceover": false,
    "fix_config": ["any config-level issue that re-rendering won't fix (e.g. cta_keyword mismatch)"]
  }
}

`rerender_hints.swap_clips` is what the orchestrator uses to auto-rerender — only list slides where the FOOTAGE is the problem (off-topic broll, artifacts, wrong scene). If the issue is config-level (CTA keyword wrong in config), put it in `fix_config` and leave `swap_clips` empty.

NEVER use em or en dashes anywhere.
"""


def probe_duration(reel_path: str) -> float:
    """Get reel duration in seconds via ffprobe."""
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", reel_path],
            capture_output=True, text=True, check=True,
        )
        return float(r.stdout.strip())
    except Exception as e:
        print(f"  ffprobe failed: {e}", file=sys.stderr)
        return 0.0


def sample_timestamps(duration: float) -> list:
    """Return list of (label, seconds) for the 6 sampled frames."""
    return [
        ("hook",     min(0.6, max(0.2, duration * 0.05))),
        ("setup",    duration * 0.20),
        ("insight1", duration * 0.45),
        ("insight2", duration * 0.70),
        ("cta",      max(0.2, duration - 2.0)),
        ("final",    max(0.2, duration - 0.3)),
    ]


def extract_frame(reel_path: str, t: float, out_path: str) -> bool:
    """Extract one frame at timestamp t, downscaled to 720x1280, q:v 3."""
    try:
        subprocess.run(
            [
                FFMPEG, "-y", "-v", "error",
                "-ss", f"{t:.3f}",
                "-i", reel_path,
                "-frames:v", "1",
                "-q:v", "3",
                "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
                out_path,
            ],
            check=True,
            capture_output=True,
        )
        return os.path.exists(out_path) and os.path.getsize(out_path) > 1000
    except Exception as e:
        print(f"  ffmpeg extract @ {t}s failed: {e}", file=sys.stderr)
        return False


def encode_image_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def call_vision(anthropic_client, model: str, frames: list, config: dict) -> dict:
    """Send 6 frames + config ground truth to Claude vision. Return scored dict."""
    ground_truth = {
        "cta_keyword": config.get("cta_keyword", ""),
        "handle": config.get("handle", "@hexa_aiagency"),
        "accent_color": config.get("accent_color", "#FFD700"),
        "slides": [
            {"index": i + 1, "text": s.get("text", ""), "emphasis": s.get("emphasis", ""), "type": s.get("type", "")}
            for i, s in enumerate(config.get("slides", []))
        ],
    }

    # Build content blocks: ground-truth header + 6 frames each labeled with timestamp
    content = [
        {
            "type": "text",
            "text": f"GROUND TRUTH (from config.json):\n{json.dumps(ground_truth, indent=2)}\n\nSampled frames follow. Each frame is labeled with its timestamp in the reel.",
        }
    ]
    for label, t, path in frames:
        content.append({
            "type": "text",
            "text": f"\n--- Frame {label} @ {t:.2f}s ---",
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": encode_image_b64(path),
            },
        })

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    result = json.loads(text)
    result["_tokens_used"] = getattr(response.usage, "input_tokens", 0) + getattr(response.usage, "output_tokens", 0)
    return result


def apply_pass_logic(eval_result: dict) -> dict:
    dims = eval_result.get("dimensions", {})
    scores = [d.get("score", 0) for d in dims.values()]
    if not scores:
        return {
            **eval_result,
            "passed": False,
            "overall_score": 0.0,
            "recommendation": "fail",
        }
    avg = sum(scores) / len(scores)
    cta = dims.get("cta_frame_correct", {}).get("score", 0)
    watermark = dims.get("watermark_present", {}).get("score", 0)
    artifacts = dims.get("visual_artifacts", {}).get("score", 0)

    passed = (avg >= MIN_AVG) and (cta >= CTA_MIN) and (watermark >= WATERMARK_MIN) and (artifacts >= ARTIFACTS_MIN)

    eval_result["overall_score"] = round(avg, 2)
    eval_result["passed"] = passed
    eval_result["recommendation"] = "pass" if passed else "fail"
    return eval_result


def main():
    parser = argparse.ArgumentParser(description="Run vision-based QA on a rendered reel.")
    parser.add_argument("--config", required=True, help="Path to the reel's config.json")
    parser.add_argument("--reel", required=True, help="Path to the rendered reel.mp4")
    parser.add_argument("--output", help="Output path for reality_qa.json (default: <reel_dir>/reality_qa.json)")
    parser.add_argument("--frames-only", action="store_true",
                        help="Just extract the 6 frames; do not call Claude vision.")
    args = parser.parse_args()

    reel_path = os.path.abspath(args.reel)
    config_path = os.path.abspath(args.config)
    reel_dir = os.path.dirname(reel_path)

    if not os.path.exists(reel_path):
        print(json.dumps({"passed": False, "error": f"reel not found: {reel_path}"}))
        sys.exit(2)
    if not os.path.exists(config_path):
        print(json.dumps({"passed": False, "error": f"config not found: {config_path}"}))
        sys.exit(2)

    with open(config_path) as f:
        config = json.load(f)

    duration = probe_duration(reel_path)
    if duration <= 0:
        print(json.dumps({"passed": False, "error": "could not probe reel duration"}))
        sys.exit(2)

    # Extract 6 frames
    frames_dir = os.path.join(reel_dir, ".qa_frames")
    os.makedirs(frames_dir, exist_ok=True)
    frames = []
    for i, (label, t) in enumerate(sample_timestamps(duration), 1):
        out = os.path.join(frames_dir, f"frame_{i:02d}_{label}.jpg")
        ok = extract_frame(reel_path, t, out)
        if not ok:
            print(f"  WARNING: failed to extract {label}@{t:.2f}s", file=sys.stderr)
            continue
        frames.append((label, t, out))

    print(f"  Extracted {len(frames)} frames from {reel_path} (duration={duration:.2f}s)")

    if args.frames_only:
        for label, t, p in frames:
            print(f"    {label:9s} @ {t:5.2f}s -> {p} ({os.path.getsize(p)} bytes)")
        sys.exit(0)

    if not os.getenv("ANTHROPIC_API_KEY"):
        err = {"passed": False, "error": "ANTHROPIC_API_KEY not set"}
        print(json.dumps(err, indent=2))
        sys.exit(2)

    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    anth = anthropic.Anthropic()

    print(f"  Sending {len(frames)} frames to Claude vision ({model})")
    try:
        result = call_vision(anth, model, frames, config)
    except anthropic.AuthenticationError as e:
        err = {"passed": False, "error": f"anthropic_auth: {str(e)[:200]}"}
        output_path = args.output or os.path.join(reel_dir, "reality_qa.json")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(err, f, indent=2)
        print(f"  Anthropic auth failed. Wrote error to {output_path}")
        sys.exit(2)
    except anthropic.APIError as e:
        err = {"passed": False, "error": f"anthropic_api: {str(e)[:200]}"}
        output_path = args.output or os.path.join(reel_dir, "reality_qa.json")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(err, f, indent=2)
        print(f"  Anthropic API error. Wrote error to {output_path}")
        sys.exit(2)

    # Attach frame metadata to output
    result["frames_analyzed"] = [
        {"timestamp": f"{t:.2f}s", "tag": label, "path": os.path.relpath(p, reel_dir)}
        for label, t, p in frames
    ]
    result = apply_pass_logic(result)
    result["model"] = model
    result["tokens_used"] = result.pop("_tokens_used", 0)
    result["reel_duration_s"] = round(duration, 2)
    result["thresholds_used"] = {
        "min_avg": MIN_AVG,
        "cta_min": CTA_MIN,
        "watermark_min": WATERMARK_MIN,
        "artifacts_min": ARTIFACTS_MIN,
    }

    output_path = args.output or os.path.join(reel_dir, "reality_qa.json")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"  Output: {output_path}")
    print(f"  passed={result['passed']} avg={result['overall_score']}")
    if not result["passed"]:
        for issue in result.get("frame_issues", []):
            print(f"    {issue.get('timestamp')}: {issue.get('issue')}")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
