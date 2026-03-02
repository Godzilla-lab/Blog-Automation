"""
Claude API Client for Blog Automation
Handles all interactions with the Anthropic Claude API
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self, api_key=None):
        """
        Initialize Claude client

        Args:
            api_key: Optional API key. If not provided, will use ANTHROPIC_API_KEY from .env
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please set it in .env file")

        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')

    def generate_qualifying_questions(self, blog_question):
        """
        Generate 5 qualifying questions to gather context for blog post

        Args:
            blog_question: The main question for the blog post

        Returns:
            List of 5 questions to ask the user
        """
        prompt = f"""I'm writing a blog post for Hex AI Agency (hexaiagency.com) answering this question:

"{blog_question}"

Ask me 5 specific questions you'd need to know the answer to in order to create a truly unique, helpful blog post. The questions should help gather:
- My expertise and experience in this area
- Specific case studies or examples I can share
- Tools or platforms I've worked with
- Unique insights or perspectives I have
- Common challenges I've observed

Keep it limited to exactly 5 questions. Make them specific and actionable.
Output only the questions, numbered 1-5, with no additional commentary."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response to extract questions
        response_text = message.content[0].text
        questions = [q.strip() for q in response_text.split('\n') if q.strip() and any(q.strip().startswith(f"{i}.") for i in range(1, 6))]

        return questions[:5]  # Ensure we only return 5 questions

    def generate_blog_post(self, blog_question, user_answers, template_path):
        """
        Generate complete blog post based on question and user's answers

        Args:
            blog_question: The main question for the blog post
            user_answers: Dictionary of question-answer pairs
            template_path: Path to the blog prompt template

        Returns:
            Generated blog post in markdown format
        """
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Format user answers for prompt
        formatted_answers = "\n\n".join([
            f"**Q: {q}**\nA: {a}" for q, a in user_answers.items()
        ])

        # Create final prompt
        prompt = template.format(
            question=blog_question,
            user_answers=formatted_answers
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def analyze_sitemap_for_links(self, blog_content, sitemap_urls):
        """
        Analyze blog content and suggest internal linking opportunities

        Args:
            blog_content: The generated blog post content
            sitemap_urls: List of URLs from the sitemap

        Returns:
            List of 3 internal linking suggestions with context
        """
        prompt = f"""You are analyzing a blog post for internal linking opportunities.

BLOG CONTENT:
{blog_content[:3000]}... # Truncated for analysis

AVAILABLE URLS FROM SITEMAP:
{chr(10).join(sitemap_urls[:50])}

Find exactly 3 internal linking opportunities where URLs from the sitemap would add value to the blog post. For each suggestion, provide:
1. The URL to link to
2. The anchor text (phrase from the blog to make clickable)
3. Brief explanation of why this link adds value

Format your response as:
1. URL: [url]
   Anchor: [anchor text]
   Reason: [explanation]

2. URL: [url]
   Anchor: [anchor text]
   Reason: [explanation]

3. URL: [url]
   Anchor: [anchor text]
   Reason: [explanation]

Be specific and only suggest links that genuinely enhance the content."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def generate_social_post(self, blog_content, template_path):
        """
        Generate social media post based on blog content and platform template

        Args:
            blog_content: The complete blog post
            template_path: Path to the platform-specific template

        Returns:
            Generated social media post
        """
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Create prompt with blog content
        prompt = template.format(blog_content=blog_content[:2500])  # Truncate to avoid token limits

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text


# Convenience function for easy import
def create_client(api_key=None):
    """Create and return a ClaudeClient instance"""
    return ClaudeClient(api_key=api_key)
