# 仓库状态

> 只记录当前阶段、阻断和下一步；长期规则见
> [`../ARCHITECTURE.md`](../ARCHITECTURE.md)。

## 当前阶段

- `mods/registry.json` 已升级为 schema v3：`origin + code + record` 分离，
  旧 v2 文件仍可由读取器兼容。
- `records/` 已按稳定 ID 存放 28 份分析记录，索引由
  `tools/kb/scan_records.py` 生成；28 份记录的 `license` 字段均已显式填写，
  作者判断与许可说明分别登记在 `author_evidence` / `license_notes`。
- `record.json` 已升级到 schema v3：记录用 `analysis_tier: initial | deep`
  分档，`verification_tier` 已移除；现有 28 份记录全部标为 `deep`。
  两档模板分别在 `tools/kb/templates/record/initial/` 与 `deep/`。
- `docs/knowledge/` 已分为 `guides/`、`reference/`、`mechanics/`、`sources/`
  与 `indexes/`；`indexes/mods.md` 是纯生成文件，人工笔记在
  [`indexes/mods-notes.md`](knowledge/indexes/mods-notes.md)。
- 知识页的反向来源列表由 `tools/kb/sync_knowledge_sources.py` 从
  `record.json.distilled_to` 生成；门禁校验双向一致，不手写 ID 列表。
- 现有 `自建/`、`收集/` 代码样本尚未迁移到 `mods/`；迁移必须先通过
  [`migration` 前置检查](../tools/kb/migrate_mods.py)。
  当前只读计划为 87 个 `move`、0 个结构错误，合计约 2,589 个文件。
- 用户已明确暂不删减 mod；本轮未移动、删除或改写任何 `收集/`、`自建/` 代码。

## 最近验证

在仓库根目录执行：

```powershell
python tools/kb/check_all.py
python -m unittest discover -s tools/kb/tests -v
```

2026-10-18 结果：`check_all.py` 退出码 0；30 个单测通过；`收集/`、`自建/`
代码目录无 diff。

## 下一步

1. 按优先级给现有深度记录补 `### 范围`、`### 未核验` 与
   `[已确认] / [推断] / [未核验]` 结论标签。
2. 用户完成 mod 删减后，先运行 `migrate_mods.py --json` 检查未登记、失效和冲突。
3. 审阅 manifest，再执行 `migrate_mods.py --apply`；迁移器会同步重写第一方引用。
4. 运行扫描器与 `check_all.py`，确认旧/新布局没有并存。

记录和知识页的修正不依赖 mods 迁移，可独立进行。
