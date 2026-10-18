#!/usr/bin/env python3
"""收录区记录门禁（acceptance gate for the 收录/ records area）.

检查项（退出码 0 = 全部通过，1 = 有问题）：
  1. 每份记录是否含四个必答锚点章节
     身份卡 / 它是什么 / 怎么验的 / 可复用结论
  2. 收录目录名能否对上 F:\\Games\\GBL\\rimworld\\Mods\\ 下的源目录
     （允许「工坊ID-可读后缀」形态）
  3. 记录里出现的 Mods 绝对路径是否真实存在
  4. 收录/README.md 的索引表是否覆盖全部记录

注意：`check_links.py` 不覆盖本区（只扫 AGENTS.md + docs/knowledge/*.md +
mod-index.md），所以本脚本是收录区唯一的自动校验。

用法：
  python tools/kb/check_records.py
  RIMWORLD_MODS_DIR=D:\\path\\to\\Mods python tools/kb/check_records.py

退出码：0 = OK，1 = 有问题，2 = 无法校验（Mods 目录不存在且未提供环境变量）。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

RECORDS_DIRNAME = "收录"
RECORDS_DIR = Path(__file__).resolve().parent.parent.parent / RECORDS_DIRNAME
INDEX_MD = RECORDS_DIR / "README.md"

REQUIRED_ANCHORS = ("身份卡", "它是什么", "怎么验的", "可复用结论")
OPTIONAL_SECTION = "修改建议"

DEFAULT_MODS_DIR = r"F:\Games\GBL\rimworld\Mods"

# 收录目录名是源目录名的「可读缩短形式」时的显式对照。
# 规则见 收录/README.md §2：太长或带无意义前后缀时可缩短，但必须能唯一识别。
DIR_ALIASES: dict[str, str] = {
    "美南烛": "1 美南烛",
    "1~11岁美狐贴图修正": "1~11岁美狐贴图修正(本体更新修复版)",
}


def find_mods_dir() -> Path | None:
    cand = os.environ.get("RIMWORLD_MODS_DIR") or DEFAULT_MODS_DIR
    p = Path(cand)
    return p if p.is_dir() else None


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def h2_sections(text: str) -> set[str]:
    """Return the set of level-2 heading titles (whitespace-normalized)."""
    return {" ".join(m.group(1).split()) for m in re.finditer(r"(?m)^##\s+(.+?)\s*$", text)}


def resolve_source_dir(name: str, mods: Path) -> Path | None:
    """Map a 收录 dir name to its source dir under Mods/.

    Accepts three shapes (see 收录/README.md §2):
      - exact source name                        美南烛
      - <workshop id>-<readable suffix>          717575199-MiscTraining
      - explicit alias (deliberate shortening)   1~11岁美狐贴图修正 -> …(本体更新修复版)
    """
    if (mods / name).is_dir():
        return mods / name
    m = re.match(r"^(\d+)-(.+)$", name)
    if m and (mods / m.group(1)).is_dir():
        return mods / m.group(1)
    alias = DIR_ALIASES.get(name)
    if alias and (mods / alias).is_dir():
        return mods / alias
    return None


def mods_paths_in(text: str) -> list[str]:
    """Extract Mods-directory paths mentioned in backtick spans.

    Backticks are used because source dir names may contain spaces
    (e.g. `1 美南烛`), which breaks naive whitespace-delimited scanning.
    """
    prefix = DEFAULT_MODS_DIR.replace("\\", "\\\\")
    out = []
    for m in re.finditer(r"`([^`\n]+)`", text):
        inner = m.group(1).strip()
        inner = re.split(r"[。；;，,]", inner)[0].strip().rstrip("\\")
        if inner.startswith(DEFAULT_MODS_DIR + "\\"):
            out.append(inner[len(DEFAULT_MODS_DIR) + 1:])
        elif inner.replace("\\\\", "\\").startswith(prefix):
            pass
    return out


def main() -> int:
    problems: list[str] = []
    warnings: list[str] = []

    if not RECORDS_DIR.is_dir():
        print("收录区不存在: %s" % RECORDS_DIR)
        return 2

    mods = find_mods_dir()
    if mods is None:
        warnings.append(
            "找不到 Mods 目录（默认 %s），跳过第 2、3 项检查。"
            "设 RIMWORLD_MODS_DIR 环境变量可启用。" % DEFAULT_MODS_DIR
        )

    records = []
    for d in sorted(RECORDS_DIR.iterdir()):
        if not d.is_dir():
            continue
        readme = d / "README.md"
        if not readme.is_file():
            problems.append("%s/: 缺少 README.md" % d.name)
            continue
        records.append((d.name, readme))

    if not records:
        problems.append("收录区没有任何记录")
        for w in warnings:
            print("  warning: %s" % w)
        for p in problems:
            print("  - %s" % p)
        return 1

    # ---- 1. anchors ----
    for name, readme in records:
        secs = h2_sections(read(readme))
        missing = [a for a in REQUIRED_ANCHORS if a not in secs]
        if missing:
            problems.append("%s/README.md: 缺少必答锚点章节 %s" % (name, "、".join(missing)))

    # ---- 2 & 3. source dir mapping + Mods paths ----
    if mods:
        for name, readme in records:
            if resolve_source_dir(name, mods) is None:
                problems.append(
                    "%s/: 在 %s 下找不到对应的源目录（需精确匹配、「工坊ID-可读名」形态，"
                    "或已在 DIR_ALIASES 中登记）" % (name, mods)
                )
            for rel in mods_paths_in(read(readme)):
                if not (mods / rel).exists():
                    problems.append("%s/README.md: 引用的路径不存在 -> %s" % (name, rel))

    # ---- 4. index coverage ----
    if INDEX_MD.is_file():
        index_text = read(INDEX_MD)
        # Only count first-column cells of markdown table rows, otherwise every
        # backticked path in the prose would look like an index entry.
        listed = set()
        for line in index_text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cell = line.strip().lstrip("|").strip()
            m = re.match(r"^`([^`]+/)`", cell)
            if m:
                listed.add(m.group(1))
        actual = {n + "/" for n, _ in records}
        for mname in sorted(actual - listed):
            problems.append("收录/README.md: 索引表缺少记录 %s" % mname)
        for ename in sorted(listed - actual):
            warnings.append("收录/README.md: 索引表列了非记录目录的条目 %s" % ename)
    else:
        problems.append("缺少收录/README.md（索引与标准本体）")

    for w in warnings:
        print("  warning: %s" % w)
    if problems:
        print("收录区问题 (%d):" % len(problems))
        for p in problems:
            print("  - %s" % p)
        return 1

    print("收录区检查通过：%d 份记录。" % len(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
