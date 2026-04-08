#!/usr/bin/env python3
"""
Generate an Instagram caption (post text) for a Reel from its config.

Reads the reel config.json and generates an engaging caption with:
- Hook line (first line visible before "...more")
- Value summary
- CTA with keyword trigger
- Relevant hashtags

Usage:
    python3 execution/generate_ig_caption.py --config workspace/reels/2026-03-30-dental/config.json
    python3 execution/generate_ig_caption.py --config config.json --output caption.txt
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed. Run: pip3 install anthropic")
    sys.exit(1)

SYSTEM_PROMPT = """You are an Instagram caption writer for Hexa AI Agency (@hexa_aiagency), an AI automation agency.

Write a caption for an Instagram Reel. The caption should:

1. FIRST LINE (most important - this is all people see before tapping "...more"):
   - Bold hook that makes people want to read more
   - Under 125 characters so it doesn't get cut off

2. BODY (2-4 short lines):
   - Expand on the value from the reel
   - Use line breaks for readability
   - Include 1-2 relevant emojis max (not excessive)

3. CTA (call to action):
   - If a keyword trigger is provided: "Comment [KEYWORD] and I'll DM you [lead magnet]"
   - Always include: "Follow @hexa_aiagency for more"
   - Optional: "Save this for later" or "Share with someone who needs this"

4. HASHTAGS (on a separate line, 15-25 relevant hashtags):
   - Mix of broad (#aiautomation #businessgrowth) and niche-specific
   - Include the niche hashtag (#dentalpractice, #propertymanagement, etc.)
   - No spaces between hashtags, just space-separated

IMPORTANT: Never use em dashes (—) or en dashes (–). Use hyphens (-) or commas instead.

Output the caption as plain text, ready to paste into Instagram. No JSON wrapper."""


def generate_caption(config: dict) -> str:
    """Generate Instagram caption from reel config."""
    client = anthropic.Anthropic()
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-5")

    # If config already has a draft caption, use it as starting point
    draft = config.get("ig_caption_draft", "")

    slides_text = "\n".join(
        f"- Slide {i+1}: {s['text']}" for i, s in enumerate(config.get("slides", []))
    )

    user_prompt = f"""Write an Instagram caption for this Reel:

**Slide content:**
{slides_text}

**Voiceover:** {config.get('voiceover_script', '(no voiceover)')}

**CTA keyword:** {config.get('cta_keyword', '')}
**Lead magnet:** {config.get('lead_magnet', '')}

**Niche:** {config.get('niche', 'AI automation for businesses')}
"""

    if draft:
        user_prompt += f"\n**Draft caption to improve:** {draft}"

    response = client.messages.create(
        model=model,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return response.content[0].text.strip()


def main():
    parser = argparse.ArgumentParser(description="Generate Instagram caption for a Reel")
    parser.add_argument("--config", required=True, help="Path to reel config.json")
    parser.add_argument("--output", help="Output caption.txt path (default: next to config)")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)

    print("Generating Instagram caption...")
    caption = generate_caption(config)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        config_dir = os.path.dirname(os.path.abspath(args.config))
        output_path = os.path.join(config_dir, "caption.txt")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(caption)

    print(f"  Saved to: {output_path}")
    print(f"\n--- Caption Preview ---")
    print(caption[:500])
    if len(caption) > 500:
        print("...")


if __name__ == "__main__":
    main()
