#!/usr/bin/env python3
"""
Generate a complete Instagram Reel config from a topic using Claude.

Takes a topic/trend + niche and outputs a full config.json ready for the render pipeline,
including slide scripts, emphasis words, Pexels search queries, voiceover script, and CTA.

Usage:
    python3 execution/generate_reel_script.py --topic "dental no-shows" --niche dental --type pas
    python3 execution/generate_reel_script.py --topic "AI scheduling" --niche cleaning --type before_after
    python3 execution/generate_reel_script.py --blog blog-automation/output/2026-03-19-why-dental-appointment-reminders-dont-work/blog_post.md --niche dental
    python3 execution/generate_reel_script.py --topic "tenant communication overload" --niche property --output workspace/reels/2026-03-30-tenant/config.json
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed. Run: pip3 install anthropic")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None


REEL_TYPES = {
    "pas": "Problem-Agitation-Solution: Hook with a bold pain point, agitate with stats/examples, offer a shift/solution, end with CTA.",
    "before_after": "Before/After Transformation: Show the painful 'before' state, contrast with the 'after' results, end with CTA.",
    "lead_magnet": "Free Value + CTA: Offer genuinely useful insight, then tell viewers to comment a keyword to get a free resource via DM.",
    "trend": "Trend Reaction / Hot Take: React to something happening in the industry right now with a contrarian or insightful angle.",
}

NICHE_CONTEXT = {
    "dental": {
        "name": "Dental Practices",
        "pain_points": "no-shows, appointment reminders, patient retention, recall systems, front desk overwhelm, insurance billing",
        "cta_keyword": "DENTAL",
        "lead_magnet": "No-Show Cost Calculator",
    },
    "property": {
        "name": "Property Management",
        "pain_points": "tenant communications, maintenance requests, rent collection, vacancy management, scheduling showings",
        "cta_keyword": "PROPERTY",
        "lead_magnet": "Tenant Communication Automation Checklist",
    },
    "cleaning": {
        "name": "Commercial Cleaning",
        "pain_points": "employee scheduling, contract retention, communication gaps, quality control, client onboarding",
        "cta_keyword": "CLEANING",
        "lead_magnet": "Scheduling Efficiency Audit Template",
    },
    "general": {
        "name": "Small/Medium Businesses",
        "pain_points": "manual processes, missed leads, slow follow-up, staff overhead, scaling operations",
        "cta_keyword": "HEXA",
        "lead_magnet": "AI Automation ROI Calculator",
    },
}

SYSTEM_PROMPT = """You are an Instagram Reels writer for Hexa AI Agency (@hexa_aiagency), an AI automation agency that helps service businesses (and broader SMBs) automate operations.

Your job is to write reel scripts that (1) stop the scroll in 1.5s, (2) hold attention through to the end, and (3) convert viewers into commenters who become DM conversations.

==================================================================
THE BEAT STRUCTURE (every reel follows this — non-negotiable)
==================================================================

Every reel has 5 beats, in order. Use this as the spine. Not every beat has to be exactly one slide; longer topics expand the middle beats with multiple slides.

  1. HOOK  (slide 1, ~1.5-3s spoken)
     Stop the scroll. Use one of these — pick the one that fits the topic best:
       - STAT SHOCK: a precise, surprising number ("$47,000. That's what one missed lease renewal costs you.")
       - CONTRARIAN: directly contradict a widely-held belief ("Stop replying to maintenance requests. You're the bottleneck.")
       - CALLOUT: name the viewer's exact situation ("Three months in and your scheduler still can't keep up.")
       - CURIOSITY GAP: tease a payoff you haven't delivered yet ("The cheapest AI use case isn't the one everyone's pushing.")
     NEVER use: "Did you know", "Have you ever wondered", "Let me tell you", any throat-clearing intro.

  2. SETUP / STAKES  (1-2 slides, ~3-5s)
     Why this matters NOW to the viewer. The cost of NOT acting. Be specific: dollars lost, hours wasted, deals missed.

  3. INSIGHT / PIVOT  (1-3 slides, ~5-15s — this is the meat)
     The thing they didn't know. The mechanic. The "actually". Use specifics: tool names, exact steps, real numbers. Avoid jargon-as-substance ("leverage AI to drive synergies" is banned).
     Plant a RETENTION HOOK every ~3s: "But here's the twist...", "And it gets weirder.", "The catch:", a question, a contradicting clause. The brain needs a new reason to stay every 3 seconds.

  4. PAYOFF / WHAT TO DO  (1-2 slides, ~3-6s)
     Give the answer or the next step. Reward the viewer for watching. This is what they post about, screenshot, save.

  5. CTA  (1 slide, ~2-4s)
     Tell them exactly what to do AND what they get for doing it. Format:
       "Comment <KEYWORD> and I'll DM you <SPECIFIC DELIVERABLE>"
     KEYWORD should match the topic, not the niche. Examples: "AUDIT", "SWAP", "TEMPLATE", "BUILD", "SHEET". Pick something that reads like a natural word the viewer would type, not "DENTAL" or "CLEANING".
     The DELIVERABLE must be specific and useful: "the 7-prompt workflow we use", "the no-show recovery template", "the cleaning route optimizer sheet", not "more info" or "a guide".

==================================================================
SLIDE RULES
==================================================================
- One thought per slide. Slide TEXT is what appears on-screen kinetically — keep it punchy (under 10 words, ideally 4-7).
- Slide TEXT and the VOICEOVER are not the same string. The voiceover can be longer and conversational; the slide is the headline of that beat.
- Each slide has one emphasis word — the single word in the slide text that gets highlighted in accent color. Pick the noun or verb that carries the punch ("$15K", "BROKEN", "REPLACE", "FREE").
- The last slide's type must be "cta".

==================================================================
VOICEOVER RULES
==================================================================
- Sound like a competent friend talking to one person. Not corporate. Not "engagement bait" tone. Direct.
- Short sentences. Periods, not commas. Read it aloud, if you need to take a breath mid-sentence, break it.
- Specifics over generics: "$1,500/month" beats "thousands", "12 hours/week" beats "a lot of time", "ServiceTitan" beats "your CRM".
- Pacing: ~2.5 words per second spoken naturally.
- Length: depends on the topic depth (see DURATION RULES below). Do not pad.
- Voiceover and slide text should follow the same beat order so the visual on screen lines up with what's being said.

==================================================================
VOICEOVER PROSODY MARKUP (in voiceover_script ONLY)
==================================================================
The voiceover_script field is delivered through ElevenLabs v3, which honors inline audio tags. Use them to shape delivery so the voice matches the meaning — pauses where a person would pause, loudness where a person would lean in, warmth on the CTA. Tags do NOT appear on screen; slide "text" fields stay 100% clean.

PLACEMENT RULES:
- Tag at the START of a sentence shapes that whole sentence's delivery.
- "[pause]" between sentences creates a beat. Use after stat reveals and before punchlines. Cap at 4 per reel; overuse kills pacing.
- "..." (three dots) creates a shorter natural hesitation than [pause].
- CAPITALIZE one or two words per beat to push volume (e.g. "85 percent of AI projects FAIL"). Use sparingly, ideally on the same word that's the slide's emphasis.
- Match each tag to the BEAT, not every sentence. A typical 30s reel uses 5-8 tags total.

ALLOWED TAGS:
[serious]        — flat, grim weight. Use on damning stats.
[firm]           — assertive but not angry. Use on rebuttals.
[matter-of-fact] — "this is just how it is" energy. Use on data citations.
[deliberate]     — slow, weighted. Use when planting an insight.
[building]       — energy ramping up. Use into the payoff.
[punchy]         — short, sharp. Use on punchlines.
[grounded]       — settled, confident. Use after the punchline.
[warm]           — inviting, friendly. Use on the CTA.
[curious]        — leaning in, asking. Use on questions.
[pause]          — explicit 0.5s beat. Use sparingly between sentences.

EXAMPLE (matches the AI vendor reel):
"voiceover_script": "[serious] If you dropped 5K on AI last year... and you can't tell me what number it moved... [firm] listen up. [matter-of-fact] Gartner says 85 percent of AI projects FAIL. [firm] Not because the tech is broken. [deliberate] Because nobody measures the ROI. No baseline. No attribution. No proof. [building] Forrester data: chatbots with no attribution retain at 31 percent. [pause] With attribution? [punchy] 87. [grounded] Same tech. The measurement is the moat. [warm] Comment VET and I'll DM the 3-question vendor checklist we use at Hexa AI Agency."

CRITICAL: slide "text" fields stay tag-free. The hook slide is "YOU SPENT $5K ON AI. IT'S DEAD." NOT "[serious] YOU SPENT $5K ON AI. IT'S DEAD." Tags are voiceover-only.

==================================================================
FOOTAGE QUERIES (this is critical — most scroll-stops fail here)
==================================================================
Each slide gets a `footage_query` that Pexels will use to find b-roll. The query must depict a SPECIFIC visual scene that matches that slide's text. Get this wrong and the reel looks random.

Rules:
  - Include the SUBJECT and the ACTION ("dentist treating patient", not "dental office")
  - 3-5 words. Concrete nouns. One adjective max.
  - The query should match THIS slide's text, not the general topic of the reel.
  - For CTA slides, use neutral but on-brand imagery: "smiling business owner phone", "person typing laptop close", NOT a cliche handshake.
  - When the slide is about a problem/pain, the query should depict that pain ("frustrated manager messy desk", "stressed receptionist phone calls").
  - When the slide is about the solution/result, the query depicts the calm/clean state ("organized office tablet schedule", "smiling owner free time").

Examples of GOOD vs BAD queries:
  Slide: "$15K/month lost to no-shows"
    GOOD: "empty dental waiting room chairs"
    BAD:  "dental office"
  Slide: "Your VA quit again"
    GOOD: "empty desk laptop closed evening"
    BAD:  "business person frustrated"
  Slide: "AI books patients while you sleep"
    GOOD: "phone screen calendar notifications night"
    BAD:  "ai technology future"
  Slide: "Comment AUDIT and I'll DM you the playbook"
    GOOD: "person typing message phone closeup"
    BAD:  "business handshake"

Banned (these are dead-on-arrival stock cliches): "business handshake", "happy team celebrating", "person at desk", "person on phone", "ai future technology", "abstract data visualization", "businesswoman smiling camera".

DURATION RULES:
- The reel's length is determined entirely by the voiceover. Slides get sized to the words spoken in them; there is no fixed seconds_per_slide. Do not pad.
- Pick the slide count + voiceover length the topic actually needs:
  - Quick tip / bold statement / single insight: ~15-30s of voiceover, 4-6 slides
  - Process / comparison / how-to: ~45-75s of voiceover, 8-12 slides
  - Deep breakdown / case study / educational: ~90-120s of voiceover, 15-20 slides
- NEVER pad a simple topic to fill time. NEVER rush a complex topic into 30 seconds.
- Voiceover pacing: ~2.5 words per second when spoken naturally.

FORMATTING RULES:
- NEVER use em dashes (—) or en dashes (–) anywhere. Use hyphens (-) or commas instead.
- Keep punctuation simple: periods, commas, question marks, exclamation marks only.

OUTPUT FORMAT — respond with ONLY valid JSON, no markdown:
{
  "slides": [
    {
      "text": "slide text shown on screen",
      "emphasis": "one_word",
      "footage_query": "pexels search query",
      "type": "broll"
    }
  ],
  "voiceover_script": "Full voiceover narration as one paragraph",
  "accent_color": "#FFD700",
  "cta_keyword": "KEYWORD",
  "ig_caption_draft": "Draft Instagram caption with hook + value + CTA + hashtags"
}

The last slide's type should be "cta" (same visual treatment as broll but flagged for analytics).
"""


def generate_script(topic: str, niche: str, reel_type: str,
                    blog_content: str = None, research_brief: dict = None,
                    critique: str = None) -> dict:
    """Use Claude to generate a reel script config."""
    client = anthropic.Anthropic()
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

    niche_info = NICHE_CONTEXT.get(niche, NICHE_CONTEXT["general"])
    type_desc = REEL_TYPES.get(reel_type, REEL_TYPES["pas"])

    user_prompt = f"""Create an Instagram Reel script for Hexa AI Agency.

**Topic:** {topic}
**Niche context (use as background, not as a cage):** {niche_info['name']}
**Pain points common in this niche:** {niche_info['pain_points']}
**Reel structure to follow:** {reel_type} — {type_desc}
**Lead magnet you can offer for the CTA (if it fits the topic):** {niche_info['lead_magnet']}

Pick the cta_keyword based on the TOPIC, not the niche. It should read like a natural word a viewer would type ("AUDIT", "SWAP", "TEMPLATE", "PLAYBOOK", "BUILD", etc.) - not a generic niche label.
"""

    if research_brief:
        user_prompt += f"""
**RESEARCH BRIEF (use ONLY these stats and pain points - do NOT invent numbers):**
{json.dumps(research_brief, indent=2)}

Strict rules when using the brief:
- Every number that appears in your voiceover_script and slides must come from `key_stats` in the brief. If a stat would help but isn't in the brief, leave it out.
- The CTA deliverable should match one of the `cta_deliverable_ideas`.
- The hook should follow one of the `recommended_hook_angles`. Do NOT copy `competitor_hook_patterns_seen` verbatim - use them only as negative inspiration (what's been done already).
- When citing a stat in the voiceover, name the source briefly ("ADA reports..." or "Forrester found...") so the claim is anchored.
"""

    if critique:
        user_prompt += f"""
**REVISION INSTRUCTIONS - this is a regeneration attempt. The previous version failed evaluation. Address every point below in this rewrite:**
{critique}
"""

    if blog_content:
        # Truncate blog to ~3000 chars to stay within budget
        truncated = blog_content[:3000]
        user_prompt += f"""
**Source blog post (extract key points from this):**
{truncated}
"""

    response = client.messages.create(
        model=model,
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Parse JSON from response
    text = response.content[0].text.strip()
    # Handle case where Claude wraps in markdown code block
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description="Generate Instagram Reel script with Claude")
    parser.add_argument("--topic", help="Topic or trend to create a reel about")
    parser.add_argument("--blog", help="Path to blog post markdown to repurpose")
    parser.add_argument("--research", action="store_true",
                        help="Research the topic online via Tavily before generating script (legacy quick mode)")
    parser.add_argument("--research-brief", help="Path to research_brief.json from research_topic.py (Agent 0). When set, the generator is constrained to only use stats from this brief.")
    parser.add_argument("--critique", help="Critique text from a prior evaluator pass — used during regeneration retries.")
    parser.add_argument("--niche", default="general",
                        choices=list(NICHE_CONTEXT.keys()),
                        help="Target niche (default: general)")
    parser.add_argument("--type", dest="reel_type", default="pas",
                        choices=list(REEL_TYPES.keys()),
                        help="Reel type/format (default: pas)")
    parser.add_argument("--output", help="Output config.json path")
    args = parser.parse_args()

    if not args.topic and not args.blog:
        print("Error: Provide --topic or --blog")
        sys.exit(1)

    # Determine topic from blog if needed
    topic = args.topic
    blog_content = None
    if args.blog:
        blog_path = os.path.join(project_root, args.blog) if not os.path.isabs(args.blog) else args.blog
        with open(blog_path, "r") as f:
            blog_content = f.read()
        if not topic:
            # Extract topic from first heading
            for line in blog_content.split("\n"):
                if line.startswith("# "):
                    topic = line[2:].strip()
                    break
            if not topic:
                topic = os.path.basename(os.path.dirname(blog_path))

    # Online research if requested
    research_context = None
    if args.research and topic:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            print(f"  Researching topic online: {topic}")
            try:
                resp = requests.post(
                    "https://api.tavily.com/search",
                    json={"api_key": tavily_key, "query": topic, "search_depth": "advanced", "max_results": 5},
                    timeout=20,
                )
                results = resp.json().get("results", [])
                research_context = "\n\n".join(
                    f"**{r['title']}**\n{r.get('content', '')[:500]}" for r in results
                )
                print(f"  Found {len(results)} research sources")
            except Exception as e:
                print(f"  Research failed: {e}")

    print(f"Generating reel script:")
    print(f"  Topic: {topic}")
    print(f"  Niche: {args.niche}")
    print(f"  Type: {args.reel_type}")

    # Combine blog content and research
    combined_content = ""
    if blog_content:
        combined_content += blog_content
    if research_context:
        combined_content += f"\n\n**Online Research:**\n{research_context}"

    # Load research brief (Agent 0 output) if provided — this is the preferred path
    research_brief = None
    if args.research_brief:
        brief_path = os.path.join(project_root, args.research_brief) if not os.path.isabs(args.research_brief) else args.research_brief
        with open(brief_path) as f:
            research_brief = json.load(f)
        print(f"  Using research brief: {brief_path}")
        print(f"    {len(research_brief.get('key_stats', []))} stats, {len(research_brief.get('recommended_hook_angles', []))} hook angles")

    if args.critique:
        print(f"  Regeneration mode: applying critique ({len(args.critique)} chars)")

    script = generate_script(
        topic, args.niche, args.reel_type,
        blog_content=combined_content or None,
        research_brief=research_brief,
        critique=args.critique,
    )

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        from datetime import date
        slug = topic.lower().replace(" ", "-")[:40]
        output_dir = os.path.join(project_root, ".tmp", "reel-scripts")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{date.today().isoformat()}-{slug}.json")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(script, f, indent=2)

    print(f"\n  Output: {output_path}")
    print(f"  Slides: {len(script.get('slides', []))}")
    print(f"\n  Voiceover script:")
    print(f"  {script.get('voiceover_script', '(none)')[:200]}...")
    print(f"\n  CTA keyword: {script.get('cta_keyword', '(none)')}")


if __name__ == "__main__":
    main()
