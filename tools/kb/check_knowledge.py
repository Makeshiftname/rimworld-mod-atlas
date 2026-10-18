#!/usr/bin/env python3
"""Check that knowledge pages are reachable from the knowledge index.

This is intentionally simple: the main README must link every Markdown page in
guides/reference/mechanics/sources (or a layer README must be linked and itself
contain the page).  It prevents reorganisations from leaving orphan docs behind.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
KB = ROOT / "docs" / "knowledge"
README = KB / "README.md"
LAYERS = ("guides", "reference", "mechanics", "sources")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def local_markdown_links(path: Path) -> set[Path]:
    text = path.read_text(encoding="utf-8", errors="replace")
    found = set()
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or "://" in target or target.startswith(("mailto:", "ftp:")):
            continue
        resolved = (path.parent / target).resolve()
        if resolved.suffix == ".md":
            found.add(resolved)
    return found


def reachable_from(start: Path) -> set[Path]:
    seen: set[Path] = set()
    queue = [start]
    while queue:
        current = queue.pop()
        if current in seen or not current.is_file():
            continue
        seen.add(current)
        for target in local_markdown_links(current):
            if target not in seen:
                queue.append(target)
        # A layer README is a hub; follow its direct links too.
        if current.name == "README.md" and current.parent.name in LAYERS:
            queue.extend(local_markdown_links(current))
    return seen


def main() -> int:
    problems = []
    reachable = reachable_from(README)
    for layer in LAYERS:
        directory = KB / layer
        if not directory.is_dir():
            problems.append(f"missing knowledge layer: {layer}")
            continue
        for page in sorted(directory.rglob("*.md")):
            if page.name == "README.md":
                continue
            if page.resolve() not in reachable:
                problems.append(f"orphan knowledge page: {page.relative_to(ROOT)}")
    if problems:
        print(f"knowledge entry problems ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("knowledge entry coverage OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
