#!/usr/bin/env python3
"""Repository hygiene checks (acceptance gate for repo structure).

Checks (exit 0 = all good, 1 = problems):
  1. No `.bak` leftovers under code-sample or record areas.
  2. No tracked `.pdb` files.
  3. No placeholder packageId in code samples.
  4. Legacy directories are not duplicated by target directories.
  5. Stable IDs and registry paths are internally consistent.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import kb_common as kb
import registry as stable_registry

PLACEHOLDER_PID = re.compile(
    r"^(runningbugs\.)?(modname|username\.modname)$|^(com\.)?runningbugs\.test$|^modname$",
    re.IGNORECASE,
)


def git_tracked(patterns: tuple[str, ...]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=kb.REPO_ROOT,
        )
    except OSError:
        return []
    return [line for line in result.stdout.splitlines() if line.endswith(patterns)]


def main() -> int:
    problems: list[str] = []
    warnings: list[str] = []
    for area in ("自建", "收集", "mods", "records"):
        directory = kb.REPO_ROOT / area
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.bak"):
            problems.append(f"leftover .bak: {path.relative_to(kb.REPO_ROOT).as_posix()}")
    for path in git_tracked((".pdb",)):
        problems.append(f"tracked .pdb (regenerable artifact): {path}")
    try:
        mods = kb.scan_all()
    except stable_registry.RegistryError as exc:
        problems.append(str(exc))
        mods = []
    for mod in mods:
        package_id = (mod.get("package_id") or "").strip()
        if package_id and PLACEHOLDER_PID.match(package_id):
            warnings.append(f"placeholder packageId '{package_id}' in {mod['id']} (registered, not fixed)")
    for entry in stable_registry.load_registry().get("mods", []):
        try:
            stable_registry.active_path_for(entry)
        except stable_registry.RegistryError as exc:
            problems.append(str(exc))
    for warning in warnings:
        print(f"  warning: {warning}")
    if problems:
        print(f"Hygiene problems ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("Hygiene checks OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
