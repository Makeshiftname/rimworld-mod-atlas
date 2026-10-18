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
import knowledge_sources  # noqa: E402
import registry as stable_registry  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
RECORDS = ROOT / "records"
INDEX = RECORDS / "index.json"
README = RECORDS / "README.md"
REQUIRED_ANCHORS = ("身份卡", "它是什么", "怎么验的", "可复用结论")
MODS_DIR_ENV = os.environ.get("RIMWORLD_MODS_DIR", "").strip()
DEFAULT_MODS_DIR = Path(MODS_DIR_ENV) if MODS_DIR_ENV else None
STATUSES = {"raw", "analyzed", "needs-recheck", "superseded", "retired"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def h2_sections(text: str) -> set[str]:
    return {" ".join(m.group(1).split()) for m in re.finditer(r"(?m)^##\s+(.+?)\s*$", text)}


def complete_record_paths(source_dir: str) -> Path | None:
    """Resolve a source directory only when the game Mods folder is available."""
    if not source_dir or DEFAULT_MODS_DIR is None or not DEFAULT_MODS_DIR.is_dir():
        return None
    source = DEFAULT_MODS_DIR / source_dir
    return source if source.exists() else None


def safe_relative(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def main() -> int:
    problems: list[str] = []
    warnings: list[str] = []
    if not RECORDS.is_dir():
        print("records/ does not exist")
        return 2
    registry = stable_registry.load_registry()
    registry_entries = {entry["id"]: entry for entry in registry.get("objects", [])}
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
        registry_entry = registry_entries.get(metadata.get("id"))
        if registry_entry is None:
            problems.append(f"{directory.name}: id is not registered in mods/registry.json")
        else:
            if metadata.get("package_id") != registry_entry.get("package_id"):
                problems.append(
                    f"{directory.name}: package_id {metadata.get('package_id')!r} "
                    f"!= registry {registry_entry.get('package_id')!r}"
                )
            if metadata.get("origin") != registry_entry.get("origin"):
                problems.append(
                    f"{directory.name}: origin {metadata.get('origin')!r} "
                    f"!= registry {registry_entry.get('origin')!r}"
                )
            record = registry_entry.get("record") or {}
            if record.get("path") != f"records/{directory.name}":
                problems.append(
                    f"{directory.name}: registry record.path "
                    f"{record.get('path')!r} != records/{directory.name}"
                )
        missing = [key for key in ("schema_version", "id", "package_id", "display_name",
                                   "authors", "license", "source_dir", "status",
                                   "modifications", "distilled_to") if key not in metadata]
        if missing:
            problems.append(f"{directory.name}: record.json missing {', '.join(missing)}")
        if not isinstance(metadata.get("schema_version"), int):
            problems.append(f"{directory.name}: schema_version must be an integer")
        elif metadata["schema_version"] < 2:
            warnings.append(f"{directory.name}: legacy record schema_version {metadata['schema_version']}")
        if metadata.get("origin") not in (None, "owned", "collected"):
            problems.append(f"{directory.name}: invalid origin {metadata.get('origin')!r}")
        if metadata.get("status") not in STATUSES:
            problems.append(f"{directory.name}: invalid status {metadata.get('status')!r}")
        if not metadata.get("display_name"):
            problems.append(f"{directory.name}: display_name is empty")
        authors = metadata.get("authors")
        if not isinstance(authors, list) or not authors or not all(
            isinstance(author, str) and author.strip() for author in authors
        ):
            problems.append(f"{directory.name}: authors must be a non-empty list of strings")
        license_value = metadata.get("license")
        if not isinstance(license_value, str) or not license_value.strip():
            problems.append(
                f"{directory.name}: license must be explicit; use '未声明' when no license exists"
            )
        if "author_evidence" in metadata and (
            not isinstance(metadata["author_evidence"], list)
            or not all(isinstance(item, str) and item.strip()
                       for item in metadata["author_evidence"])
        ):
            problems.append(f"{directory.name}: author_evidence must be a list of strings")
        if "license_notes" in metadata and not isinstance(metadata["license_notes"], str):
            problems.append(f"{directory.name}: license_notes must be a string")
        if not isinstance(metadata.get("modifications"), list):
            problems.append(f"{directory.name}: modifications must be a list")
        if not isinstance(metadata.get("distilled_to"), list) or not all(
            isinstance(path, str) for path in metadata.get("distilled_to", [])
        ):
            problems.append(f"{directory.name}: distilled_to must be a list of strings")
        for distilled in metadata.get("distilled_to", []):
            if not safe_relative(distilled) or not knowledge_sources.is_knowledge_target(
                ROOT, distilled
            ):
                problems.append(
                    f"{directory.name}: distilled_to must point to a knowledge page: {distilled}"
                )
            elif not (ROOT / distilled).exists():
                problems.append(f"{directory.name}: distilled_to target missing: {distilled}")
        source_dir = metadata.get("source_dir", "")
        if source_dir and not safe_relative(source_dir):
            problems.append(f"{directory.name}: unsafe source_dir {source_dir!r}")
        if "verification_tier" in metadata:
            tier = metadata["verification_tier"]
            if tier not in (None, 1, 2, 3, 4):
                problems.append(f"{directory.name}: verification_tier must be 1-4 or null")
        if "code_removed" in metadata and not isinstance(metadata["code_removed"], bool):
            problems.append(f"{directory.name}: code_removed must be boolean")
        if "source_url" in metadata and not isinstance(metadata["source_url"], str):
            problems.append(f"{directory.name}: source_url must be a string")
        if "workshop_id" in metadata and not isinstance(metadata["workshop_id"], (str, int)):
            problems.append(f"{directory.name}: workshop_id must be a string or integer")
        if "retrieved_at" in metadata and not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", str(metadata["retrieved_at"])
        ):
            problems.append(f"{directory.name}: retrieved_at must be YYYY-MM-DD")
        missing_anchors = [a for a in REQUIRED_ANCHORS if a not in h2_sections(read(readme))]
        if missing_anchors:
            problems.append(f"{directory.name}: missing anchors {', '.join(missing_anchors)}")
        if source_dir and DEFAULT_MODS_DIR is not None and DEFAULT_MODS_DIR.is_dir() \
                and complete_record_paths(source_dir) is None:
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
