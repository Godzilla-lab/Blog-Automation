#!/usr/bin/env python3
"""
Smoke test: imports + module sanity. Does NOT make API calls.

Run: cd blog-automation && python test_run.py
"""

import json
import os
import sys
from pathlib import Path


def main():
    failures = []

    # 1. Module imports
    try:
        from modules.claude_client import create_client
        from modules.social_generator import create_generator
        from modules.blog_research import research_blog_topic  # noqa: F401
        from modules.blog_validator import validate_blog, critique_from_failures
        from modules.blog_evaluator import evaluate_blog  # noqa: F401
        print("[OK] all modules import")
    except Exception as e:
        failures.append(f"module import: {e}")
        print(f"[FAIL] module import: {e}")

    # 2. hexa_urls.json exists and parses
    here = Path(__file__).resolve().parent
    urls_path = here / "hexa_urls.json"
    try:
        with open(urls_path) as f:
            hexa_urls = json.load(f)
        n = sum(len(hexa_urls.get(k, [])) for k in ("services", "industries", "case_studies"))
        print(f"[OK] hexa_urls.json: {n} allowed paths")
    except Exception as e:
        failures.append(f"hexa_urls.json: {e}")
        print(f"[FAIL] hexa_urls.json: {e}")
        return _exit(failures)

    # 3. Validator catches a malformed sample
    bad_html = "<p>Short post.</p>"
    result = validate_blog(bad_html, hexa_urls)
    if not result["passed"]:
        print(f"[OK] validator rejected a malformed sample: {len(result['failures'])} failures listed")
    else:
        failures.append("validator should have rejected the malformed sample but passed")
        print("[FAIL] validator did not catch the malformed sample")

    # 4. critique formatter produces a non-empty string when given failures
    critique = critique_from_failures(result["failures"])
    if critique and "Fix every one" in critique:
        print("[OK] critique formatter produced a non-empty critique")
    else:
        failures.append("critique formatter output is empty or malformed")
        print("[FAIL] critique formatter output looks wrong")

    # 5. Claude client constructable (without making an API call)
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            c = create_client()
            print(f"[OK] Claude client initialised (model={c.model})")
        except Exception as e:
            failures.append(f"claude client init: {e}")
            print(f"[FAIL] claude client init: {e}")
    else:
        print("[SKIP] Claude client init - ANTHROPIC_API_KEY not set")

    # 6. run_blog_post orchestrator imports + parses sections
    try:
        from run_blog_post import parse_sections
        sample = """### TITLE
My Post

### SLUG
my-post

### BODY (HTML)
<p>Body content.</p>
"""
        sections = parse_sections(sample)
        assert sections.get("TITLE", "").strip() == "My Post", f"got {sections.get('TITLE')!r}"
        assert sections.get("BODY", "").strip().startswith("<p>"), f"got {sections.get('BODY')!r}"
        print("[OK] run_blog_post.parse_sections works")
    except Exception as e:
        failures.append(f"parse_sections: {e}")
        print(f"[FAIL] parse_sections: {e}")

    return _exit(failures)


def _exit(failures):
    print()
    if failures:
        print(f"FAILED ({len(failures)} issues):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("SYSTEM READY")
    sys.exit(0)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
