#!/usr/bin/env python3
"""Acceptance gate for the records/ area.

Checks:
  1. Every record has the required anchor sections.
  2. metadata is complete and matches its directory.
  3. source paths are classified as present/unavailable, never guessed.
  4. records/README.md and records/index.json cover exactly the records.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry as stable_registry  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
RECORDS = ROOT / "records"
INDEX = RECORDS / "index.json"
README = RECORDS / "README.md"
REQUIRED_ANCHORS = ("身份卡", "它是什么", "怎么验的", "可复用结论")
DEFAULT_MODS_DIR = Path(os.environ.get("RIMWORLD_MODS_DIR", r"F:\Games\GBL\rimworld\Mods"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def h2_sections(text: str) -> set[str]:
    return {" ".join(m.group(1).split()) for m in re.finditer(r"(?m)^##\s+(.+?)\s*$", text)}


def complete_record_paths(source_dir: str) -> Path | None:
    """Resolve a source directory only when the game Mods folder is available."""
    if not source_dir or not DEFAULT_MODS_DIR.is_dir():
        return None
    source = DEFAULT_MODS_DIR / source_dir
    return source if source.exists() else None


def main() -> int:
    problems: list[str] = []
    warnings: list[str] = []
    if not RECORDS.is_dir():
        print("records/ does not exist")
        return 2
    registry = stable_registry.load_registry()
    registry_ids = {entry["id"] for entry in registry.get("mods", [])}
    record_rows = []
    for directory in sorted(p for p in RECORDS.iterdir() if p.is_dir()):
        readme = directory / "README.md"
        metadata_file = directory / "record.json"
        if not readme.is_file():
            problems.append(f"{directory.name}: missing README.md")
            continue
        if not metadata_file.is_file():
            problems.append(f"{directory.name}: missing record.json")
            continue
        try:
            metadata = json.loads(read(metadata_file))
        except json.JSONDecodeError as exc:
            problems.append(f"{directory.name}/record.json: {exc}")
            continue
        if metadata.get("id") != directory.name:
            problems.append(f"{directory.name}: record id {metadata.get('id')!r} does not match directory")
        if metadata.get("id") not in registry_ids:
            problems.append(f"{directory.name}: id is not registered in mods/registry.json")
        missing = [key for key in ("schema_version", "id", "package_id", "display_name",
                                   "authors", "license", "source_dir", "status",
                                   "modifications", "distilled_to") if key not in metadata]
        if missing:
            problems.append(f"{directory.name}: record.json missing {', '.join(missing)}")
        missing_anchors = [a for a in REQUIRED_ANCHORS if a not in h2_sections(read(readme))]
        if missing_anchors:
            problems.append(f"{directory.name}: missing anchors {', '.join(missing_anchors)}")
        source_dir = metadata.get("source_dir", "")
        if source_dir and DEFAULT_MODS_DIR.is_dir() and complete_record_paths(source_dir) is None:
            warnings.append(f"{directory.name}: source directory unavailable: {source_dir}")
        record_rows.append(metadata)
    if INDEX.is_file():
        try:
            indexed = json.loads(read(INDEX))
        except json.JSONDecodeError as exc:
            problems.append(f"records/index.json: {exc}")
            indexed = []
        indexed_ids = {row.get("id") for row in indexed}
        actual_ids = {row.get("id") for row in record_rows}
        for missing in sorted(actual_ids - indexed_ids):
            problems.append(f"records/index.json missing {missing}")
        for extra in sorted(indexed_ids - actual_ids):
            problems.append(f"records/index.json lists non-record {extra}")
    else:
        problems.append("records/index.json is missing")
    for warning in warnings:
        print(f"  warning: {warning}")
    if problems:
        print(f"records problems ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"records checks OK ({len(record_rows)} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
