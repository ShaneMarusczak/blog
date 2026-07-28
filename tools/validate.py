#!/usr/bin/env python3
"""Validate the build sources before generating.

Checks that posts.json is well formed, that every entry has the keys the
templates need, that a content fragment exists for each post, and that no
fragment is orphaned. It does NOT check the generated HTML — that's the
build's job, and CI separately rebuilds and fails on any drift.

    python3 tools/validate.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "posts"
REQUIRED = ("file", "title", "date", "category", "description")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def main() -> int:
    try:
        posts = json.loads((ROOT / "posts.json").read_text())
    except json.JSONDecodeError as e:
        print(f"posts.json is not valid JSON: {e}")
        return 1

    if not isinstance(posts, list) or not posts:
        print("posts.json must be a non-empty list")
        return 1

    referenced: set[str] = set()

    for i, post in enumerate(posts):
        label = post.get("file") or f"entry {i}"

        for key in REQUIRED:
            if not post.get(key):
                err(f"{label}: missing or empty '{key}'")
        if not all(post.get(k) for k in REQUIRED):
            continue

        if post["file"] in referenced:
            err(f"{label}: listed twice in posts.json")
        referenced.add(post["file"])

        if not DATE_RE.match(post["date"]):
            err(f"{label}: date '{post['date']}' is not YYYY-MM-DD")

        if not (CONTENT / post["file"]).is_file():
            err(f"{label}: no content fragment at content/posts/{post['file']}")

    for fragment in sorted(CONTENT.glob("*.html")):
        if fragment.name not in referenced:
            err(f"{fragment.name}: content fragment not listed in posts.json")

    if errors:
        print(f"{len(errors)} problem(s) found:\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK - {len(posts)} posts, sources consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
