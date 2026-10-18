# 知识库维护指南（CONTRIBUTING）

本文档说明如何维护 `docs/knowledge/` 与代码样本、分析记录之间的关系。完整架构见
[`ARCHITECTURE.md`](../../ARCHITECTURE.md)，工具说明见 [`tools/kb/README.md`](../../tools/kb/README.md)。

**验收门槛：任何改动后运行 `python tools/kb/check_all.py`，必须退出码 0。**

## 知识库结构

```text
docs/knowledge/
├── README.md              # 按任务导航的主入口
├── CONTRIBUTING.md        # 本文档
├── guides/                # 从代码样本和分析记录提炼的实操方法
├── reference/             # rimworldwiki vetted 区的参考手册
├── mechanics/             # 本地 Defs + 官方简中译文整理的游戏机制
├── sources/               # 外部来源、抓取与核验规则
└── indexes/               # 自动生成的 mod 元数据与人工要点
```

## 规则

1. **生成/手写分离**：`indexes/mods.md` 完全由 `scan_mods.py` 重写；
   人工维护的单 mod 要点放在 `indexes/mods-notes.md`。
2. **知识分层**：单 mod 事实和未审核推断留在 `records/`；只有跨 mod、已复核的结论才进入 `guides/reference/mechanics`。
3. **稳定 ID**：目录、记录和知识页引用使用 `mods/registry.json` 登记的稳定 ID；
   registry 是人工维护的 schema v3 身份表，`code` 与 `record` 分开登记。
4. **链接相对所在文件解析**：迁移后优先用注册表 ID 或脚本生成的相对路径，不手写旧编号。

## 更新场景

### A. 新增代码样本

1. 放进 `mods/owned/<stable-id>/` 或 `mods/collected/<stable-id>/`。
2. 在 `mods/registry.json` 登记 `id`、`origin`、`packageId`、别名和
   `code.legacy_paths` / `code.target_path`；作者与许可写进 `record.json`。
3. 运行 `python tools/kb/scan_mods.py`。
4. 运行 `python tools/kb/scan_records.py --check` 与 `python tools/kb/check_all.py`。

### B. 新增或修改分析记录

1. 先读 [`records/STANDARD.md`](../../records/STANDARD.md) 和
   `tools/kb/templates/record/`。
2. 在 `records/<stable-id>/` 更新 `README.md` 与 `record.json`。
3. 运行 `python tools/kb/scan_records.py`。
4. 若产生已审核的跨 mod 结论，按 `STANDARD.md` 的提炼规则写入知识页并登记
   `record.json.distilled_to`，然后运行
   `python tools/kb/sync_knowledge_sources.py --write` 更新知识页底部的
   `## 来源记录` 段。
5. 运行 `python tools/kb/check_all.py`。

### B2. 删除或退役一个代码样本

1. 从 `mods/` 或旧 `收集/`、`自建/` 删除代码目录。
2. 保留 `records/<id>/`，在 `record.json` 设置 `code_removed: true`；
   registry 条目可设置 `retired: true`。
3. 如果该记录来源的知识页仍依赖它，把相关结论标为
   `needs-recheck`，不要静默删除证据。
4. 运行 `python tools/kb/scan_records.py` 和 `python tools/kb/check_all.py`。

### C. 修改知识页

1. 确认结论适用于跨 mod 场景，并保留来源 ID 或记录链接。
2. 只改对应层：实操 → `guides/`；参考手册 → `reference/`；机制手册 → `mechanics/`；外部来源 → `sources/`。
3. 若新增/删除来源记录，先改 `record.json.distilled_to`，再运行
   `python tools/kb/sync_knowledge_sources.py --write`；不要手改
   `## 来源记录` 段。
4. 运行 `python tools/kb/check_all.py`。

### D. 迁移旧 `收集/`、`自建/` 到 `mods/`

1. 运行 `python tools/kb/migrate_mods.py --json` 查看包含文件数和冲突的计划。
2. 确认无 `missing` / `conflict` 后运行 `python tools/kb/migrate_mods.py --apply`；
   该命令会同步重写第一方引用。
3. 运行 `python tools/kb/scan_mods.py`、`python tools/kb/scan_records.py` 和
   `python tools/kb/check_all.py`。

## README 重写模板

代码样本的 README 仍按下面结构书写；第三方内容只补充记录，不改本体：

```markdown
# <Mod 名称> Notes

## 一句话定位

## 解决的问题 / 关键要点

## 目录结构

## 构建与部署

## 相关文件
```

内容必须与 `About/About.xml` 一致（名称、描述、依赖），不得为模板占位。
