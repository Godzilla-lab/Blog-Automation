#!/usr/bin/env python3
"""
TikTok image ads v4 — CLEAN DESIGN, REFINED TYPOGRAPHY.
Aesthetic: Stripe / Linear / Apple-style. No mixed fonts. No AI photo backgrounds.
Single font family (Avenir Next) at multiple weights for clean hierarchy.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = "madebyhexa-ads/tiktok-images"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"

# Font hierarchy via Avenir Next weights
def F(weight, size):
    idx = {"heavy": 8, "bold": 0, "demi": 2, "medium": 5, "regular": 7}[weight]
    return ImageFont.truetype(AVENIR, size=size, index=idx)

# Design tokens
BG_DARK = (8, 8, 14)
BG_DARK_2 = (16, 16, 26)
BG_LIGHT = (250, 250, 252)
TEXT_W = (255, 255, 255)
TEXT_W_DIM = (170, 170, 190)
TEXT_W_MUTED = (110, 110, 130)
TEXT_K = (16, 16, 24)
TEXT_K_DIM = (90, 90, 105)
TEXT_K_MUTED = (160, 160, 170)
BLUE = (0, 184, 255)
YELLOW = (255, 230, 40)
RED = (240, 60, 70)
DIVIDER_DARK = (50, 50, 70)
DIVIDER_LIGHT = (220, 220, 230)
CARD_BG = (255, 255, 255)
CARD_OUTLINE = (228, 228, 232)

URL = "madebyhexa.co/offer"
CTA_Y = 1380
URL_Y = 1470


def gradient_bg(size=(1080, 1920), top=BG_DARK, bottom=BG_DARK_2):
    img = Image.new("RGB", size, color=top)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / size[1]
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (size[0], y)], fill=c)
    return img


def radial_glow(img, center, color, radius, opacity=60):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = center
    gd.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)],
               fill=(*color, opacity))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius // 2))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def t(draw, xy, msg, font, fill=TEXT_W, anchor="mm"):
    draw.text(xy, msg, font=font, fill=fill, anchor=anchor)


def pill(img, xy, msg, font, bg=BLUE, fg=TEXT_W, px=44, py=22, arrow=False):
    """Pill button. If arrow=True, draws a custom ↓ triangle after the text."""
    d = ImageDraw.Draw(img)
    # Measure base text
    bbox = d.textbbox(xy, msg, font=font, anchor="mm")
    text_w = bbox[2] - bbox[0]
    arrow_gap = 18
    arrow_w = 28 if arrow else 0
    total_w = text_w + (arrow_gap + arrow_w if arrow else 0)
    cx, cy = xy
    text_cx = cx - (arrow_gap + arrow_w) // 2 if arrow else cx
    # Recompute box around composite
    half_w = total_w // 2
    half_h = (bbox[3] - bbox[1]) // 2
    box = (cx - half_w - px, cy - half_h - py,
           cx + half_w + px, cy + half_h + py)
    r = (box[3] - box[1]) // 2
    d.rounded_rectangle(box, radius=r, fill=bg)
    d.text((text_cx, cy), msg, font=font, fill=fg, anchor="mm")
    if arrow:
        # Custom down-triangle, sized to match cap-height
        ax = text_cx + text_w // 2 + arrow_gap + arrow_w // 2
        ay = cy
        s = 18
        d.polygon([(ax - s, ay - s + 2), (ax + s, ay - s + 2), (ax, ay + s)],
                  fill=fg)


def footer(img, cta_msg, dark_mode=True, cta_bg=BLUE):
    """Standard CTA pill (with down-arrow) + URL footer at safe-zone Y."""
    pill(img, (540, CTA_Y), cta_msg, F("heavy", 52), bg=cta_bg, fg=TEXT_W, arrow=True)
    d = ImageDraw.Draw(img)
    d.text((540, URL_Y), URL, font=F("demi", 28),
           fill=TEXT_W_MUTED if dark_mode else TEXT_K_MUTED, anchor="mm")


def hline(draw, y, width=440, color=DIVIDER_DARK, thickness=2):
    x = (1080 - width) // 2
    draw.line([(x, y), (x + width, y)], fill=color, width=thickness)


def x_mark(draw, xy, size=28, color=RED, w=10):
    cx, cy = xy
    draw.line([(cx - size, cy - size), (cx + size, cy + size)], fill=color, width=w)
    draw.line([(cx - size, cy + size), (cx + size, cy - size)], fill=color, width=w)


# ============================================================
# 1. j-without-x — Triple negation clean card
# ============================================================
def make_j():
    img = gradient_bg()
    img = radial_glow(img, (540, 250), BLUE, 600, opacity=35)
    d = ImageDraw.Draw(img)

    # Eyebrow
    t(d, (540, 200), "MADEBYHEXA", F("heavy", 28), fill=BLUE)

    # Hero
    t(d, (540, 360), "Cinematic ad.", F("heavy", 96), fill=TEXT_W)
    t(d, (540, 480), "48 hours.", F("heavy", 96), fill=BLUE)

    hline(d, 600, width=120)

    # Triple negation
    items = ["No studio.", "No crew.", "No shoot day."]
    for i, item in enumerate(items):
        y = 770 + i * 130
        x_mark(d, (300, y))
        t(d, (390, y), item, F("bold", 64), fill=TEXT_W, anchor="lm")

    # Kicker
    t(d, (540, 1230), "Made from one of your photos.",
      F("medium", 42), fill=TEXT_W_DIM)

    footer(img, "Get free 48-hr ad")
    img.save(os.path.join(OUT, "j-without-x.png"), "PNG")


# ============================================================
# 2. l-tenth-potential — 1/10th hero
# ============================================================
def make_l():
    img = gradient_bg()
    img = radial_glow(img, (540, 720), RED, 500, opacity=40)
    d = ImageDraw.Draw(img)

    t(d, (540, 180), "RUNNING META ADS WITH",
      F("heavy", 36), fill=TEXT_W_DIM)
    t(d, (540, 240), "THE SAME 3 PRODUCT SHOTS?",
      F("heavy", 36), fill=TEXT_W_DIM)

    # Hero
    t(d, (540, 580), "1/10th", F("heavy", 300), fill=RED)

    t(d, (540, 830), "of what AI can do",
      F("heavy", 60), fill=TEXT_W)
    t(d, (540, 900), "for your ROAS.",
      F("heavy", 60), fill=TEXT_W)

    hline(d, 1000, width=400)

    # Proof stack
    pill(img, (540, 1090), "100× cheaper than a shoot",
         F("heavy", 42), bg=(30, 30, 48), fg=BLUE, px=32, py=18)
    pill(img, (540, 1190), "48-hour turnaround",
         F("heavy", 42), bg=(30, 30, 48), fg=TEXT_W, px=32, py=18)

    footer(img, "Tap for $59 sample")
    img.save(os.path.join(OUT, "l-tenth-potential.png"), "PNG")


# ============================================================
# 3. cost-split — Refined split-screen
# ============================================================
def make_cost_split():
    img = Image.new("RGB", (1080, 1920), color=BG_DARK)
    d = ImageDraw.Draw(img)

    # Right half: light card
    d.rectangle([(540, 0), (1080, 1920)], fill=BG_LIGHT)

    # Eyebrows
    t(d, (270, 200), "STUDIO SHOOT",
      F("heavy", 32), fill=(220, 140, 140))
    t(d, (810, 200), "MADEBYHEXA",
      F("heavy", 32), fill=BLUE)

    # Hero numbers
    t(d, (270, 460), "$15K", F("heavy", 200), fill=TEXT_W)
    t(d, (810, 460), "$59", F("heavy", 200), fill=TEXT_K)

    # Sub
    t(d, (270, 620), "per shoot day", F("medium", 32), fill=(200, 150, 150))
    t(d, (810, 620), "per video", F("medium", 32), fill=(140, 140, 150))

    # Vertical divider
    d.line([(540, 150), (540, 1700)], fill=(70, 70, 90), width=2)

    # Comparison rows
    left = ["6 weeks", "studio", "crew of 8", "$50K+ total"]
    right = ["48 hours", "no studio", "no crew", "1 photo"]
    for i in range(4):
        y = 850 + i * 90
        t(d, (270, y), left[i], F("bold", 36), fill=(210, 130, 130))
        t(d, (810, y), right[i], F("bold", 36),
          fill=BLUE if i == 0 else TEXT_K)

    # Micro-disclaimer
    t(d, (270, 1240), "*typical 2026 agency cost",
      F("medium", 22), fill=(160, 100, 100))

    # CTA spans both halves
    pill(img, (540, CTA_Y), "Get your $59 ad",
         F("heavy", 52), bg=BLUE, fg=TEXT_W, arrow=True)
    # URL in both visual modes
    t(d, (540, URL_Y), URL, F("demi", 28), fill=(120, 120, 130))

    img.save(os.path.join(OUT, "cost-split.png"), "PNG")


# ============================================================
# 4. imessage — Clean iMessage (drawn in code)
# ============================================================
def make_imessage():
    img = Image.new("RGB", (1080, 1920), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # iOS status bar
    t(d, (60, 45), "9:41", F("heavy", 32), fill=TEXT_K, anchor="lm")
    t(d, (1020, 45), "•••• 5G", F("heavy", 32), fill=TEXT_K, anchor="rm")

    # Contact header
    d.rectangle([(0, 90), (1080, 230)], fill=(247, 247, 247))
    d.ellipse([(60, 110), (180, 230)], fill=(180, 200, 220))
    t(d, (120, 170), "S", F("heavy", 60), fill=TEXT_W)
    t(d, (220, 150), "Sarah · Brand owner",
      F("heavy", 40), fill=TEXT_K, anchor="lm")
    t(d, (220, 195), "iMessage",
      F("medium", 26), fill=(140, 140, 150), anchor="lm")
    d.line([(0, 230), (1080, 230)], fill=(220, 220, 220), width=2)

    IMSG_BLUE = (10, 132, 255)
    IMSG_GRAY = (229, 229, 234)

    def bubble(y, msg, side="left", max_w=720):
        font = F("bold", 44)
        words = msg.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if d.textbbox((0, 0), test, font=font)[2] > max_w:
                lines.append(cur); cur = w
            else:
                cur = test
        if cur: lines.append(cur)
        lh = 60
        h = len(lines) * lh + 50
        bw = max(d.textbbox((0, 0), l, font=font)[2] for l in lines) + 80
        if side == "left":
            box = (40, y, 40 + bw, y + h); bg, fg = IMSG_GRAY, TEXT_K
        else:
            box = (1080 - 40 - bw, y, 1080 - 40, y + h); bg, fg = IMSG_BLUE, TEXT_W
        d.rounded_rectangle(box, radius=40, fill=bg)
        for i, l in enumerate(lines):
            tx = box[0] + 40 if side == "left" else box[2] - 40
            d.text((tx, y + 30 + i * lh), l, font=font, fill=fg,
                   anchor="lm" if side == "left" else "rm")
        return y + h + 30

    y = 290
    y = bubble(y, "wait what did you spend on that ad?", side="left")
    y = bubble(y, "$59", side="right")
    y = bubble(y, "STOP. for that quality??", side="left")
    y = bubble(y, "AI made it in 48 hrs", side="right")
    y = bubble(y, "no studio?? send link", side="left")
    y = bubble(y, URL, side="right")

    # CTA + URL
    pill(img, (540, CTA_Y), "Free ad in 48 hrs",
         F("heavy", 52), bg=BLUE, fg=TEXT_W, arrow=True)
    t(d, (540, URL_Y), URL, F("demi", 28), fill=(120, 120, 130))

    img.save(os.path.join(OUT, "imessage.png"), "PNG")


# ============================================================
# 5. stat-card — 881K hero stat with quote
# ============================================================
def make_stat_card():
    img = gradient_bg()
    img = radial_glow(img, (540, 580), BLUE, 600, opacity=55)
    d = ImageDraw.Draw(img)

    t(d, (540, 180), "ONE CREATOR · 30 DAYS",
      F("heavy", 32), fill=TEXT_W_DIM)

    # Hero stat
    t(d, (540, 500), "881K", F("heavy", 340), fill=BLUE)
    t(d, (540, 740), "FOLLOWERS",
      F("heavy", 72), fill=TEXT_W)

    hline(d, 840, width=440)

    # Supporting stats
    stats = [
        ("10M views", BLUE),
        ("0 shoots · 0 studio days", TEXT_W),
        ("$0 production", BLUE),
    ]
    for i, (s, c) in enumerate(stats):
        t(d, (540, 920 + i * 70), s, F("heavy", 46), fill=c)

    # Quote kicker
    t(d, (540, 1220), '"all of it was AI."',
      F("medium", 40), fill=TEXT_W_DIM)

    footer(img, "Free $59 ad")
    img.save(os.path.join(OUT, "stat-card.png"), "PNG")


# ============================================================
# 6. receipt — Clean designed receipt card
# ============================================================
def make_receipt():
    img = Image.new("RGB", (1080, 1920), color=BG_LIGHT)
    d = ImageDraw.Draw(img)

    # Eyebrow
    t(d, (540, 140), "WHAT BRANDS USED TO PAY",
      F("heavy", 36), fill=(130, 130, 145))

    # Receipt card with subtle shadow
    # shadow
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shd = ImageDraw.Draw(sh)
    shd.rounded_rectangle([(125, 245), (965, 905)], radius=20,
                          fill=(20, 20, 30, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=12))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img)
    # card
    d.rounded_rectangle([(120, 240), (960, 900)], radius=20,
                        fill=CARD_BG, outline=CARD_OUTLINE, width=2)

    # Card content
    t(d, (540, 340), "STUDIO PRODUCTION QUOTE",
      F("heavy", 36), fill=(60, 60, 75))
    d.line([(180, 400), (900, 400)], fill=DIVIDER_LIGHT, width=1)

    t(d, (540, 470), "Brand Product Video",
      F("bold", 34), fill=(70, 70, 85))
    t(d, (540, 525), "One Shoot Day",
      F("medium", 28), fill=(140, 140, 150))

    # $15,000 with strikethrough
    t(d, (540, 700), "$15,000", F("heavy", 160), fill=TEXT_K)
    bbox = d.textbbox((540, 700), "$15,000", font=F("heavy", 160), anchor="mm")
    d.line([(bbox[0] - 30, bbox[3] - 40), (bbox[2] + 30, bbox[1] + 40)],
           fill=RED, width=14)

    # Micro-disclaimer below card
    t(d, (540, 945), "*typical 2026 agency cost",
      F("demi", 24), fill=(140, 140, 150))

    # NOW IT'S
    t(d, (540, 1050), "NOW IT'S",
      F("heavy", 80), fill=TEXT_K)

    # Yellow highlight box with $59
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([(260, 1130), (820, 1310)], radius=18,
                         fill=(*YELLOW, 255))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    t(d, (540, 1220), "$59", F("heavy", 180), fill=TEXT_K)

    # CTA
    pill(img, (540, CTA_Y), "Free 48-hr ad",
         F("heavy", 52), bg=BLUE, fg=TEXT_W, arrow=True)
    t(d, (540, URL_Y), URL, F("demi", 28), fill=(120, 120, 130))

    img.save(os.path.join(OUT, "receipt.png"), "PNG")


if __name__ == "__main__":
    print("Building 6 TikTok images v4 (clean Avenir Next type system)...")
    for fn in [make_j, make_l, make_cost_split, make_imessage, make_stat_card, make_receipt]:
        fn()
        print(f"  ✓ {fn.__name__}")
    print("Done.")
