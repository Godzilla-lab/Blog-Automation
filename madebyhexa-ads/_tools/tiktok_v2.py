#!/usr/bin/env python3
"""
6 TikTok image ads v2 — research-driven refresh:
  1. CTA pill moved up to y=1380 (clear of TikTok's 370px bottom UI zone)
  2. CTA copy = deliverable-specific (rotated for A/B test)
  3. stat-card  → phone-screenshot background (UGC-coded, not designed slide)
  4. cost-split → handwritten napkin background (UGC-coded)
  5. receipt    → yellow highlighter swipe + micro-disclaimer for pricing claim
  6. URL kept small below CTA pill; rely on TikTok's CTA button for the click
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = "madebyhexa-ads/tiktok-images"
ASSETS = "madebyhexa-ads/public/assets"

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
ARIAL_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
BRADLEY = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

BLUE = (0, 184, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INK = (28, 22, 18)
RED = (220, 30, 35)
YELLOW = (255, 230, 40)
HIGHLIGHT = (255, 235, 60)
URL = "madebyhexa.co/offer"

# CTA pill Y position — clear of TikTok's 370px bottom UI band
CTA_Y = 1380
URL_Y = 1480


def open_bg(name):
    img = Image.open(os.path.join(OUT_DIR, name)).convert("RGBA")
    return img.resize((1080, 1920), Image.LANCZOS)


def solid_mask(img, y0, y1, opacity=255):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([(0, y0), (img.size[0], y1)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img, overlay)


def gradient_mask(img, y0, y1, top=255, bot=0):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    h = y1 - y0
    for y in range(y0, y1):
        t = (y - y0) / h
        a = int(top + (bot - top) * t)
        od.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(img, overlay)


def text_stroke(draw, xy, text, font, fill, sf=BLACK, sw=6, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, stroke_fill=sf, stroke_width=sw, anchor=anchor)


def text_pill(img, xy, text, font, bg=BLUE, fg=WHITE, px=44, py=22, anchor="mm"):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox(xy, text, font=font, anchor=anchor)
    box = (bbox[0] - px, bbox[1] - py, bbox[2] + px, bbox[3] + py)
    r = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=r, fill=bg)
    draw.text(xy, text, font=font, fill=fg, anchor=anchor)


def cta_pill(img, text, bg=BLUE, fg=WHITE, font_size=56):
    """Standard CTA pill at the research-safe position."""
    text_pill(img, (540, CTA_Y), text,
              ImageFont.truetype(ARIAL_BLACK, font_size), bg=bg, fg=fg, px=44, py=22)


def url_mark(img, y=URL_Y, fill=WHITE, stroke=BLACK):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ARIAL_BOLD, 32)
    draw.text((540, y), URL, font=font, fill=fill, anchor="mm",
              stroke_fill=stroke, stroke_width=3)


def watermark_tiny(img, y=1880):
    """Small fallback brand mark below safe zone (gets covered by TikTok UI on-platform, fine)."""
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ARIAL_BOLD, 22)
    draw.text((540, y), URL, font=font, fill=(255, 255, 255, 150), anchor="mm")


# ============================================================
# 1. j-without-x — handwritten sticky note (kept design, fix CTA position)
# ============================================================
def make_j():
    img = open_bg("j-bg.png")
    draw = ImageDraw.Draw(img)

    font_t = ImageFont.truetype(BRADLEY, 88)
    draw.text((540, 530), "Cinematic ad,", font=font_t, fill=INK, anchor="mm")
    draw.text((540, 640), "48 hrs.", font=font_t, fill=INK, anchor="mm")

    font_l = ImageFont.truetype(BRADLEY, 72)
    lines = ["No studio", "No crew", "No shoot day"]
    for i, line in enumerate(lines):
        y = 800 + i * 100
        cx, cy, s = 320, y, 28
        draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=RED, width=10)
        draw.line([(cx - s, cy + s), (cx + s, cy - s)], fill=RED, width=10)
        draw.text((470, y), line, font=font_l, fill=INK, anchor="lm")

    font_u = ImageFont.truetype(BRADLEY, 50)
    draw.text((540, 1180), URL, font=font_u, fill=BLUE, anchor="mm")

    cta_pill(img, "Get free 48-hr ad ↓")
    url_mark(img, fill=WHITE, stroke=BLACK)
    watermark_tiny(img)
    img.convert("RGB").save(os.path.join(OUT_DIR, "j-without-x.png"), "PNG")


# ============================================================
# 2. l-tenth-potential — keep design but CTA position fix
# ============================================================
def make_l():
    img = open_bg("l-bg.png")
    img = solid_mask(img, 740, 1340, opacity=240)
    img = gradient_mask(img, 0, 200, top=180, bot=0)

    draw = ImageDraw.Draw(img)
    font_h = ImageFont.truetype(IMPACT, 110)
    text_stroke(draw, (540, 160), "YOUR META ADS", font_h, WHITE, BLACK, 8)
    text_stroke(draw, (540, 270), "ARE USING", font_h, WHITE, BLACK, 8)

    font_n = ImageFont.truetype(IMPACT, 240)
    text_stroke(draw, (540, 470), "1/10th", font_n, RED, BLACK, 12)

    font_s = ImageFont.truetype(ARIAL_BLACK, 60)
    text_stroke(draw, (540, 660), "of what AI can do.", font_s, WHITE, BLACK, 5)

    font_p = ImageFont.truetype(ARIAL_BLACK, 52)
    text_pill(img, (540, 920), "100× cheaper than a shoot",
              ImageFont.truetype(ARIAL_BLACK, 52), bg=BLACK, fg=BLUE, px=36, py=20)
    text_pill(img, (540, 1050), "48-hour turnaround",
              ImageFont.truetype(ARIAL_BLACK, 52), bg=BLACK, fg=WHITE, px=36, py=20)

    cta_pill(img, "Tap for $59 sample ↓")
    url_mark(img)
    watermark_tiny(img)
    img.convert("RGB").save(os.path.join(OUT_DIR, "l-tenth-potential.png"), "PNG")


# ============================================================
# 3. cost-split — NEW: handwritten napkin
# ============================================================
def make_cost_split():
    img = open_bg("napkin-bg.png")
    draw = ImageDraw.Draw(img)

    # Stack vertically: title → $15K crossed → $59 → notes
    font_t = ImageFont.truetype(BRADLEY, 70)
    draw.text((540, 480), "old way vs new way", font=font_t, fill=INK, anchor="mm")

    # $15K crossed out (no overlap with $59 — stacked)
    font_n_big = ImageFont.truetype(BRADLEY, 140)
    draw.text((540, 660), "$15,000", font=font_n_big, fill=INK, anchor="mm")
    bbox = draw.textbbox((540, 660), "$15,000", font=font_n_big, anchor="mm")
    draw.line([(bbox[0] - 30, bbox[3] - 35), (bbox[2] + 30, bbox[1] + 35)],
              fill=RED, width=16)

    # Down-arrow
    font_arrow = ImageFont.truetype(ARIAL_BLACK, 80)
    draw.text((540, 800), "↓", font=font_arrow, fill=INK, anchor="mm")

    # $59 — the reveal
    draw.text((540, 950), "$59", font=ImageFont.truetype(BRADLEY, 180), fill=INK, anchor="mm")

    # Notes
    font_note = ImageFont.truetype(BRADLEY, 60)
    draw.text((540, 1100), "100× cheaper", font=font_note, fill=RED, anchor="mm")
    draw.text((540, 1180), "48 hrs · from 1 photo",
              font=ImageFont.truetype(BRADLEY, 48), fill=INK, anchor="mm")

    # Micro-disclaimer
    draw.text((540, 1260), "*typical 2026 agency cost",
              font=ImageFont.truetype(BRADLEY, 28),
              fill=(120, 100, 80), anchor="mm")

    cta_pill(img, "Get your $59 ad ↓")
    url_mark(img, fill=WHITE, stroke=BLACK)
    watermark_tiny(img)
    img.convert("RGB").save(os.path.join(OUT_DIR, "cost-split.png"), "PNG")


# ============================================================
# 4. imessage — keep design, fix CTA position + new CTA
# ============================================================
def make_imessage():
    img = Image.new("RGB", (1080, 1920), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Status bar
    draw.rectangle([(0, 0), (1080, 90)], fill=WHITE)
    font_time = ImageFont.truetype(ARIAL_BOLD, 32)
    draw.text((60, 45), "9:41", font=font_time, fill=BLACK, anchor="lm")
    draw.text((1020, 45), "•••• 5G", font=font_time, fill=BLACK, anchor="rm")

    # Contact header
    draw.rectangle([(0, 90), (1080, 230)], fill=(247, 247, 247))
    draw.ellipse([(60, 110), (180, 230)], fill=(180, 200, 220))
    draw.text((120, 170), "S", font=ImageFont.truetype(ARIAL_BLACK, 60),
              fill=WHITE, anchor="mm")
    draw.text((220, 150), "Sarah · Brand owner",
              font=ImageFont.truetype(ARIAL_BLACK, 42), fill=BLACK, anchor="lm")
    draw.text((220, 195), "iMessage",
              font=ImageFont.truetype(ARIAL, 28), fill=(140, 140, 140), anchor="lm")
    draw.line([(0, 230), (1080, 230)], fill=(220, 220, 220), width=2)

    IMSG_BLUE = (10, 132, 255)
    IMSG_GRAY = (229, 229, 234)

    def bubble(y, text, side="left", max_w=720):
        font = ImageFont.truetype(ARIAL_BOLD, 44)
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_w:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
        line_h = 60
        height = len(lines) * line_h + 50
        bbox_w = 0
        for line in lines:
            b = draw.textbbox((0, 0), line, font=font)
            bbox_w = max(bbox_w, b[2] - b[0])
        bubble_w = bbox_w + 80
        if side == "left":
            box = (40, y, 40 + bubble_w, y + height)
            bg, fg = IMSG_GRAY, BLACK
        else:
            box = (1080 - 40 - bubble_w, y, 1080 - 40, y + height)
            bg, fg = IMSG_BLUE, WHITE
        draw.rounded_rectangle(box, radius=40, fill=bg)
        for i, line in enumerate(lines):
            tx = box[0] + 40 if side == "left" else box[2] - 40
            draw.text((tx, y + 30 + i * line_h), line, font=font, fill=fg,
                      anchor="lm" if side == "left" else "rm")
        return y + height + 30

    y = 290
    y = bubble(y, "wait what did you spend on that ad?", side="left")
    y = bubble(y, "$59", side="right")
    y = bubble(y, "STOP. for that quality??", side="left")
    y = bubble(y, "AI made it in 48 hrs", side="right")
    y = bubble(y, "no studio?? send me the link", side="left")
    y = bubble(y, URL, side="right")

    cta_pill(img, "Free ad in 48 hrs ↓")
    url_mark(img, y=URL_Y, fill=(80, 80, 80), stroke=WHITE)
    watermark_tiny(img, y=1880)
    img.save(os.path.join(OUT_DIR, "imessage.png"), "PNG")


# ============================================================
# 5. stat-card — NEW: phone screenshot with 881K overlay
# ============================================================
def make_stat_card():
    img = open_bg("stat-card-bg.png")
    # Light dark gradient at top for text pop
    img = gradient_mask(img, 0, 280, top=200, bot=0)
    # Dark band at bottom for stats stack (ends well before CTA at y=1380)
    img = gradient_mask(img, 980, 1260, top=0, bot=220)

    draw = ImageDraw.Draw(img)

    # Top: massive 881K headline (over gradient masked top)
    font_n = ImageFont.truetype(IMPACT, 220)
    text_stroke(draw, (540, 180), "881K", font_n, BLUE, BLACK, 14)

    font_sub = ImageFont.truetype(ARIAL_BLACK, 56)
    text_stroke(draw, (540, 320), "FOLLOWERS · 30 DAYS", font_sub, WHITE, BLACK, 5)

    # Annotation arrow + caption — use Arial Black for arrow glyph
    font_anno_arrow = ImageFont.truetype(ARIAL_BLACK, 64)
    draw.text((400, 1040), "↑", font=font_anno_arrow, fill=WHITE, anchor="mm",
              stroke_fill=BLACK, stroke_width=4)
    font_anno = ImageFont.truetype(BRADLEY, 50)
    draw.text((540, 1040), "this client. all AI.", font=font_anno,
              fill=WHITE, anchor="lm", stroke_fill=BLACK, stroke_width=3)

    # Stats tighter, moved up to leave room for CTA at y=1380
    font_stat = ImageFont.truetype(ARIAL_BLACK, 46)
    stats = [
        ("10M views", BLUE),
        ("0 shoots · 0 studio days", WHITE),
    ]
    for i, (s, c) in enumerate(stats):
        text_stroke(draw, (540, 1150 + i * 70), s, font_stat, c, BLACK, 4)

    cta_pill(img, "Free $59 ad ↓")
    url_mark(img)
    watermark_tiny(img)
    img.convert("RGB").save(os.path.join(OUT_DIR, "stat-card.png"), "PNG")


# ============================================================
# 6. receipt — yellow swipe + micro-disclaimer
# ============================================================
def make_receipt():
    img = Image.open(os.path.join(ASSETS, "invoice-12400.png")).convert("RGBA")
    img = img.resize((1080, 1920), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Header
    font_lab = ImageFont.truetype(ARIAL_BLACK, 42)
    text_stroke(draw, (540, 130), "WHAT BRANDS USED TO PAY", font_lab, WHITE, BLACK, 5)

    # Micro-disclaimer (under the invoice area)
    font_dis = ImageFont.truetype(ARIAL_BOLD, 26)
    text_stroke(draw, (540, 1000), "*typical 2026 agency cost",
                font_dis, (220, 220, 220), BLACK, 3)

    # "NOW IT'S" tag
    font_vs = ImageFont.truetype(IMPACT, 110)
    text_stroke(draw, (540, 1090), "NOW IT'S", font_vs, WHITE, BLACK, 8)

    # YELLOW highlighter swipe behind $59
    swipe_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(swipe_overlay)
    sd.rounded_rectangle([(280, 1170), (800, 1340)], radius=20,
                         fill=(*HIGHLIGHT, 235))
    img = Image.alpha_composite(img, swipe_overlay)
    draw = ImageDraw.Draw(img)

    # $59 handwritten on yellow swipe
    font_n = ImageFont.truetype(BRADLEY, 200)
    draw.text((540, 1255), "$59", font=font_n, fill=BLACK, anchor="mm")

    # CTA pill (default safe position)
    cta_pill(img, "Free 48-hr ad ↓")

    # Tag line + URL below
    font_t = ImageFont.truetype(ARIAL_BLACK, 40)
    text_stroke(draw, (540, 1490), "48 hrs · AI · from 1 photo",
                font_t, WHITE, BLACK, 4)
    url_mark(img, y=1560)
    watermark_tiny(img)
    img.convert("RGB").save(os.path.join(OUT_DIR, "receipt.png"), "PNG")


if __name__ == "__main__":
    print("Building 6 TikTok image ads v2 (research-driven refresh)...")
    for fn in [make_j, make_l, make_cost_split, make_imessage, make_stat_card, make_receipt]:
        fn()
        print(f"  ✓ {fn.__name__}")
    print("Done.")
