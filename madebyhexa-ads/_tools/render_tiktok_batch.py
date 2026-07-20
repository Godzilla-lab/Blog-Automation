#!/usr/bin/env python3
"""
Render each tt-* concept serially via Remotion with --concurrency=1 (dodges the
browser-pool race we hit on the p/q/r batch).

After each successful render, extract a thumbnail and copy the mp4 to
~/Desktop/MadeByHexa-TikTok-W1/<slug>.mp4
"""
import json
import os
import subprocess
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADS_DIR = os.path.join(PROJECT_ROOT, "madebyhexa-ads")
REMOTION_DIR = os.path.join(PROJECT_ROOT, "skills", "remotion-video", "remotion")
NODE_BIN = os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin")
DESKTOP_OUT = os.path.expanduser("~/Desktop/MadeByHexa-TikTok-W1")


def render_one(slug):
    folder = os.path.join(ADS_DIR, slug)
    cfg_path = os.path.join(folder, "config.json")
    cfg = json.load(open(cfg_path))

    props = {
        "slides": cfg["slides"],
        "secondsPerSlide": cfg.get("seconds_per_slide", 4),
        "accentColor": cfg.get("accent_color", "#FFD700"),
        "handle": cfg.get("handle", "@hexa_aiagency"),
        "voiceover": cfg.get("voiceover"),
        "wordTimestamps": cfg.get("word_timestamps"),
        "bgMusic": cfg.get("bg_music"),
        "bgMusicVolume": cfg.get("bg_music_volume", 0.1),
    }

    props_file = os.path.join(REMOTION_DIR, f".tmp-{slug}.json")
    with open(props_file, "w") as f:
        json.dump(props, f)

    out = os.path.abspath(os.path.join(folder, "reel.mp4"))

    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:" + env.get("PATH", "")

    cmd = ["npx", "remotion", "render", "src/index.ts", "DailyReel", out,
           "--codec=h264", f"--props={props_file}", "--concurrency=1"]

    print(f"\n=== {slug} ===")
    t0 = time.time()
    r = subprocess.run(cmd, cwd=REMOTION_DIR, env=env, capture_output=True, text=True)
    dt = time.time() - t0

    try:
        os.remove(props_file)
    except FileNotFoundError:
        pass

    if r.returncode != 0:
        print(f"  ✗ render failed ({dt:.0f}s):")
        for line in r.stderr.splitlines()[-4:]:
            print(f"    {line}")
        return False
    sz = os.path.getsize(out) / 1024 / 1024
    print(f"  ✓ rendered ({dt:.0f}s, {sz:.1f} MB)")

    # Thumbnail
    thumb = os.path.join(folder, "thumb.jpg")
    subprocess.run(["ffmpeg", "-y", "-ss", "1.5", "-i", out, "-frames:v", "1",
                    "-q:v", "2", thumb], capture_output=True)

    # Desktop copy
    os.makedirs(DESKTOP_OUT, exist_ok=True)
    desktop_dst = os.path.join(DESKTOP_OUT, f"{slug}.mp4")
    subprocess.run(["cp", out, desktop_dst])
    return True


def main():
    slugs = sorted([d for d in os.listdir(ADS_DIR)
                    if d.startswith("tt-") and os.path.isdir(os.path.join(ADS_DIR, d))])
    print(f"Rendering {len(slugs)} TikTok pieces serially (concurrency=1)...\n")

    started = time.time()
    succeeded = []
    failed = []
    for s in slugs:
        ok = render_one(s)
        if ok:
            succeeded.append(s)
        else:
            failed.append(s)
    elapsed_min = (time.time() - started) / 60

    print(f"\n=== SUMMARY ===")
    print(f"  Succeeded: {len(succeeded)}/{len(slugs)}")
    print(f"  Failed: {len(failed)}")
    if failed:
        for s in failed:
            print(f"    - {s}")
    print(f"  Total time: {elapsed_min:.1f} min")
    print(f"  Output dir: {DESKTOP_OUT}")


if __name__ == "__main__":
    main()
