#!/usr/bin/env python3
"""Detect placeholder READMEs in code samples.

Usage:
  python tools/kb/validate_readme.py --list
  python tools/kb/validate_readme.py --todo
  python tools/kb/validate_readme.py --verify <stable-id>
  python tools/kb/validate_readme.py --progress
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import kb_common as kb

PROGRESS_FILE = Path(__file__).resolve().parent / "kb-progress.json"
NEEDS_REWRITE = {"template", "stub", "missing"}


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"batches": [], "done": []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="list all mods + README status")
    parser.add_argument("--todo", action="store_true", help="list mods needing rewrite")
    parser.add_argument("--verify", metavar="STABLE_ID", help="verify one mod README")
    parser.add_argument("--progress", action="store_true", help="show batch rewrite progress")
    args = parser.parse_args()

    mods = kb.scan_all()
    by_id = {mod["id"]: mod for mod in mods}
    if args.verify:
        mod = by_id.get(args.verify)
        if mod is None:
            print(f"unknown stable id: {args.verify}", file=sys.stderr)
            return 2
        if mod["readme_status"] in NEEDS_REWRITE:
            print(f"{args.verify}: FAIL ({mod['readme_status']})")
            return 1
        print(f"{args.verify}: OK ({mod['readme_status']})")
        return 0
    todo = [mod["id"] for mod in mods if mod["readme_status"] in NEEDS_REWRITE]
    if args.todo:
        if not todo:
            print("All READMEs are in good shape.")
            return 0
        print(f"{len(todo)} README(s) need attention:")
        for mod_id in todo:
            print(f"  - {mod_id} ({by_id[mod_id]['readme_status']})")
        return 0
    if args.progress:
        progress = load_progress()
        done = set(progress.get("done", []))
        remaining = [mod_id for mod_id in todo if mod_id not in done]
        print(f"batches: {len(progress.get('batches', []))}")
        print(f"done:    {len(done)}")
        print(f"still placeholder: {len(remaining)}")
        for mod_id in remaining:
            print(f"  - {mod_id}")
        return 0
    for mod in mods:
        print(f"{mod['readme_status']:<8} {mod['id']} ({mod['dir']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
