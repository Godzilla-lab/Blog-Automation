#!/usr/bin/env python3
"""
BlogValidator: deterministic post-draft check that runs BEFORE any LLM eval.

Implements the indexing-guide §4 pre-publish checklist + writer-guide §§3, 5, 8
as code. Cheap, fast, no API calls. Any failure here is a hard signal to
regenerate before spending tokens on an LLM evaluator.

Usage as a module:
    from modules.blog_validator import validate_blog
    result = validate_blog(article_text_or_html, hexa_urls_dict)
    # result = {"passed": bool, "failures": [...], "stats": {...}}

Usage from CLI (for testing against an existing post):
    python -m modules.blog_validator <path-to-blog_post.md-or-article.html>
"""

import json
import os
import re
import sys
from pathlib import Path


# ---------- Limits & rules (single source of truth) ----------

WORD_COUNT_MIN = 1800
WORD_COUNT_MAX = 2200
INTERNAL_LINKS_MIN = 3
INTERNAL_LINKS_MAX = 5
EXTERNAL_LINKS_MIN = 6
EXTERNAL_LINKS_MAX = 12

# Banned phrases (writer guide §3 + indexing guide). Case-insensitive substring
# match unless the entry is a regex pattern (compiled below).
BANNED_PHRASES = [
    "in today's fast-paced",
    "in today's ever-evolving",
    "in today's rapidly-changing",
    "in today's digital",
    "delve into",
    "dive deep into",
    "unlock",
    "unleash",
    "supercharge",
    "revolutionize",
    "navigate the complexities",
    "robust",
    "seamless",
    "cutting-edge",
    "game-changing",
    "next-level",
    "it's important to note that",
    "it's worth noting that",
    "the ultimate guide to",
    "proven strategies for",
    "whether you're a small business or a large enterprise",
    "in conclusion,",
]

# "leverage" as a verb is banned, but "leverage" as a noun (financial leverage,
# operational leverage) is OK, AND compound adjectives like "highest-leverage
# starting point" are OK. The leading (?:^|\s) prevents matching inside a
# hyphenated compound (e.g. "highest-leverage"). The trailing alternation
# requires a determiner / gerund / past-participle, which is the verb pattern.
LEVERAGE_VERB = re.compile(r"(?:^|\s)leverage[ds]?\b\s+(the|a|an|our|your|their|its|these|those|some|all|any|new|existing|\w+ing\b|\w+ed\b)", re.IGNORECASE)

# First-hand experience signal — at least one of these must appear at least once
FIRST_HAND_PATTERNS = re.compile(
    r"\b("
    r"we built|we shipped|we[''']ve built|we[''']ve shipped|we[''']ve seen|we[''']ve done|"
    r"when we built|when we shipped|when we tried|when we ran|"
    r"the first time we|the last time we|"
    r"in our experience|across our engagements|across (our|the) engagements|"
    r"we ran this for|we did this for|"
    r"our team built|our team shipped"
    r")\b",
    re.IGNORECASE,
)

# TL;DR / Key Takeaways block — accept HTML aside/div or Markdown heading + bullets
TLDR_HTML = re.compile(r'<(div|aside)[^>]*class=["\'][^"\']*\btldr\b[^"\']*["\'][^>]*>', re.IGNORECASE)
TLDR_HEADING = re.compile(r'<h[23][^>]*>\s*(tl[;:]?\s*dr|key\s+takeaways)\s*</h[23]>', re.IGNORECASE)
TLDR_MD_HEADING = re.compile(r'^#{2,3}\s+(tl[;:]?\s*dr|key\s+takeaways)\b', re.IGNORECASE | re.MULTILINE)

# Em / en dash (existing brand rule, feedback_no_em_dashes.md)
DASH_PATTERN = re.compile(r"[—–]")  # — and –

# Brand spelling.
# WRONG_BRAND requires whitespace between Hex / AI / Agency so the regex catches
# the actual misspelling pattern (which a human types with spaces) but not the
# spaceless cal.com slug "hexaiagency", which is the legitimate booking URL.
WRONG_BRAND = re.compile(r"\bhex\s+ai\s+agency\b|\bhexaiagency\.com\b", re.IGNORECASE)
RIGHT_BRAND = re.compile(r"\bhexa\s*ai\s*agency\b|\bhexaaiagency\.com\b", re.IGNORECASE)

# Link extraction (Markdown + HTML)
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]+)\)")
HTML_LINK = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', re.IGNORECASE)

# §7 output sections that must be labelled in paste_sections.md
PASTE_SECTIONS = ["TITLE", "SLUG", "EXCERPT", "BODY", "COVER IMAGE BRIEF", "INTERNAL LINKS USED", "EXTERNAL CITATIONS USED"]


# ---------- Helpers ----------

def _strip_html_tags(html: str) -> str:
    """Crude HTML tag stripper. Good enough for word counting on a clean article."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _count_words(text: str) -> int:
    cleaned = _strip_html_tags(text) if "<" in text else text
    return len([w for w in re.split(r"\s+", cleaned) if w])


def _extract_links(text: str):
    """Return list of (href, anchor_text)."""
    links = []
    for m in MD_LINK.finditer(text):
        anchor, href = m.group(1), m.group(2)
        links.append((href, anchor))
    for m in HTML_LINK.finditer(text):
        href, anchor = m.group(1), m.group(2)
        links.append((href, anchor))
    return links


def _allowed_internal_paths(hexa_urls: dict) -> set:
    """Flatten hexa_urls.json into a set of allowed paths."""
    allowed = set()
    for category in ("services", "industries", "case_studies"):
        for entry in hexa_urls.get(category, []):
            allowed.add(entry["path"].rstrip("/"))
    return allowed


def _is_internal_link(href: str) -> bool:
    if href.startswith("/"):
        return True
    if "hexaaiagency.com" in href.lower():
        return True
    return False


def _normalize_internal_href(href: str) -> str:
    """Drop the domain prefix and trailing slash so /services/foo and https://hexaaiagency.com/services/foo compare equal."""
    if href.lower().startswith(("http://", "https://")):
        # Strip protocol + domain
        href = re.sub(r"^https?://[^/]+", "", href, flags=re.IGNORECASE)
    stripped = href.rstrip("/")
    return stripped if stripped else "/"


# ---------- The check itself ----------

def validate_blog(text: str, hexa_urls: dict) -> dict:
    """
    Run every deterministic check. Returns:
        {
          "passed": bool,
          "failures": [{"check": str, "detail": str}, ...],
          "stats": {"words": int, "internal_links": int, "external_links": int, ...}
        }
    """
    failures = []
    body_only = _strip_html_tags(text) if "<" in text else text
    word_count = _count_words(text)

    # 1. Word count
    if word_count < WORD_COUNT_MIN or word_count > WORD_COUNT_MAX:
        failures.append({
            "check": "word_count",
            "detail": f"{word_count} words; must be in [{WORD_COUNT_MIN}, {WORD_COUNT_MAX}]",
        })

    # 2. TL;DR block present
    has_tldr = bool(TLDR_HTML.search(text) or TLDR_HEADING.search(text) or TLDR_MD_HEADING.search(text))
    if not has_tldr:
        failures.append({
            "check": "tldr_missing",
            "detail": "no <div class=\"tldr\">, <aside class=\"tldr\">, or 'Key Takeaways' / 'TL;DR' heading found near the top",
        })

    # 3. Internal links: count + allowlist
    all_links = _extract_links(text)
    internal = [(h, a) for (h, a) in all_links if _is_internal_link(h)]
    external = [(h, a) for (h, a) in all_links if not _is_internal_link(h)]

    if len(internal) < INTERNAL_LINKS_MIN:
        failures.append({
            "check": "internal_links_too_few",
            "detail": f"{len(internal)} internal links; need >= {INTERNAL_LINKS_MIN}",
        })
    elif len(internal) > INTERNAL_LINKS_MAX:
        failures.append({
            "check": "internal_links_too_many",
            "detail": f"{len(internal)} internal links; max is {INTERNAL_LINKS_MAX} (link-stuffing risk)",
        })

    allowed = _allowed_internal_paths(hexa_urls)
    bad_internal = []
    for (h, _a) in internal:
        norm = _normalize_internal_href(h)
        # Allow /blog/<slug> and the root site links (homepage, /blog, /contact, /about) without allowlist check
        if norm.startswith("/blog/") or norm in ("/", "/blog", "/contact", "/about", "/about/team"):
            continue
        if norm not in allowed:
            bad_internal.append(h)
    if bad_internal:
        failures.append({
            "check": "internal_link_not_in_allowlist",
            "detail": f"these internal URLs are not in hexa_urls.json (likely 404): {bad_internal}",
        })

    # 4. External links: count
    if len(external) < EXTERNAL_LINKS_MIN:
        failures.append({
            "check": "external_links_too_few",
            "detail": f"{len(external)} external links; need >= {EXTERNAL_LINKS_MIN}",
        })
    elif len(external) > EXTERNAL_LINKS_MAX:
        failures.append({
            "check": "external_links_too_many",
            "detail": f"{len(external)} external links; max is {EXTERNAL_LINKS_MAX}",
        })

    # 5. Banned phrases
    body_lower = body_only.lower()
    hits = [p for p in BANNED_PHRASES if p in body_lower]
    if hits:
        failures.append({
            "check": "banned_phrases",
            "detail": f"AI-tell phrases present: {hits}",
        })
    if LEVERAGE_VERB.search(body_only):
        failures.append({
            "check": "leverage_as_verb",
            "detail": "'leverage' used as a verb; replace with 'use'",
        })

    # 6. Em/en dashes
    dash_count = len(DASH_PATTERN.findall(text))
    if dash_count:
        failures.append({
            "check": "em_or_en_dash",
            "detail": f"{dash_count} em/en dashes present; brand rule is hyphens or commas only",
        })

    # 7. Brand spelling
    if WRONG_BRAND.search(text):
        failures.append({
            "check": "brand_misspelled",
            "detail": "'Hex AI Agency' or 'hexaiagency.com' present; correct is 'Hexa AI Agency' / 'hexaaiagency.com'",
        })
    if not RIGHT_BRAND.search(text):
        failures.append({
            "check": "brand_missing",
            "detail": "neither 'Hexa AI Agency' nor 'hexaaiagency.com' appears anywhere in the post",
        })

    # 8. First-hand experience paragraph
    if not FIRST_HAND_PATTERNS.search(body_only):
        failures.append({
            "check": "first_hand_missing",
            "detail": "no first-hand-experience signal ('we built…', 'when we shipped…', 'in our experience…')",
        })

    stats = {
        "words": word_count,
        "internal_links": len(internal),
        "external_links": len(external),
        "internal_links_off_allowlist": len(bad_internal),
        "has_tldr": has_tldr,
        "has_first_hand": bool(FIRST_HAND_PATTERNS.search(body_only)),
        "em_en_dashes": dash_count,
        "banned_phrase_hits": hits,
    }

    return {"passed": len(failures) == 0, "failures": failures, "stats": stats}


def validate_paste_sections(paste_text: str) -> dict:
    """Check that paste_sections.md has every required §7 section label."""
    failures = []
    for section in PASTE_SECTIONS:
        # match `### TITLE`, `## TITLE`, `**TITLE**`, `Section 1 — TITLE`, etc.
        if not re.search(rf"\b{re.escape(section)}\b", paste_text):
            failures.append({"check": "paste_section_missing", "detail": f"missing section label: {section}"})
    return {"passed": len(failures) == 0, "failures": failures}


def critique_from_failures(failures: list) -> str:
    """Format failures as a critique string the writer prompt can consume on retry."""
    if not failures:
        return ""
    lines = ["The previous draft failed these mandatory checks. Fix every one of them in the next draft:"]
    for f in failures:
        lines.append(f"  - [{f['check']}] {f['detail']}")
    return "\n".join(lines)


# ---------- CLI ----------

def _load_hexa_urls() -> dict:
    """Locate hexa_urls.json relative to this module."""
    here = Path(__file__).resolve().parent
    candidates = [here.parent / "hexa_urls.json", Path.cwd() / "hexa_urls.json"]
    for p in candidates:
        if p.exists():
            with open(p) as f:
                return json.load(f)
    print(f"  ! hexa_urls.json not found in {candidates}", file=sys.stderr)
    return {"services": [], "industries": [], "case_studies": []}


def _cli():
    if len(sys.argv) < 2:
        print("usage: python -m modules.blog_validator <path-to-blog-file>")
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        sys.exit(2)
    text = path.read_text(encoding="utf-8")
    hexa_urls = _load_hexa_urls()
    result = validate_blog(text, hexa_urls)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    _cli()
