#!/usr/bin/env python3
"""Migrate code samples to stable-ID ``mods/`` paths.

Default mode is a read-only plan.  ``--apply`` is explicit, refuses structural
conflicts, moves directories with ``git mv`` and rewrites first-party
references in the same operation.  Third-party ``mods/collected/**`` content is
never edited.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry as stable_registry  # noqa: E402

REPO_ROOT = stable_registry.REPO_ROOT
TEXT_SUFFIXES = {".md", ".json", ".txt", ".yml", ".yaml"}


def file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def build_plan(root: Path = REPO_ROOT, data: dict | None = None) -> list[dict]:
    data = data or stable_registry.load_registry()
    rows: list[dict] = []
    for entry in stable_registry.iter_code_entries(data):
        code = entry.get("code") or {}
        if code.get("kind") == "external":
            continue
        target = root / code.get("target_path", "")
        legacy = [root / path for path in code.get("legacy_paths", []) if (root / path).exists()]
        if not code.get("target_path"):
            status = "invalid"
        elif target.exists() and legacy:
            status = "conflict"
        elif target.exists():
            status = "already"
        elif legacy:
            status = "move"
        elif entry.get("retired"):
            status = "retired"
        else:
            status = "missing"
        rows.append({
            "id": entry["id"],
            "origin": entry.get("origin", ""),
            "source": str(legacy[0].relative_to(root)).replace("\\", "/") if legacy else "",
            "sources": [str(path.relative_to(root)).replace("\\", "/") for path in legacy],
            "target": code.get("target_path", ""),
            "status": status,
            "file_count": file_count(legacy[0]) if len(legacy) == 1 else 0,
        })
    return rows


def plan_errors(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    targets: dict[str, str] = {}
    sources: dict[str, str] = {}
    for row in rows:
        if row["status"] in {"conflict", "missing", "invalid"}:
            errors.append(f"{row['id']}: {row['status']} ({row['source'] or '-'} -> {row['target'] or '-'})")
        if len(row["sources"]) > 1:
            errors.append(f"{row['id']}: multiple source paths are not supported: {row['sources']}")
        if row["target"]:
            if row["target"] in targets and targets[row["target"]] != row["id"]:
                errors.append(
                    f"target {row['target']} belongs to both {targets[row['target']]} and {row['id']}"
                )
            targets[row["target"]] = row["id"]
        for source in row["sources"]:
            if source in sources and sources[source] != row["id"]:
                errors.append(f"source {source} belongs to both {sources[source]} and {row['id']}")
            sources[source] = row["id"]
    return errors


def build_manifest(rows: list[dict], root: Path = REPO_ROOT) -> dict:
    head = ""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            head = result.stdout.strip()
    except OSError:
        pass
    return {
        "schema_version": 1,
        "repo_head": head,
        "entries": rows,
    }


def write_manifest(path: Path, rows: list[dict], root: Path = REPO_ROOT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_manifest(rows, root), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_manifest(path: Path, rows: list[dict], root: Path = REPO_ROOT) -> list[str]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read manifest {path}: {exc}"]
    expected = build_manifest(rows, root)
    problems: list[str] = []
    old = {entry.get("id"): entry for entry in manifest.get("entries", [])}
    current = {entry.get("id"): entry for entry in expected["entries"]}
    for mod_id in sorted(set(old) | set(current)):
        if old.get(mod_id) != current.get(mod_id):
            problems.append(f"manifest drift for {mod_id}")
    if manifest.get("repo_head") and expected.get("repo_head") \
            and manifest["repo_head"] != expected["repo_head"]:
        problems.append("manifest was created from a different git HEAD")
    return problems


def reference_map(data: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    def add(old: str, new: str) -> None:
        mapping[old] = new
        windows_old = old.replace("/", "\\")
        if windows_old != old:
            mapping[windows_old] = new.replace("/", "\\")

    for entry in data.get("objects", []):
        code = entry.get("code") or {}
        target = code.get("target_path", "")
        for source in code.get("legacy_paths", []):
            if target:
                add(source, target)
        record = entry.get("record") or {}
        record_target = record.get("path", "")
        for source in record.get("legacy_paths", []):
            if record_target:
                add(source, record_target)
    # Longer paths first so a directory mapping cannot consume a file suffix.
    return dict(sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True))


def first_party_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in ("README.md", "ARCHITECTURE.md", "AGENTS.md"):
        path = root / name
        if path.is_file():
            files.append(path)
    for area in (root / "docs", root / "records"):
        if area.is_dir():
            files.extend(
                path for path in area.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    for area in (root / "mods" / "owned",):
        if area.is_dir():
            files.extend(
                path for path in area.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    mods_readme = root / "mods" / "README.md"
    if mods_readme.is_file():
        files.append(mods_readme)
    return sorted(set(files))


def rewrite_references(root: Path, data: dict) -> tuple[list[str], int, list[str]]:
    mapping = reference_map(data)
    changed: list[str] = []
    replacements = 0
    unresolved: list[str] = []
    for path in first_party_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        original = text
        for old, new in mapping.items():
            if old in text:
                count = text.count(old)
                text = text.replace(old, new)
                replacements += count
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(root)).replace("\\", "/"))
        for old in mapping:
            if old in text:
                unresolved.append(f"{path.relative_to(root).as_posix()}: {old}")
    return changed, replacements, unresolved


def worktree_is_dirty(root: Path = REPO_ROOT) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        return bool(result.stdout.strip())
    except OSError:
        return False


def apply_plan(rows: list[dict], root: Path = REPO_ROOT) -> list[str]:
    moved: list[str] = []
    for row in rows:
        if row["status"] != "move":
            continue
        target = root / row["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "-C", str(root), "mv", "--", row["source"], row["target"]],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode != 0:
            moved.append(f"FAILED {row['id']}: {result.stderr.strip()}")
            return moved
        moved.append(f"MOVED {row['id']}: {row['source']} -> {row['target']}")
    return moved


def print_rows(rows: list[dict]) -> None:
    for row in rows:
        prefix = row["status"].upper()
        source = row["source"] or "(already moved)"
        print(f"{prefix:9} {row['id']}: {source} -> {row['target'] or '-'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="move code and rewrite first-party references")
    parser.add_argument("--json", action="store_true", help="emit the plan as JSON")
    parser.add_argument("--manifest", type=Path, help="write/read a migration manifest")
    parser.add_argument("--allow-dirty", action="store_true", help="allow apply with uncommitted changes")
    args = parser.parse_args()

    rows = build_plan(REPO_ROOT)
    errors = plan_errors(rows)
    if args.manifest and not args.apply:
        write_manifest(args.manifest, rows)
        print(f"wrote manifest {args.manifest}")
    if args.manifest and args.apply:
        errors.extend(validate_manifest(args.manifest, rows))
    if args.json:
        print(json.dumps({"entries": rows, "errors": errors}, ensure_ascii=False, indent=2))
        return 1 if errors else 0
    print_rows(rows)
    if errors:
        print("refusing migration:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    if not args.apply:
        print("dry run only; pass --apply after reviewing the plan")
        return 0
    if worktree_is_dirty(REPO_ROOT) and not args.allow_dirty:
        print("refusing apply: worktree is dirty; commit first or pass --allow-dirty", file=sys.stderr)
        return 1

    moved = apply_plan(rows, REPO_ROOT)
    for line in moved:
        print(line)
    if any(line.startswith("FAILED") for line in moved):
        print("migration stopped after a partial move; inspect git status before retrying", file=sys.stderr)
        return 1

    data = stable_registry.load_registry()
    changed, replacements, unresolved = rewrite_references(REPO_ROOT, data)
    print(f"rewrote {replacements} reference(s) in {len(changed)} file(s)")
    for path in changed:
        print(f"  {path}")
    if unresolved:
        print("unresolved legacy references:", file=sys.stderr)
        for item in unresolved:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("next: python tools/kb/scan_mods.py && python tools/kb/scan_records.py && python tools/kb/check_all.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
