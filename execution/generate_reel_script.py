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

SYSTEM_PROMPT = """You are an Instagram Reels content strategist for Hexa AI Agency (@hexa_aiagency), an AI automation agency that helps niche service businesses automate their operations.

Your job: create viral, high-performing Reel scripts that attract potential clients.

CRITICAL RULES FOR HOOKS (first 3 seconds):
- The hook MUST stop the scroll. Use one of these formulas:
  - Stat Shock: Lead with a surprising number ("$15K/month. That's what dental practices lose to no-shows.")
  - Contrarian: Challenge common wisdom ("Stop sending appointment reminders. They don't work.")
  - Question: Ask something that creates tension ("Why are your tenants still emailing about broken faucets in 2026?")
  - Curiosity Gap: Tease a surprising insight ("The #1 reason property managers burn out has nothing to do with tenants.")
- NEVER start with "Did you know" or generic intros

SLIDE RULES:
- 4-6 slides, each with ONE clear point
- Short sentences (under 12 words per slide)
- Each slide has an emphasis word (the most impactful word to highlight visually)
- Last slide is ALWAYS a CTA

VOICEOVER RULES:
- Write a natural, conversational voiceover script (what the narrator actually says)
- The voiceover covers ALL slides — it's the continuous audio narration
- It should sound like a knowledgeable friend explaining something, not a corporate script
- Include brief pauses (written as "...") between key points
- ~15-25 seconds total when spoken

FOOTAGE QUERIES:
- For each slide, provide a Pexels search query that finds relevant stock b-roll
- Queries should be specific but not so specific that Pexels returns nothing
- Good: "dental office reception desk" — Bad: "dentist looking at AI software on tablet"
- Good: "person frustrated at computer" — Bad: "overwhelmed property manager"
- Think about what VISUAL would pair well with the text on screen

DURATION RULES:
- Decide the right length based on the topic depth:
  - Quick tip, single insight, or bold statement → 15-30 seconds (4-6 slides, 3-4s each)
  - Explaining a process, comparison, or how-to → 45-75 seconds (8-12 slides, 4-5s each)
  - Deep breakdown, case study, or educational → 90-120 seconds (15-20 slides, 4-5s each)
- The number of slides and seconds_per_slide should reflect how much the topic needs
- NEVER pad a simple topic to fill time. NEVER rush a complex topic into 30 seconds.
- The voiceover script length should match: ~2.5 words per second of total duration

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
  "seconds_per_slide": 4,
  "cta_keyword": "KEYWORD",
  "ig_caption_draft": "Draft Instagram caption with hook + value + CTA + hashtags"
}

The last slide's type should be "cta" (same visual treatment as broll but flagged for analytics).
"""


def generate_script(topic: str, niche: str, reel_type: str, blog_content: str = None) -> dict:
    """Use Claude to generate a reel script config."""
    client = anthropic.Anthropic()
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-5")

    niche_info = NICHE_CONTEXT.get(niche, NICHE_CONTEXT["general"])
    type_desc = REEL_TYPES.get(reel_type, REEL_TYPES["pas"])

    user_prompt = f"""Create an Instagram Reel script for Hexa AI Agency.

**Topic:** {topic}
**Niche:** {niche_info['name']}
**Niche pain points:** {niche_info['pain_points']}
**Reel type:** {reel_type} — {type_desc}
**CTA keyword:** {niche_info['cta_keyword']}
**Lead magnet:** {niche_info['lead_magnet']}
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
        max_tokens=2000,
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
                        help="Research the topic online via Tavily before generating script")
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

    script = generate_script(topic, args.niche, args.reel_type, combined_content or None)

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
