#!/usr/bin/env python3
"""Migrate record.json metadata to schema v3 without rewriting prose."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RECORDS = ROOT / "records"
SCHEMA_VERSION = 3
RECORD_ORDER = (
    "schema_version", "id", "package_id", "display_name", "origin", "authors",
    "author_evidence", "license", "license_notes", "source_url", "workshop_id",
    "retrieved_at", "source_dir", "status", "analysis_tier", "modifications",
    "distilled_to", "code_removed",
)


def normalize_record(data: dict) -> dict:
    data = dict(data)
    data["schema_version"] = SCHEMA_VERSION
    data.setdefault("origin", "collected")
    data.setdefault("analysis_tier", "deep")
    data.setdefault("code_removed", False)
    if data.get("status") == "raw":
        data["status"] = "analyzed"
    data.pop("verification_tier", None)
    ordered = {key: data[key] for key in RECORD_ORDER if key in data}
    ordered.update({key: value for key, value in data.items() if key not in ordered})
    return ordered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write expanded record.json files")
    args = parser.parse_args()
    changed = 0
    for path in sorted(RECORDS.glob("*/record.json")):
        data = normalize_record(json.loads(path.read_text(encoding="utf-8")))
        before = json.loads(path.read_text(encoding="utf-8"))
        if data != before:
            changed += 1
            if args.write:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
    print(
        f"records schema v{SCHEMA_VERSION}: {changed} file(s) "
        f"{'written' if args.write else 'would change'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
