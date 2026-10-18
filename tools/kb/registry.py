"""Stable IDs and the mod identity registry.

The registry is the single authority for repository identities.  Schema v3
separates ownership/origin from the optional code and record locations:

    {
      "id": "alert-utility",
      "origin": "collected",
      "package_id": "RunningBugs.AlertUtility",
      "aliases": ["01-standalone-AlertUtility"],
      "code": {
        "legacy_paths": ["收集/01-standalone-AlertUtility"],
        "target_path": "mods/collected/alert-utility"
      },
      "record": null
    }

Readers still accept the previous v2 shape (``mods`` + ``category`` +
``legacy_paths`` + ``record_paths``) so that the transition is expand/migrate/
verify rather than a flag day.  ``load_registry`` always returns the v3 shape
in memory; only the on-disk file is migrated.
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
ORIGINS = {"owned", "collected"}
TARGET_CATEGORIES = ORIGINS
SCHEMA_VERSION = 3
LEGACY_SCHEMA_VERSION = 2
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_SLUG_RE = re.compile(r"[^a-z0-9]+")


class RegistryError(ValueError):
    """Raised when registry data or ID resolution is inconsistent."""


def normalize_id(value: str) -> str:
    """Return a stable, filesystem-safe slug for a proposed ID."""
    value = (value or "").strip().lower()
    value = value.replace("_", "-").replace(".", "-")
    value = _SLUG_RE.sub("-", value).strip("-")
    return value


def display_slug(value: str) -> str:
    """Return an ASCII slug suitable for a human-readable ID proposal.

    Non-ASCII text is deliberately dropped.  A caller that ends up with an
    empty slug must choose an ID manually instead of accepting an
    ``unidentified-*`` placeholder.
    """
    value = (value or "").strip()
    ascii_part = "".join(c if ord(c) < 128 else "" for c in value)
    return normalize_id(ascii_part)


def _legacy_number(dirname: str) -> str:
    match = re.match(r"^(\d+)", dirname)
    return match.group(1) if match else ""


def _legacy_title(dirname: str) -> str:
    return re.sub(
        r"^\d+[-_](?:standalone|patch|xml|translation|lib|empty|special)[-_]",
        "",
        dirname,
    )


def initial_id(package_id: str, package_counts: dict[str, int], dirname: str) -> str:
    """Propose an initial ID, but never bless a placeholder as meaningful.

    The returned value may be an ``unidentified-*`` sentinel for Chinese-only
    names or placeholder package IDs.  ``check_registry.py`` treats that
    sentinel as an error, forcing a manual ID before migration.
    """
    normalized = normalize_id(package_id)
    placeholders = {"modname", "username-modname"}
    is_placeholder = (
        not normalized
        or normalized in placeholders
        or normalized.endswith("-modname")
    )
    if normalized and not is_placeholder:
        if package_counts.get(package_id, 0) <= 1:
            return normalized
        suffix = display_slug(_legacy_title(dirname))
        return f"{normalized}-{suffix}" if suffix else normalized
    suffix = display_slug(_legacy_title(dirname))
    return suffix or f"unidentified-{_legacy_number(dirname) or 'mod'}"


def _path_string(value: str) -> str:
    return (value or "").replace("\\", "/").strip().strip("/")


def _origin_for(entry: dict[str, Any]) -> str:
    origin = entry.get("origin")
    if origin:
        return str(origin)
    category = entry.get("category")
    if category == "record-only":
        # A record-only object is an analysis artifact, not a third code
        # category.  Current records are third-party analyses; keep the
        # origin explicit rather than inventing a fourth ownership value.
        return "collected"
    return LEGACY_CATEGORIES.get(str(category), str(category or ""))


def _code_for(entry: dict[str, Any], origin: str) -> dict[str, Any] | None:
    if "code" in entry:
        code = entry.get("code")
        if code is None:
            return None
        if not isinstance(code, dict):
            raise RegistryError(f"{entry.get('id', '?')}: code must be an object or null")
        result = dict(code)
    else:
        paths = entry.get("legacy_paths", [])
        if not paths or origin not in ORIGINS:
            return None
        result = {"legacy_paths": list(paths)}
    result["legacy_paths"] = [
        _path_string(str(path)) for path in result.get("legacy_paths", []) if str(path).strip()
    ]
    result["target_path"] = _path_string(
        result.get("target_path") or f"mods/{origin}/{entry['id']}"
    )
    return result


def _record_for(entry: dict[str, Any]) -> dict[str, Any] | None:
    if "record" in entry:
        record = entry.get("record")
        if record is None:
            return None
        if not isinstance(record, dict):
            raise RegistryError(f"{entry.get('id', '?')}: record must be an object or null")
        result = dict(record)
    else:
        paths = entry.get("record_paths", [])
        if not paths:
            return None
        result = {"legacy_paths": list(paths)}
    result["legacy_paths"] = [
        _path_string(str(path)) for path in result.get("legacy_paths", []) if str(path).strip()
    ]
    result["path"] = _path_string(result.get("path") or f"records/{entry['id']}")
    return result


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Return one registry entry in the v3 shape without dropping metadata."""
    if not isinstance(entry, dict):
        raise RegistryError("registry entry must be an object")
    mod_id = str(entry.get("id", "")).strip()
    if not mod_id:
        raise RegistryError("registry entry is missing id")
    origin = _origin_for(entry)
    result: dict[str, Any] = {
        "id": mod_id,
        "origin": origin,
        "package_id": str(entry.get("package_id", "") or ""),
        "display_name": str(entry.get("display_name") or mod_id),
        "aliases": [str(alias) for alias in entry.get("aliases", []) if str(alias).strip()],
        "code": _code_for(entry, origin),
        "record": _record_for(entry),
    }
    for key in ("type", "retired", "retired_at", "retired_reason", "notes"):
        if key in entry:
            result[key] = entry[key]
    return result


def normalize_registry(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RegistryError("registry must contain an object")
    raw_entries = data.get("objects")
    if raw_entries is None:
        raw_entries = data.get("mods")
    if not isinstance(raw_entries, list):
        raise RegistryError("registry must contain an objects list")
    return {
        "schema_version": SCHEMA_VERSION,
        "objects": [normalize_entry(entry) for entry in raw_entries],
    }


def load_registry(path: Path | None = None) -> dict[str, Any]:
    path = path or REGISTRY_PATH
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "objects": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot read registry {path}: {exc}") from exc
    return normalize_registry(data)


def save_registry(data: dict[str, Any], path: Path | None = None) -> None:
    path = path or REGISTRY_PATH
    normalized = normalize_registry(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entries_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    normalized = normalize_registry(data)
    result: dict[str, dict[str, Any]] = {}
    for entry in normalized["objects"]:
        mod_id = entry["id"]
        if mod_id in result:
            raise RegistryError(f"duplicate registry id: {mod_id}")
        result[mod_id] = entry
    return result


def aliases_for(data: dict[str, Any]) -> dict[str, str]:
    normalized = normalize_registry(data)
    aliases: dict[str, str] = {}
    for entry in normalized["objects"]:
        mod_id = entry["id"]
        for alias in entry.get("aliases", []):
            if alias in aliases and aliases[alias] != mod_id:
                raise RegistryError(f"alias {alias!r} belongs to both {aliases[alias]} and {mod_id}")
            aliases[alias] = mod_id
    return aliases


def resolve_id(data: dict[str, Any], value: str) -> str | None:
    by_id = entries_by_id(data)
    if value in by_id:
        return value
    by_alias = aliases_for(data)
    return by_alias.get(value) or by_alias.get(normalize_id(value))


def entry_for_legacy_path(data: dict[str, Any], relative_path: str) -> dict[str, Any] | None:
    relative_path = _path_string(relative_path)
    for entry in normalize_registry(data)["objects"]:
        code = entry.get("code") or {}
        record = entry.get("record") or {}
        candidates = set(code.get("legacy_paths", [])) | set(record.get("legacy_paths", []))
        if relative_path in candidates:
            return entry
    return None


def target_path_for(entry: dict[str, Any]) -> Path | None:
    normalized = normalize_entry(entry)
    code = normalized.get("code")
    if code is None:
        return None
    target = code.get("target_path", "")
    if not target:
        return None
    return REPO_ROOT / target


def legacy_paths_for(entry: dict[str, Any]) -> list[Path]:
    normalized = normalize_entry(entry)
    code = normalized.get("code") or {}
    return [REPO_ROOT / path for path in code.get("legacy_paths", [])]


def record_path_for(entry: dict[str, Any]) -> Path | None:
    normalized = normalize_entry(entry)
    record = normalized.get("record")
    if record is None:
        return None
    return REPO_ROOT / record["path"]


def record_legacy_paths_for(entry: dict[str, Any]) -> list[Path]:
    normalized = normalize_entry(entry)
    record = normalized.get("record") or {}
    return [REPO_ROOT / path for path in record.get("legacy_paths", [])]


def active_path_for(entry: dict[str, Any]) -> Path | None:
    """Return the single active code path, or raise when duplicated."""
    normalized = normalize_entry(entry)
    target = target_path_for(normalized)
    legacy = [p for p in legacy_paths_for(normalized) if p.exists()]
    if target is not None and target.exists() and legacy:
        raise RegistryError(
            f"{normalized['id']}: duplicate mod directories: "
            f"{target} and {', '.join(map(str, legacy))}"
        )
    if target is not None and target.exists():
        return target
    if len(legacy) > 1:
        raise RegistryError(f"{normalized['id']}: multiple legacy directories: {legacy}")
    return legacy[0] if legacy else None


def all_active_mod_dirs(data: dict[str, Any]) -> list[tuple[str, Path]]:
    result = []
    for entry in normalize_registry(data)["objects"]:
        path = active_path_for(entry)
        if path is not None:
            result.append((entry["id"], path))
    return result


def iter_code_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for entry in normalize_registry(data)["objects"] if entry.get("code")]


def iter_record_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for entry in normalize_registry(data)["objects"] if entry.get("record")]


def entry_kind(entry: dict[str, Any]) -> str:
    normalized = normalize_entry(entry)
    has_code = bool(normalized.get("code"))
    has_record = bool(normalized.get("record"))
    if has_code and has_record:
        return "code+record"
    if has_code:
        return "code"
    if has_record:
        return "record"
    return "empty"
