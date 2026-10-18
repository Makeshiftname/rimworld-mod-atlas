"""Stable IDs and the mod registry.

The registry is the single authority for repository identities.  Entries may
have a code sample (owned/collected), a record only (record-only), or both.
Directory names and numbering may change; IDs do not.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "mods" / "registry.json"

LEGACY_CATEGORIES = {
    "自建": "owned",
    "收集": "collected",
}
TARGET_CATEGORIES = {"owned", "collected", "record-only"}
SCHEMA_VERSION = 2

_SLUG_RE = re.compile(r"[^a-z0-9]+")


class RegistryError(ValueError):
    """Raised when registry data or ID resolution is inconsistent."""


def normalize_id(value: str) -> str:
    """Return a stable, filesystem-safe ID for an initial packageId."""
    value = (value or "").strip().lower()
    value = value.replace("_", "-").replace(".", "-")
    value = _SLUG_RE.sub("-", value).strip("-")
    return value


def display_slug(value: str) -> str:
    """Return a readable ASCII slug; non-ASCII values are lowercased."""
    value = (value or "").strip()
    ascii_part = "".join(c if ord(c) < 128 else "" for c in value)
    slug = normalize_id(ascii_part)
    return slug or normalize_id(value)


def _legacy_number(dirname: str) -> str:
    match = re.match(r"^(\d+)", dirname)
    return match.group(1) if match else ""


def _legacy_title(dirname: str) -> str:
    return re.sub(r"^\d+[-_](?:standalone|patch|xml|translation|lib|empty|special)[-_]", "", dirname)


def initial_id(package_id: str, package_counts: dict[str, int], dirname: str) -> str:
    normalized = normalize_id(package_id)
    if normalized and normalized not in {"modname", "username-modname"}:
        if package_counts.get(package_id, 0) <= 1:
            return normalized
        suffix = display_slug(_legacy_title(dirname))
        return f"{normalized}-{suffix}" if suffix else normalized
    suffix = display_slug(_legacy_title(dirname))
    return suffix or f"unidentified-{_legacy_number(dirname) or 'mod'}"


def load_registry(path: Path | None = None) -> dict[str, Any]:
    path = path or REGISTRY_PATH
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "mods": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot read registry {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("mods", None), list):
        raise RegistryError(f"registry {path} must contain a mods list")
    return data


def save_registry(data: dict[str, Any], path: Path | None = None) -> None:
    path = path or REGISTRY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entries_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for entry in data.get("mods", []):
        mod_id = entry.get("id", "")
        if not mod_id:
            raise RegistryError("registry entry is missing id")
        if mod_id in result:
            raise RegistryError(f"duplicate registry id: {mod_id}")
        result[mod_id] = entry
    return result


def aliases_for(data: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for entry in data.get("mods", []):
        mod_id = entry["id"]
        for alias in entry.get("aliases", []):
            if alias in aliases and aliases[alias] != mod_id:
                raise RegistryError(f"alias {alias!r} belongs to both {aliases[alias]} and {mod_id}")
            aliases[alias] = mod_id
    return aliases


def resolve_id(data: dict[str, Any], value: str) -> str | None:
    if value in entries_by_id(data):
        return value
    return aliases_for(data).get(value)


def entry_for_legacy_path(data: dict[str, Any], relative_path: str) -> dict[str, Any] | None:
    relative_path = relative_path.replace("\\", "/").strip("/")
    for entry in data.get("mods", []):
        if relative_path in {p.replace("\\", "/") for p in entry.get("legacy_paths", [])}:
            return entry
    return None


def target_path_for(entry: dict[str, Any]) -> Path | None:
    category = entry.get("category")
    if category == "record-only":
        return None
    if category not in TARGET_CATEGORIES:
        raise RegistryError(f"{entry.get('id', '?')}: invalid category {category!r}")
    return REPO_ROOT / "mods" / category / entry["id"]


def legacy_paths_for(entry: dict[str, Any]) -> list[Path]:
    return [REPO_ROOT / p for p in entry.get("legacy_paths", [])
            if not p.replace("\\", "/").startswith("收录/")]


def active_path_for(entry: dict[str, Any]) -> Path | None:
    """Return the single active code path, or raise when duplicated."""
    target = target_path_for(entry)
    legacy = [p for p in legacy_paths_for(entry) if p.exists()]
    if target is not None and target.exists() and legacy:
        raise RegistryError(
            f"{entry['id']}: duplicate mod directories: {target} and {', '.join(map(str, legacy))}"
        )
    if target is not None and target.exists():
        return target
    if len(legacy) > 1:
        raise RegistryError(f"{entry['id']}: multiple legacy directories: {legacy}")
    return legacy[0] if legacy else None


def all_active_mod_dirs(data: dict[str, Any]) -> list[tuple[str, Path]]:
    result = []
    for entry in data.get("mods", []):
        path = active_path_for(entry)
        if path is not None:
            result.append((entry["id"], path))
    return result
