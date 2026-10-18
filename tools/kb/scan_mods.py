#!/usr/bin/env python3
"""Scan all RimWorld mods and generate the knowledge-base indexes.

Outputs:
  docs/knowledge/indexes/mods.json - machine-readable metadata
  docs/knowledge/indexes/mods.md   - Markdown index (auto section + manual notes)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import kb_common as kb


def tick(value: bool) -> str:
    return "✓" if value else "–"


def type_label(type_name: str, confidence: str) -> str:
    return f"{type_name}?" if confidence == "low" else type_name


def build_markdown(mods: list[dict]) -> str:
    stats: dict[str, int] = {}
    for mod in mods:
        stats[mod["type"]] = stats.get(mod["type"], 0) + 1
    readme_stats: dict[str, int] = {}
    for mod in mods:
        readme_stats[mod["readme_status"]] = readme_stats.get(mod["readme_status"], 0) + 1

    lines = [
        "# Mod Index — RimWorld 知识库",
        "",
        "> 元数据表由 `tools/kb/scan_mods.py` 自动生成，请勿手改本区间。",
        "> 「要点与知识点链接」在文件末尾 `<!-- MANUAL -->` 区间内人工维护。",
        "",
        "## 统计",
        "",
    ]
    cat_stats: dict[str, int] = {}
    for mod in mods:
        category = mod.get("category", "")
        cat_stats[category] = cat_stats.get(category, 0) + 1
    lines.append(
        f"- Mod 总数：**{len(mods)}**（"
        + "、".join(f"`{c}` × {n}" for c, n in sorted(cat_stats.items(), key=lambda x: x[1], reverse=True))
        + "）"
    )
    lines.append("- 类型分布：" + "、".join(f"`{t}` × {c}" for t, c in sorted(stats.items())))
    lines.append("- README 状态：" + "、".join(f"`{k}` × {v}" for k, v in sorted(readme_stats.items())))
    lines.extend([
        "",
        "## 索引表",
        "",
        "| ID | # | 类 | Mod | Type | Versions | C# | 翻 | Doc | Tst | Pub | README |",
        "|----|---|----|-----|------|----------|----|----|-----|-----|-----|--------|",
    ])
    for mod in mods:
        versions = ",".join(mod["versions"]) or ("backup" if mod["in_backup"] else "-")
        lines.append(
            f"| `{mod['id']}` | {mod['number']} | {mod.get('category', '')} | {mod['title']} | "
            f"{type_label(mod['type'], mod['type_conf'])} "
            f"| {versions} | {tick(mod['has_csharp'])} | {tick(mod['has_languages'])} "
            f"| {tick(mod['has_docs'])} | {tick(mod['has_tests'])} "
            f"| {tick(mod['has_publisher_plus'])} | {mod['readme_status']} |"
        )
    lines.extend([
        "",
        "> 图例：C#=有 C# 源码；翻=Languages/ 翻译；Doc=docs/；Tst=Tests/；",
        "> Pub=`_PublisherPlus.xml`；README=ok/模板占位(template)/空壳(stub)/缺失(missing)。",
        "> Type 带 `?` 表示启发式推断置信度低（patch 与 standalone 需人工核实）。",
        "",
    ])
    return "\n".join(lines)


def build_json(mods: list[dict]) -> str:
    return json.dumps(mods, ensure_ascii=False, indent=2)


def write_index(mods: list[dict], json_only: bool = False) -> None:
    kb.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    kb.INDEX_JSON.write_text(build_json(mods) + "\n", encoding="utf-8")
    if json_only:
        print(f"wrote {kb.INDEX_JSON}")
        return

    auto = f"{kb.AUTO_START}\n{build_markdown(mods)}\n{kb.AUTO_END}"
    manual = ""
    if kb.INDEX_MD.exists():
        existing = kb.INDEX_MD.read_text(encoding="utf-8", errors="replace")
        body = kb.extract_manual(existing)
        if body is not None:
            manual = f"\n{kb.MANUAL_START}\n{body}\n{kb.MANUAL_END}\n"

    header = (
        "# RimWorld Mod 知识库 — Mod 索引\n\n"
        "> 本文件两段式：上方「索引表」由脚本自动维护；下方「要点」为人工维护的"
        "知识点与链接，脚本更新时保留不动。\n\n"
    )
    kb.INDEX_MD.write_text(header + auto + "\n" + manual, encoding="utf-8")
    print(f"wrote {kb.INDEX_MD}")
    print(f"wrote {kb.INDEX_JSON}")


def check_changes(mods: list[dict]) -> int:
    if not kb.INDEX_JSON.exists():
        print(f"no previous {kb.INDEX_JSON}; run without --check first", file=sys.stderr)
        return 2
    previous = json.loads(kb.INDEX_JSON.read_text(encoding="utf-8"))
    previous_by_id = {m["id"]: m for m in previous}
    current_by_id = {m["id"]: m for m in mods}
    changes = []
    for mod_id in sorted(set(current_by_id) - set(previous_by_id)):
        changes.append(f"  [added]   {mod_id}")
    for mod_id in sorted(set(previous_by_id) - set(current_by_id)):
        changes.append(f"  [removed] {mod_id}")
    fields = (
        "readme_status", "type", "versions", "has_csharp", "has_languages",
        "has_docs", "has_tests", "has_agents", "has_publisher_plus", "dir",
    )
    for mod_id in sorted(set(current_by_id) & set(previous_by_id)):
        old, new = previous_by_id[mod_id], current_by_id[mod_id]
        diffs = [f"{field}:{old.get(field)}->{new.get(field)}"
                 for field in fields if old.get(field) != new.get(field)]
        if diffs:
            changes.append(f"  [changed] {mod_id}: {'; '.join(diffs)}")
    if changes:
        print("Changes since last index:")
        print("\n".join(changes))
        return 1
    print("No changes since last index.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="compare vs last index and report changes (no rewrite)")
    parser.add_argument("--json-only", action="store_true",
                        help="only refresh mods.json, leave mods.md untouched")
    args = parser.parse_args()
    mods = kb.scan_all()
    if args.check:
        return check_changes(mods)
    write_index(mods, json_only=args.json_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
