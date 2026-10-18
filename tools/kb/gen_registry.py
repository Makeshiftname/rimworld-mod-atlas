#!/usr/bin/env python3
"""Propose registry additions without overwriting the identity authority.

``registry.json`` is manually maintained because it contains frozen IDs,
aliases and retired/record-only decisions.  This helper scans the current
filesystem and emits a *proposal* that preserves every existing object and
adds only missing directories.  It never writes ``mods/registry.json``.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402
import registry as stable_registry  # noqa: E402

LEGACY_PARENTS = {"自建": "owned", "收集": "collected"}
TARGET_PARENTS = {"mods/owned": "owned", "mods/collected": "collected"}


def scan_dirs() -> list[dict]:
    rows: list[dict] = []
    for parent_name, origin in {**LEGACY_PARENTS, **TARGET_PARENTS}.items():
        parent = kb.REPO_ROOT / parent_name
        if not parent.is_dir():
            continue
        for child in sorted(parent.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            probe = kb.probe_mod(child)
            rows.append({
                "origin": origin,
                "legacy_path": f"{parent_name}/{child.name}",
                "package_id": probe.get("package_id", ""),
                "display_name": probe.get("name") or probe.get("title") or child.name,
                "type": probe.get("type", ""),
                "dirname": child.name,
            })
    return rows


def build_registry(existing: dict | None = None) -> dict:
    existing = existing or {"schema_version": stable_registry.SCHEMA_VERSION, "objects": []}
    normalized = stable_registry.normalize_registry(existing)
    objects = [dict(entry) for entry in normalized["objects"]]

    known_paths: dict[str, dict] = {}
    for entry in objects:
        code = entry.get("code") or {}
        for path in code.get("legacy_paths", []):
            known_paths[path] = entry
        target = code.get("target_path")
        if target:
            known_paths[target] = entry

    discovered = scan_dirs()
    counts = Counter(row["package_id"] for row in discovered if row["package_id"])
    used = {entry["id"] for entry in objects}
    for row in discovered:
        if row["legacy_path"] in known_paths:
            continue
        mod_id = stable_registry.initial_id(row["package_id"], counts, row["dirname"])
        base = mod_id
        n = 2
        while mod_id in used:
            mod_id = f"{base}-{n}"
            n += 1
        used.add(mod_id)
        objects.append({
            "id": mod_id,
            "origin": row["origin"],
            "package_id": row["package_id"],
            "display_name": row["display_name"],
            "aliases": [],
            "code": {
                "legacy_paths": [row["legacy_path"]],
                "target_path": f"mods/{row['origin']}/{mod_id}",
            },
            "record": None,
            "type": row["type"],
        })
    objects.sort(key=lambda entry: (entry.get("origin", ""), entry["id"]))
    return {"schema_version": stable_registry.SCHEMA_VERSION, "objects": objects}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write mods/registry.proposed.json (never the authority)",
    )
    args = parser.parse_args()
    existing = stable_registry.load_registry()
    proposed = build_registry(existing)
    if args.write:
        path = stable_registry.REPO_ROOT / "mods" / "registry.proposed.json"
        path.write_text(
            json.dumps(proposed, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote proposal {path} ({len(proposed['objects'])} objects)")
        print("review and merge manually; mods/registry.json was not changed")
    else:
        print(json.dumps(proposed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
