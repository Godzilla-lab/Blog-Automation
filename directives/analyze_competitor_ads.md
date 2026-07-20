# Analyze Competitor Ads

SOP for pulling live winning ads from Meta and turning them into structured "clone briefs" the user can model new Hexa ads on.

## When to use
- User asks to find winning ads to model in a new niche.
- User asks to research competitors before authoring a new ad.
- Weekly Monday refresh (per `swipe_brief.md` cadence).

## Inputs needed
- A list of Meta Ad Library `ad_id`s (or a search query + min days_active).
- `SCRAPECREATORS_API_KEY` in `.env`.
- `ELEVENLABS_API_KEY` in `.env` (for Scribe transcription).

## Pipeline (3 steps)

### Step 1 — Fetch
```
python3 execution/fetch_competitor_ad.py --ad-id <META_AD_ID>
```
Saves to `.tmp/competitor_ads/<ad_id>/`: `meta.json`, `raw.json`, `creative.mp4` or `creative.jpg`, `cover.jpg`.

Format handling:
- `display_format=VIDEO` → downloads `snapshot.videos[0].video_hd_url`.
- `display_format=IMAGE` → downloads `snapshot.images[0].original_image_url`.
- `display_format=DCO` (Dynamic Creative Optimization, multi-card) → fetcher warns and skips media; manually download from `snapshot.cards[N].video_hd_url`. See `r-burst-spectacle` workflow in `.tmp/competitor_ads/2559024980964576/` for the pattern.

### Step 2 — Stage analysis inputs
```
python3 execution/analyze_competitor_ad.py --ad-id <META_AD_ID>
```
Does NOT call Claude directly. Stages:
- 8 frames extracted at hook-heavy timestamps (0.5s, 1s, 2s, 3s, mid, end-3s, end-1.5s, end-0.3s) into `frames/`.
- ElevenLabs Scribe transcript with word timestamps in `transcript.json`.
- `brief_inputs.json` bundling everything the agent needs.

(Reason for skipping the in-script Claude call: the project's `ANTHROPIC_API_KEY` was revoked at the time of writing. Even after rotation, doing the synthesis in-session lets the agent Read frames directly and produces a stronger analysis than an API round-trip would.)

### Step 3 — Agent synthesis (in-session)
The agent (Claude in this session) Reads:
1. `.tmp/competitor_ads/<ad_id>/meta.json` (context)
2. `transcript.json` (full spoken VO with timestamps)
3. Every file in `frames/` via the Read tool (multimodal vision)

Then writes `analysis.json` with the schema documented in the `SYSTEM_PROMPT` constant inside `execution/analyze_competitor_ad.py`. Key fields: `hook_first_3s`, `hook_archetype`, `structure_beats`, `cta`, `pacing`, `proof_elements`, `visual_style`, `restyle_ideas_for_hexa`, `clone_template_for_hexa`.

After analyzing 3+ ads, write `swipe_brief.md` summarizing cross-ad patterns: shared hook structures, what every winner did/didn't do, restyle priorities.

## Output → Hexa ad config
Each new madebyhexa-ads concept folder must include a top-level `_modeled_after` field:
```
"_modeled_after": {
  "ad_id": "1110229847960703",
  "page_name": "Arcads AI",
  "days_active": 259,
  "library_url": "https://www.facebook.com/ads/library/?id=1110229847960703",
  "archetype": "realism-reveal",
  "analyzed_on": "2026-06-18"
}
```
This is the swipe-file → pipeline link. If a config has no `_modeled_after`, it was authored from intuition (acceptable but not the default).

## Verification
1. After fetch: `creative.mp4`/`.jpg` plays in QT.
2. After stage: 4-8 frames in `frames/`, transcript text non-empty.
3. After synthesis: agent has personally Read each frame.jpg + transcript before writing analysis.json. Per `feedback_always_run_qa_agents.md`, never claim "done" without doing this.
4. After config draft: render the Hexa ad and Read its thumb to confirm the cloned visual pattern actually transferred.

## Cost
- ScrapeCreators: 1 credit per ad fetch (~$0.01).
- ElevenLabs Scribe: ~$0.40/hour of audio.
- Total for a 5-ad sweep: <$1.

## Gotchas
- ffprobe is not installed on this box; `analyze_competitor_ad.py:probe_duration()` parses Duration from `ffmpeg -i` stderr.
- Captions/Tyler-style 12+ minute long-form VSLs do not transfer to 15-30s Hexa ads — only the HOOK is cloneable, not the body. Always check `meta.json:duration_s` (via probe) before committing to clone the full structure.
- Burst Creatine type DCO ads need manual card download (see Step 1).
- Long-running winners often have multiple variants on the same page. Always check `view_all_page_id=` URL after fetching to see if a short-form sibling exists for a long-form pull.
