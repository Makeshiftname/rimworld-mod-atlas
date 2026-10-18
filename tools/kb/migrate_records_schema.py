#!/usr/bin/env python3
"""Expand record.json metadata to schema v2 without rewriting prose."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RECORDS = ROOT / "records"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write expanded record.json files")
    args = parser.parse_args()
    changed = 0
    for path in sorted(RECORDS.glob("*/record.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        before = dict(data)
        data["schema_version"] = 2
        data.setdefault("origin", "collected")
        data.setdefault("code_removed", False)
        if data != before:
            changed += 1
            if args.write:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
    print(f"records schema v2: {changed} file(s) {'written' if args.write else 'would change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
