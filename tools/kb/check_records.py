#!/usr/bin/env python3
"""Acceptance gate for the records/ area.

The record contract has two tiers:

* ``initial``: identity, a quick scope check, explicit verified/unverified
  lists, and next steps.  It cannot be distilled or carry modifications.
* ``deep``: the four-anchor analysis, with conditional evidence sections and
  distillation allowed only while the record is ``analyzed``.

The checker validates structure and metadata, not the truth of prose.  It does
not keyword-scan for negative claims; conditional evidence (positive control,
self-correction, scope, unverified boundaries) is a review rule in
``records/STANDARD.md``.
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
SCHEMA_VERSION = 3
MODS_DIR_ENV = os.environ.get("RIMWORLD_MODS_DIR", "").strip()
DEFAULT_MODS_DIR = Path(MODS_DIR_ENV) if MODS_DIR_ENV else None
STATUSES = {"analyzed", "needs-recheck", "superseded", "retired"}
INITIAL_ANCHORS = ("身份卡", "它是什么", "初步核验", "下一步")
DEEP_ANCHORS = ("身份卡", "它是什么", "怎么验的", "可复用结论")
INITIAL_SUBSECTIONS = ("已核验", "未核验")
DEEP_OPTIONAL_SUBSECTIONS = ("范围", "方法", "阳性对照", "自查纠错", "未核验")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def h2_sections(text: str) -> set[str]:
    return {" ".join(m.group(1).split()) for m in re.finditer(r"(?m)^##\s+(.+?)\s*$", text)}


def h2_body(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
    )
    return match.group(1) if match else ""


def h3_sections(text: str, parent: str) -> set[str]:
    body = h2_body(text, parent)
    return {" ".join(m.group(1).split()) for m in re.finditer(r"(?m)^###\s+(.+?)\s*$", body)}


def subsection_body(text: str, parent: str, heading: str) -> str | None:
    body = h2_body(text, parent)
    match = re.search(
        rf"(?ms)^###\s+{re.escape(heading)}\s*$\n(.*?)(?=^###\s+|^##\s+|\Z)",
        body,
    )
    return match.group(1).strip() if match else None


def validate_structure(metadata: dict, text: str) -> tuple[list[str], list[str]]:
    """Validate one record's tier-specific skeleton."""
    problems: list[str] = []
    warnings: list[str] = []
    tier = metadata.get("analysis_tier")
    sections = h2_sections(text)
    if tier == "initial":
        missing = [name for name in INITIAL_ANCHORS if name not in sections]
        if missing:
            problems.append(f"initial record missing anchors: {', '.join(missing)}")
        for forbidden in ("可复用结论", "修改建议"):
            if forbidden in sections:
                problems.append(f"initial record must not contain ## {forbidden}")
        for name in INITIAL_SUBSECTIONS:
            if name not in h3_sections(text, "初步核验"):
                problems.append(f"initial record missing ### {name} under ## 初步核验")
            elif not subsection_body(text, "初步核验", name):
                problems.append(f"initial record has empty ### {name}")
        if metadata.get("distilled_to"):
            problems.append("initial record must not have distilled_to")
    elif tier == "deep":
        missing = [name for name in DEEP_ANCHORS if name not in sections]
        if missing:
            problems.append(f"deep record missing anchors: {', '.join(missing)}")
        subs = h3_sections(text, "怎么验的")
        for name in DEEP_OPTIONAL_SUBSECTIONS:
            if name in subs and not subsection_body(text, "怎么验的", name):
                problems.append(f"deep record has empty ### {name} under ## 怎么验的")
        if metadata.get("distilled_to") and metadata.get("status") != "analyzed":
            warnings.append(
                f"deep record keeps distilled_to while status is "
                f"{metadata.get('status')!r}; review the linked knowledge pages"
            )
    else:
        problems.append("analysis_tier must be 'initial' or 'deep'")
    return problems, warnings


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
        required = (
            "schema_version", "id", "package_id", "display_name", "authors",
            "license", "source_dir", "status", "analysis_tier", "modifications",
            "distilled_to",
        )
        missing = [key for key in required if key not in metadata]
        if missing:
            problems.append(f"{directory.name}: record.json missing {', '.join(missing)}")
        if metadata.get("schema_version") != SCHEMA_VERSION:
            problems.append(
                f"{directory.name}: schema_version {metadata.get('schema_version')!r}; "
                f"expected {SCHEMA_VERSION} (run tools/kb/migrate_records_schema.py --write)"
            )
        if "verification_tier" in metadata:
            problems.append(
                f"{directory.name}: verification_tier was removed; use analysis_tier"
            )
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
        structure_problems, structure_warnings = validate_structure(metadata, read(readme))
        problems.extend(f"{directory.name}: {item}" for item in structure_problems)
        warnings.extend(f"{directory.name}: {item}" for item in structure_warnings)
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
