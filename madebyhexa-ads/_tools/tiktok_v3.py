#!/usr/bin/env python3
"""
TikTok image ads v3 — CLEAN DESIGNED.
No AI-generated photographic backgrounds. Pure typography on solid/gradient
backgrounds. Apple/Linear/Stripe-style aesthetic.

Six images:
  1. j-checklist     — clean triple-negation card (replaces sticky note)
  2. l-tenth         — 1/10th hero stat card
  3. cost-split      — clean split-screen $15K vs $59
  4. imessage        — clean iMessage screenshot (kept — drawn in code, not AI)
  5. stat-card       — 881K hero stat card with quote
  6. receipt-clean   — clean receipt-style $12,400 → $59 reveal
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = "madebyhexa-ads/tiktok-images"

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
ARIAL_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"
BRADLEY = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"

# Design tokens — restrained palette
BG_DARK = (10, 10, 16)
BG_DARK_2 = (18, 18, 28)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (160, 160, 180)
TEXT_MUTED = (110, 110, 130)
ACCENT_BLUE = (0, 184, 255)
ACCENT_YELLOW = (255, 230, 40)
ACCENT_RED = (240, 60, 70)
ACCENT_GREEN = (60, 220, 130)

URL = "madebyhexa.co/offer"
CTA_Y = 1380


def gradient_bg(size=(1080, 1920), top=BG_DARK, bottom=BG_DARK_2):
    """Subtle vertical gradient background."""
    img = Image.new("RGB", size, color=top)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / size[1]
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (size[0], y)], fill=c)
    return img


def radial_glow(img, center, color, radius, opacity=80):
    """Soft radial glow at a point."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = center
    gd.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)],
               fill=(*color, opacity))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius // 2))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def text(draw, xy, msg, font, fill=TEXT_PRIMARY, anchor="mm"):
    draw.text(xy, msg, font=font, fill=fill, anchor=anchor)


def text_pill(img, xy, msg, font, bg=ACCENT_BLUE, fg=TEXT_PRIMARY, px=44, py=22):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox(xy, msg, font=font, anchor="mm")
    box = (bbox[0] - px, bbox[1] - py, bbox[2] + px, bbox[3] + py)
    r = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=r, fill=bg)
    draw.text(xy, msg, font=font, fill=fg, anchor="mm")


def cta_and_url(img, cta_text, cta_bg=ACCENT_BLUE):
    """Standard footer: CTA pill at safe-zone Y, small URL below."""
    text_pill(img, (540, CTA_Y), cta_text,
              ImageFont.truetype(ARIAL_BLACK, 54), bg=cta_bg, fg=TEXT_PRIMARY)
    draw = ImageDraw.Draw(img)
    draw.text((540, 1470), URL, font=ImageFont.truetype(ARIAL_BOLD, 28),
              fill=TEXT_MUTED, anchor="mm")


def divider(draw, y, width=540, color=None, thickness=2):
    color = color or TEXT_MUTED
    x = (1080 - width) // 2
    draw.line([(x, y), (x + width, y)], fill=color, width=thickness)


# ============================================================
# 1. j-checklist — clean triple-negation card
# ============================================================
def make_j():
    img = gradient_bg(top=BG_DARK, bottom=BG_DARK_2)
    img = radial_glow(img, (540, 200), ACCENT_BLUE, 500, opacity=40)
    draw = ImageDraw.Draw(img)

    text(draw, (540, 200), "MADEBYHEXA",
         ImageFont.truetype(ARIAL_BLACK, 36), fill=ACCENT_BLUE)

    # Hero
    text(draw, (540, 360), "CINEMATIC AD",
         ImageFont.truetype(IMPACT, 130), fill=TEXT_PRIMARY)
    text(draw, (540, 490), "IN 48 HOURS.",
         ImageFont.truetype(IMPACT, 130), fill=ACCENT_BLUE)

    divider(draw, 620, width=200, color=TEXT_MUTED, thickness=3)

    # Triple negation as a clean checklist
    items = ["No studio.", "No crew.", "No shoot day."]
    font_item = ImageFont.truetype(ARIAL_BLACK, 64)
    for i, item in enumerate(items):
        y = 760 + i * 110
        # Red ✗ via two diagonal strokes
        cx, cy, s = 280, y, 32
        draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=ACCENT_RED, width=12)
        draw.line([(cx - s, cy + s), (cx + s, cy - s)], fill=ACCENT_RED, width=12)
        text(draw, (370, y), item, font_item, fill=TEXT_PRIMARY, anchor="lm")

    # Made from one of your photos kicker
    text(draw, (540, 1180), "Made from one of your photos.",
         ImageFont.truetype(ARIAL_BOLD, 38), fill=TEXT_SECONDARY)

    cta_and_url(img, "Get free 48-hr ad ↓")
    img.save(os.path.join(OUT, "j-without-x.png"), "PNG")


# ============================================================
# 2. l-tenth — 1/10th hero stat card
# ============================================================
def make_l():
    img = gradient_bg(top=BG_DARK, bottom=BG_DARK_2)
    img = radial_glow(img, (540, 700), ACCENT_RED, 600, opacity=50)
    draw = ImageDraw.Draw(img)

    text(draw, (540, 200), "IF YOU'RE RUNNING META ADS",
         ImageFont.truetype(ARIAL_BLACK, 38), fill=TEXT_SECONDARY)
    text(draw, (540, 280), "WITH THE SAME 3 PRODUCT SHOTS",
         ImageFont.truetype(ARIAL_BLACK, 38), fill=TEXT_SECONDARY)

    # Hero
    text(draw, (540, 540), "1/10th",
         ImageFont.truetype(IMPACT, 320), fill=ACCENT_RED)

    text(draw, (540, 800), "of what AI can do",
         ImageFont.truetype(ARIAL_BLACK, 64), fill=TEXT_PRIMARY)
    text(draw, (540, 880), "for your ROAS",
         ImageFont.truetype(ARIAL_BLACK, 64), fill=TEXT_PRIMARY)

    divider(draw, 980, width=400)

    # Proof bars
    text_pill(img, (540, 1090), "100× cheaper than a shoot",
              ImageFont.truetype(ARIAL_BLACK, 46), bg=(35, 35, 50),
              fg=ACCENT_BLUE, px=32, py=18)
    text_pill(img, (540, 1190), "48-hour turnaround",
              ImageFont.truetype(ARIAL_BLACK, 46), bg=(35, 35, 50),
              fg=TEXT_PRIMARY, px=32, py=18)

    cta_and_url(img, "Tap for $59 sample ↓")
    img.save(os.path.join(OUT, "l-tenth-potential.png"), "PNG")


# ============================================================
# 3. cost-split — clean split-screen $15K vs $59
# ============================================================
def make_cost_split():
    img = Image.new("RGB", (1080, 1920), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    # Right half white panel
    draw.rectangle([(540, 0), (1080, 1920)], fill=(248, 248, 250))

    # Headline labels
    text(draw, (270, 200), "STUDIO SHOOT",
         ImageFont.truetype(ARIAL_BLACK, 38), fill=(180, 80, 80))
    text(draw, (810, 200), "MADEBYHEXA",
         ImageFont.truetype(ARIAL_BLACK, 38), fill=ACCENT_BLUE)

    # Hero numbers
    text(draw, (270, 440), "$15K",
         ImageFont.truetype(IMPACT, 220), fill=TEXT_PRIMARY)
    text(draw, (810, 440), "$59",
         ImageFont.truetype(IMPACT, 220), fill=(20, 20, 30))

    # Sub
    text(draw, (270, 600), "per shoot day",
         ImageFont.truetype(ARIAL_BOLD, 36), fill=(180, 130, 130))
    text(draw, (810, 600), "per video",
         ImageFont.truetype(ARIAL_BOLD, 36), fill=(110, 110, 120))

    # Divider
    draw.line([(540, 130), (540, 1680)], fill=(80, 80, 95), width=4)

    # Comparison rows
    rows_left = ["6 weeks", "studio", "crew of 8", "$50K+ total"]
    rows_right = ["48 hours", "no studio", "no crew", "1 photo"]
    font_li = ImageFont.truetype(ARIAL_BLACK, 38)
    for i in range(4):
        y = 830 + i * 90
        text(draw, (270, y), rows_left[i], font_li, fill=(220, 130, 130))
        text(draw, (810, y), rows_right[i], font_li,
             fill=ACCENT_BLUE if i == 0 else (30, 30, 40))

    # Micro-disclaimer
    text(draw, (270, 1240), "*typical 2026 agency cost",
         ImageFont.truetype(ARIAL_BOLD, 22), fill=(160, 100, 100))

    # CTA pill spans both halves
    text_pill(img, (540, CTA_Y), "Get your $59 ad ↓",
              ImageFont.truetype(ARIAL_BLACK, 54), bg=ACCENT_BLUE, fg=TEXT_PRIMARY)
    draw.text((540, 1470), URL, font=ImageFont.truetype(ARIAL_BOLD, 28),
              fill=(120, 120, 130), anchor="mm")
    img.save(os.path.join(OUT, "cost-split.png"), "PNG")


# ============================================================
# 4. imessage — clean iMessage screenshot (drawn in code, not AI)
# ============================================================
def make_imessage():
    img = Image.new("RGB", (1080, 1920), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Status bar
    text(draw, (60, 45), "9:41", ImageFont.truetype(ARIAL_BOLD, 32),
         fill=BG_DARK, anchor="lm")
    text(draw, (1020, 45), "•••• 5G", ImageFont.truetype(ARIAL_BOLD, 32),
         fill=BG_DARK, anchor="rm")

    # Contact header
    draw.rectangle([(0, 90), (1080, 230)], fill=(247, 247, 247))
    draw.ellipse([(60, 110), (180, 230)], fill=(180, 200, 220))
    text(draw, (120, 170), "S", ImageFont.truetype(ARIAL_BLACK, 60), fill=TEXT_PRIMARY)
    text(draw, (220, 150), "Sarah · Brand owner",
         ImageFont.truetype(ARIAL_BLACK, 42), fill=BG_DARK, anchor="lm")
    text(draw, (220, 195), "iMessage",
         ImageFont.truetype(ARIAL, 28), fill=(140, 140, 140), anchor="lm")
    draw.line([(0, 230), (1080, 230)], fill=(220, 220, 220), width=2)

    IMSG_BLUE = (10, 132, 255)
    IMSG_GRAY = (229, 229, 234)

    def bubble(y, msg, side="left", max_w=720):
        font = ImageFont.truetype(ARIAL_BOLD, 44)
        words = msg.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textbbox((0, 0), test, font=font)[2] > max_w:
                lines.append(cur); cur = w
            else:
                cur = test
        if cur: lines.append(cur)
        line_h = 60
        height = len(lines) * line_h + 50
        bbox_w = max(draw.textbbox((0, 0), l, font=font)[2] for l in lines)
        bw = bbox_w + 80
        if side == "left":
            box = (40, y, 40 + bw, y + height); bg, fg = IMSG_GRAY, BG_DARK
        else:
            box = (1080 - 40 - bw, y, 1080 - 40, y + height); bg, fg = IMSG_BLUE, TEXT_PRIMARY
        draw.rounded_rectangle(box, radius=40, fill=bg)
        for i, l in enumerate(lines):
            tx = box[0] + 40 if side == "left" else box[2] - 40
            draw.text((tx, y + 30 + i * line_h), l, font=font, fill=fg,
                      anchor="lm" if side == "left" else "rm")
        return y + height + 30

    y = 290
    y = bubble(y, "wait what did you spend on that ad?", side="left")
    y = bubble(y, "$59", side="right")
    y = bubble(y, "STOP. for that quality??", side="left")
    y = bubble(y, "AI made it in 48 hrs", side="right")
    y = bubble(y, "no studio?? send link", side="left")
    y = bubble(y, URL, side="right")

    # CTA
    text_pill(img, (540, CTA_Y), "Free ad in 48 hrs ↓",
              ImageFont.truetype(ARIAL_BLACK, 54), bg=ACCENT_BLUE, fg=TEXT_PRIMARY)
    draw.text((540, 1470), URL, font=ImageFont.truetype(ARIAL_BOLD, 28),
              fill=(120, 120, 130), anchor="mm")
    img.save(os.path.join(OUT, "imessage.png"), "PNG")


# ============================================================
# 5. stat-card — 881K hero stat card with verbatim quote
# ============================================================
def make_stat_card():
    img = gradient_bg(top=BG_DARK, bottom=BG_DARK_2)
    img = radial_glow(img, (540, 600), ACCENT_BLUE, 600, opacity=50)
    draw = ImageDraw.Draw(img)

    text(draw, (540, 180), "ONE CREATOR · 30 DAYS",
         ImageFont.truetype(ARIAL_BLACK, 38), fill=TEXT_SECONDARY)

    # Hero stat
    text(draw, (540, 480), "881K",
         ImageFont.truetype(IMPACT, 360), fill=ACCENT_BLUE)
    text(draw, (540, 730), "FOLLOWERS",
         ImageFont.truetype(ARIAL_BLACK, 76), fill=TEXT_PRIMARY)

    divider(draw, 830, width=440)

    # Supporting stats
    stats = [
        ("10M views", ACCENT_BLUE),
        ("0 shoots · 0 studio days", TEXT_PRIMARY),
        ("$0 production", ACCENT_BLUE),
    ]
    for i, (s, c) in enumerate(stats):
        text(draw, (540, 920 + i * 70), s,
             ImageFont.truetype(ARIAL_BLACK, 50), fill=c)

    # Italic kicker
    text(draw, (540, 1200), '"all of it was AI."',
         ImageFont.truetype(ARIAL_BOLD, 40), fill=TEXT_SECONDARY)

    cta_and_url(img, "Free $59 ad ↓")
    img.save(os.path.join(OUT, "stat-card.png"), "PNG")


# ============================================================
# 6. receipt — clean designed receipt $15K → $59
# ============================================================
def make_receipt():
    img = Image.new("RGB", (1080, 1920), color=(248, 248, 248))
    draw = ImageDraw.Draw(img)

    # Top label
    text(draw, (540, 130), "WHAT BRANDS USED TO PAY",
         ImageFont.truetype(ARIAL_BLACK, 38), fill=(120, 120, 130))

    # Receipt card (white rectangle with shadow effect)
    draw.rectangle([(120, 230), (960, 870)], fill=(255, 255, 255),
                   outline=(220, 220, 230), width=2)

    # Receipt content
    text(draw, (540, 320), "STUDIO PRODUCTION QUOTE",
         ImageFont.truetype(ARIAL_BLACK, 36), fill=(60, 60, 70))
    draw.line([(180, 380), (900, 380)], fill=(220, 220, 230), width=1)

    text(draw, (540, 440), "Brand Product Video",
         ImageFont.truetype(ARIAL_BOLD, 32), fill=(80, 80, 90))
    text(draw, (540, 490), "One Shoot Day",
         ImageFont.truetype(ARIAL, 28), fill=(140, 140, 150))

    # $15,000 with strikethrough
    font_old = ImageFont.truetype(IMPACT, 150)
    text(draw, (540, 660), "$15,000", font_old, fill=(40, 40, 50))
    bbox = draw.textbbox((540, 660), "$15,000", font=font_old, anchor="mm")
    draw.line([(bbox[0] - 30, bbox[3] - 40), (bbox[2] + 30, bbox[1] + 40)],
              fill=ACCENT_RED, width=12)

    # Micro-disclaimer
    text(draw, (540, 800), "*typical 2026 agency cost",
         ImageFont.truetype(ARIAL_BOLD, 24), fill=(140, 140, 150))

    # NOW IT'S transition
    text(draw, (540, 980), "NOW IT'S",
         ImageFont.truetype(IMPACT, 100), fill=(20, 20, 30))

    # Yellow highlight box with $59
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([(260, 1110), (820, 1290)], radius=18,
                         fill=(*ACCENT_YELLOW, 255))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    text(draw, (540, 1200), "$59",
         ImageFont.truetype(IMPACT, 170), fill=(20, 20, 30))

    # CTA
    text_pill(img, (540, CTA_Y), "Free 48-hr ad ↓",
              ImageFont.truetype(ARIAL_BLACK, 54), bg=ACCENT_BLUE, fg=TEXT_PRIMARY)
    draw.text((540, 1470), URL, font=ImageFont.truetype(ARIAL_BOLD, 28),
              fill=(120, 120, 130), anchor="mm")
    img.save(os.path.join(OUT, "receipt.png"), "PNG")


if __name__ == "__main__":
    print("Building 6 clean designed TikTok images (v3)...")
    for fn in [make_j, make_l, make_cost_split, make_imessage, make_stat_card, make_receipt]:
        fn()
        print(f"  ✓ {fn.__name__}")
    print("Done.")
