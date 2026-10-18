#!/usr/bin/env python3
"""Validate links and references in the knowledge base.

Checks:
  1. Every relative link in AGENTS.md, docs/knowledge/**/*.md and records/**/*.md resolves.
  2. Stable mod IDs in indexes/mods.json are unique.
  3. Every relative link in the architecture entrypoints resolves.

Usage:
  python tools/kb/check_links.py
Exit code 0 = all good, 1 = problems found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import kb_common as kb

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def iter_md_files() -> list[Path]:
    files = []
    for rel in ("AGENTS.md", "ARCHITECTURE.md", "README.md"):
        path = kb.REPO_ROOT / rel
        if path.exists():
            files.append(path)
    for root in (kb.KB_DIR, kb.REPO_ROOT / "records", kb.REPO_ROOT / "mods"):
        if root.is_dir():
            files.extend(sorted(root.rglob("*.md")))
    return sorted(set(files))


def check_file(path: Path, problems: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        problems.append(f"{path.relative_to(kb.REPO_ROOT)}: cannot read: {exc}")
        return
    rel = path.relative_to(kb.REPO_ROOT)
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "ftp://", "#")):
            continue
        if "://" in target:
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (path.parent / path_part).resolve()
        if not resolved.exists():
            problems.append(f"{rel}: broken link -> `{target}`")


def check_mod_ids(problems: list[str]) -> None:
    if not kb.INDEX_JSON.exists():
        problems.append("docs/knowledge/indexes/mods.json missing; run scan_mods.py first")
        return
    try:
        mods = json.loads(kb.INDEX_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        problems.append(f"docs/knowledge/indexes/mods.json: {exc}")
        return
    seen: dict[str, list[str]] = {}
    for mod in mods:
        seen.setdefault(mod["id"], []).append(mod["dir"])
    for mod_id, dirs in sorted(seen.items()):
        if len(dirs) > 1:
            problems.append(f"duplicate stable id {mod_id}: {', '.join(dirs)}")


def main() -> int:
    problems: list[str] = []
    for path in iter_md_files():
        check_file(path, problems)
    check_mod_ids(problems)
    if problems:
        print(f"Found {len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("All links and references OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
