#!/usr/bin/env python3
"""
Blog Post Automation System
Main orchestration script for generating blog posts and social media content
"""

import os
import json
from datetime import datetime
from pathlib import Path

from modules.claude_client import create_client
from modules.sitemap_analyzer import create_analyzer
from modules.social_generator import create_generator


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print("   BLOG POST AUTOMATION SYSTEM")
    print("   Powered by Claude AI | Hex AI Agency")
    print("="*60 + "\n")


def load_questions_bank():
    """Load questions from questions_bank.json"""
    try:
        with open('questions_bank.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['questions']
    except FileNotFoundError:
        print("⚠️  Warning: questions_bank.json not found. You'll need to enter questions manually.")
        return []


def select_question(questions_bank):
    """
    Let user select a question from the bank or enter custom

    Args:
        questions_bank: List of question dictionaries

    Returns:
        Selected question string
    """
    if not questions_bank:
        return input("\n📝 Enter the question for your blog post:\n> ")

    print("\n📋 AVAILABLE QUESTIONS")
    print("-" * 60)

    # Show first 10 questions
    for i, q in enumerate(questions_bank[:10], 1):
        print(f"{i}. {q['question']}")

    print(f"\n... and {len(questions_bank) - 10} more questions in the bank")
    print("\nOptions:")
    print("  • Enter a number (1-10) to select from above")
    print("  • Enter 'all' to see all questions")
    print("  • Enter 'custom' to write your own question")

    while True:
        choice = input("\nYour choice: ").strip().lower()

        if choice == 'all':
            print("\n📋 ALL QUESTIONS")
            print("-" * 60)
            for i, q in enumerate(questions_bank, 1):
                print(f"{i}. {q['question']}")
            print()
            continue

        elif choice == 'custom':
            return input("\n📝 Enter your custom question:\n> ")

        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(questions_bank):
                return questions_bank[idx]['question']
            else:
                print(f"❌ Please enter a number between 1 and {len(questions_bank)}")

        else:
            print("❌ Invalid choice. Please try again.")


def collect_user_answers(questions):
    """
    Collect answers to qualifying questions from user

    Args:
        questions: List of questions to ask

    Returns:
        Dictionary mapping questions to answers
    """
    print("\n" + "="*60)
    print("   QUALIFYING QUESTIONS")
    print("   Answer these to personalize your blog post")
    print("="*60 + "\n")

    answers = {}
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}/{len(questions)}:")
        print(f"{question}")
        print("-" * 60)
        answer = input("Your answer:\n> ")
        answers[question] = answer

    return answers


def get_sitemap_content():
    """
    Get sitemap content from user (paste or URL)

    Returns:
        Tuple of (sitemap_analyzer, list of URLs)
    """
    print("\n" + "="*60)
    print("   SITEMAP CONFIGURATION")
    print("="*60 + "\n")

    analyzer = create_analyzer()

    print("How would you like to provide your sitemap?")
    print("  1. Use sitemap.xml file in current directory")
    print("  2. Paste XML content directly")
    print("  3. Provide sitemap URL")
    print("  4. Skip sitemap (no internal linking)")

    choice = input("\nYour choice (1-4): ").strip()

    if choice == '1':
        # Read from sitemap.xml file
        if os.path.exists('sitemap.xml'):
            print("\n📄 Reading sitemap.xml...")
            with open('sitemap.xml', 'r', encoding='utf-8') as f:
                xml_content = f.read()
            urls = analyzer.parse_sitemap_content(xml_content)
            print(f"✓ Parsed {len(urls)} URLs from sitemap.xml")
            return analyzer, urls
        else:
            print("\n❌ sitemap.xml not found in current directory")
            print("   Continuing without internal linking...")
            return analyzer, []

    elif choice == '2':
        print("\n📋 Paste your sitemap XML content below.")
        print("   (Paste content and press Enter, then Ctrl+D or Ctrl+Z+Enter when done)")
        print("-" * 60)

        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        xml_content = '\n'.join(lines)
        urls = analyzer.parse_sitemap_content(xml_content)
        print(f"\n✓ Parsed {len(urls)} URLs from sitemap")
        return analyzer, urls

    elif choice == '3':
        sitemap_url = input("\n🔗 Enter sitemap URL (e.g., https://hexaaiagency.com/sitemap.xml):\n> ")
        try:
            urls = analyzer.parse_sitemap_from_url(sitemap_url)
            print(f"\n✓ Fetched {len(urls)} URLs from sitemap")
            return analyzer, urls
        except Exception as e:
            print(f"\n❌ Error fetching sitemap: {e}")
            print("   Continuing without internal linking...")
            return analyzer, []

    else:
        print("\n⏭️  Skipping sitemap configuration")
        return analyzer, []


def add_internal_links(blog_content, link_suggestions):
    """
    Display link suggestions and allow user to confirm

    Args:
        blog_content: The blog post content
        link_suggestions: AI-generated link suggestions

    Returns:
        Blog content with internal links added (if confirmed)
    """
    print("\n" + "="*60)
    print("   INTERNAL LINKING SUGGESTIONS")
    print("="*60 + "\n")

    print(link_suggestions)

    confirm = input("\n Would you like to add these links to your blog post? (y/n): ").strip().lower()

    if confirm == 'y':
        # In a production version, we'd parse the suggestions and add them
        # For now, we'll append them as a note
        blog_content += "\n\n---\n## Suggested Internal Links\n\n"
        blog_content += link_suggestions
        print("\n✓ Link suggestions added to blog post")

    return blog_content


def save_output(blog_question, blog_content, social_posts, metadata):
    """
    Save all generated content to organized files

    Args:
        blog_question: The question being answered
        blog_content: Generated blog post
        social_posts: Dictionary of social media posts
        metadata: Additional metadata to save

    Returns:
        Path to output directory
    """
    # Create output directory with date and slug
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = blog_question.lower()[:50].replace(' ', '-').replace('?', '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')

    output_dir = Path('output') / f"{date_str}-{slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save blog post
    with open(output_dir / 'blog_post.md', 'w', encoding='utf-8') as f:
        f.write(blog_content)

    # Save social posts
    with open(output_dir / 'linkedin_post.md', 'w', encoding='utf-8') as f:
        f.write(social_posts.get('linkedin', ''))

    with open(output_dir / 'twitter_thread.md', 'w', encoding='utf-8') as f:
        f.write(social_posts.get('twitter', ''))

    with open(output_dir / 'threads_post.md', 'w', encoding='utf-8') as f:
        f.write(social_posts.get('threads', ''))

    # Save metadata
    metadata['generated_at'] = datetime.now().isoformat()
    metadata['question'] = blog_question
    with open(output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    return output_dir


def main():
    """Main workflow orchestration"""
    print_banner()

    # Load questions bank
    questions_bank = load_questions_bank()

    # Step 1: Select question
    blog_question = select_question(questions_bank)
    print(f"\n✓ Selected question: {blog_question}\n")

    # Step 2: Initialize Claude client
    print("🤖 Initializing Claude AI client...")
    try:
        claude = create_client()
        print("✓ Connected to Claude API\n")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your ANTHROPIC_API_KEY to .env")
        print("  3. Run the script again\n")
        return

    # Step 3: Generate qualifying questions
    print("💭 Generating qualifying questions...\n")
    qualifying_questions = claude.generate_qualifying_questions(blog_question)

    # Step 4: Collect user answers
    user_answers = collect_user_answers(qualifying_questions)

    # Step 5: Generate blog post
    print("\n" + "="*60)
    print("   GENERATING BLOG POST")
    print("="*60 + "\n")
    print("✍️  Claude is writing your blog post...")
    print("   (This may take 30-60 seconds)")

    template_path = os.path.join('templates', 'blog_prompt.txt')
    blog_content = claude.generate_blog_post(blog_question, user_answers, template_path)
    print("\n✓ Blog post generated!\n")

    # Step 6: Sitemap and internal linking
    analyzer, sitemap_urls = get_sitemap_content()

    if sitemap_urls:
        print("\n🔗 Analyzing internal linking opportunities...")
        link_suggestions = claude.analyze_sitemap_for_links(blog_content, sitemap_urls)
        blog_content = add_internal_links(blog_content, link_suggestions)

    # Step 7: Generate social media posts
    social_generator = create_generator(claude)
    social_posts = social_generator.generate_all_posts(blog_content)

    # Step 8: Save everything
    print("\n" + "="*60)
    print("   SAVING OUTPUT")
    print("="*60 + "\n")

    metadata = {
        'website': 'hexaiagency.com',
        'sitemap_urls_count': len(sitemap_urls) if sitemap_urls else 0
    }

    output_dir = save_output(blog_question, blog_content, social_posts, metadata)

    # Step 9: Summary
    print("\n" + "="*60)
    print("   ✅ COMPLETE!")
    print("="*60 + "\n")

    print(f"📁 All files saved to: {output_dir}\n")
    print("Generated files:")
    print(f"  ✓ {output_dir / 'blog_post.md'}")
    print(f"  ✓ {output_dir / 'linkedin_post.md'}")
    print(f"  ✓ {output_dir / 'twitter_thread.md'}")
    print(f"  ✓ {output_dir / 'threads_post.md'}")
    print(f"  ✓ {output_dir / 'metadata.json'}")

    print("\n📝 Next steps:")
    print("  • Review and edit the blog post")
    print("  • Copy social posts to your scheduling tool")
    print("  • Publish and promote!\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.\n")
