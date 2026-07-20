#!/usr/bin/env python3
"""
For each tt-* concept folder under madebyhexa-ads/:
  1. Read its config.json
  2. If voiceover.mp3 doesn't exist, run gen_voice_natural.py
  3. Run sync_manual.py with the config's _end_word_indices
  4. Copy voiceover.mp3 to madebyhexa-ads/public/<slug>/

Parallelization: voiceovers run in batches of 4 (rate-limit safety on ElevenLabs).
"""
import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADS_DIR = os.path.join(PROJECT_ROOT, "madebyhexa-ads")
PUBLIC_DIR = os.path.join(ADS_DIR, "public")
TOOLS_DIR = os.path.join(ADS_DIR, "_tools")
VOICE_ID = "tnSpp4vdxKPjI9w0GnoV"


def gen_voice(slug):
    folder = os.path.join(ADS_DIR, slug)
    cfg_path = os.path.join(folder, "config.json")
    cfg = json.load(open(cfg_path))
    vo_text = cfg["voiceover_script"]
    out = os.path.join(folder, "voiceover.mp3")
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        return f"  ✓ {slug}: voiceover already exists ({os.path.getsize(out)//1024} KB), skipping"
    cmd = ["python3", os.path.join(TOOLS_DIR, "gen_voice_natural.py"),
           "--voice-id", VOICE_ID, "--text", vo_text, "--output", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return f"  ✗ {slug}: gen_voice failed: {r.stderr[:200]}"
    # extract size
    sz = os.path.getsize(out) // 1024
    return f"  ✓ {slug}: voiceover ({sz} KB)"


def sync_one(slug):
    folder = os.path.join(ADS_DIR, slug)
    cfg = json.load(open(os.path.join(folder, "config.json")))
    end_indices = cfg.get("_end_word_indices")
    if not end_indices:
        return f"  ✗ {slug}: no _end_word_indices in config"
    cmd = ["python3", os.path.join(TOOLS_DIR, "sync_manual.py"), folder] + [str(i) for i in end_indices]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return f"  ✗ {slug}: sync failed: {r.stderr[:200]}"
    return f"  ✓ {slug}: synced"


def copy_to_public(slug):
    src = os.path.join(ADS_DIR, slug, "voiceover.mp3")
    dst_dir = os.path.join(PUBLIC_DIR, slug)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, "voiceover.mp3")
    shutil.copy2(src, dst)
    return f"  ✓ {slug}: copied to public/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-workers", type=int, default=4)
    args = ap.parse_args()

    slugs = sorted([d for d in os.listdir(ADS_DIR) if d.startswith("tt-") and os.path.isdir(os.path.join(ADS_DIR, d))])
    print(f"Found {len(slugs)} TikTok concepts")

    print(f"\nPhase 1: Generating voiceovers (parallel, max_workers={args.max_workers})...")
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        for r in ex.map(gen_voice, slugs):
            print(r)
    print(f"  Phase 1 done in {time.time()-t0:.1f}s")

    print(f"\nPhase 2: Syncing slide durations from word_timestamps...")
    for s in slugs:
        print(sync_one(s))

    print(f"\nPhase 3: Copying voiceovers to public/...")
    for s in slugs:
        print(copy_to_public(s))


if __name__ == "__main__":
    main()
