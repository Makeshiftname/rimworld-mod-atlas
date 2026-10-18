# 仓库架构 — RimWorld Modding 学习库

## 一句话

仓库同时保存三类不同产物，并让它们保持单向、可追踪的关系：

```text
mods/collected/<stable-id>/            本地第三方代码样本
rimworld-mod-forge (external)          原创与补丁 mod 的生产仓库
        │
        │ 分析
        ▼
records/<stable-id>/                  单个 mod 的调查档案、证据、建议
        │
        │ 审核后提炼
        ▼
docs/knowledge/                       跨 mod 通用知识
```

## 区域职责

| 区域 | 职责 | 是否可直接改 |
|---|---|---|
| `mods/` | 本地代码样本；`collected/` 第三方，`owned/` 只保留外部登记说明 | `collected/` 视为只读；生产代码在 forge 修改 |
| registry `code.kind: external` | 指向 forge/forks 的仓库、路径和 commit | 只改元数据，不复制外部代码 |
| `records/` | 单个 mod 的分析；初步档做分流，深度档保留“它是什么 / 怎么验的 / 可复用结论 / 修改建议” | 可以追加调查与纠错 |
| `docs/knowledge/` | 经审核提炼的通用知识 | 可以维护，但必须能追溯来源 |
| `tools/` | 生成索引、迁移路径、运行门禁的 Python 标准库工具 | 可以改，但必须保留 dry-run 与验收 |

`mods/collected/` 暂未迁移现有 86 个 `收集/` 代码样本，由
`mods/registry.json` 统一登记旧路径与目标路径。删减完成后运行一次
manifest 预览，确认后再 `--apply`。原创生产代码不在 Atlas 本地保存，
通过 `code.kind: external` 指向 `rimworld-mod-forge`。

## 真相源

| 产物 | 只负责 |
|---|---|
| `mods/registry.json` | 稳定 ID、`origin`、别名、代码与记录的关联 |
| `records/<id>/record.json` | 来源、作者、许可、分析档位、分析状态、提炼去向 |
| `records/<id>/README.md` | 证据、反面发现，以及深度档的结论和可选修改建议 |
| `docs/knowledge/indexes/*` | 从注册表和记录生成的视图，不手改 |

`registry.json` 是人工维护的身份表，不是生成文件。`gen_registry.py`
只生成 `mods/registry.proposed.json` 供合并，不会覆盖权威文件。`indexes/mods.md`
是纯生成索引；人工要点在 `indexes/mods-notes.md`。

## 稳定 ID

- 唯一权威来源：`mods/registry.json`。
- schema v4 把 `origin` 与 `code` / `record` 分开；`code.kind` 区分
  `local` 与 `external`，`record-only` 不再是一个容易与来源混淆的目录类别。
- 外部代码必须登记 `repo`、`path` 和固定 `commit`；Atlas 不 clone、不扫描
  外部仓库，只校验元数据。
- ID 使用小写 ASCII slug；`packageId` 是独立字段和 alias。新 ID 不再机械
  等于 `packageId`，占位 packageId、中文名和无 packageId 对象必须人工命名。
- 目录名一旦使用稳定 ID 就不再变更；编号、类型、显示名和路径都可以在索引或
  注册表中更新。
- 记录和知识页只引用稳定 ID 与 packageId，不依赖目录编号。
- 同一 ID 不允许同时存在于旧目录和目标目录；`check_registry.py` 和
  `check_repo_hygiene.py` 都会直接失败。

## 记录生命周期

1. 新记录按任务选择 `tools/kb/templates/record/initial/` 或
   `deep/`，写 `records/<id>/README.md` 和 `record.json`。
2. `analysis_tier` 使用 `initial` / `deep`；`status` 使用
   `analyzed` / `needs-recheck` / `superseded` / `retired`。不再使用 `raw`。
3. 初步记录只做分流，不写可复用结论和修改建议，不能提炼；深度记录才支撑
   修改、发布、兼容性/许可判断和知识提炼。
4. 初步记录原地升级为深度记录，同一个稳定 ID、同一个路径，不新建
   `-initial` / `-deep` 副本；深度记录不降级，证据失效用 `status` 表达。
5. 代码被删除时保留记录，设置 `code_removed: true` 或 registry 的
   `retired`，不要把分析一起删掉。
6. 只有 `deep + analyzed`、复核过且脱离单个 mod 仍成立的结论才写入
   `docs/knowledge/guides|reference|mechanics`。
7. 提炼后在知识页保留稳定 ID 或记录链接，并在
   `record.json.distilled_to` 登记去向。知识页底部的 `## 来源记录`
   段由 `tools/kb/sync_knowledge_sources.py --write` 生成，门禁会同时检查
   目标存在、记录 ID 和反向列表是否一致。

## 新增与维护

### 新增一个本地第三方代码样本

1. 放进 `mods/collected/<stable-id>/`。
2. 在 `mods/registry.json` 登记 `id`、`origin`、`packageId`、别名，以及
   `code.legacy_paths` / `code.target_path`。作者和许可写进 `record.json`，
   不要重复塞进 registry。
3. 运行 `python tools/kb/scan_mods.py`，把元数据刷新到
   `docs/knowledge/indexes/`。
4. 运行 `python tools/kb/check_all.py`。

### 新增一个外部原创/补丁 mod

1. 生产代码放进 `rimworld-mod-forge` 或 `rimworld-mod-forks`，不在 Atlas 复制。
2. 在 `mods/registry.json` 登记稳定 ID、`packageId` 和外部代码位置：

   ```json
   "code": {
     "kind": "external",
     "repo": "https://github.com/Makeshiftname/rimworld-mod-forge",
     "path": "mods/owned/<stable-id>",
     "commit": "<固定 SHA>"
   }
   ```

3. 需要分析记录时，在 `records/<stable-id>/` 建立记录，并链接回具体 commit。
4. 运行 `python tools/kb/check_all.py`；`scan_mods.py` 不会扫描外部代码。

### 新增一份分析记录

1. 读取 `records/AGENT_WORKFLOW.md` 与 `records/STANDARD.md`，选择
   `tools/kb/templates/record/initial/` 或 `deep/`。
2. 建立 `records/<stable-id>/README.md` 与 `record.json`，填写
   `analysis_tier`。
3. 运行 `python tools/kb/scan_records.py`。
4. 运行 `python tools/kb/check_all.py`。

### 迁移旧目录

```powershell
python tools/kb/migrate_mods.py --json
python tools/kb/migrate_mods.py --apply
```

先确认 plan 中没有 `missing` / `conflict`，并审阅 `--json` 的文件数量。`--apply`
会移动代码、用精确路径映射重写根文档/`docs/`/`records/`/`mods/owned/` 的第一方引用，
然后提示重新生成索引。第三方 `mods/collected/**` 的正文和资源永远不改写。

## 扩展规则

- 新增知识层前先在 `docs/knowledge/README.md` 说明用途，并保证
  `check_knowledge.py` 能从主入口到达。
- 新增工具必须提供默认 dry-run；会改路径的工具必须支持重复执行或明确拒绝冲突。
- 生成文件必须由脚本重建，不手工维护：`indexes/mods.md`、`indexes/mods.json`、
  `records/index.json`。`indexes/mods-notes.md`、`registry.json` 和
  `record.json` 是人工维护的身份/证据/笔记文件，不当作纯生成物。
- 运行时数据、缓存、构建产物不进入知识结构；本机 Mods 路径只通过
  `RIMWORLD_MODS_DIR` 环境变量提供。
- 阶段状态写在 `docs/STATUS.md`，不要依赖临时 handoff 文件或 Git 提交说明。
