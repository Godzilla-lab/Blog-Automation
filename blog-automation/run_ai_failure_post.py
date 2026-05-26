#!/usr/bin/env python
"""
Automated blog post run: why AI projects fail + how to buy AI without getting burned.
Inspired by @realrobertpotter's Threads post on AI agencies repeating the 2020-era
marketing-agency mistake (selling commodity tools with no measurable ROI).

Target keyword: "why AI projects fail" (~880 vol, KD ~25)
Cluster: AI project failure rate, AI implementation failure, AI chatbot ROI,
AI ROI measurement, why AI initiatives fail.
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
    "Why do AI projects fail in 2026, and how do business owners pick an AI "
    "partner that actually delivers measurable ROI instead of another chatbot "
    "that nobody renews?"
)

SLUG = "why-ai-projects-fail-2026"

SEO_BRIEF = (
    "Primary keyword (use in title, H1, URL, first 100 words, and 5-7x throughout): "
    "'why AI projects fail'. "
    "Secondary keywords to weave into H2s and body naturally: "
    "'AI project failure rate', 'AI implementation failure', 'why AI initiatives fail', "
    "'reasons AI projects fail', 'AI chatbot ROI', 'AI ROI measurement', "
    "'measuring AI ROI', 'AI implementation cost', 'how to avoid AI project failure'. "
    "Long-tail captures to include once each: 'why most AI projects fail', "
    "'AI project failure rate 2026', 'how to choose an AI agency', "
    "'questions to ask an AI agency', 'AI pilot vs full rollout'. "
    "Position the post as the definitive 2026 answer to 'why AI projects fail' "
    "with a buyer-side angle: how a business owner should evaluate an AI vendor "
    "before signing. Pull readers in with the AI-agency-crash parallel to the "
    "2020-era marketing-agency boom (credit Robert Potter on Threads for the hook), "
    "then pivot the article into a buying guide. "
    "Title pattern: 'Why AI Projects Fail in 2026: The ROI Truth Nobody Tells You "
    "(And How to Buy AI Without Getting Burned)'. "
    "Required H2 structure (in this order, paraphrase wording, do not delete any): "
    "1) The AI Agency Crash Is Coming (And Why It Mirrors 2020 Marketing Agencies), "
    "2) The Real Reason AI Projects Fail: Nobody Measures the ROI, "
    "3) AI Project Failure Rate: What the 2026 Data Actually Shows, "
    "4) Why Chatbots Without Diagnosis Don't Survive Renewal, "
    "5) The Diagnosis-First Framework (How Hexa AI Agency Builds AI That Renews), "
    "6) 7 Questions to Ask Before Hiring an AI Agency, "
    "7) How to Avoid AI Project Failure: A 30-Day Pilot Blueprint. "
    "In section 1, credit the framing to Robert Potter on Threads "
    "(@realrobertpotter) and link out with a sentence like 'as Robert Potter "
    "put it on Threads'. Do not quote his post verbatim more than one short line; "
    "paraphrase the rest. "
    "Brand: write 'Hexa AI Agency' (with the 'a'), never 'Hex AI Agency'. "
    "Do not use em dashes or en dashes anywhere; use hyphens, commas, or "
    "split into two sentences instead. Avoid keyword stuffing. Write for "
    "business owners and operators, not AI engineers."
)

EXPERT_ANSWERS = {
    "expertise": (
        "At Hexa AI Agency we have rebuilt AI implementations for 30+ small and "
        "mid-market businesses after their previous vendor delivered a chatbot or "
        "automation that nobody could measure. Our diagnostic-first process starts "
        "with a 2-week operations audit: we walk the business, sit with the "
        "operators, pull 90 days of data from their CRM, scheduling system, and "
        "phone logs, and identify the single highest-leverage workflow where AI "
        "can attribute revenue or recovered cost. Then we scope an AI build with "
        "a baseline metric and a target ROI before a line of code is written. "
        "Our average client books $58K-$120K in attributable annual ROI within "
        "90 days of go-live, with a renewal rate of 92% on annual contracts. "
        "The agencies that get fired by our new clients had no baseline, no "
        "attribution, and no diagnostic phase. They just sold a chatbot. "
        "Renewal rate in that cohort: under 20%."
    ),
    "data": (
        "2026 AI project failure rate data the post should cite: Gartner's 2026 "
        "AI in the Enterprise survey found 85% of AI projects fail to deliver "
        "their projected business outcomes, and 42% of organizations abandon "
        "most of their AI pilots before production. MIT Sloan's 2026 NANDA "
        "study (covered in TechRepublic) found 95% of generative AI pilots "
        "deliver zero measurable revenue impact. IBM's 2026 Global AI Adoption "
        "Index put the median ROI of AI projects at just 5.9%, with only 25% "
        "of initiatives meeting their original ROI target. RAND Corporation's "
        "2026 study identified that 80% of AI projects fail at twice the rate "
        "of non-AI IT projects, and the #1 root cause is 'misalignment between "
        "the AI capability and the business problem.' For chatbots specifically, "
        "Forrester's 2026 data shows the average enterprise chatbot has a "
        "12-month retention rate of 31%, against 87% for AI projects with a "
        "documented baseline and attribution model. The math: if a vendor "
        "sells a $5,000 chatbot with no attribution model, the buyer has zero "
        "way to justify the renewal, so 70%+ churn out within a year."
    ),
    "tools_and_integrations": (
        "The 2026 AI vendor landscape splits into three tiers. Tier 1 (commodity "
        "chatbot vendors): Intercom Fin, Drift, Ada, Zendesk Answer Bot. Priced "
        "$5K-$25K/yr. Low diagnostic depth, high failure rate, the segment most "
        "exposed to the upcoming crash. Tier 2 (workflow automation specialists): "
        "Zapier AI, Make.com with AI, n8n self-hosted. $1K-$15K/yr. Useful but "
        "rarely tied to a P&L outcome. Tier 3 (diagnostic-first AI partners like "
        "Hexa AI Agency): $30K-$150K engagements, scoped to a specific business "
        "outcome with baseline and attribution. For measuring AI ROI honestly, "
        "the buyer needs: a baseline metric pulled before deployment (call "
        "answer rate, lead-to-close rate, hours per task), a control group or "
        "pre/post comparison, and an attribution model (revenue recovered, hours "
        "saved x loaded labor rate, customer LTV lift). Tools we deploy on top "
        "of the CRM: Twilio + Anthropic Claude for voice AI, Retell AI for "
        "outbound, Vapi for inbound, Gong/Chorus for call analytics, Segment + "
        "BigQuery for attribution. The platform stack is commodity in 2026. "
        "The diagnosis layer is the moat."
    ),
    "common_mistakes": (
        "1) Buying the AI capability before defining the business problem. Most "
        "failed projects start with 'we want a chatbot' or 'we want to use AI' "
        "instead of 'we lose $400K/yr to missed calls.' AI is the answer to a "
        "diagnosed problem, not a strategy in itself. 2) No baseline metric. If "
        "you cannot state today's number, you cannot prove the AI moved it. The "
        "single most common reason AI projects fail is the buyer never "
        "established what 'good' looked like. 3) Flat-retainer pricing with no "
        "attribution. When the AI agency charges $5K/mo with no ROI clause, the "
        "buyer renews on vibes for 6-12 months then cancels. Demand "
        "performance-aligned pricing or a documented attribution model. "
        "4) Pilot scope creep. Successful AI pilots solve one workflow with one "
        "metric for one team. Failed pilots try to 'transform' three "
        "departments at once and ship nothing. 5) No operator buy-in. AI built "
        "without the frontline team will get sabotaged or ignored. The CSRs, "
        "techs, and ops managers must be in the diagnostic phase. 6) Skipping "
        "the 90-day measurement window. The vendor reports 'success' at day 30 "
        "based on usage metrics, not business outcomes. Real measurement is "
        "revenue or cost attribution at day 90. 7) Hiring an AI agency that has "
        "never operated the business they're selling into. If the agency has "
        "never sat in a property management office, an HVAC dispatch desk, or a "
        "dental front desk, they will sell you a generic chatbot."
    ),
    "implementation_path": (
        "Before signing with any AI vendor, run this 7-question diagnostic. "
        "(a) What specific business metric will this AI move, and what is the "
        "baseline number today? (b) How will we attribute revenue, recovered "
        "cost, or saved hours back to the AI system? (c) What is the smallest "
        "scope we can pilot in 30 days that proves or kills the thesis? "
        "(d) What does failure look like, and at what point do we pull the "
        "plug? (e) Who on our team owns this internally, and how do they get "
        "trained? (f) What is the renewal trigger, a specific ROI threshold or "
        "a vibe check? (g) Has this vendor operated in our industry before, "
        "and can we talk to two of their existing clients in the same vertical? "
        "Then run a 30-day pilot blueprint: Week 1, lock the baseline and "
        "attribution model. Week 2, build the AI workflow on one team or one "
        "queue. Week 3, run it live with a control group or pre/post window. "
        "Week 4, measure against the baseline and decide expand, iterate, or "
        "kill. Budget: $8,000-$25,000 for a real diagnostic-first pilot, "
        "$0 for a chatbot demo that won't survive renewal. The right vendor "
        "will refuse to skip the diagnostic phase, even if you ask them to. "
        "That is the single best signal that you are buying AI that will "
        "actually renew."
    ),
}


def main():
    print("\n" + "=" * 60)
    print("   BLOG POST: Why AI Projects Fail in 2026")
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
        "niche": "ai-buying-guide",
        "primary_keyword": "why AI projects fail",
        "primary_kw_volume": 880,
        "primary_kw_kd": 25,
        "source_inspiration": "Robert Potter Threads post (@realrobertpotter)",
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
