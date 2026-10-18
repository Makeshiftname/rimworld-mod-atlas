#!/usr/bin/env python3
"""Migrate mods/registry.json from schema v2 to v3.

The migration is intentionally one-way on disk, but the reader remains
backward-compatible.  Run with ``--check`` first; ``--write`` is explicit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry as stable_registry  # noqa: E402


def object_ids(data: dict) -> set[str]:
    raw = data.get("objects")
    if raw is None:
        raw = data.get("mods", [])
    return {str(entry.get("id", "")) for entry in raw if entry.get("id")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the v3 registry")
    parser.add_argument(
        "--registry",
        type=Path,
        default=stable_registry.REGISTRY_PATH,
        help="registry path (default: mods/registry.json)",
    )
    args = parser.parse_args()

    raw = json.loads(args.registry.read_text(encoding="utf-8"))
    normalized = stable_registry.normalize_registry(raw)
    before = object_ids(raw)
    after = object_ids(normalized)
    if before != after:
        print("refusing migration: object IDs are not preserved", file=sys.stderr)
        print(f"  before-only: {sorted(before - after)}", file=sys.stderr)
        print(f"  after-only:  {sorted(after - before)}", file=sys.stderr)
        return 1
    print(
        f"schema {raw.get('schema_version', '?')} -> {stable_registry.SCHEMA_VERSION}; "
        f"{len(after)} objects; IDs preserved"
    )
    if args.write:
        stable_registry.save_registry(normalized, args.registry)
        print(f"wrote {args.registry}")
    else:
        print("check only; pass --write to replace the registry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
