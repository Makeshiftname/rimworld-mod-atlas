# 仓库架构 — RimWorld Modding 学习库

## 一句话

这个仓库同时保存三类不同产物，并让它们保持单向、可追踪的关系：

```text
mods/<stable-id>/           可运行的 mod 代码与资源
        │
        │ 分析
        ▼
records/<stable-id>/        单个 mod 的调查档案、证据、建议
        │
        │ 审核后提炼
        ▼
docs/knowledge/             跨 mod 通用知识（guides/reference/mechanics/sources）
```

## 四个区域

| 区域 | 职责 | 是否可直接改 |
|---|---|---|
| `mods/` | 可运行代码样本；`owned/` 原创，`collected/` 第三方 | 只改 `owned/`；`collected/` 视为只读 |
| `records/` | 单个 mod 的分析，保留“它是什么 / 怎么验的 / 可复用结论 / 修改建议” | 可以追加调查与纠错 |
| `docs/knowledge/` | 经审核提炼的通用知识 | 可以维护，但必须能追溯来源 |
| `tools/` | 生成索引、迁移路径、运行门禁的 Python 标准库工具 | 可以改，但必须保留 dry-run 与验收 |

`mods/` 暂未迁移现有代码样本：当前 `自建/`、`收集/` 仍在原位，由 `mods/registry.json` 统一登记旧路径与目标路径。删减完成后运行一次 dry-run，确认后再 `--apply`。

## 稳定 ID

- 唯一权威来源：`mods/registry.json`。
- 初始值优先来自 packageId，冲突或缺失时使用可读名称并在注册表冻结。
- 目录名一旦使用稳定 ID 就不再变更；编号、类型、显示名和路径都可以在索引或注册表中更新。
- 记录和知识页只引用稳定 ID 与 packageId，不依赖目录编号。
- 同一 ID 不允许同时存在于旧目录和目标目录；`check_repo_hygiene.py` 会直接失败。

## 知识提炼规则

1. 单个 mod 的原始结论先进入 `records/<id>/README.md`。
2. 只有复核过、脱离单个 mod 仍成立的结论才写入 `docs/knowledge/guides|reference|mechanics`。
3. 提炼后在知识页保留稳定 ID 或记录链接，并在 `record.json.distilled_to` 登记去向。
4. 记录中的 `modifications` 只记录已经执行的改动；建议仍留在正文，不代表已授权修改。
5. 不自动做过时判断或自动搬运结论；需要时人工标注 `needs-recheck` 或 `superseded`。

## 新增与维护

### 新增一个代码样本

1. 放进 `mods/owned/<stable-id>/` 或 `mods/collected/<stable-id>/`。
2. 在 `mods/registry.json` 登记 `id`、`packageId`、类别、显示名、作者与授权。
3. 运行 `python tools/kb/scan_mods.py`，把元数据刷新到 `docs/knowledge/indexes/`。
4. 运行 `python tools/kb/check_all.py`。

### 新增一份分析记录

1. 读取 `records/STANDARD.md`。
2. 建立 `records/<stable-id>/README.md` 与 `record.json`。
3. 运行 `python tools/kb/scan_records.py`。
4. 运行 `python tools/kb/check_all.py`。

### 迁移旧目录

```powershell
python tools/kb/migrate_mods.py           # 只读预览
python tools/kb/migrate_mods.py --apply   # 确认后一次性 git mv
```

迁移器只处理 `mods/` 代码样本；`records/` 已有自己的稳定 ID 目录。第三方 `mods/collected/**` 的正文和资源永远不由迁移器改写。

## 扩展规则

- 新增知识层前先在 `docs/knowledge/README.md` 说明用途，并保证 `check_knowledge.py` 能从主入口到达。
- 新增工具必须提供默认 dry-run；会改路径的工具必须支持重复执行或明确拒绝冲突。
- 生成文件必须由脚本重建，不手工维护：`registry.json`、`indexes/mods.md`、`indexes/mods.json`、`records/index.json`。
- 运行时数据、缓存、构建产物不进入知识结构；本机 Mods 路径只通过环境变量覆盖，不写入共享逻辑。
