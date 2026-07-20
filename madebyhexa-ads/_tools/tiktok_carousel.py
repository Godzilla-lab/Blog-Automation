#!/usr/bin/env python3
"""
Build a 10-frame TikTok carousel optimized for swipe-through:
  Frame 1: imessage (hook)
  Frame 2: receipt ($59 reveal)
  Frame 3: cost-split (old vs new)
  Frame 4: step 1 - send your product
  Frame 5: step 2 - AI generates
  Frame 6: step 3 - delivered in 48hr
  Frame 7: l-tenth-potential
  Frame 8: stat-card (881K proof)
  Frame 9: testimonial quote
  Frame 10: j-without-x (CTA close)

Carousel sequencing rationale (from research):
  - Lead with iMessage / receipt = highest pattern-interrupt openers
  - Mid: process steps build understanding
  - Late: social proof + final CTA card
"""
import os, shutil
from PIL import Image, ImageDraw, ImageFont

OUT = "madebyhexa-ads/tiktok-images/carousel"
SRC = "madebyhexa-ads/tiktok-images"

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
ARIAL_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BRADLEY = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

BLUE = (0, 184, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INK = (28, 22, 18)
URL = "madebyhexa.co/offer"
CTA_Y = 1380

os.makedirs(OUT, exist_ok=True)


def text_stroke(draw, xy, text, font, fill, sf=BLACK, sw=6, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, stroke_fill=sf, stroke_width=sw, anchor=anchor)


def text_pill(img, xy, text, font, bg=BLUE, fg=WHITE, px=44, py=22, anchor="mm"):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox(xy, text, font=font, anchor=anchor)
    box = (bbox[0] - px, bbox[1] - py, bbox[2] + px, bbox[3] + py)
    r = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=r, fill=bg)
    draw.text(xy, text, font=font, fill=fg, anchor=anchor)


def watermark_small(img, fill=(140, 140, 140)):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ARIAL_BOLD, 28)
    draw.text((540, 1860), URL, font=font, fill=fill, anchor="mm")


def step_frame(num, total, big_text, sub_text, color_accent, file_name):
    """Process step frame with step counter + big bold message."""
    img = Image.new("RGB", (1080, 1920), color=(20, 20, 28))
    draw = ImageDraw.Draw(img)

    # Top step counter
    font_step = ImageFont.truetype(ARIAL_BLACK, 50)
    draw.text((540, 200), f"STEP {num} OF {total}", font=font_step,
              fill=color_accent, anchor="mm")

    # Big number
    font_n = ImageFont.truetype(IMPACT, 400)
    text_stroke(draw, (540, 540), str(num), font_n, color_accent, BLACK, 18)

    # Big text block (centered, wrapped)
    font_big = ImageFont.truetype(ARIAL_BLACK, 86)
    # Wrap manually
    words = big_text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font_big)
        if bbox[2] - bbox[0] > 960:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines):
        text_stroke(draw, (540, 920 + i * 100), line, font_big, WHITE, BLACK, 6)

    # Sub
    font_sub = ImageFont.truetype(ARIAL_BOLD, 46)
    text_stroke(draw, (540, 1240), sub_text, font_sub, (180, 180, 200), BLACK, 3)

    # Swipe hint
    font_swipe = ImageFont.truetype(ARIAL_BOLD, 36)
    draw.text((540, 1700), "swipe →", font=font_swipe,
              fill=(120, 120, 140), anchor="mm")

    watermark_small(img)
    img.save(os.path.join(OUT, file_name), "PNG")


def testimonial_frame(file_name):
    """Quote-style testimonial card."""
    img = Image.new("RGB", (1080, 1920), color=(18, 18, 24))
    draw = ImageDraw.Draw(img)

    # Big quotation marks
    font_quote = ImageFont.truetype(IMPACT, 400)
    draw.text((540, 280), '"', font=font_quote, fill=BLUE, anchor="mm")

    # Quote text
    font_t = ImageFont.truetype(ARIAL_BOLD, 60)
    quote_lines = [
        "I handed Hexa AI",
        "my content and stopped",
        "thinking about it.",
        "",
        "881K followers,",
        "10M views in 30 days.",
        "",
        "No shoots. No studio.",
    ]
    y = 580
    for line in quote_lines:
        if not line:
            y += 30
            continue
        text_stroke(draw, (540, y), line, font_t, WHITE, BLACK, 4)
        y += 80

    # Attribution
    font_a = ImageFont.truetype(BRADLEY, 44)
    draw.text((540, 1500), "— anonymous creator client", font=font_a,
              fill=(180, 180, 200), anchor="mm")
    draw.text((540, 1570), "verified outcome", font=ImageFont.truetype(ARIAL_BOLD, 32),
              fill=(120, 120, 140), anchor="mm")

    watermark_small(img)
    img.save(os.path.join(OUT, file_name), "PNG")


# Build sequence
def build():
    # Copy existing frames into carousel folder with numbered order
    sequence = [
        ("imessage.png", "01-imessage.png"),
        ("receipt.png", "02-receipt.png"),
        ("cost-split.png", "03-cost-split.png"),
    ]
    for src, dst in sequence:
        shutil.copy(os.path.join(SRC, src), os.path.join(OUT, dst))

    # 3 process steps
    step_frame(1, 3, "Send us your product photo",
               "(any photo, any product)", BLUE, "04-step-1.png")
    step_frame(2, 3, "AI generates your ad",
               "cinematic. brand-grade. no shoot.", (255, 230, 40), "05-step-2.png")
    step_frame(3, 3, "Delivered in 48 hours",
               "you keep it whether or not you hire us.", BLUE, "06-step-3.png")

    # Proof + close
    more = [
        ("l-tenth-potential.png", "07-l-tenth-potential.png"),
        ("stat-card.png", "08-stat-card.png"),
    ]
    for src, dst in more:
        shutil.copy(os.path.join(SRC, src), os.path.join(OUT, dst))

    # Testimonial
    testimonial_frame("09-testimonial.png")

    # CTA close
    shutil.copy(os.path.join(SRC, "j-without-x.png"),
                os.path.join(OUT, "10-cta-close.png"))

    print("Carousel built (10 frames):")
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            print(f"  {f}")


if __name__ == "__main__":
    build()
