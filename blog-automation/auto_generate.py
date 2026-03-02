#!/usr/bin/env python
"""
Automated blog post generation - runs without user input for demo
"""

import os
import json
from datetime import datetime
from pathlib import Path

from modules.claude_client import create_client
from modules.sitemap_analyzer import create_analyzer
from modules.social_generator import create_generator


def main():
    print("\n" + "="*60)
    print("   AUTOMATED BLOG POST GENERATION")
    print("   Demo Mode - No user input required")
    print("="*60 + "\n")

    # Pre-set answers for demo
    blog_question = "What are the best AI tools for business?"

    print(f"📝 Question: {blog_question}\n")

    # Initialize Claude client
    print("🤖 Initializing Claude AI client...")
    try:
        claude = create_client()
        print("✓ Connected to Claude API\n")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return

    # Generate qualifying questions
    print("💭 Generating qualifying questions...\n")
    qualifying_questions = claude.generate_qualifying_questions(blog_question)

    print("Questions generated:")
    for i, q in enumerate(qualifying_questions, 1):
        print(f"  {i}. {q}")

    # Pre-filled answers for demo
    print("\n📝 Using demo answers about Hex AI Agency expertise...\n")
    user_answers = {
        qualifying_questions[0]: "At Hex AI Agency, we've implemented AI solutions across 50+ businesses including ChatGPT for customer service, Anthropic Claude for content generation, and custom AI models for data analysis. Results include 40% reduction in response time and 3x content output.",
        qualifying_questions[1]: "We specialize in AI chatbots (Intercom AI, Drift), CRM automation (HubSpot AI, Salesforce Einstein), marketing tools (Jasper, Copy.ai), and analytics platforms (Tableau AI, Power BI). Each serves different business needs and scales.",
        qualifying_questions[2]: "Common mistakes include: 1) Not training AI on company data, 2) Over-automating customer interactions, 3) Ignoring data quality, 4) Lack of human oversight, 5) Not measuring ROI properly.",
        qualifying_questions[3]: "Small businesses see ROI within 3-6 months typically. Key metrics: time saved (50-70%), cost reduction (30-40%), revenue increase (20-30%). One client saved $50K annually using AI for invoice processing.",
        qualifying_questions[4]: "Start with one high-impact area like customer support or content creation. Use established platforms before custom solutions. Budget $500-2000/month initially. Scale based on results. Always maintain human oversight."
    }

    # Generate blog post
    print("✍️  Generating comprehensive blog post...")
    print("   (This takes 30-60 seconds with Claude API...)\n")

    template_path = os.path.join('templates', 'blog_prompt.txt')
    blog_content = claude.generate_blog_post(blog_question, user_answers, template_path)

    print("✓ Blog post generated!")
    print(f"   Length: {len(blog_content)} characters\n")

    # Load and parse sitemap
    print("🔗 Loading sitemap.xml...")
    analyzer = create_analyzer()

    if os.path.exists('sitemap.xml'):
        with open('sitemap.xml', 'r', encoding='utf-8') as f:
            xml_content = f.read()
        sitemap_urls = analyzer.parse_sitemap_content(xml_content)
        print(f"✓ Parsed {len(sitemap_urls)} URLs from sitemap\n")

        # Analyze for internal links
        print("🔗 Analyzing internal linking opportunities...")
        link_suggestions = claude.analyze_sitemap_for_links(blog_content, sitemap_urls)
        print("✓ Link suggestions generated\n")

        # Add suggestions to blog
        blog_content += "\n\n---\n## Suggested Internal Links\n\n"
        blog_content += link_suggestions
    else:
        print("⚠️  sitemap.xml not found, skipping internal links\n")
        sitemap_urls = []
        link_suggestions = ""

    # Generate social media posts
    print("📱 Generating social media posts...")
    social_generator = create_generator(claude)

    print("  → LinkedIn post...")
    linkedin_post = social_generator.generate_linkedin_post(blog_content)

    print("  → Twitter thread...")
    twitter_thread = social_generator.generate_twitter_thread(blog_content)

    print("  → Threads post...")
    threads_post = social_generator.generate_threads_post(blog_content)

    print("✓ All social media posts generated!\n")

    # Save output
    print("💾 Saving all content...\n")

    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = "what-are-the-best-ai-tools-for-business"
    output_dir = Path('output') / f"{date_str}-{slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all files
    with open(output_dir / 'blog_post.md', 'w', encoding='utf-8') as f:
        f.write(blog_content)

    with open(output_dir / 'linkedin_post.md', 'w', encoding='utf-8') as f:
        f.write(linkedin_post)

    with open(output_dir / 'twitter_thread.md', 'w', encoding='utf-8') as f:
        f.write(twitter_thread)

    with open(output_dir / 'threads_post.md', 'w', encoding='utf-8') as f:
        f.write(threads_post)

    # Save metadata
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'question': blog_question,
        'website': 'hexaiagency.com',
        'sitemap_urls_count': len(sitemap_urls),
        'blog_length': len(blog_content),
        'mode': 'automated_demo'
    }

    with open(output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Display results
    print("\n" + "="*60)
    print("   ✅ GENERATION COMPLETE!")
    print("="*60 + "\n")

    print(f"📁 Output location: {output_dir}\n")

    print("Generated files:")
    print(f"  ✓ blog_post.md ({len(blog_content):,} chars)")
    print(f"  ✓ linkedin_post.md ({len(linkedin_post):,} chars)")
    print(f"  ✓ twitter_thread.md ({len(twitter_thread):,} chars)")
    print(f"  ✓ threads_post.md ({len(threads_post):,} chars)")
    print(f"  ✓ metadata.json")

    print("\n" + "-"*60)
    print("📊 CONTENT PREVIEW")
    print("-"*60 + "\n")

    print("BLOG POST (first 500 chars):")
    print(blog_content[:500] + "...\n")

    print("-"*60)
    print("LINKEDIN POST (first 300 chars):")
    print(linkedin_post[:300] + "...\n")

    print("-"*60)
    print("TWITTER THREAD (first 300 chars):")
    print(twitter_thread[:300] + "...\n")

    print("\n✨ Success! Check the output folder for full content.\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
