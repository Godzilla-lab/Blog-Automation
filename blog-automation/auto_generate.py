#!/usr/bin/env python3
"""
Non-interactive blog post generator (demo / smoke test).

Uses a pre-set question + pre-filled operator answers so the new pipeline can
be exercised end-to-end without typing. Useful for:
  - Verifying the orchestrator wiring after a change
  - Smoke-testing API keys
  - Running a deterministic CI check

For real interactive use, see main.py.
"""

from modules.claude_client import create_client
from run_blog_post import generate_one_post


BLOG_QUESTION = "What are the best AI tools for business in 2026?"
NICHE = "general"

# Pre-filled operator answers (the 5 questions Claude would ask interactively).
# These ground the post in plausible first-hand context.
USER_ANSWERS = {
    "What is your direct experience with AI tools for businesses?": (
        "At Hexa AI Agency we've implemented AI stacks for 50+ small-to-mid service "
        "businesses since early 2025. Common builds: Claude for support triage, "
        "HubSpot Workflows for CRM automation, Make.com for cross-tool orchestration, "
        "and Twilio + Anthropic for AI voice agents."
    ),
    "Which specific tools or platforms have you worked with most?": (
        "Heavily: Claude (Opus 4.7 and Sonnet 4.6), GPT-4, HubSpot AI features, "
        "Salesforce Einstein, Pipedrive, Make.com, Zapier, n8n, Twilio, Anthropic API. "
        "Lighter touch: Jasper, Copy.ai, Tableau AI, Power BI."
    ),
    "What are the most common mistakes you see businesses make?": (
        "1) Buying tools before defining the problem; 2) Over-automating customer-facing "
        "interactions; 3) Skipping a baseline metric so ROI is unprovable; 4) No human "
        "in the loop on high-stakes decisions; 5) Treating AI as a one-time setup vs "
        "an ongoing workflow."
    ),
    "What ROI numbers have you seen?": (
        "Typical pattern: 3-6 month payback for $50K-$100K of annualized savings on "
        "a $5K-$15K build. One AP automation client cut invoice processing time from "
        "47 minutes per bill to 8 minutes, recovering ~22 hours of finance team time "
        "per week."
    ),
    "What would you recommend a business owner do first?": (
        "Pick one high-cost, repetitive workflow (intake, AP, support triage, follow-up). "
        "Document today's baseline metric. Build the simplest version possible against "
        "existing tools (HubSpot Workflows + Claude API beats a custom platform). "
        "Run for 60 days. Measure. Iterate."
    ),
}


def main():
    print("\n" + "=" * 60)
    print("   AUTOMATED BLOG POST GENERATION (demo mode)")
    print("=" * 60 + "\n")

    print(f"  Question: {BLOG_QUESTION}")
    print(f"  Niche: {NICHE}")

    print("\n  Initializing Claude client ...")
    try:
        create_client()  # validate API key presence
    except ValueError as e:
        print(f"  ! {e}")
        return

    result = generate_one_post(
        question=BLOG_QUESTION,
        user_answers=USER_ANSWERS,
        niche=NICHE,
    )

    if result.get("success"):
        print(f"\n  COMPLETE -> {result['output_dir']}")
    else:
        print(f"\n  ! QA did not pass: {result.get('reason_if_failed')}")
        print(f"  Review {result.get('output_dir')}/draft_eval.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  ! Error: {e}")
        import traceback
        traceback.print_exc()
