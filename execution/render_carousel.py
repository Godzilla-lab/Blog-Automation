#!/usr/bin/env python3
"""
Thread-to-Carousel Renderer
Generates Instagram carousel slides (1080x1350) from a config.json.
Each slide renders tweet cards with profile pic, name, handle, and text.
"""

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

# --- Constants ---
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350
PADDING_X = 70
CONTENT_WIDTH = CANVAS_WIDTH - (PADDING_X * 2)  # 940px

# Profile row dimensions
AVATAR_SIZE = 80
AVATAR_GAP = 16
BADGE_SIZE = 28
NAME_BADGE_GAP = 6
BADGE_HANDLE_GAP = 8

# Spacing
PROFILE_TEXT_GAP = 24  # gap between profile row and tweet text
TWEET_IMAGE_GAP = 24   # gap between tweet text and embedded image
DIVIDER_PADDING = 40    # vertical padding around divider for dual-tweet slides
IMAGE_CORNER_RADIUS = 20

# Theme definitions
THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "text": "#0F1419",
        "secondary": "#536471",
        "divider": "#CFD9DE",
        "badge_bg": "#1D9BF0",
        "badge_check": "#FFFFFF",
    },
    "dark": {
        "bg": "#000000",
        "text": "#E7E9EA",
        "secondary": "#71767B",
        "divider": "#2F3336",
        "badge_bg": "#1D9BF0",
        "badge_check": "#FFFFFF",
    },
}

# Font paths (macOS)
FONT_PATHS = {
    "regular": [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "bold": [
        ("/System/Library/Fonts/HelveticaNeue.ttc", 1),  # index 1 = Bold
        "/System/Library/Fonts/SFNS.ttf",
    ],
}


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def load_font(style, size):
    """Load a font with fallbacks."""
    paths = FONT_PATHS.get(style, FONT_PATHS["regular"])
    for entry in paths:
        try:
            if isinstance(entry, tuple):
                path, index = entry
                return ImageFont.truetype(path, size, index=index)
            else:
                return ImageFont.truetype(entry, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def load_fonts():
    """Load all font variants needed for rendering."""
    return {
        "name": load_font("bold", 30),
        "handle": load_font("regular", 26),
        "text": load_font("regular", 30),
    }


def create_circular_mask(size):
    """Create a circular alpha mask."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def load_headshot(path, size=AVATAR_SIZE):
    """Load and crop headshot to a circle."""
    if not path or not os.path.exists(path):
        # Create a gray placeholder circle
        img = Image.new("RGBA", (size, size), (200, 200, 200, 255))
        mask = create_circular_mask(size)
        img.putalpha(mask)
        return img

    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    mask = create_circular_mask(size)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    return output


def draw_verified_badge(draw, x, y, size, theme):
    """Draw a blue verified checkmark badge."""
    colors = THEMES[theme]
    bg = hex_to_rgb(colors["badge_bg"])
    check = hex_to_rgb(colors["badge_check"])

    # Blue circle
    draw.ellipse((x, y, x + size, y + size), fill=bg)

    # White checkmark (simplified)
    cx, cy = x + size // 2, y + size // 2
    s = size / 18  # scale factor
    points = [
        (cx - 4 * s, cy),
        (cx - 1.5 * s, cy + 3.5 * s),
        (cx + 4.5 * s, cy - 3 * s),
    ]
    draw.line(points, fill=check, width=max(2, int(2.2 * s)))


def round_corners(image, radius):
    """Apply rounded corners to an image."""
    mask = Image.new("L", image.size, 255)
    draw = ImageDraw.Draw(mask)
    w, h = image.size

    # Draw black corners, then invert approach:
    # Actually, draw a rounded rect on the mask
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)

    output = image.copy()
    output.putalpha(mask)
    return output


def word_wrap_text(text, font, max_width, draw_obj):
    """Wrap text to fit within max_width, respecting explicit \\n breaks."""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        # Use textwrap as a rough guide, then verify with font metrics
        avg_char_width = font.getlength("M")
        chars_per_line = max(1, int(max_width / avg_char_width * 1.6))
        wrapped = textwrap.wrap(paragraph, width=chars_per_line)

        # Refine: split lines that are still too wide
        for line in wrapped:
            while font.getlength(line) > max_width and len(line) > 1:
                # Find last space that fits
                split_at = len(line)
                for i in range(len(line) - 1, 0, -1):
                    if line[i] == " " and font.getlength(line[:i]) <= max_width:
                        split_at = i
                        break
                if split_at == len(line):
                    # No space found, force break
                    for i in range(len(line) - 1, 0, -1):
                        if font.getlength(line[:i]) <= max_width:
                            split_at = i
                            break
                lines.append(line[:split_at].rstrip())
                line = line[split_at:].lstrip()
            if line:
                lines.append(line)

    return lines


def measure_text_height(lines, font, line_spacing=1.4):
    """Measure total height of wrapped text lines."""
    if not lines:
        return 0
    line_height = font.size * line_spacing
    return int(line_height * len(lines))


def render_profile_row(canvas, draw, x, y, config, fonts, theme):
    """Render the profile row: avatar + name + badge + handle on one line. Returns row height."""
    profile = config["profile"]
    colors = THEMES[theme]

    # Avatar
    headshot = load_headshot(profile.get("headshot"), AVATAR_SIZE)
    canvas.paste(headshot, (x, y), headshot)

    # All text vertically centered with avatar
    text_x = x + AVATAR_SIZE + AVATAR_GAP

    # Measure total text line height to center vertically
    name_bbox = fonts["name"].getbbox(profile["display_name"])
    name_height = name_bbox[3] - name_bbox[1]
    text_y = y + (AVATAR_SIZE - name_height) // 2

    # Name (bold)
    name_color = hex_to_rgb(colors["text"])
    draw.text((text_x, text_y), profile["display_name"], font=fonts["name"], fill=name_color)
    cursor_x = text_x + int(fonts["name"].getlength(profile["display_name"]))

    # Verified badge (inline after name)
    if profile.get("verified", False):
        cursor_x += NAME_BADGE_GAP
        badge_y = text_y + (name_height - BADGE_SIZE) // 2
        draw_verified_badge(draw, cursor_x, badge_y, BADGE_SIZE, theme)
        cursor_x += BADGE_SIZE

    # Handle (gray, same line)
    cursor_x += BADGE_HANDLE_GAP
    handle_color = hex_to_rgb(colors["secondary"])
    draw.text((cursor_x, text_y), profile["handle"], font=fonts["handle"], fill=handle_color)

    return AVATAR_SIZE


def render_tweet_block(canvas, draw, x, y, tweet, config, fonts, theme, max_width):
    """Render a single tweet block (profile + text + optional image). Returns total height."""
    colors = THEMES[theme]
    current_y = y

    # Profile row
    row_height = render_profile_row(canvas, draw, x, current_y, config, fonts, theme)
    current_y += row_height + PROFILE_TEXT_GAP

    # Tweet text with emoji support
    text = tweet.get("text", "")
    lines = word_wrap_text(text, fonts["text"], max_width, draw)
    text_color = hex_to_rgb(colors["text"])
    line_height = int(fonts["text"].size * 1.5)

    with Pilmoji(canvas) as pilmoji:
        for line in lines:
            pilmoji.text((x, current_y), line, font=fonts["text"], fill=text_color)
            current_y += line_height

    # Embedded image
    image_path = tweet.get("image")
    if image_path and os.path.exists(image_path):
        current_y += TWEET_IMAGE_GAP
        img = Image.open(image_path).convert("RGBA")

        # Scale to fit content width
        scale = max_width / img.width
        new_width = max_width
        new_height = int(img.height * scale)

        # Cap image height
        max_img_height = 600
        if new_height > max_img_height:
            new_height = max_img_height
            new_width = int(img.width * (max_img_height / img.height))

        img = img.resize((new_width, new_height), Image.LANCZOS)
        img = round_corners(img, IMAGE_CORNER_RADIUS)

        # Center image horizontally if narrower than content width
        img_x = x + (max_width - new_width) // 2
        canvas.paste(img, (img_x, current_y), img)
        current_y += new_height

    return current_y - y


def measure_tweet_block(tweet, config, fonts, theme, max_width):
    """Measure the height a tweet block would take without rendering."""
    height = AVATAR_SIZE + PROFILE_TEXT_GAP  # profile row + gap

    # Text height
    text = tweet.get("text", "")
    # Create a temporary image for measurement
    tmp = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp)
    lines = word_wrap_text(text, fonts["text"], max_width, tmp_draw)
    line_height = int(fonts["text"].size * 1.5)
    height += line_height * len(lines)

    # Image height
    image_path = tweet.get("image")
    if image_path and os.path.exists(image_path):
        height += TWEET_IMAGE_GAP
        img = Image.open(image_path)
        scale = max_width / img.width
        img_height = int(img.height * scale)
        height += min(img_height, 600)

    return height


def render_slide(config, slide_data, slide_num, output_dir, fonts):
    """Render a single carousel slide. Returns output path."""
    theme = config.get("theme", "light")
    colors = THEMES[theme]
    bg_color = hex_to_rgb(colors["bg"])

    canvas = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), bg_color + (255,))
    draw = ImageDraw.Draw(canvas)

    tweets = slide_data.get("tweets", [])

    if len(tweets) == 1:
        # Single tweet slide
        tweet = tweets[0]
        block_height = measure_tweet_block(tweet, config, fonts, theme, CONTENT_WIDTH)
        y_start = max(PADDING_X, (CANVAS_HEIGHT - block_height) // 2)
        render_tweet_block(canvas, draw, PADDING_X, y_start, tweet, config, fonts, theme, CONTENT_WIDTH)

    elif len(tweets) == 2:
        # Dual tweet slide with divider
        tweet_a, tweet_b = tweets[0], tweets[1]
        height_a = measure_tweet_block(tweet_a, config, fonts, theme, CONTENT_WIDTH)
        height_b = measure_tweet_block(tweet_b, config, fonts, theme, CONTENT_WIDTH)
        divider_height = 1
        total_height = height_a + DIVIDER_PADDING * 2 + divider_height + height_b
        y_start = max(PADDING_X, (CANVAS_HEIGHT - total_height) // 2)

        # First tweet
        actual_a = render_tweet_block(canvas, draw, PADDING_X, y_start, tweet_a, config, fonts, theme, CONTENT_WIDTH)

        # Divider
        divider_y = y_start + actual_a + DIVIDER_PADDING
        divider_color = hex_to_rgb(colors["divider"])
        draw.line(
            [(PADDING_X, divider_y), (CANVAS_WIDTH - PADDING_X, divider_y)],
            fill=divider_color,
            width=divider_height,
        )

        # Second tweet
        tweet_b_y = divider_y + divider_height + DIVIDER_PADDING
        render_tweet_block(canvas, draw, PADDING_X, tweet_b_y, tweet_b, config, fonts, theme, CONTENT_WIDTH)

    # Save
    output_path = os.path.join(output_dir, f"slide_{slide_num}.png")
    canvas_rgb = Image.new("RGB", canvas.size, bg_color)
    canvas_rgb.paste(canvas, mask=canvas.split()[3])
    canvas_rgb.save(output_path, "PNG", quality=95)
    return output_path


def render_carousel(config_path):
    """Main entry point: render all slides from a config.json."""
    config_path = os.path.abspath(config_path)
    with open(config_path) as f:
        config = json.load(f)

    # Resolve paths relative to project root
    project_root = os.path.dirname(os.path.dirname(config_path))
    # Try to find project root by looking for CLAUDE.md
    search = os.path.dirname(config_path)
    for _ in range(5):
        if os.path.exists(os.path.join(search, "CLAUDE.md")):
            project_root = search
            break
        search = os.path.dirname(search)

    # Resolve headshot path
    headshot = config["profile"].get("headshot", "")
    if headshot and not os.path.isabs(headshot):
        config["profile"]["headshot"] = os.path.join(project_root, headshot)

    # Resolve image paths in slides
    for slide in config.get("slides", []):
        for tweet in slide.get("tweets", []):
            img = tweet.get("image")
            if img and not os.path.isabs(img):
                tweet["image"] = os.path.join(project_root, img)

    # Output directory
    output_dir = config.get("output_dir", ".")
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(project_root, output_dir)
    os.makedirs(output_dir, exist_ok=True)

    fonts = load_fonts()
    slides = config.get("slides", [])

    print(f"Rendering {len(slides)} slide(s)...")
    print(f"Theme: {config.get('theme', 'light')}")
    print(f"Output: {output_dir}")
    print()

    generated = []
    for i, slide_data in enumerate(slides, 1):
        path = render_slide(config, slide_data, i, output_dir, fonts)
        tweet_count = len(slide_data.get("tweets", []))
        has_image = any(t.get("image") for t in slide_data.get("tweets", []))
        label = f"Slide {i}: {tweet_count} tweet(s)"
        if has_image:
            label += " + image"
        print(f"  ✓ {label} → {os.path.basename(path)}")
        generated.append(path)

    print(f"\nDone! {len(generated)} slides saved to {output_dir}")
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Instagram carousel slides from config.json")
    parser.add_argument("--config", required=True, help="Path to config.json")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: config file not found: {args.config}")
        sys.exit(1)

    render_carousel(args.config)
