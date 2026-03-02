"""
Social Media Post Generator
Handles generation of platform-optimized social media content
"""

import os
from modules.claude_client import ClaudeClient


class SocialGenerator:
    """Generate optimized posts for different social media platforms"""

    def __init__(self, claude_client=None):
        """
        Initialize social media generator

        Args:
            claude_client: Optional ClaudeClient instance. If not provided, creates new one.
        """
        self.claude = claude_client or ClaudeClient()
        self.templates_dir = "templates"

    def generate_linkedin_post(self, blog_content):
        """
        Generate LinkedIn-optimized post

        Args:
            blog_content: The full blog post content

        Returns:
            LinkedIn post (1300-1900 characters, professional tone)
        """
        template_path = os.path.join(self.templates_dir, "linkedin_prompt.txt")
        return self.claude.generate_social_post(blog_content, template_path)

    def generate_twitter_thread(self, blog_content):
        """
        Generate Twitter/X thread

        Args:
            blog_content: The full blog post content

        Returns:
            Twitter thread (4-6 tweets, 200-280 chars each)
        """
        template_path = os.path.join(self.templates_dir, "twitter_prompt.txt")
        return self.claude.generate_social_post(blog_content, template_path)

    def generate_threads_post(self, blog_content):
        """
        Generate Threads post

        Args:
            blog_content: The full blog post content

        Returns:
            Threads post (300-500 characters, casual tone)
        """
        template_path = os.path.join(self.templates_dir, "threads_prompt.txt")
        return self.claude.generate_social_post(blog_content, template_path)

    def generate_all_posts(self, blog_content):
        """
        Generate posts for all platforms at once

        Args:
            blog_content: The full blog post content

        Returns:
            Dictionary with posts for each platform
        """
        print("\n📱 Generating social media posts...")

        posts = {}

        print("  → LinkedIn post...")
        posts['linkedin'] = self.generate_linkedin_post(blog_content)

        print("  → Twitter thread...")
        posts['twitter'] = self.generate_twitter_thread(blog_content)

        print("  → Threads post...")
        posts['threads'] = self.generate_threads_post(blog_content)

        print("✓ All social media posts generated!\n")

        return posts

    def format_post_preview(self, platform, content, max_length=200):
        """
        Format a preview of the post for console display

        Args:
            platform: Name of the platform
            content: Post content
            max_length: Maximum length for preview

        Returns:
            Formatted preview string
        """
        preview = content[:max_length]
        if len(content) > max_length:
            preview += "..."

        return f"\n{platform.upper()}:\n{'-' * 40}\n{preview}\n{'-' * 40}\n"


def create_generator(claude_client=None):
    """Create and return a SocialGenerator instance"""
    return SocialGenerator(claude_client=claude_client)
