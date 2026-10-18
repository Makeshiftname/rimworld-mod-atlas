#!/usr/bin/env python3
"""Generate the records index and validate record identity.

Reads records/<id>/record.json, validates required metadata, and rewrites the
index table between the AUTO markers in records/README.md.  It never edits a
record's prose.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RECORDS = ROOT / "records"
INDEX = RECORDS / "index.json"
README = RECORDS / "README.md"
AUTO_START = "<!-- AUTO-GENERATED-START -->"
AUTO_END = "<!-- AUTO-GENERATED-END -->"
REQUIRED = (
    "schema_version", "id", "package_id", "display_name", "authors", "license",
    "source_dir", "status", "modifications", "distilled_to",
)


def load_records() -> list[dict]:
    rows = []
    for directory in sorted(p for p in RECORDS.iterdir() if p.is_dir()):
        metadata_path = directory / "record.json"
        if not metadata_path.is_file():
            raise SystemExit(f"missing record.json: {directory.name}")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON: {metadata_path}: {exc}") from exc
        missing = [key for key in REQUIRED if key not in metadata]
        if missing:
            raise SystemExit(f"{metadata_path}: missing {', '.join(missing)}")
        if metadata["id"] != directory.name:
            raise SystemExit(f"{metadata_path}: id does not match directory")
        readme = directory / "README.md"
        if not readme.is_file():
            raise SystemExit(f"missing record README: {directory.name}")
        text = readme.read_text(encoding="utf-8", errors="replace")
        missing_sections = [name for name in ("身份卡", "它是什么", "怎么验的", "可复用结论")
                            if f"## {name}" not in text]
        if missing_sections:
            raise SystemExit(f"{readme}: missing sections {', '.join(missing_sections)}")
        metadata["_readme"] = f"{directory.name}/README.md"
        rows.append(metadata)
    return rows


def build_table(rows: list[dict]) -> str:
    lines = [
        "| ID | 记录 | packageId | 作者 | 状态 | 提炼 |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        authors = "、".join(row.get("authors", [])) or "—"
        pid = row.get("package_id") or "—"
        distilled = len(row.get("distilled_to", []))
        lines.append(
            f"| `{row['id']}` | [{row['display_name']}]({row['_readme']}) | `{pid}` | "
            f"{authors} | {row['status']} | {distilled or '—'} |"
        )
    return "\n".join(lines)


def rewrite_readme(table: str) -> None:
    text = README.read_text(encoding="utf-8")
    start = text.find(AUTO_START)
    end = text.find(AUTO_END)
    block = f"{AUTO_START}\n{table}\n{AUTO_END}"
    if start != -1 and end != -1 and end > start:
        text = text[:start] + block + text[end + len(AUTO_END):]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    README.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if index is stale")
    args = parser.parse_args()
    rows = load_records()
    rows_for_json = [{k: v for k, v in row.items() if k != "_readme"} for row in rows]
    generated = json.dumps(rows_for_json, ensure_ascii=False, indent=2) + "\n"
    table = build_table(rows)
    if args.check:
        if not INDEX.exists() or INDEX.read_text(encoding="utf-8") != generated:
            print("records/index.json is stale", file=sys.stderr)
            return 1
        text = README.read_text(encoding="utf-8")
        if table not in text:
            print("records/README.md table is stale", file=sys.stderr)
            return 1
        print(f"records index OK ({len(rows)} records)")
        return 0
    INDEX.write_text(generated, encoding="utf-8")
    rewrite_readme(table)
    print(f"wrote {INDEX} ({len(rows)} records)")
    print(f"updated {README}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
