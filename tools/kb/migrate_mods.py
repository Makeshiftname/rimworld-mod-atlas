#!/usr/bin/env python3
"""Migrate legacy 自建/收集 directories to stable-ID mods/ paths.

Default mode is a dry run. ``--apply`` performs git mv operations for code
samples only; records are migrated separately and collected content is never
edited in place.  The registry remains the authority for both old and target
paths.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry as stable_registry  # noqa: E402


def run_git(*args: str) -> int:
    result = subprocess.run(["git", *args], cwd=stable_registry.REPO_ROOT)
    return result.returncode


def migration_rows() -> list[dict]:
    data = stable_registry.load_registry()
    rows = []
    for entry in data.get("mods", []):
        if entry.get("category") not in {"owned", "collected"}:
            continue
        old_paths = [stable_registry.REPO_ROOT / path for path in entry.get("legacy_paths", [])]
        existing_old = [path for path in old_paths if path.exists()]
        target = stable_registry.target_path_for(entry)
        if target is None:
            continue
        rows.append({"entry": entry, "legacy": existing_old, "target": target})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform git mv")
    parser.add_argument("--json", action="store_true", help="emit machine-readable dry-run rows")
    args = parser.parse_args()

    rows = migration_rows()
    conflicts = []
    for row in rows:
        if row["target"].exists() and row["legacy"]:
            conflicts.append(row)
    if args.json:
        import json
        print(json.dumps([
            {
                "id": row["entry"]["id"],
                "legacy": [str(path.relative_to(stable_registry.REPO_ROOT)) for path in row["legacy"]],
                "target": str(row["target"].relative_to(stable_registry.REPO_ROOT)),
            }
            for row in rows
        ], ensure_ascii=False, indent=2))
        return 1 if conflicts else 0

    for row in rows:
        entry = row["entry"]
        old = ", ".join(str(path.relative_to(stable_registry.REPO_ROOT)) for path in row["legacy"]) or "(already moved)"
        target = str(row["target"].relative_to(stable_registry.REPO_ROOT))
        prefix = "CONFLICT" if row in conflicts else ("MOVE" if row["legacy"] else "OK")
        print(f"{prefix:8} {entry['id']}: {old} -> {target}")
    if conflicts:
        print("refusing to migrate: target exists while legacy path still exists", file=sys.stderr)
        return 1
    if not args.apply:
        print("dry run only; pass --apply after reviewing the list")
        return 0
    for row in rows:
        for old in row["legacy"]:
            row["target"].parent.mkdir(parents=True, exist_ok=True)
            if run_git("mv", str(old.relative_to(stable_registry.REPO_ROOT)),
                       str(row["target"].relative_to(stable_registry.REPO_ROOT))) != 0:
                return 1
    print("migration complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
