#!/usr/bin/env python
"""
Automated blog post run: AI roofing estimating software + sales cycle compression.
Pre-fills expert answers from Hexa AI Agency's roofing automation playbook.

Target keyword: "roofing estimating software" (480 vol, KD 18)
Secondary: "AI roofing software", "roofing CRM", "roofing sales cycle"
"""

import os

os.environ["CLAUDE_MODEL"] = "claude-opus-4-7"

import json
from datetime import datetime
from pathlib import Path

from modules.claude_client import create_client
from modules.sitemap_analyzer import create_analyzer
from modules.social_generator import create_generator


BLOG_QUESTION = (
    "How does AI roofing estimating software cut roofing sales cycles "
    "from 21 days to 7 days in 2026?"
)

SLUG = "ai-roofing-estimating-software-cut-sales-cycle"

SEO_BRIEF = (
    "Primary keyword (use in title, H1, URL, first 100 words, and 5-7x throughout): "
    "'roofing estimating software'. "
    "Secondary keywords to weave into H2s and body naturally: "
    "'AI roofing estimating software', 'roofing CRM', 'roofing CRM software', "
    "'roofing sales cycle', 'commercial roofing estimating software', "
    "'best roofing estimating software', 'crm software for roofing contractors', "
    "'roofing sales automation'. "
    "Long-tail captures to include once each: 'how to shorten roofing sales cycle', "
    "'AI roofing software', 'roofing proposal automation'. "
    "Avoid keyword stuffing. Write for buyer-stage roofing contractors searching "
    "for software solutions. Title pattern: 'AI Roofing Estimating Software: "
    "How to Cut Your Sales Cycle from 21 to 7 Days (2026 Guide)'. "
    "Do not use em dashes or en dashes; use hyphens or commas instead."
)

EXPERT_ANSWERS = {
    "expertise": (
        "At Hexa AI Agency we build AI estimating and proposal automation stacks "
        "for roofing contractors running AccuLynx, JobNimbus, and Roofr. Our "
        "standard build pulls aerial measurements from EagleView, Hover, or GAF "
        "QuickMeasure, ingests CompanyCam ground photos, runs an AI estimator "
        "against the contractor's material and labor pricing, and ships a signed-"
        "ready proposal with financing options inside 24 hours of the first call. "
        "Typical residential roofer running 40-60 jobs/month compresses their "
        "lead-to-contract cycle from 21 days to 6-7 days. Same crew, same lead "
        "volume, just faster execution. Average client recovers 12-15 deals/year "
        "from being first to quote, worth $120K-$180K in additional revenue. "
        "ROI math on a $9,800 average residential job: 12 recovered closes x "
        "$9,800 = $117,600 against $14,400/yr platform cost. Net $103K per "
        "location, per year."
    ),
    "data": (
        "Roofing-specific 2026 benchmarks: average sales cycle from first call "
        "to signed contract runs 18-25 days for residential, 30-60 days for "
        "commercial (Roofing Contractor 2026 State of the Industry). 78% of "
        "homeowners go with the first roofer to send a written proposal "
        "(InsideAdvisorPro 2026 study). HubSpot's 2026 sales benchmark shows "
        "leads contacted within 5 minutes are 100x more likely to convert than "
        "leads contacted after 30 minutes. GAF reports contractors using AI "
        "measurements close 35% more deals on average. Our client data across "
        "32 roofing operators shows close rate jumps from 22% (manual quoting) "
        "to 41% (AI quoting under 24 hours). Average residential roofing job in "
        "2026: $9,800. Commercial: $42,000+. A 100-call/month operation losing "
        "20% of qualified leads to slow follow-up is leaving $235K/yr on the "
        "table at residential pricing."
    ),
    "tools_and_integrations": (
        "Aerial measurement: EagleView ($30-75/report, gold standard for "
        "insurance), Hover ($25-50, best for sales-stage visuals), GAF "
        "QuickMeasure (free for GAF partners), Roofr (bundled). CRMs/job "
        "management: AccuLynx ($200/user/mo, most popular roofing CRM software), "
        "JobNimbus ($35-150/user/mo, lighter weight), Roofr (all-in-one for "
        "smaller crews), Improveit360 (Salesforce-based for larger operations). "
        "Proposal automation: Roofr proposal builder, Leap, custom AI proposal "
        "generators built on Anthropic Claude or GPT-4. Field photo capture: "
        "CompanyCam ($24-49/user/mo). Voice AI for inbound lead intake: routes "
        "calls to estimator pipeline same-day with full transcript and "
        "qualification data. SMS follow-up: Twilio + custom drip sequences, or "
        "HubSpot/Podium. Insurance jobs: Xactimate integration (separate "
        "workflow). Setup runs $2,000-$8,000 one-time depending on CRM "
        "complexity; ongoing $300-$1,200/mo per location."
    ),
    "common_mistakes": (
        "1) Automating the close instead of the quote. The close still needs a "
        "human; AI's job is to get the quote out fast and accurate. 2) Relying "
        "only on aerial measurements without ground verification photos. You "
        "will miss decking, ventilation, and flashing details and your margin "
        "evaporates on rework. 3) Sending generic proposals. AI personalization "
        "based on neighborhood, material preference, and storm exposure "
        "increases close rate by 15-25%. 4) Mixing storm/insurance jobs into "
        "the same workflow as retail. They have different scopes, different "
        "approval gates, and need their own pipeline. 5) Not integrating the "
        "CRM with the estimating tool. Data silos kill the speed advantage. "
        "Every minute of manual data entry is a minute the competitor's "
        "proposal beats yours to the homeowner's inbox. 6) Skipping SMS "
        "follow-up sequences. 60% of roofing deals close on touch 3 or later. "
        "If you quote once and stop, you lose to the contractor who follows up "
        "five times."
    ),
    "implementation_path": (
        "Run a 30-day pilot on ONE crew before rolling out to the whole "
        "operation. Week 1: audit current sales cycle, lock down API access "
        "for your measurement provider (EagleView or Hover), connect your "
        "CRM (AccuLynx/JobNimbus/Roofr). Week 2-3: build the AI estimate "
        "template, train it on 20 historical jobs to learn your pricing logic, "
        "set guardrails for material costs and labor multipliers. Week 4: "
        "pilot on 10 fresh leads. Measure two metrics: (a) time from first "
        "call to proposal sent (should drop below 24 hours), (b) close rate "
        "vs your historical baseline. Day 30-60: roll to the full sales team, "
        "add SMS follow-up automation, integrate financing partners (GreenSky, "
        "Service Finance). Day 60-90: layer in commercial workflow if you do "
        "commercial, add insurance/storm pipeline if applicable. Budget for "
        "pilot: $3,000-$10,000 setup, $500-$1,500/mo ongoing. Most roofers see "
        "full payback in 60-90 days from recovered deals alone."
    ),
}


def main():
    print("\n" + "=" * 60)
    print("   BLOG POST: AI Roofing Estimating Software")
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

    user_answers["**SEO Targeting Brief (follow these keyword instructions strictly)**"] = SEO_BRIEF

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
        "niche": "roofing",
        "primary_keyword": "roofing estimating software",
        "primary_kw_volume": 480,
        "primary_kw_kd": 18,
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
