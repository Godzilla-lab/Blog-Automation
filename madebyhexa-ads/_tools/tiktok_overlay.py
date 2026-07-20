#!/usr/bin/env python3
"""
TikTok image ads v2: tighter typographic alignment + dark-gradient masks over
the Higgsfield-hallucinated UI text + TikTok safe-zone aware composition.

TikTok safe zones (the engagement UI overlays the bottom-right + bottom-center):
  - top safe: y < 250 reserved for TikTok username/follow tag
  - right safe: x > 950 reserved for like/comment/share buttons
  - bottom safe: y > 1500 reserved for caption + sound

We keep all critical text in the 540 horizontal center band, 250<y<1450.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BG_DIR = "madebyhexa-ads/tiktok-images"
OUT_DIR = "madebyhexa-ads/tiktok-images"

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
ARIAL_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BRADLEY = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

BLUE = (0, 184, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INK = (28, 22, 18)
RED = (220, 30, 35)
URL = "madebyhexa.co/offer"


def open_bg(name):
    img = Image.open(os.path.join(BG_DIR, name)).convert("RGBA")
    return img.resize((1080, 1920), Image.LANCZOS)


def gradient_mask(img, y_start, y_end, opacity_top=200, opacity_bottom=0):
    """Add a vertical dark gradient over a y-band — used to hide background noise."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    h = y_end - y_start
    for y in range(y_start, y_end):
        t = (y - y_start) / h
        alpha = int(opacity_top + (opacity_bottom - opacity_top) * t)
        od.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, overlay)


def solid_mask(img, y_start, y_end, opacity=220):
    """Add a solid dark rectangle to fully blackout a band."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([(0, y_start), (img.size[0], y_end)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img, overlay)


def text_stroke(draw, xy, text, font, fill, stroke_fill=BLACK, stroke_w=6, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill,
              stroke_fill=stroke_fill, stroke_width=stroke_w, anchor=anchor)


def text_pill(img, xy, text, font, bg=BLUE, fg=WHITE, pad_x=40, pad_y=18, anchor="mm"):
    """Draw a rounded pill behind text, TikTok caption style."""
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox(xy, text, font=font, anchor=anchor)
    box = (bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y)
    radius = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=radius, fill=bg)
    draw.text(xy, text, font=font, fill=fg, anchor=anchor)


def watermark(img, y=1700):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ARIAL_BOLD, 30)
    draw.text((540, y), URL, font=font, fill=WHITE, anchor="mm",
              stroke_fill=BLACK, stroke_width=3)


# ============================================================
# I — Give me 60 seconds
# Layout: top half = headline (over masked bg) / phone visible in mid / CTA at safe bottom
# ============================================================
def make_i():
    img = open_bg("i-bg.png")
    # Fully hide the garbled "I an vdoh..." text at top of bg with a solid black band
    img = solid_mask(img, 0, 460, opacity=255)
    img = gradient_mask(img, 460, 750, opacity_top=255, opacity_bottom=0)

    draw = ImageDraw.Draw(img)

    # Top safe boundary line (visual breathing): y=260
    # Headline
    font_h = ImageFont.truetype(IMPACT, 150)
    text_stroke(draw, (540, 290), "GIVE ME", font_h, WHITE, BLACK, 10)
    text_stroke(draw, (540, 410), "60 SECONDS.", font_h, BLUE, BLACK, 10)

    # Body
    font_b = ImageFont.truetype(ARIAL_BLACK, 46)
    body = [
        "to show you what your",
        "product looks like",
        "as a cinematic ad.",
    ]
    for i, line in enumerate(body):
        text_stroke(draw, (540, 540 + i * 60), line, font_b, WHITE, BLACK, 4)

    # CTA pill in TikTok safe zone
    font_c = ImageFont.truetype(ARIAL_BLACK, 56)
    text_pill(img, (540, 1450), "FREE SAMPLE ↓", font_c, bg=BLUE, fg=WHITE)

    watermark(img)
    out = os.path.join(OUT_DIR, "i-60-seconds.png")
    img.convert("RGB").save(out, "PNG")
    return out


# ============================================================
# J — Triple negation on sticky note
# Layout: handwriting centered on the sticky note (sticky is mid-frame in bg)
# ============================================================
def make_j():
    img = open_bg("j-bg.png")
    draw = ImageDraw.Draw(img)

    # Title block on top of sticky (sticky note region ~y=400-1200)
    font_t = ImageFont.truetype(BRADLEY, 88)
    draw.text((540, 530), "Cinematic ad,", font=font_t, fill=INK, anchor="mm")
    draw.text((540, 640), "48 hrs.", font=font_t, fill=INK, anchor="mm")

    # Three "✗ NAME" lines, hand-aligned to a virtual left edge
    font_l = ImageFont.truetype(BRADLEY, 72)
    lines = ["No studio", "No crew", "No shoot day"]
    y_start = 800
    LINE_GAP = 100
    X_MARK = 320
    LINE_X = 470  # left edge of each line label
    for i, line in enumerate(lines):
        y = y_start + i * LINE_GAP
        # Hand-drawn red X via two crossed lines (Impact lacks U+2717)
        cx, cy, s = X_MARK, y, 28
        draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=RED, width=10)
        draw.line([(cx - s, cy + s), (cx + s, cy - s)], fill=RED, width=10)
        draw.text((LINE_X, y), line, font=font_l, fill=INK, anchor="lm")

    # Small handwriting CTA on bottom of sticky
    font_u = ImageFont.truetype(BRADLEY, 50)
    draw.text((540, 1180), URL, font=font_u, fill=BLUE, anchor="mm")

    # TikTok-safe-zone CTA pill below sticky
    font_c = ImageFont.truetype(ARIAL_BLACK, 56)
    text_pill(img, (540, 1450), "FREE SAMPLE ↓", font_c, bg=BLUE, fg=WHITE)

    watermark(img)
    out = os.path.join(OUT_DIR, "j-without-x.png")
    img.convert("RGB").save(out, "PNG")
    return out


# ============================================================
# K — 881K Followers
# Layout: massive number at top / phone chart in middle (mask garbled UI) / proof + CTA bottom
# ============================================================
def make_k():
    img = open_bg("k-bg.png")
    # Fully mask the garbled chart UI text in the lower half of the phone screen
    img = solid_mask(img, 1020, 1380, opacity=255)
    img = gradient_mask(img, 1380, 1500, opacity_top=255, opacity_bottom=80)
    # Soften the very top so the headline pops
    img = gradient_mask(img, 0, 250, opacity_top=200, opacity_bottom=80)

    draw = ImageDraw.Draw(img)

    # MASSIVE 881K
    font_n = ImageFont.truetype(IMPACT, 200)
    text_stroke(draw, (540, 170), "881K", font_n, BLUE, BLACK, 12)

    font_sub = ImageFont.truetype(ARIAL_BLACK, 64)
    text_stroke(draw, (540, 320), "FOLLOWERS", font_sub, WHITE, BLACK, 5)

    # Proof bar over the masked area
    font_p = ImageFont.truetype(ARIAL_BLACK, 56)
    text_pill(img, (540, 1140), "10M VIEWS · 30 DAYS",
              font_p, bg=BLACK, fg=WHITE, pad_x=36, pad_y=22)

    # Italic kicker
    font_k = ImageFont.truetype(ARIAL_BOLD, 44)
    text_stroke(draw, (540, 1260), "all AI. no shoots. no studio.",
                font_k, WHITE, BLACK, 4)

    # CTA pill
    font_c = ImageFont.truetype(ARIAL_BLACK, 56)
    text_pill(img, (540, 1450), "FREE SAMPLE ↓", font_c, bg=BLUE, fg=WHITE)

    watermark(img)
    out = os.path.join(OUT_DIR, "k-how-many-products.png")
    img.convert("RGB").save(out, "PNG")
    return out


# ============================================================
# L — 1/10th Potential
# Layout: headline stack at top / 1/10 hero / proof bars + CTA at bottom
# ============================================================
def make_l():
    img = open_bg("l-bg.png")
    # Fully mask the laptop screen middle (garbled dashboard UI)
    img = solid_mask(img, 740, 1340, opacity=240)
    img = gradient_mask(img, 0, 200, opacity_top=180, opacity_bottom=0)

    draw = ImageDraw.Draw(img)

    # Top stack
    font_h = ImageFont.truetype(IMPACT, 110)
    text_stroke(draw, (540, 160), "YOUR META ADS", font_h, WHITE, BLACK, 8)
    text_stroke(draw, (540, 270), "ARE USING", font_h, WHITE, BLACK, 8)

    # Hero 1/10th
    font_n = ImageFont.truetype(IMPACT, 240)
    text_stroke(draw, (540, 470), "1/10th", font_n, RED, BLACK, 12)

    font_s = ImageFont.truetype(ARIAL_BLACK, 60)
    text_stroke(draw, (540, 660), "of what AI can do.", font_s, WHITE, BLACK, 5)

    # Two proof bars over masked laptop area
    font_p = ImageFont.truetype(ARIAL_BLACK, 52)
    text_pill(img, (540, 920), "100× cheaper than a shoot",
              font_p, bg=BLACK, fg=BLUE, pad_x=36, pad_y=20)
    text_pill(img, (540, 1050), "48-hour turnaround",
              font_p, bg=BLACK, fg=WHITE, pad_x=36, pad_y=20)

    # CTA pill
    font_c = ImageFont.truetype(ARIAL_BLACK, 56)
    text_pill(img, (540, 1450), "FREE SAMPLE ↓", font_c, bg=BLUE, fg=WHITE)

    watermark(img)
    out = os.path.join(OUT_DIR, "l-tenth-potential.png")
    img.convert("RGB").save(out, "PNG")
    return out


if __name__ == "__main__":
    print("Regenerating 4 TikTok image ads v2 (aligned + masked + /offer)...")
    for fn in [make_i, make_j, make_k, make_l]:
        path = fn()
        print(f"  ✓ {path}")
    print("Done.")
