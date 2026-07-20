"""
Claude API Client for Blog Automation
Handles all interactions with the Anthropic Claude API
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please set it in .env file")

        self.client = Anthropic(api_key=self.api_key)
        # Project default is Opus 4.7 per CLAUDE.md
        self.model = os.getenv('CLAUDE_MODEL', 'claude-opus-4-7')

    def generate_qualifying_questions(self, blog_question):
        """Generate 5 qualifying questions to gather operator context."""
        prompt = f"""I'm writing a blog post for Hexa AI Agency (hexaaiagency.com) answering this question:

"{blog_question}"

Ask me 5 specific questions you'd need to know the answer to in order to create a truly unique, helpful blog post. The questions should help gather:
- My expertise and experience in this area
- Specific case studies or examples I can share
- Tools or platforms I've worked with
- Unique insights or perspectives I have
- Common challenges I've observed

Keep it to exactly 5 questions. Make them specific and actionable.
Output only the questions, numbered 1-5, with no additional commentary."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        questions = [
            q.strip() for q in response_text.split('\n')
            if q.strip() and any(q.strip().startswith(f"{i}.") for i in range(1, 6))
        ]
        return questions[:5]

    def generate_blog_post(self, blog_question, user_answers, niche, research_brief,
                           hexa_urls, template_path, critique=None):
        """
        Generate complete blog post grounded in:
          - operator first-hand answers
          - the research brief (sourced stats)
          - the allowlist of internal URLs
          - optional critique from a prior failed validation pass

        Returns: raw model output (the 8-section format from blog_prompt.txt).
        Caller is responsible for parsing into TITLE/SLUG/EXCERPT/BODY/etc.
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        formatted_answers = "\n\n".join(
            f"**Q: {q}**\nA: {a}" for q, a in user_answers.items()
        )

        critique_block = ""
        if critique:
            critique_block = (
                "================================================================================\n"
                "REGENERATION CRITIQUE (the previous draft failed - fix every item before returning)\n"
                "================================================================================\n\n"
                + critique
                + "\n"
            )

        prompt = template.format(
            question=blog_question,
            niche=niche or "general",
            user_answers=formatted_answers,
            research_brief=json.dumps(research_brief, indent=2),
            hexa_urls=json.dumps(hexa_urls, indent=2),
            critique_block=critique_block,
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def generate_social_post(self, blog_content, template_path):
        """Generate social media post from blog body + a platform-specific template."""
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        prompt = template.format(blog_content=blog_content[:2500])

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


def create_client(api_key=None):
    """Create and return a ClaudeClient instance"""
    return ClaudeClient(api_key=api_key)
