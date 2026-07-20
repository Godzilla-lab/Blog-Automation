#!/usr/bin/env python3
"""
Interactive blog post generator.

Walks the operator through:
  1. Picking a question (from questions_bank.json or custom)
  2. Picking a niche
  3. Answering 5 Claude-generated qualifying questions (so the post has real
     first-hand context to ground claims in)
  4. Running the full pipeline (research -> draft -> validate -> evaluate ->
     save) via run_blog_post.generate_one_post

For non-interactive demos, see auto_generate.py.
For niche-specific runs with pre-baked expert answers, see run_*_post.py.
"""

import json
from pathlib import Path

from modules.claude_client import create_client
from run_blog_post import generate_one_post


SCRIPT_DIR = Path(__file__).resolve().parent


def print_banner():
    print("\n" + "=" * 60)
    print("   BLOG POST AUTOMATION SYSTEM")
    print("   Powered by Claude AI | Hexa AI Agency")
    print("=" * 60 + "\n")


def load_questions_bank():
    qb_path = SCRIPT_DIR / "questions_bank.json"
    if not qb_path.exists():
        print("  Warning: questions_bank.json not found. You'll enter a question manually.")
        return []
    with open(qb_path, "r", encoding="utf-8") as f:
        return json.load(f).get("questions", [])


def select_question(questions_bank):
    if not questions_bank:
        return input("\n  Enter the question for your blog post:\n> ").strip()

    print("\n  AVAILABLE QUESTIONS")
    print("-" * 60)
    for i, q in enumerate(questions_bank[:10], 1):
        print(f"{i}. {q['question']}")
    print(f"\n  ... and {len(questions_bank) - 10} more in the bank")
    print("\nOptions:")
    print("  - Enter a number (1-10) to select")
    print("  - 'all' to see all questions")
    print("  - 'custom' to write your own")

    while True:
        choice = input("\nYour choice: ").strip().lower()
        if choice == "all":
            for i, q in enumerate(questions_bank, 1):
                print(f"{i}. {q['question']}")
            continue
        if choice == "custom":
            return input("\n  Enter your custom question:\n> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(questions_bank):
                return questions_bank[idx]["question"]
            print(f"  ! Enter a number between 1 and {len(questions_bank)}")
        else:
            print("  ! Invalid choice. Try again.")


def select_niche():
    options = ["finance", "property-management", "healthcare", "retail", "real-estate", "general"]
    print("\n  NICHE (informs which industry page the post links to)")
    print("-" * 60)
    for i, n in enumerate(options, 1):
        print(f"{i}. {n}")
    while True:
        choice = input("\nNiche number (default 6 = general): ").strip()
        if not choice:
            return "general"
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  ! Invalid choice. Try again.")


def collect_user_answers(claude, blog_question):
    print("\n  Generating 5 qualifying questions ...")
    questions = claude.generate_qualifying_questions(blog_question)

    print("\n" + "=" * 60)
    print("   QUALIFYING QUESTIONS")
    print("   Answer these so the post is grounded in real experience")
    print("=" * 60 + "\n")

    answers = {}
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}/{len(questions)}:\n{q}")
        print("-" * 60)
        answers[q] = input("Your answer:\n> ").strip()
    return answers


def main():
    print_banner()

    questions_bank = load_questions_bank()
    blog_question = select_question(questions_bank)
    print(f"\n  Selected: {blog_question}")

    niche = select_niche()
    print(f"  Niche: {niche}")

    print("\n  Initializing Claude client ...")
    try:
        claude = create_client()
    except ValueError as e:
        print(f"\n  ! {e}")
        print("  Copy .env.example to .env and add your ANTHROPIC_API_KEY.")
        return

    user_answers = collect_user_answers(claude, blog_question)

    result = generate_one_post(
        question=blog_question,
        user_answers=user_answers,
        niche=niche,
    )

    if result.get("success"):
        print("\n  COMPLETE")
        print(f"  Output: {result['output_dir']}")
        print("  Next: open paste_sections.md and copy each section into the admin form fields.")
    else:
        print(f"\n  ! Did not pass all QA gates.")
        print(f"  Reason: {result.get('reason_if_failed')}")
        print(f"  Review {result.get('output_dir')}/draft_eval.json for the failure list.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye.")
    except Exception as e:
        print(f"\n  ! Unexpected error: {e}")
        import traceback
        traceback.print_exc()
