#!/usr/bin/env python3
"""
Master orchestrator: generate N Instagram Reels per day.

Full pipeline per reel (gated by 3 AI agents to keep the user out of the loop):
  0. RESEARCH topic         — Tavily + Claude → research_brief.json
  1. GENERATE reel script   — Claude (constrained by the brief) → config.json
  1b. EVALUATE script        — Claude scores 9 dimensions; up to 2 retries with critique
  2. DOWNLOAD stock footage  — Pexels (and Pixabay fallback)
  3. GENERATE voiceover      — ElevenLabs / Edge TTS + word timestamps
  4. RENDER video            — Remotion DailyReel
  5. GENERATE IG caption
  6. DETERMINISTIC QA        — review_reel.py (existing rule-based)
  6b. REALITY QA (VISION)     — Claude vision on 6 sampled frames; one auto-rerender on fail

Usage:
    python3 execution/run_daily_reels.py --count 3
    python3 execution/run_daily_reels.py --count 1 --niche dental
    python3 execution/run_daily_reels.py --count 3 --dry-run
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

REMOTION_PUBLIC = os.path.join(project_root, "skills", "remotion-video", "remotion", "public")
NODE_BIN = os.path.expanduser("~/.local/node-v22.22.2-darwin-arm64/bin")

# Content mix: how often each reel type should appear
REEL_TYPE_WEIGHTS = {
    "pas": 40,
    "before_after": 25,
    "lead_magnet": 20,
    "trend": 15,
}

NICHES = ["dental", "property", "cleaning", "general"]


def pick_reel_type() -> str:
    """Pick a reel type based on content mix weights."""
    types = list(REEL_TYPE_WEIGHTS.keys())
    weights = list(REEL_TYPE_WEIGHTS.values())
    return random.choices(types, weights=weights, k=1)[0]


def pick_niche(exclude: list = None) -> str:
    """Pick a niche, avoiding the ones we just used (rotation)."""
    available = [n for n in NICHES if n not in (exclude or [])]
    if not available:
        available = NICHES
    return random.choice(available)


def pick_topic(niche: str) -> str:
    """Pick a topic — from trends file, blog posts, or evergreen fallback."""
    # Try trend file first
    trends_file = os.path.join(project_root, ".tmp", "ai_trends.json")
    if os.path.exists(trends_file):
        with open(trends_file, "r") as f:
            trends_data = json.load(f)
        niche_trends = trends_data.get("niche_trends", [])
        if niche_trends:
            trend = random.choice(niche_trends)
            return trend["title"]

    # Try blog posts
    blog_output = os.path.join(project_root, "blog-automation", "output")
    if os.path.exists(blog_output):
        blog_dirs = [d for d in os.listdir(blog_output) if os.path.isdir(os.path.join(blog_output, d))]
        if blog_dirs:
            chosen = random.choice(blog_dirs)
            # Convert slug to topic: "2026-03-19-why-dental-appointment-reminders-dont-work"
            topic = chosen.split("-", 3)[-1].replace("-", " ") if len(chosen.split("-")) > 3 else chosen
            return topic

    # Evergreen fallback
    evergreen = {
        "dental": [
            "dental no-shows cost practices thousands",
            "why dental appointment reminders don't work",
            "how AI recall systems increase chair utilization",
        ],
        "property": [
            "why property managers are overwhelmed with tenant communications",
            "automating maintenance requests saves 10+ hours a week",
            "the hidden cost of manual rent collection",
        ],
        "cleaning": [
            "why cleaning companies lose contracts over communication",
            "employee scheduling kills cleaning business productivity",
            "automating client check-ins retains more contracts",
        ],
        "general": [
            "why most small businesses waste 20 hours a week on manual tasks",
            "AI automation ROI: what businesses actually see in 90 days",
            "the 3 workflows every service business should automate first",
        ],
    }
    topics = evergreen.get(niche, evergreen["general"])
    return random.choice(topics)


def run_step(description: str, cmd: list, env: dict = None, cwd: str = None) -> bool:
    """Run a pipeline step with logging."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")

    result = subprocess.run(
        cmd,
        env=env or os.environ.copy(),
        cwd=cwd or project_root,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode})")
        if result.stderr:
            print(result.stderr[:500])
        return False
    return True


def generate_one_reel(index: int, niche: str, reel_type: str, topic: str, output_base: str) -> dict:
    """Generate a single reel through the full pipeline. Returns result dict."""
    today = date.today().isoformat()
    slug = topic.lower().replace(" ", "-").replace("'", "")[:50]
    reel_dir = os.path.join(output_base, f"{today}-{slug}")
    os.makedirs(reel_dir, exist_ok=True)

    config_path = os.path.join(reel_dir, "config.json")
    footage_dir = os.path.join(REMOTION_PUBLIC, "reels", f"{today}-{slug}")
    voiceover_path = os.path.join(REMOTION_PUBLIC, "reels", f"{today}-{slug}", "voiceover.mp3")
    timestamps_path = os.path.join(REMOTION_PUBLIC, "reels", f"{today}-{slug}", "voiceover_timestamps.json")
    reel_output = os.path.join(reel_dir, "reel.mp4")

    env = os.environ.copy()
    env["PATH"] = f"{NODE_BIN}:{env.get('PATH', '')}"

    result = {
        "index": index,
        "niche": niche,
        "type": reel_type,
        "topic": topic,
        "dir": reel_dir,
        "success": False,
    }

    # ---------------- Step 0: Research the topic ----------------
    research_brief_path = os.path.join(reel_dir, "research_brief.json")
    if not run_step(
        f"[Reel {index+1}] Researching: {topic}",
        ["python3", os.path.join(script_dir, "research_topic.py"),
         "--niche", niche, "--topic", topic, "--reel-type", reel_type,
         "--output", research_brief_path],
    ):
        result["research_failed"] = True
        if os.path.exists(research_brief_path):
            try:
                with open(research_brief_path) as f:
                    rb = json.load(f)
                result["research_warnings"] = rb.get("warnings", [])
            except Exception:
                pass
        return result

    # ---------------- Steps 1 + 1b: Generate + Evaluate (with retry loop) ----------------
    eval_path = os.path.join(reel_dir, "script_eval.json")
    MAX_SCRIPT_RETRIES = int(os.getenv("SCRIPT_EVAL_MAX_RETRIES", "2"))
    critique = None
    eval_result = None
    for attempt in range(MAX_SCRIPT_RETRIES + 1):
        attempt_label = "initial" if attempt == 0 else f"retry {attempt}/{MAX_SCRIPT_RETRIES}"
        gen_cmd = [
            "python3", os.path.join(script_dir, "generate_reel_script.py"),
            "--topic", topic, "--niche", niche, "--type", reel_type,
            "--output", config_path,
            "--research-brief", research_brief_path,
        ]
        if critique:
            gen_cmd += ["--critique", critique]
        if not run_step(
            f"[Reel {index+1}] Generating script ({attempt_label}): {topic}",
            gen_cmd,
        ):
            result["script_generation_failed"] = True
            return result

        # Evaluate (do not treat non-zero exit as fatal — the JSON tells us)
        eval_cmd = [
            "python3", os.path.join(script_dir, "evaluate_reel_script.py"),
            "--script", config_path,
            "--research-brief", research_brief_path,
            "--niche", niche, "--topic", topic, "--reel-type", reel_type,
            "--output", eval_path,
        ]
        subprocess.run(eval_cmd, capture_output=True, text=True, cwd=project_root)

        if not os.path.exists(eval_path):
            result["script_eval_failed"] = True
            result["script_eval_reason"] = "evaluator did not produce output"
            return result

        with open(eval_path) as f:
            eval_result = json.load(f)
        print(f"  Eval: passed={eval_result.get('passed')} avg={eval_result.get('overall_score')} "
              f"min_dim={eval_result.get('min_dimension_score')}")

        if eval_result.get("passed"):
            break
        if not eval_result.get("regenerate"):
            result["script_eval_failed"] = True
            result["script_eval_reason"] = eval_result.get("critique", "hard fail")
            print(f"  Hard fail. No retry. Critique: {eval_result.get('critique', '')[:200]}")
            return result
        critique = eval_result.get("critique", "")
        print(f"  Soft fail. Will retry with critique ({len(critique)} chars).")
    else:
        # Loop completed without break — retries exhausted
        result["script_eval_failed"] = True
        result["script_eval_reason"] = f"exhausted {MAX_SCRIPT_RETRIES} retries; last critique: {critique[:300] if critique else ''}"
        return result

    # Load the (now-passing) generated config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Step 2: Download footage for each slide
    # Check curated library first, then fall back to API search
    os.makedirs(footage_dir, exist_ok=True)
    slides = config.get("slides", [])
    library_dir = os.path.join(project_root, "workspace", "footage-library", niche)
    library_meta = None
    if os.path.exists(os.path.join(library_dir, "metadata.json")):
        with open(os.path.join(library_dir, "metadata.json"), "r") as f:
            library_meta = json.load(f)

    for i, slide in enumerate(slides):
        query = slide.get("footage_query", slide.get("text", "business")[:30])
        clip_path = os.path.join(footage_dir, f"clip-{i+1}.mp4")
        frame_path = os.path.join(footage_dir, f"clip-{i+1}.jpg")

        # Try curated library first (keyword match against tags)
        library_hit = False
        if library_meta:
            query_words = set(query.lower().split())
            best_match = None
            best_score = 0
            for entry in library_meta:
                tags = set(t.lower() for t in entry.get("tags", []))
                score = len(query_words & tags)
                if score > best_score:
                    best_score = score
                    best_match = entry
            if best_match and best_score >= 1:
                src = os.path.join(library_dir, best_match["filename"])
                if os.path.exists(src):
                    import shutil
                    shutil.copy2(src, clip_path)
                    # Copy thumbnail if it exists
                    thumb_src = src.replace(".mp4", ".jpg")
                    if os.path.exists(thumb_src):
                        shutil.copy2(thumb_src, frame_path)
                    library_hit = True
                    print(f"  [Reel {index+1}] Slide {i+1}: library hit '{best_match['filename']}' (score={best_score})")

        if not library_hit and not run_step(
            f"[Reel {index+1}] Downloading footage {i+1}/{len(slides)}: '{query}'",
            ["python3", os.path.join(script_dir, "download_pexels_video.py"),
             "--query", query, "--output", footage_dir,
             "--filename", f"clip-{i+1}.mp4",
             "--orientation", "portrait"],
        ):
            print(f"  Warning: Footage download failed for slide {i+1}, using fallback")

        # Use .mp4 for Remotion (OffthreadVideo decodes via FFmpeg, not Chrome)
        slide["footage"] = f"reels/{today}-{slug}/clip-{i+1}.mp4"
        # Fall back to .jpg if .mp4 doesn't exist
        if not os.path.exists(clip_path) and os.path.exists(frame_path):
            slide["footage"] = f"reels/{today}-{slug}/clip-{i+1}.jpg"

    # Step 3: Generate voiceover
    voiceover_script = config.get("voiceover_script", "")
    if voiceover_script:
        os.makedirs(os.path.dirname(voiceover_path), exist_ok=True)
        if run_step(
            f"[Reel {index+1}] Generating voiceover",
            ["python3", os.path.join(script_dir, "generate_voiceover.py"),
             "--text", voiceover_script,
             "--output", voiceover_path],
        ):
            config["voiceover"] = f"reels/{today}-{slug}/voiceover.mp3"

            # Load word timestamps and size each slide to its spoken segment.
            # Reel total = voiceover duration + transitions + small tail. No padding.
            if os.path.exists(timestamps_path):
                with open(timestamps_path, "r") as f:
                    config["word_timestamps"] = json.load(f)
                sys.path.insert(0, script_dir)
                from sync_slides_to_voice import sync_slides_to_voice
                durations, total_frames = sync_slides_to_voice(
                    config["slides"], config["word_timestamps"]
                )
                for slide, frames in zip(config["slides"], durations):
                    slide["durationFrames"] = frames
                voice_s = config["word_timestamps"][-1]["endMs"] / 1000
                print(f"  Synced slides to voice: {total_frames/30:.2f}s reel for {voice_s:.2f}s voice")

                # ---- Multi-clip slides: any slide whose voiceover segment is >6s
                # gets a second Pexels clip so the visual doesn't sit on one frame.
                # The renderer (FootageBackground) divides the slide window evenly
                # between sub-clips. Threshold matches feedback_multi_clip_slides.md.
                MULTI_CLIP_THRESHOLD_FRAMES = 180  # 6s @ 30fps
                for i, slide in enumerate(config["slides"]):
                    if slide.get("durationFrames", 0) <= MULTI_CLIP_THRESHOLD_FRAMES:
                        continue
                    query = slide.get("footage_query", slide.get("text", "business")[:30])
                    clip_a = os.path.join(footage_dir, f"clip-{i+1}.mp4")
                    clip_a_renamed = os.path.join(footage_dir, f"clip-{i+1}a.mp4")
                    clip_b = os.path.join(footage_dir, f"clip-{i+1}b.mp4")
                    if not os.path.exists(clip_a):
                        continue  # primary clip missing — skip variant
                    if not os.path.exists(clip_a_renamed):
                        os.rename(clip_a, clip_a_renamed)
                    if not os.path.exists(clip_b):
                        run_step(
                            f"[Reel {index+1}] Slide {i+1} is {slide['durationFrames']/30:.1f}s — "
                            f"downloading 2nd clip for visual variety",
                            ["python3", os.path.join(script_dir, "download_pexels_video.py"),
                             "--query", query, "--output", footage_dir,
                             "--filename", f"clip-{i+1}b.mp4",
                             "--orientation", "portrait"],
                        )
                    if os.path.exists(clip_b):
                        slide.pop("footage", None)
                        slide["footages"] = [
                            f"reels/{today}-{slug}/clip-{i+1}a.mp4",
                            f"reels/{today}-{slug}/clip-{i+1}b.mp4",
                        ]
                    else:
                        # 2nd clip didn't land — keep single-clip path with rename undone
                        if os.path.exists(clip_a_renamed) and not os.path.exists(clip_a):
                            os.rename(clip_a_renamed, clip_a)
                        slide["footage"] = f"reels/{today}-{slug}/clip-{i+1}.mp4"

    # Pick background music based on reel type (randomly from available tracks per mood)
    BG_MUSIC_MAP = {
        "pas": "bg-dramatic",         # problem-agitation-solution: serious tone
        "before_after": "bg-upbeat",   # transformation: motivational
        "lead_magnet": "bg-corporate",  # free value + CTA: professional
        "trend": "bg-energetic",        # trend reaction: high energy
    }
    BG_MUSIC_FALLBACK = "bg-chill"
    mood_prefix = BG_MUSIC_MAP.get(reel_type, BG_MUSIC_FALLBACK)
    sfx_dir = os.path.join(REMOTION_PUBLIC, "sfx")
    mood_tracks = [
        f for f in os.listdir(sfx_dir)
        if f.startswith(mood_prefix) and f.endswith(".mp3")
    ] if os.path.exists(sfx_dir) else []
    if mood_tracks:
        bg_track = f"sfx/{random.choice(mood_tracks)}"
        config["bg_music"] = bg_track
        config["bg_music_volume"] = 0.12

    # Save updated config with footage paths and voiceover
    config["handle"] = "@hexa_aiagency"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Step 4: Render video
    if not run_step(
        f"[Reel {index+1}] Rendering video",
        ["python3", os.path.join(script_dir, "generate_reel.py"),
         "--config", config_path, "--output", reel_output],
        env=env,
    ):
        return result

    # Step 5: Generate Instagram caption
    run_step(
        f"[Reel {index+1}] Generating Instagram caption",
        ["python3", os.path.join(script_dir, "generate_ig_caption.py"),
         "--config", config_path],
    )

    if os.path.exists(reel_output):
        size_mb = os.path.getsize(reel_output) / 1024 / 1024
        result["success"] = True
        result["output"] = reel_output
        result["size_mb"] = round(size_mb, 1)
        print(f"\n  Reel {index+1} complete: {reel_output} ({size_mb:.1f} MB)")

    # ---------------- Step 6: Deterministic QA (existing review_reel.py) ----------------
    review_result = subprocess.run(
        ["python3", os.path.join(script_dir, "review_reel.py"), reel_dir],
        capture_output=True, text=True, cwd=project_root,
    )
    if review_result.stdout:
        print(review_result.stdout)
    deterministic_qa_passed = (review_result.returncode == 0)
    if not deterministic_qa_passed:
        print(f"  [Reel {index+1}] Deterministic QA FAILED — review errors above")
    result["deterministic_qa_passed"] = deterministic_qa_passed

    # ---------------- Step 6b: RealityQA (vision) + auto-rerender on fail ----------------
    reality_qa_path = os.path.join(reel_dir, "reality_qa.json")
    rqa_cmd = [
        "python3", os.path.join(script_dir, "reality_qa_reel.py"),
        "--config", config_path,
        "--reel", reel_output,
        "--output", reality_qa_path,
    ]
    print(f"\n{'='*60}\n  [Reel {index+1}] Running RealityQA (vision)\n{'='*60}")
    rqa_proc = subprocess.run(rqa_cmd, capture_output=True, text=True, cwd=project_root)
    if rqa_proc.stdout:
        print(rqa_proc.stdout)

    rqa_result = {}
    if os.path.exists(reality_qa_path):
        with open(reality_qa_path) as f:
            rqa_result = json.load(f)

    reality_qa_passed = rqa_result.get("passed", False)

    # Auto-rerender once if RealityQA failed AND the fix is footage-level (not config-level)
    if not reality_qa_passed:
        hints = rqa_result.get("rerender_hints", {})
        swap_clips = hints.get("swap_clips", [])
        fix_config = hints.get("fix_config", [])

        if swap_clips and not fix_config:
            print(f"\n  [Reel {index+1}] RealityQA flagged footage issues on slides {swap_clips}. "
                  f"Auto-rerendering once.")

            for slide_idx in swap_clips:
                # 1-indexed in the rubric
                slide = config["slides"][slide_idx - 1] if 0 < slide_idx <= len(config["slides"]) else None
                if not slide:
                    continue
                query = slide.get("footage_query", slide.get("text", "business")[:30])
                # Multi-clip slide? Swap the FIRST clip in the array (clip-Na.mp4);
                # the second (clip-Nb.mp4) stays so we don't waste credits.
                # Single-clip slide? Swap the legacy clip-N.mp4 in place.
                if slide.get("footages"):
                    swap_filename = f"clip-{slide_idx}a.mp4"
                else:
                    swap_filename = f"clip-{slide_idx}.mp4"
                run_step(
                    f"[Reel {index+1}] Re-downloading footage for slide {slide_idx} ({swap_filename}): '{query}'",
                    ["python3", os.path.join(script_dir, "download_pexels_video.py"),
                     "--query", query, "--output", footage_dir,
                     "--filename", swap_filename,
                     "--orientation", "portrait"],
                )

            # Re-render
            run_step(
                f"[Reel {index+1}] Re-rendering after footage swap",
                ["python3", os.path.join(script_dir, "generate_reel.py"),
                 "--config", config_path, "--output", reel_output],
                env=env,
            )

            # Re-run RealityQA once
            print(f"  [Reel {index+1}] Re-running RealityQA after rerender")
            rqa_proc2 = subprocess.run(rqa_cmd, capture_output=True, text=True, cwd=project_root)
            if rqa_proc2.stdout:
                print(rqa_proc2.stdout)
            if os.path.exists(reality_qa_path):
                with open(reality_qa_path) as f:
                    rqa_result = json.load(f)
            reality_qa_passed = rqa_result.get("passed", False)
        elif fix_config:
            print(f"  [Reel {index+1}] RealityQA flagged config-level issues; no auto-rerender. "
                  f"Surfacing to user: {fix_config}")

    result["reality_qa_passed"] = reality_qa_passed
    if not reality_qa_passed:
        result["reality_qa_failed"] = True
        result["reality_qa_reason"] = {
            "overall_score": rqa_result.get("overall_score"),
            "frame_issues": rqa_result.get("frame_issues", []),
            "fix_config": rqa_result.get("rerender_hints", {}).get("fix_config", []),
        }

    # Final composite QA flag: BOTH gates must pass
    result["qa_passed"] = deterministic_qa_passed and reality_qa_passed
    if not result["qa_passed"]:
        print(f"  [Reel {index+1}] FINAL QA: failed (deterministic={deterministic_qa_passed}, "
              f"reality={reality_qa_passed})")
    else:
        print(f"  [Reel {index+1}] FINAL QA: PASSED")

    return result


def main():
    parser = argparse.ArgumentParser(description="Generate daily Instagram Reels")
    parser.add_argument("--count", type=int, default=3, help="Number of reels to generate (default: 3)")
    parser.add_argument("--niche", choices=NICHES, help="Force a specific niche (otherwise rotates)")
    parser.add_argument("--topic", help="Force a specific topic for all reels")
    parser.add_argument("--type", dest="reel_type", choices=list(REEL_TYPE_WEIGHTS.keys()),
                        help="Force a specific reel type")
    parser.add_argument("--output", default=os.path.join(project_root, "workspace", "reels"),
                        help="Output base directory")
    parser.add_argument("--dry-run", action="store_true", help="Plan the reels without generating")
    args = parser.parse_args()

    print(f"\n{'#'*60}")
    print(f"  DAILY REELS PIPELINE — {date.today().isoformat()}")
    print(f"  Generating {args.count} reel(s)")
    print(f"{'#'*60}")

    # Plan the reels
    recent_niches = []
    plans = []
    for i in range(args.count):
        niche = args.niche or pick_niche(exclude=recent_niches[-2:] if len(recent_niches) >= 2 else [])
        reel_type = args.reel_type or pick_reel_type()
        topic = args.topic or pick_topic(niche)

        plans.append({"niche": niche, "type": reel_type, "topic": topic})
        recent_niches.append(niche)

    print(f"\n  Planned reels:")
    for i, p in enumerate(plans):
        print(f"    {i+1}. [{p['niche']}] [{p['type']}] {p['topic']}")

    if args.dry_run:
        print("\n  Dry run — no reels generated.")
        return

    # Generate each reel
    results = []
    for i, plan in enumerate(plans):
        result = generate_one_reel(
            index=i,
            niche=plan["niche"],
            reel_type=plan["type"],
            topic=plan["topic"],
            output_base=args.output,
        )
        results.append(result)

    # Summary
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\n{'#'*60}")
    print(f"  SUMMARY")
    print(f"{'#'*60}")
    print(f"  Generated: {len(successful)}/{len(results)} reels")

    for r in successful:
        print(f"    {r['index']+1}. [{r['niche']}] {r['topic'][:50]} -> {r.get('output', '?')}")

    if failed:
        print(f"\n  Failed (never rendered):")
        for r in failed:
            reason = "unknown"
            if r.get("research_failed"):
                reason = "research"
            elif r.get("script_eval_failed"):
                reason = f"script_eval: {r.get('script_eval_reason', '')[:120]}"
            elif r.get("script_generation_failed"):
                reason = "script_gen"
            print(f"    {r['index']+1}. [{r['niche']}] {r['topic'][:50]} - {reason}")

    qa_failed = [r for r in successful if not r.get("qa_passed", True)]
    if qa_failed:
        print(f"\n  QA Failed ({len(qa_failed)} rendered but did not pass both gates):")
        for r in qa_failed:
            det = "OK" if r.get("deterministic_qa_passed") else "FAIL"
            rea = "OK" if r.get("reality_qa_passed") else "FAIL"
            print(f"    {r['index']+1}. [{r['niche']}] {r['topic'][:50]} - "
                  f"deterministic={det} reality={rea}")
            if r.get("reality_qa_reason", {}).get("fix_config"):
                print(f"       config issues: {r['reality_qa_reason']['fix_config']}")

    # Save run log
    log_path = os.path.join(args.output, f"run-{date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump({"date": date.today().isoformat(), "results": results}, f, indent=2, default=str)
    print(f"\n  Run log: {log_path}")


if __name__ == "__main__":
    main()
