
# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_website.md` and come up with inputs/outputs and then run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs that the user can access
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `execution/` - Python scripts (the deterministic tools)
- `directives/` - SOPs in Markdown (the instruction set)
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)

**Key principle:** Local files are only for processing. Deliverables live in cloud services (Google Sheets, Slides, etc.) where the user can access them. Everything in `.tmp/` can be deleted and regenerated.

## Cloud Webhooks (Modal)

The system supports event-driven execution via Modal webhooks. Each webhook maps to exactly one directive with scoped tool access.

**When user says "add a webhook that...":**
1. Read `directives/add_webhook.md` for complete instructions
2. Create the directive file in `directives/`
3. Add entry to `execution/webhooks.json`
4. Deploy: `modal deploy execution/modal_webhook.py`
5. Test the endpoint

**Key files:**
- `execution/webhooks.json` - Webhook slug → directive mapping
- `execution/modal_webhook.py` - Modal app (do not modify unless necessary)
- `directives/add_webhook.md` - Complete setup guide

**Endpoints:**
- `https://nick-90891--claude-orchestrator-list-webhooks.modal.run` - List webhooks
- `https://nick-90891--claude-orchestrator-directive.modal.run?slug={slug}` - Execute directive
- `https://nick-90891--claude-orchestrator-test-email.modal.run` - Test email

**Available tools for webhooks:** `send_email`, `read_sheet`, `update_sheet`

**All webhook activity streams to Slack in real-time.**

## Workflow Router

When the user requests one of these workflows, read the linked directive FIRST before doing anything:

| User says... | Read this directive | Key scripts |
|---|---|---|
| "make a carousel" / "carousel" / "thread to carousel" | `directives/thread_to_carousel.md` | `execution/search_images.py`, `execution/render_carousel.py`, `execution/generate_ig_caption.py` |
| "generate reels" / "daily reels" / "make reels" | `directives/generate_daily_reels.md` | `execution/run_daily_reels.py` (orchestrates all steps) |
| "make a reel" / "single reel" / "generate reel" | `directives/generate_daily_reel.md` | `execution/generate_reel.py`, `execution/generate_voiceover.py` |
| "highlight covers" / "generate video" | `directives/generate_video.md` | `execution/render_video.py` |
| "tweets" / "viral tweets" / "tweet ideas" | `directives/generate_viral_tweets.md` | `execution/generate_tweets.py` |
| "content strategy" / "instagram strategy" | `directives/instagram_content_strategy.md` | (reference doc, not a pipeline) |

### Global Defaults (override everything else)
- **Voiceover voice**: ElevenLabs **Ellen** (voice_id `BIvP0GN1cAtSRTxNHnWS`) — serious, direct, confident female. Set as `ELEVENLABS_VOICE_ID` in `.env`; `generate_voiceover.py --engine auto` picks ElevenLabs whenever the key + voice_id are present. Edge TTS (`en-US-EmmaNeural`) is the free fallback only when ElevenLabs is unavailable.
- **Image search for carousels**: Use `execution/search_images.py` (Tavily API). NOT Pexels. NOT download_image.py for discovery.
- **Always generate caption.txt**: Every carousel AND every reel must include a `caption.txt` with hook, CTA, and hashtags. Use `execution/generate_ig_caption.py` or write manually.
- **Carousels must have images**: Slide 1 (hook) MUST have an image. Aim for 50%+ slides with images. Never create text-only carousels.
- **Reels are lead-gen, not commentary**: Every reel is scored against the 9-dimension rubric in `directives/evaluate_reel_script.md`. Hooks must hit visceral pain (dollar amount or time amount in first 6 words). CTAs must name a concrete deliverable ("the calculator", "the checklist") — never "more info" or vague "the playbook". Thought-leadership reels fail `lead_gen_intent`.
- **Reel video element is `<Video>`, not `<OffthreadVideo>`.** `skills/remotion-video/remotion/src/reels/scenes/FootageBackground.tsx` must use `<Video>` from Remotion. OffthreadVideo bakes horizontal stripe artifacts into every frame. If stripes appear, FIRST check `git diff HEAD -- FootageBackground.tsx`.

## Layered Reel QA (3 gates — every reel passes all three)

The reel pipeline (`execution/run_daily_reels.py`) wires three AI quality gates around the existing render step. All three must pass for a reel to ship.

| Gate | Script | Directive | When it runs | What it catches |
|---|---|---|---|---|
| **0. TopicResearcher** | `execution/research_topic.py` | `directives/research_topic.md` | Before script gen | No real stats / hallucinated numbers — emits `research_brief.json` with sourced stats, pain points, hook angles, CTA deliverable ideas |
| **1. ScriptEvaluator** | `execution/evaluate_reel_script.py` | `directives/evaluate_reel_script.md` | After script gen, before Pexels/ElevenLabs spend | Weak hooks, vague CTAs, low specificity, hallucinated stats not from the brief. 2 auto-retries with critique fed back. Hard-fails before any paid API spend. |
| **2. RealityQA** | `execution/reality_qa_reel.py` | `directives/reality_qa_reel.md` | After render, alongside `review_reel.py` | Clipped captions, off-topic b-roll, missing watermark on a frame, wrong CTA keyword baked into the final frame, decode artifacts (stripes). One auto-rerender on footage-level fail. |

The existing `execution/review_reel.py` (deterministic file-level checks) is unchanged and runs alongside RealityQA. Final `qa_passed = review_passed AND reality_qa_passed`.

Outputs per reel: `<reel_dir>/research_brief.json`, `script_eval.json`, `reality_qa.json`, plus `.qa_frames/` for post-hoc review.

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

Also, use Opus-4.7 for everything while building. It came out a few days ago and is an order of magnitude better than Sonnet and other models. If you can't find it, look it up first.