#!/usr/bin/env python3
"""Generate or check the stable mod registry.

The command reads the existing legacy directories, preserves every manually
approved ID already present in ``mods/registry.json``, and only generates
missing entries.  It never renames a mod and never writes outside the registry
unless ``--write`` is supplied.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402
import registry  # noqa: E402


def discover_legacy() -> list[dict]:
    rows = []
    for mod in kb.scan_all():
        rows.append({
            "category": registry.LEGACY_CATEGORIES.get(mod["category"], mod["category"]),
            "dir": mod["dir"],
            "legacy_path": f"{mod['category']}/{mod['dir']}",
            "package_id": mod.get("package_id", ""),
            "display_name": mod.get("name") or mod.get("title") or mod["dir"],
            "type": mod.get("type", ""),
        })
    return rows


def build_registry(existing: dict | None = None) -> dict:
    existing = existing or {"schema_version": registry.SCHEMA_VERSION, "mods": []}
    known = {tuple(e.get("legacy_paths", [])): e for e in existing.get("mods", [])}
    known_by_pid = {e.get("package_id"): e for e in existing.get("mods", []) if e.get("package_id")}
    discovered = discover_legacy()
    counts = Counter(r["package_id"] for r in discovered if r["package_id"])

    entries = []
    used: set[str] = set()
    for row in discovered:
        old = known.get((row["legacy_path"],)) or known_by_pid.get(row["package_id"])
        if old:
            entry = dict(old)
            entry.setdefault("legacy_paths", [row["legacy_path"]])
            entry.setdefault("package_id", row["package_id"])
            entry.setdefault("display_name", row["display_name"])
            entry.setdefault("category", row["category"])
            entry.setdefault("type", row["type"])
            entry.setdefault("aliases", [])
        else:
            mod_id = registry.initial_id(row["package_id"], counts, row["dir"])
            base = mod_id
            n = 2
            while mod_id in used:
                mod_id = f"{base}-{n}"
                n += 1
            entry = {
                "id": mod_id,
                "category": row["category"],
                "package_id": row["package_id"],
                "display_name": row["display_name"],
                "type": row["type"],
                "aliases": [],
                "legacy_paths": [row["legacy_path"]],
            }
        used.add(entry["id"])
        entries.append(entry)

    entries.sort(key=lambda e: (e["category"], e["id"]))
    return {"schema_version": registry.SCHEMA_VERSION, "mods": entries}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="write mods/registry.json")
    args = ap.parse_args()
    existing = registry.load_registry()
    generated = build_registry(existing)
    if args.write:
        registry.save_registry(generated)
        print(f"wrote {registry.REGISTRY_PATH} ({len(generated['mods'])} mods)")
        return 0
    import json
    print(json.dumps(generated, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
