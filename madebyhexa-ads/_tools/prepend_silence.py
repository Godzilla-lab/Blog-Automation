#!/usr/bin/env python3
"""
Prepend N ms of silence to a voiceover.mp3 + shift word_timestamps.json by the
same offset. Used for the Skeptic Trap concept (D) which needs a silent visual
intro before the voice kicks in.

Writes alongside originals: voiceover.mp3 (overwrites) + voiceover_timestamps.json (overwrites).
Backups go to .orig.mp3 and .orig.json.

Usage:
    python3 madebyhexa-ads/_tools/prepend_silence.py <concept_dir> <ms>
    e.g. python3 madebyhexa-ads/_tools/prepend_silence.py madebyhexa-ads/d-skeptic-trap 1500
"""
import json
import os
import shutil
import subprocess
import sys

FFMPEG = "/Users/godzilla/.local/node-v22.22.2-darwin-arm64/bin/ffmpeg"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    concept_dir = sys.argv[1]
    ms = int(sys.argv[2])

    mp3_p = os.path.join(concept_dir, "voiceover.mp3")
    ts_p = os.path.join(concept_dir, "voiceover_timestamps.json")
    backup_mp3 = mp3_p + ".orig"
    backup_ts = ts_p + ".orig"

    if not os.path.exists(backup_mp3):
        shutil.copy(mp3_p, backup_mp3)
    if not os.path.exists(backup_ts):
        shutil.copy(ts_p, backup_ts)

    # Prepend silence via ffmpeg adelay filter (works for stereo by default)
    tmp = mp3_p + ".tmp.mp3"
    seconds = ms / 1000.0
    cmd = [
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-i", backup_mp3,
        "-af", f"adelay={ms}|{ms}",
        tmp,
    ]
    subprocess.run(cmd, check=True)
    shutil.move(tmp, mp3_p)

    # Shift all word_timestamps by +ms
    with open(backup_ts) as f:
        ts = json.load(f)
    for w in ts:
        w["startMs"] += ms
        w["endMs"] += ms
    with open(ts_p, "w") as f:
        json.dump(ts, f, indent=2)

    new_dur = subprocess.check_output(
        [FFMPEG, "-hide_banner", "-i", mp3_p], stderr=subprocess.STDOUT
    ).decode()
    for line in new_dur.split("\n"):
        if "Duration" in line:
            print(f"  Prepended {ms}ms silence to {concept_dir}/voiceover.mp3")
            print(f"  New: {line.strip()}")
            break


if __name__ == "__main__":
    main()
