#!/usr/bin/env python
"""
Automated blog post run: HVAC CRM + maintenance contract retention.
Pre-fills expert answers from Hexa AI Agency's HVAC retention playbook.

Target keyword: "HVAC CRM" (590 vol, KD 29)
Cluster total: 4,580 vol, avg KD 20% (Semrush, 2026-05-18)
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
    "How can HVAC contractors use a CRM to retain maintenance contract customers "
    "and stop losing 60% of one-time service customers after the first visit in 2026?"
)

SLUG = "hvac-crm-maintenance-contract-retention"

SEO_BRIEF = (
    "Primary keyword (use in title, H1, URL, first 100 words, and 5-7x throughout): "
    "'HVAC CRM'. "
    "Secondary keywords to weave into H2s and body naturally: "
    "'CRM for HVAC', 'HVAC CRM software', 'CRM software for HVAC companies', "
    "'Best HVAC CRM', 'HVAC CRM app', 'HVAC maintenance contract', "
    "'HVAC customer retention', 'HVAC recurring revenue'. "
    "Long-tail captures to include once each: 'best HVAC CRM software', "
    "'CRM software for HVAC contractors', 'HVAC maintenance plan software', "
    "'HVAC service agreement software'. "
    "Position the post as 'the HVAC CRM angle on maintenance contract retention' "
    "so it does not fight ServiceTitan/Housecall Pro on the head term. "
    "Title pattern: 'HVAC CRM for Maintenance Contract Retention: How to Stop Losing "
    "60% of Customers After One Service Call (2026 Guide)'. "
    "Avoid keyword stuffing. Write for HVAC business owners and service managers. "
    "Do not use em dashes or en dashes; use hyphens or commas instead."
)

EXPERT_ANSWERS = {
    "expertise": (
        "At Hexa AI Agency we build HVAC CRM stacks layered on top of ServiceTitan, "
        "Housecall Pro, FieldEdge, and Jobber, focused specifically on maintenance "
        "contract retention. Our standard build automates four flows: 6-month "
        "maintenance reminders (SMS + email + voice AI), seasonal tune-up booking, "
        "contract renewal sequences 60 days before expiration, and AI churn-risk "
        "scoring based on service history. A typical residential HVAC operator "
        "running 1,500 active customers takes their maintenance contract attach rate "
        "from 22% to 41% within 6 months, lifts recurring revenue from $300K to "
        "$560K/year, and pushes customer lifetime value from $1,800 to $4,200. "
        "ROI math on a 5-truck shop: 19 additional contracts/month x $300 avg annual "
        "value x 12 = $68,400/yr recovered, against $6,000-$10,000/yr in platform "
        "and integration cost. Net $58K+ per location, per year."
    ),
    "data": (
        "Industry benchmarks for 2026: one-time HVAC customer retention rate is "
        "around 40% within 12 months (ACCA 2026 Service Survey), meaning 60% of "
        "one-time customers never come back to you. Maintenance contract customer "
        "retention rate is 87% year over year (Nexstar Network 2026 benchmarks). "
        "Average maintenance contract value: $180-$400/yr per system. Top operators "
        "run 50-70% maintenance contract attach rate; industry average is 22-30%. "
        "LTV of a maintenance contract customer is 4x that of a one-time customer "
        "(Service Roundtable 2026). Cost to acquire a new HVAC customer is $250-$450; "
        "cost to retain an existing one via a maintenance contract is $25-$45/yr. "
        "The biggest churn moment is the 6-month mark after a one-time service call. "
        "Our client data across 22 HVAC operators shows attach rate jumping from 22% "
        "to 41% after deploying AI-driven retention flows on top of their existing "
        "HVAC CRM."
    ),
    "tools_and_integrations": (
        "HVAC CRM and field service platforms in 2026: ServiceTitan ($350+/user/mo, "
        "enterprise-grade, dominant in 5+ truck shops), Housecall Pro ($65-$199/mo, "
        "SMB favorite), FieldEdge ($199+/user/mo, mid-market), Jobber ($69-$249/mo, "
        "lighter weight), Service Fusion ($165+/mo, SMB). The AI layer we build on "
        "top: voice AI for inbound reminder calls (Twilio + Anthropic Claude), "
        "automated SMS reminder sequences (Podium, custom Twilio), AI churn-risk "
        "scoring trained on the operator's last 24 months of service history, "
        "maintenance plan recommendation engine based on system age and customer "
        "value. For pricing the maintenance plans themselves: Profit Rhino, Coolfront. "
        "For reactivation campaigns and reviews: Podium, NiceJob. Setup cost: "
        "$3,000-$10,000 one-time depending on CRM complexity. Ongoing: $300-$800/mo "
        "per location for the AI layer."
    ),
    "common_mistakes": (
        "1) Only selling the maintenance plan at tune-up time. By then it is too "
        "late. The plan needs to be offered on EVERY service call, with AI handling "
        "the follow-up if the customer says 'maybe later.' 2) Generic 'your tune-up "
        "is due' reminders. AI personalization based on system age, last service "
        "history, and seasonal context lifts conversion by 30% over the generic "
        "version. 3) No churn-risk scoring. Most HVAC operators do not know which "
        "customers will leave until they are already gone. AI scores every customer "
        "monthly so you can intervene before they churn. 4) Manual renewal calls "
        "burning out your CSRs. Automation books 60-70% of renewals without a human "
        "touch; CSRs only handle exceptions and high-value accounts. 5) One-size-fits-"
        "all plans. Operators who tier their plans (Silver/Gold/Platinum) based on "
        "system age and customer LTV hit 50%+ attach rates. Single-tier plans cap "
        "attach rate at 25%. 6) Skipping the 6-month touchpoint. The biggest churn "
        "moment is the 6-month gap when the customer forgets you exist. A simple "
        "AI-driven check-in at month 5 recovers 15-20% of the at-risk base."
    ),
    "implementation_path": (
        "Run a 30-day pilot at ONE location before rolling out across the portfolio. "
        "Week 1: baseline your current maintenance contract attach rate, your 12-"
        "month retention rate, and connect API access to your existing HVAC CRM "
        "(ServiceTitan, Housecall Pro, FieldEdge, or Jobber). Week 2-3: build the AI "
        "reminder sequences for 6mo, 9mo, and 11mo touchpoints; train churn-risk "
        "scoring on your last 12 months of customer data; set up plan tiering. "
        "Week 4: launch on your 100 most recent service customers and measure two "
        "metrics: (a) maintenance contract attach rate vs your historical baseline, "
        "(b) booked tune-ups in the first 30 days vs baseline. Day 30-60: roll to "
        "the full customer base, add voice AI for high-value renewal calls and "
        "after-hours service. Day 60-90: layer in commercial maintenance program if "
        "you do commercial. Budget for pilot: $3,000-$10,000 setup, $300-$800/mo "
        "ongoing per location. Most HVAC operators see full payback in 60-90 days "
        "from recovered contract revenue alone."
    ),
}


def main():
    print("\n" + "=" * 60)
    print("   BLOG POST: HVAC CRM + Maintenance Contract Retention")
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
        "niche": "hvac",
        "primary_keyword": "HVAC CRM",
        "primary_kw_volume": 590,
        "primary_kw_kd": 29,
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
