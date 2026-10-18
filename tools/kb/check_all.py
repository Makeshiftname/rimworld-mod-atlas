#!/usr/bin/env python3
"""Run all repository acceptance gates in one command."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHECKS = (
    ("registry", ["tools/kb/check_registry.py"]),
    ("links", ["tools/kb/check_links.py"]),
    ("records", ["tools/kb/check_records.py"]),
    ("knowledge entries + sources", ["tools/kb/check_knowledge.py"]),
    ("hygiene", ["tools/kb/check_repo_hygiene.py"]),
    ("mod index drift", ["tools/kb/scan_mods.py", "--check"]),
    ("record index drift", ["tools/kb/scan_records.py", "--check"]),
    ("unit tests", ["-m", "unittest", "discover", "-s", "tools/kb/tests", "-q"]),
)


def main() -> int:
    failures = []
    for name, command in CHECKS:
        print(f"\n== {name} ==")
        result = subprocess.run([sys.executable, *command], cwd=ROOT)
        if result.returncode != 0:
            failures.append(name)
    print("\n== summary ==")
    if failures:
        print("FAILED: " + ", ".join(failures))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
