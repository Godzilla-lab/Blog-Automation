#!/usr/bin/env python
"""
Automated blog post run: self-storage missed calls + voice agents.
Pre-fills expert answers from the storage-voice-agent lead magnet so we don't
need interactive input.
"""

import os
import json
from datetime import datetime
from pathlib import Path

from modules.claude_client import create_client
from modules.sitemap_analyzer import create_analyzer
from modules.social_generator import create_generator


BLOG_QUESTION = (
    "Why do self-storage facilities lose 25-60% of move-in calls, "
    "and how can AI voice agents fix it in 2026?"
)

SLUG = "why-self-storage-facilities-lose-move-in-calls"

EXPERT_ANSWERS = {
    "expertise": (
        "At Hexa AI Agency we deploy AI voice agents for self-storage operators "
        "running SiteLink, Storable, and storEDGE. Our standard build answers "
        "inbound calls in 2 rings 24/7, quotes a unit by size and climate, "
        "qualifies the lead (move-in date, what's being stored, vehicle/item size), "
        "and books the reservation directly into the PMS with an SMS confirmation. "
        "Typical facility recovers 10+ leases/month that were going to voicemail or "
        "hanging up. ROI math on a 300-unit facility: 10 recovered leases x $160/mo "
        "x 12 = $19,200/yr revenue, against $6,000/yr in platform cost. Net $13,200 "
        "per facility, per year."
    ),
    "data": (
        "The 2026 PCN Answers Small Business Missed Call Revenue Study found SMBs "
        "miss 25-60% of inbound calls depending on staffing and time of day. "
        "Storable's 2026 Self-Storage Industry Outlook flagged Q4 2025 move-in "
        "rates dropping 10.7% YoY to $96.44, with 24% of operators citing staffing "
        "shortages as their #2 concern behind occupancy pressure. Invoca's data "
        "shows 85% of callers who don't reach a live person never call back, and "
        "62% immediately call a competitor. For a typical 300-unit facility with "
        "$160 average monthly rent and 12-month average tenancy, every missed "
        "qualified call is roughly $1,920 in lifetime value walking out the door."
    ),
    "tools_and_integrations": (
        "Easy plug-and-play (1-2 days): SiteLink Web Edition (REST API for unit "
        "lookup and reservation), Storable, storEDGE with partner approval, Twilio "
        "for the phone number/SMS layer. Medium effort (1-2 weeks): PTI EMS or "
        "Sentinel Systems gate integration, HubSpot or Pipedrive for lead logging "
        "if no PMS, Google/Outlook Calendar for tour scheduling. Harder (3-4 weeks): "
        "legacy PMS without APIs - we use RPA or screen scraping. Voice platform "
        "fees run $150-$300/mo entry tier, $300-$600/mo standard (200-800 calls), "
        "$600-$1,200/mo for 800+ calls. Twilio adds $20-$50/mo. Setup is $1,500-$5,000 "
        "one-time depending on PMS complexity."
    ),
    "common_mistakes": (
        "1) Operators try to make the agent close 100% of calls and it sounds robotic. "
        "Our rule: handle 60-70% autonomously, route the rest with full transcript. "
        "2) Skipping handoff triggers. The agent MUST escalate on 'billing problem,' "
        "'charge I don't recognize,' 'lost my key,' 'speak to a manager,' or any "
        "detected anger/distress. 3) No after-hours pilot data. Most facilities "
        "don't realize 30-40% of their lost leads are calling between 6pm-9am when "
        "the office is closed. 4) Bolting voice AI onto a broken sales process. "
        "If your quote-to-book flow is unclear, the agent will fail the same way "
        "your staff does - just faster. 5) Trying to do it all in-house without "
        "PMS API access. Get partner credentials first or you'll waste 3 weeks."
    ),
    "implementation_path": (
        "Pick ONE facility for a 30-day pilot. Don't roll out to the whole portfolio. "
        "Port your main line or use a tracked number on top. Track three metrics: "
        "(a) answer rate - should hit 95%+, (b) book rate on qualified calls, "
        "(c) leads captured after 6pm (your current blind spot). Week 1: integrate "
        "PMS, build call script, set handoff triggers. Week 2: shadow mode - agent "
        "answers but staff verifies bookings. Week 3-4: live, with daily transcript "
        "review. If pilot hits 95% answer rate and books 30%+ of qualified calls, "
        "roll out to the rest of the portfolio. Budget $3K-$8K all-in for the pilot, "
        "$500/mo per facility ongoing. Most operators see payback in 60-90 days."
    ),
}


def main():
    print("\n" + "=" * 60)
    print("   BLOG POST: Self-Storage Missed Calls + Voice AI")
    print("=" * 60 + "\n")

    print(f"Question: {BLOG_QUESTION}\n")

    print("Initializing Claude client...")
    claude = create_client()
    print(f"Connected. Model: {claude.model}\n")

    print("Generating qualifying questions (used for prompt structure)...")
    qualifying_questions = claude.generate_qualifying_questions(BLOG_QUESTION)
    for i, q in enumerate(qualifying_questions, 1):
        print(f"  {i}. {q}")
    print()

    answer_values = list(EXPERT_ANSWERS.values())
    user_answers = {}
    for i, q in enumerate(qualifying_questions):
        user_answers[q] = answer_values[i % len(answer_values)]

    print("Generating blog post...")
    template_path = os.path.join("templates", "blog_prompt.txt")
    blog_content = claude.generate_blog_post(
        BLOG_QUESTION, user_answers, template_path
    )
    print(f"Done. Length: {len(blog_content)} chars\n")

    print("Loading sitemap and analyzing internal links...")
    analyzer = create_analyzer()
    sitemap_urls = []
    if os.path.exists("sitemap.xml"):
        with open("sitemap.xml", "r", encoding="utf-8") as f:
            sitemap_urls = analyzer.parse_sitemap_content(f.read())
        print(f"Parsed {len(sitemap_urls)} URLs")
        link_suggestions = claude.analyze_sitemap_for_links(blog_content, sitemap_urls)
        blog_content += "\n\n---\n## Suggested Internal Links\n\n" + link_suggestions
    else:
        print("sitemap.xml not found, skipping internal links")

    print("\nGenerating social posts...")
    gen = create_generator(claude)
    linkedin = gen.generate_linkedin_post(blog_content)
    twitter = gen.generate_twitter_thread(blog_content)
    threads = gen.generate_threads_post(blog_content)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("output") / f"{date_str}-{SLUG}"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "blog_post.md").write_text(blog_content, encoding="utf-8")
    (output_dir / "linkedin_post.md").write_text(linkedin, encoding="utf-8")
    (output_dir / "twitter_thread.md").write_text(twitter, encoding="utf-8")
    (output_dir / "threads_post.md").write_text(threads, encoding="utf-8")

    metadata = {
        "generated_at": datetime.now().isoformat(),
        "question": BLOG_QUESTION,
        "model": claude.model,
        "website": "hexaaiagency.com",
        "sitemap_urls_count": len(sitemap_urls),
        "blog_length": len(blog_content),
        "niche": "self-storage",
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("\n" + "=" * 60)
    print(f"DONE. Output: {output_dir}")
    print("=" * 60 + "\n")
    print(f"  blog_post.md      ({len(blog_content):,} chars)")
    print(f"  linkedin_post.md  ({len(linkedin):,} chars)")
    print(f"  twitter_thread.md ({len(twitter):,} chars)")
    print(f"  threads_post.md   ({len(threads):,} chars)")
    print(f"  metadata.json")


if __name__ == "__main__":
    main()
