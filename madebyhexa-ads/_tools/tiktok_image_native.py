#!/usr/bin/env python3
"""
4 image-native TikTok ad hooks (no Higgsfield required). Pure typography
designs that land in <0.5s of scroll:

  1. cost-split    — $59 vs $15K split-screen
  2. imessage      — fake iMessage UGC screenshot
  3. stat-card     — massive single-stat 881K card
  4. receipt       — $12,400 strikethrough → $59 (uses existing invoice asset)

All 1080×1920 TikTok-native.
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
SF = "/System/Library/Fonts/SFNS.ttf"  # iMessage uses SF Pro

BLUE = (0, 184, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INK = (28, 22, 18)
RED = (220, 30, 35)
DEEP_RED = (140, 18, 22)
URL = "madebyhexa.co/offer"

IMSG_BLUE = (10, 132, 255)   # iMessage send blue
IMSG_GRAY = (229, 229, 234)  # iMessage incoming gray
IMSG_DARK = (28, 28, 30)
CHAT_BG = (255, 255, 255)


def text_stroke(draw, xy, text, font, fill, stroke_fill=BLACK, stroke_w=6, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill,
              stroke_fill=stroke_fill, stroke_width=stroke_w, anchor=anchor)


def text_pill(img, xy, text, font, bg=BLUE, fg=WHITE, pad_x=40, pad_y=18, anchor="mm"):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox(xy, text, font=font, anchor=anchor)
    box = (bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y)
    radius = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=radius, fill=bg)
    draw.text(xy, text, font=font, fill=fg, anchor=anchor)


def watermark(img, fill=WHITE, y=1860):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ARIAL_BOLD, 28)
    draw.text((540, y), URL, font=font, fill=fill, anchor="mm",
              stroke_fill=BLACK, stroke_width=2)


# ============================================================
# 1. cost-split.png — $59 vs $15K split-screen
# ============================================================
def make_cost_split():
    img = Image.new("RGB", (1080, 1920), color=WHITE)
    draw = ImageDraw.Draw(img)

    # LEFT half: dark deep-red, the "old way"
    draw.rectangle([(0, 0), (540, 1920)], fill=(38, 8, 10))
    # RIGHT half: bright clean, the "AI way"
    draw.rectangle([(540, 0), (1080, 1920)], fill=(245, 245, 248))

    # Top labels — TikTok scroll-stopper
    font_lab = ImageFont.truetype(ARIAL_BLACK, 38)
    draw.text((270, 130), "STUDIO SHOOT", font=font_lab, fill=(255, 100, 100), anchor="mm")
    draw.text((810, 130), "MADEBYHEXA", font=font_lab, fill=BLUE, anchor="mm")

    # Hero numbers
    font_n = ImageFont.truetype(IMPACT, 200)
    draw.text((270, 380), "$15K", font=font_n, fill=WHITE, anchor="mm")
    draw.text((810, 380), "$59", font=font_n, fill=BLACK, anchor="mm")

    # Subline
    font_sub = ImageFont.truetype(ARIAL_BOLD, 36)
    draw.text((270, 540), "per shoot day", font=font_sub, fill=(220, 180, 180), anchor="mm")
    draw.text((810, 540), "per video", font=font_sub, fill=(100, 100, 110), anchor="mm")

    # Divider line
    draw.line([(540, 100), (540, 1700)], fill=(180, 180, 180), width=4)

    # Feature lists
    font_li = ImageFont.truetype(ARIAL_BLACK, 38)
    left = [
        ("6 weeks", (255, 130, 130)),
        ("studio", (255, 130, 130)),
        ("crew of 8", (255, 130, 130)),
        ("$50K+ total", (255, 130, 130)),
    ]
    right = [
        ("48 HOURS", BLUE),
        ("no studio", BLACK),
        ("no crew", BLACK),
        ("1 photo", BLACK),
    ]
    y0 = 760
    for i, (txt, color) in enumerate(left):
        draw.text((270, y0 + i * 90), txt, font=font_li, fill=color, anchor="mm")
    for i, (txt, color) in enumerate(right):
        draw.text((810, y0 + i * 90), txt, font=font_li, fill=color, anchor="mm")

    # Bottom CTA spanning both halves
    text_pill(img, (540, 1500), "FREE SAMPLE ↓",
              ImageFont.truetype(ARIAL_BLACK, 56), bg=BLUE, fg=WHITE, pad_x=44, pad_y=22)
    # And big "100× cheaper" stamp above CTA
    font_stamp = ImageFont.truetype(IMPACT, 110)
    draw.text((540, 1330), "100× cheaper", font=font_stamp,
              fill=RED, anchor="mm", stroke_fill=BLACK, stroke_width=6)

    watermark(img, fill=(80, 80, 80))
    out = os.path.join(OUT_DIR, "cost-split.png")
    img.save(out, "PNG")
    return out


# ============================================================
# 2. imessage.png — fake iMessage UGC screenshot
# ============================================================
def make_imessage():
    img = Image.new("RGB", (1080, 1920), color=CHAT_BG)
    draw = ImageDraw.Draw(img)

    # Top status bar (clean iOS look)
    draw.rectangle([(0, 0), (1080, 90)], fill=CHAT_BG)
    font_time = ImageFont.truetype(ARIAL_BOLD, 32)
    draw.text((60, 45), "9:41", font=font_time, fill=BLACK, anchor="lm")
    draw.text((1020, 45), "•••• 5G", font=font_time, fill=BLACK, anchor="rm")

    # Contact header
    draw.rectangle([(0, 90), (1080, 230)], fill=(247, 247, 247))
    # Avatar circle
    draw.ellipse([(60, 110), (180, 230)], fill=(180, 200, 220))
    font_avatar = ImageFont.truetype(ARIAL_BLACK, 60)
    draw.text((120, 170), "S", font=font_avatar, fill=WHITE, anchor="mm")
    # Name
    font_name = ImageFont.truetype(ARIAL_BLACK, 42)
    draw.text((220, 150), "Sarah · Brand owner", font=font_name, fill=BLACK, anchor="lm")
    font_status = ImageFont.truetype(ARIAL, 28)
    draw.text((220, 195), "iMessage", font=font_status, fill=(140, 140, 140), anchor="lm")
    # Separator
    draw.line([(0, 230), (1080, 230)], fill=(220, 220, 220), width=2)

    # Bubble helper
    def bubble(xy_top, text, side="left", max_w=720):
        """Draw an iMessage bubble. Returns new y after bubble."""
        font = ImageFont.truetype(ARIAL_BOLD, 44)
        x, y = xy_top
        # Wrap text
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

        # Measure
        line_h = 60
        height = len(lines) * line_h + 50
        bbox_w = 0
        for line in lines:
            b = draw.textbbox((0, 0), line, font=font)
            bbox_w = max(bbox_w, b[2] - b[0])
        bubble_w = bbox_w + 80

        if side == "left":
            box = (40, y, 40 + bubble_w, y + height)
            bg = IMSG_GRAY
            fg = BLACK
        else:
            box = (1080 - 40 - bubble_w, y, 1080 - 40, y + height)
            bg = IMSG_BLUE
            fg = WHITE

        draw.rounded_rectangle(box, radius=40, fill=bg)
        for i, line in enumerate(lines):
            tx = box[0] + 40 if side == "left" else box[2] - 40
            draw.text((tx, y + 30 + i * line_h),
                      line, font=font, fill=fg, anchor="lm" if side == "left" else "rm")
        return y + height + 30

    # Conversation
    y = 290
    y = bubble((40, y), "wait what did you spend on that ad?", side="left")
    y = bubble((40, y), "$59", side="right")
    y = bubble((40, y), "STOP. for that quality??", side="left")
    y = bubble((40, y), "AI made it in 48 hrs", side="right")
    y = bubble((40, y), "no studio?? send me the link", side="left")
    y = bubble((40, y), "madebyhexa.co/offer", side="right")
    y = bubble((40, y), "free sample. you keep it.", side="right")

    # Bottom CTA pill
    text_pill(img, (540, 1740), "FREE SAMPLE ↓",
              ImageFont.truetype(ARIAL_BLACK, 56), bg=BLUE, fg=WHITE, pad_x=44, pad_y=22)

    watermark(img, fill=(120, 120, 120))
    out = os.path.join(OUT_DIR, "imessage.png")
    img.save(out, "PNG")
    return out


# ============================================================
# 3. stat-card.png — massive single-stat 881K card
# ============================================================
def make_stat_card():
    img = Image.new("RGB", (1080, 1920), color=(8, 8, 14))
    draw = ImageDraw.Draw(img)

    # Subtle radial-ish glow at top
    glow = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(180, -300), (900, 600)], fill=(0, 184, 255, 60))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(radius=80))).convert("RGB"))
    # Re-draw on top of pasted result
    draw = ImageDraw.Draw(img)

    # Top label
    font_lab = ImageFont.truetype(ARIAL_BLACK, 40)
    draw.text((540, 280), "ONE CREATOR · 30 DAYS", font=font_lab,
              fill=(180, 180, 200), anchor="mm")

    # The hero stat
    font_n = ImageFont.truetype(IMPACT, 380)
    text_stroke(draw, (540, 560), "881K", font_n,
                fill=BLUE, stroke_fill=BLACK, stroke_w=18)
    font_sub = ImageFont.truetype(ARIAL_BLACK, 84)
    text_stroke(draw, (540, 790), "FOLLOWERS", font_sub,
                fill=WHITE, stroke_fill=BLACK, stroke_w=6)

    # Divider
    draw.line([(280, 920), (800, 920)], fill=(80, 80, 100), width=4)

    # Stats stack
    font_stat = ImageFont.truetype(ARIAL_BLACK, 64)
    stats = [
        ("10M views", BLUE),
        ("0 shoots", WHITE),
        ("0 studio days", WHITE),
        ("$0 production", BLUE),
    ]
    y0 = 1020
    for i, (s, c) in enumerate(stats):
        draw.text((540, y0 + i * 100), s, font=font_stat,
                  fill=c, anchor="mm", stroke_fill=BLACK, stroke_width=3)

    # Kicker
    font_k = ImageFont.truetype(ARIAL_BOLD, 50)
    draw.text((540, 1500), "all of it was AI.", font=font_k,
              fill=(200, 200, 220), anchor="mm")

    # CTA
    text_pill(img, (540, 1660), "FREE SAMPLE ↓",
              ImageFont.truetype(ARIAL_BLACK, 56), bg=BLUE, fg=WHITE, pad_x=44, pad_y=22)

    watermark(img)
    out = os.path.join(OUT_DIR, "stat-card.png")
    img.save(out, "PNG")
    return out


# ============================================================
# 4. receipt.png — $12,400 strikethrough → $59
# Reuses the Higgsfield-generated invoice asset as background
# ============================================================
def make_receipt():
    invoice = Image.open(os.path.join(ASSETS, "invoice-12400.png")).convert("RGBA")
    invoice = invoice.resize((1080, 1920), Image.LANCZOS)
    # Add slight darkening on edges so overlay text pops
    img = invoice
    draw = ImageDraw.Draw(img)

    # Top label
    font_lab = ImageFont.truetype(ARIAL_BLACK, 42)
    text_stroke(draw, (540, 130), "WHAT BRANDS USED TO PAY", font_lab,
                fill=WHITE, stroke_fill=BLACK, stroke_w=5)

    # The big $12,400 lands on the invoice (it's in the image already)
    # Add diagonal red strikethrough (additional emphasis if not visible enough)
    # Already in source — skip drawing

    # Big "VS" tag in middle-bottom area
    font_vs = ImageFont.truetype(IMPACT, 140)
    text_stroke(draw, (540, 1200), "NOW IT'S", font_vs,
                fill=WHITE, stroke_fill=BLACK, stroke_w=10)

    # The $59 reveal in giant blue
    font_n = ImageFont.truetype(IMPACT, 300)
    text_stroke(draw, (540, 1430), "$59", font_n,
                fill=BLUE, stroke_fill=BLACK, stroke_w=14)

    # Tag line
    font_t = ImageFont.truetype(ARIAL_BLACK, 46)
    text_stroke(draw, (540, 1620), "48 hrs · AI · from 1 photo", font_t,
                fill=WHITE, stroke_fill=BLACK, stroke_w=4)

    # CTA pill
    text_pill(img, (540, 1740), "FREE SAMPLE ↓",
              ImageFont.truetype(ARIAL_BLACK, 56), bg=BLUE, fg=WHITE, pad_x=44, pad_y=22)

    watermark(img.convert("RGB"))
    out = os.path.join(OUT_DIR, "receipt.png")
    img.convert("RGB").save(out, "PNG")
    return out


if __name__ == "__main__":
    print("Building 4 image-native TikTok hooks...")
    for fn in [make_cost_split, make_imessage, make_stat_card, make_receipt]:
        path = fn()
        print(f"  ✓ {path}")
    print("Done.")
