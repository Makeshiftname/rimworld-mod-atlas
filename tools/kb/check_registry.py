#!/usr/bin/env python3
"""Validate the identity registry and its filesystem coverage.

This is the gate that makes ``mods/registry.json`` authoritative:

* every code directory is registered exactly once;
* every record directory is registered exactly once;
* IDs, aliases, package IDs and target paths do not collide;
* pre-migration and post-migration layouts are both understood, but an entry
  must not exist in both layouts at once.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry as stable_registry  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = ROOT / "mods" / "registry.json"
CODE_PARENTS = ("自建", "收集", "mods/owned", "mods/collected")
ALLOWED_TYPES = {"standalone", "patch", "xml", "translation", "lib", "empty", "special", "unknown"}
PLACEHOLDER_PID = re.compile(
    r"^(runningbugs\.)?(modname|username\.modname)$|^(com\.)?runningbugs\.test$|^modname$",
    re.IGNORECASE,
)
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_safe_relative(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def is_repo_url(value: str) -> bool:
    if value.startswith("git@"):
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"https", "http", "ssh"} and bool(parsed.netloc)


def actual_code_dirs() -> set[str]:
    found: set[str] = set()
    for parent_name in CODE_PARENTS:
        parent = ROOT / parent_name
        if not parent.is_dir():
            continue
        for child in parent.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                found.add(relative(child))
    return found


def actual_record_dirs() -> set[str]:
    records = ROOT / "records"
    if not records.is_dir():
        return set()
    return {
        relative(child)
        for child in records.iterdir()
        if child.is_dir() and not child.name.startswith(".")
    }


def raw_registry() -> dict:
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise stable_registry.RegistryError(f"cannot read {REGISTRY}: {exc}") from exc


def validate() -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    raw = raw_registry()
    if raw.get("schema_version") != stable_registry.SCHEMA_VERSION:
        problems.append(
            f"registry schema is {raw.get('schema_version')!r}; "
            f"expected {stable_registry.SCHEMA_VERSION} (run tools/kb/migrate_registry_schema.py)"
        )
    try:
        data = stable_registry.normalize_registry(raw)
    except stable_registry.RegistryError as exc:
        return [str(exc)], warnings

    entries = data["objects"]
    ids = Counter(entry["id"] for entry in entries)
    for mod_id, count in ids.items():
        if count > 1:
            problems.append(f"duplicate id: {mod_id} ({count} entries)")
    all_ids = set(ids)
    alias_owner: dict[str, str] = {}
    alias_norm_owner: dict[str, str] = {}
    package_owner: dict[str, str] = {}
    package_norm_owner: dict[str, str] = {}
    target_owner: dict[str, str] = {}
    legacy_owner: dict[str, str] = {}
    registered_code: set[str] = set()
    registered_records: set[str] = set()

    for entry in entries:
        mod_id = entry["id"]
        origin = entry.get("origin")
        package_id = entry.get("package_id", "")
        if not stable_registry.ID_RE.fullmatch(mod_id):
            problems.append(f"{mod_id}: id must match {stable_registry.ID_RE.pattern}")
        if mod_id.startswith("unidentified-"):
            problems.append(f"{mod_id}: placeholder ID must be replaced with a manual slug")
        if origin not in stable_registry.ORIGINS:
            problems.append(f"{mod_id}: invalid origin {origin!r}")
        if not entry.get("display_name"):
            problems.append(f"{mod_id}: display_name is empty")
        if entry.get("type") and entry["type"] not in ALLOWED_TYPES:
            problems.append(f"{mod_id}: invalid type {entry['type']!r}")
        if package_id:
            if package_id in package_owner and package_owner[package_id] != mod_id:
                problems.append(
                    f"duplicate package_id {package_id!r}: {package_owner[package_id]} and {mod_id}"
                )
            package_owner[package_id] = mod_id
            package_norm = package_id.casefold()
            if package_norm in package_norm_owner and package_norm_owner[package_norm] != mod_id:
                problems.append(
                    f"package_id differs only by case: "
                    f"{package_norm_owner[package_norm]} and {mod_id}"
                )
            package_norm_owner[package_norm] = mod_id
            if PLACEHOLDER_PID.match(package_id):
                warnings.append(f"{mod_id}: placeholder package_id {package_id!r} (manual review pending)")
        else:
            warnings.append(f"{mod_id}: empty package_id")

        for alias in entry.get("aliases", []):
            if not alias.strip():
                problems.append(f"{mod_id}: empty alias")
            if alias in all_ids:
                problems.append(f"{mod_id}: alias {alias!r} collides with an existing id")
            if alias in alias_owner and alias_owner[alias] != mod_id:
                problems.append(
                    f"alias {alias!r} belongs to both {alias_owner[alias]} and {mod_id}"
                )
            alias_owner[alias] = mod_id
            alias_norm = stable_registry.normalize_id(alias)
            if alias_norm in all_ids:
                problems.append(f"{mod_id}: alias {alias!r} normalizes to existing id {alias_norm!r}")
            if alias_norm in alias_norm_owner and alias_norm_owner[alias_norm] != mod_id:
                problems.append(
                    f"alias {alias!r} normalizes to {alias_norm!r}, "
                    f"which belongs to both {alias_norm_owner[alias_norm]} and {mod_id}"
                )
            alias_norm_owner[alias_norm] = mod_id

        code = entry.get("code")
        if code:
            kind = code.get("kind", "local")
            if kind not in stable_registry.CODE_KINDS:
                problems.append(f"{mod_id}: invalid code.kind {kind!r}")
                continue
            if kind == "external":
                repo = code.get("repo", "")
                repo_path = code.get("path", "")
                commit = code.get("commit", "")
                if not is_repo_url(repo):
                    problems.append(f"{mod_id}: external code.repo is not a git URL: {repo!r}")
                if not is_safe_relative(repo_path):
                    problems.append(f"{mod_id}: unsafe external code.path {repo_path!r}")
                if not COMMIT_RE.fullmatch(commit):
                    problems.append(f"{mod_id}: external code.commit must be a 7-40 char SHA")
                continue
            paths = code.get("legacy_paths", [])
            target = code.get("target_path", "")
            expected_target = f"mods/{origin}/{mod_id}"
            if target != expected_target:
                problems.append(
                    f"{mod_id}: code.target_path {target!r} != expected {expected_target!r}"
                )
            if not paths:
                problems.append(f"{mod_id}: code entry has no legacy_paths")
            for path in paths:
                if not is_safe_relative(path):
                    problems.append(f"{mod_id}: unsafe code path {path!r}")
                if path in legacy_owner and legacy_owner[path] != mod_id:
                    problems.append(
                        f"code path {path!r} belongs to both {legacy_owner[path]} and {mod_id}"
                    )
                legacy_owner[path] = mod_id
                registered_code.add(path)
            if not is_safe_relative(target):
                problems.append(f"{mod_id}: unsafe code target {target!r}")
            if target in target_owner and target_owner[target] != mod_id:
                problems.append(
                    f"code target {target!r} belongs to both {target_owner[target]} and {mod_id}"
                )
            target_owner[target] = mod_id
            registered_code.add(target)
            source_exists = any((ROOT / path).exists() for path in paths)
            target_exists = (ROOT / target).exists()
            if source_exists and target_exists:
                problems.append(f"{mod_id}: code exists in both legacy and target layouts")
            if not source_exists and not target_exists and not entry.get("retired"):
                problems.append(f"{mod_id}: code path is missing in both layouts")
            if entry.get("retired") and (source_exists or target_exists):
                problems.append(f"{mod_id}: retired entry still has a code directory")

        record = entry.get("record")
        if record:
            record_path = record.get("path", "")
            expected_record = f"records/{mod_id}"
            if record_path != expected_record:
                problems.append(
                    f"{mod_id}: record.path {record_path!r} != expected {expected_record!r}"
                )
            if not is_safe_relative(record_path):
                problems.append(f"{mod_id}: unsafe record path {record_path!r}")
            if (ROOT / record_path).exists():
                registered_records.add(record_path)
            else:
                problems.append(f"{mod_id}: record path is missing: {record_path}")
            for legacy in record.get("legacy_paths", []):
                if not is_safe_relative(legacy):
                    problems.append(f"{mod_id}: unsafe record legacy path {legacy!r}")
        if not code and not record and not entry.get("retired"):
            problems.append(f"{mod_id}: entry has neither code nor record")

    actual_code = actual_code_dirs()
    for path in sorted(actual_code - registered_code):
        problems.append(f"unregistered code directory: {path}")
    for path in sorted(registered_code - actual_code):
        # A registered target that does not exist before migration is expected;
        # the per-entry check above distinguishes missing from pre-migration.
        if not (ROOT / path).exists() and path.startswith("mods/"):
            continue
        problems.append(f"registered code path is missing: {path}")

    actual_records = actual_record_dirs()
    for path in sorted(actual_records - registered_records):
        problems.append(f"unregistered record directory: {path}")
    for path in sorted(registered_records - actual_records):
        problems.append(f"registered record path is missing: {path}")

    return problems, warnings


def main() -> int:
    try:
        problems, warnings = validate()
    except stable_registry.RegistryError as exc:
        problems, warnings = [str(exc)], []
    for warning in warnings:
        print(f"  warning: {warning}")
    if problems:
        print(f"registry problems ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("registry checks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
