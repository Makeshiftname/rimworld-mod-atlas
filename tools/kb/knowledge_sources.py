#!/usr/bin/env python3
"""Synchronize source-record links between records and knowledge pages.

``record.json.distilled_to`` is the authoritative direction.  Each target
knowledge page gets a generated ``## 来源记录`` section listing the records
that point to it.  The generated block is deliberately visible and bounded by
markers so a reviewer can see the provenance and the checker can detect drift.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LAYERS = ("guides", "reference", "mechanics", "sources")
HEADING = "## 来源记录"
START = "<!-- AUTO-GENERATED-SOURCE-START -->"
END = "<!-- AUTO-GENERATED-SOURCE-END -->"
SECTION_RE = re.compile(
    rf"(?ms)^{re.escape(HEADING)}\s*\n"
    rf"{re.escape(START)}.*?{re.escape(END)}\s*"
)


def relative(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def iter_pages(root: Path = ROOT) -> list[Path]:
    kb = root / "docs" / "knowledge"
    pages: list[Path] = []
    for layer in LAYERS:
        directory = kb / layer
        if directory.is_dir():
            pages.extend(p for p in directory.rglob("*.md") if p.name != "README.md")
    return sorted(pages)


def is_knowledge_target(root: Path, value: str) -> bool:
    """Return True only for Markdown pages inside a knowledge layer."""
    if not value or not value.endswith(".md") or Path(value).name == "README.md":
        return False
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return False
    target = (root / path).resolve()
    kb = (root / "docs" / "knowledge").resolve()
    try:
        rel = target.relative_to(kb)
    except ValueError:
        return False
    return len(rel.parts) >= 2 and rel.parts[0] in LAYERS


def load_links(root: Path = ROOT) -> tuple[dict[str, set[str]], list[str]]:
    """Return ``page -> record IDs`` plus validation problems."""
    links: dict[str, set[str]] = defaultdict(set)
    problems: list[str] = []
    for metadata_path in sorted((root / "records").glob("*/record.json")):
        try:
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{relative(metadata_path, root)}: {exc}")
            continue
        mod_id = str(data.get("id") or metadata_path.parent.name)
        targets = data.get("distilled_to", [])
        if not isinstance(targets, list):
            problems.append(f"{mod_id}: distilled_to must be a list")
            continue
        for target in targets:
            if not isinstance(target, str) or not is_knowledge_target(root, target):
                problems.append(
                    f"{mod_id}: distilled_to must be a Markdown page under "
                    f"docs/knowledge/{{guides,reference,mechanics,sources}}; got {target!r}"
                )
                continue
            if not (root / target).is_file():
                problems.append(f"{mod_id}: distilled_to target missing: {target}")
                continue
            links[target].add(mod_id)
    return dict(links), problems


def render_section(page: Path, ids: list[str], root: Path = ROOT) -> str:
    lines = [HEADING, "", START]
    for mod_id in sorted(ids):
        record_readme = root / "records" / mod_id / "README.md"
        link = os.path.relpath(record_readme, page.parent).replace("\\", "/")
        lines.append(f"- `{mod_id}` — [分析记录]({link})")
    lines.extend([END, ""])
    return "\n".join(lines)


def check_page(page: Path, ids: set[str], root: Path = ROOT) -> list[str]:
    text = page.read_text(encoding="utf-8", errors="replace")
    page_rel = relative(page, root)
    heading_count = len(re.findall(rf"(?m)^{re.escape(HEADING)}\s*$", text))
    if not ids:
        if heading_count:
            return [f"{page_rel}: stale 来源记录 section; no record lists this page"]
        return []
    if heading_count == 0:
        return [f"{page_rel}: missing 来源记录 section for {len(ids)} record(s)"]
    if heading_count > 1:
        return [f"{page_rel}: multiple 来源记录 sections"]
    expected = render_section(page, sorted(ids), root)
    if expected not in text:
        return [
            f"{page_rel}: 来源记录 section is stale; "
            "run tools/kb/sync_knowledge_sources.py --write"
        ]
    return []


def check_all(root: Path = ROOT) -> list[str]:
    links, problems = load_links(root)
    pages = iter_pages(root)
    known = {relative(page, root): page for page in pages}
    for target in links:
        if target not in known:
            problems.append(f"{target}: distilled_to target is not a scanned knowledge page")
    for page in pages:
        problems.extend(check_page(page, links.get(relative(page, root), set()), root))
    return problems


def sync_all(root: Path = ROOT, write: bool = False) -> tuple[list[str], list[str]]:
    links, problems = load_links(root)
    changed: list[str] = []
    for page in iter_pages(root):
        page_rel = relative(page, root)
        ids = links.get(page_rel, set())
        text = page.read_text(encoding="utf-8", errors="replace")
        if not ids:
            new_text = SECTION_RE.sub("", text)
            if HEADING in new_text:
                problems.append(
                    f"{page_rel}: manual 来源记录 section without generated markers"
                )
                continue
        else:
            expected = render_section(page, sorted(ids), root)
            if SECTION_RE.search(text):
                new_text = SECTION_RE.sub(expected, text, count=1)
            elif HEADING in text:
                problems.append(
                    f"{page_rel}: manual 来源记录 section without generated markers"
                )
                continue
            else:
                new_text = text.rstrip() + "\n\n" + expected
        if new_text != text:
            changed.append(page_rel)
            if write:
                page.write_text(new_text, encoding="utf-8")
    return changed, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite the generated sections")
    parser.add_argument("--check", action="store_true", help="fail when sections are stale")
    args = parser.parse_args()

    changed, problems = sync_all(ROOT, write=args.write)
    if args.check:
        problems = check_all(ROOT) + problems
    for page in changed:
        print(f"{'updated' if args.write else 'would update'}: {page}")
    if problems:
        print(f"knowledge source problems ({len(problems)}):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    if not args.write and not args.check:
        print("dry run only; pass --write to update generated sections")
    elif args.check:
        print("knowledge source links OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
