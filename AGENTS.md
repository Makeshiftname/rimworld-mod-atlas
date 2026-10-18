# AGENTS.md — RimWorld Modding 仓库

本仓库的目录职责、稳定 ID、提炼规则和迁移流程以
[`ARCHITECTURE.md`](ARCHITECTURE.md) 为唯一入口；本文件只保留执行任务时容易踩错的约定。

## 开始前

1. 先读根 [`ARCHITECTURE.md`](ARCHITECTURE.md) 与 [`docs/knowledge/README.md`](docs/knowledge/README.md)。
2. 单 mod 调查先读 [`records/AGENT_WORKFLOW.md`](records/AGENT_WORKFLOW.md)
   （操作流程）和 [`records/STANDARD.md`](records/STANDARD.md)（契约），
   再按任务选择 `tools/kb/templates/record/initial/` 或 `deep/`。
3. 开始迁移或审查结构前先看 [`docs/STATUS.md`](docs/STATUS.md)。
4. 需要游戏机制/实现背景时，按知识库主入口选择 `guides/`、`reference/` 或 `mechanics/`。
5. 不读取整个大目录做无差别审阅；先查索引、注册表和目标记录。

## 目录与编辑边界

- `mods/owned/` 与现有 `自建/`：仓库主原创，可按任务修改。
- `mods/collected/` 与现有 `收集/`：第三方供应内容，默认只读；不要改 About/C#/Defs/资源。
- `records/`：分析档案；保留证据与纠错，不删除反面发现。
- `docs/knowledge/`：只放经审核的通用结论；单 mod 专属信息留在记录。
- `mods/registry.json` 是稳定 ID 唯一权威；schema v3 使用 `origin + code + record`，
  该文件人工维护，不能由脚本覆盖。

## 常用命令

```powershell
python tools/kb/check_all.py                 # 所有门禁
python tools/kb/scan_mods.py                 # 刷新代码样本索引
python tools/kb/scan_records.py              # 刷新记录索引
python tools/kb/migrate_mods.py --json       # mods/ 迁移计划（含文件数）
python tools/kb/migrate_mods.py --manifest migration.json
python tools/kb/migrate_mods.py --apply      # 确认后移动并重写第一方引用
```

## 构建与测试

- 构建：`cd <版本>/Source && dotnet build -c Release`，产物 DLL 随源码提交。
- 纯逻辑可加 C# 单测；RimWorld 运行时对象无法在游戏外实例化时，使用 Python 静态白盒测试。
- 运行时路径只在本地配置或环境变量中提供；共享脚本不硬编码某台机器的游戏目录。

## 维护规则

- 生成物由脚本重建，不手改：`indexes/mods.md`、`indexes/mods.json`、`records/index.json`。
- `indexes/mods-notes.md` 是人工笔记；`registry.json` 和 `record.json` 是身份/证据文件。
- 记录用 `analysis_tier: initial | deep` 分档；初步记录禁止提炼和修改建议。
- 修改结构后运行 `check_all.py`；链接、记录身份、目录卫生、索引漂移都必须通过。
- 第三方 mod 的 `packageId` 应进入 `<loadAfter>` 而非 `<modDependencies>`（仅当它是补丁前置而非硬依赖）。
- 改动 `About.xml` 后同步对应描述与记录。
- 新增长期规则时先更新 `ARCHITECTURE.md`，不要继续把背景知识堆进本文件。

## 技能触发

显式点名最可靠；常用映射：

| 任务 | skill / 触发 |
|---|---|
| 外部资料调研并落盘 | `research` / “研究 X” |
| 难缠 bug 或性能回归 | `diagnosing-bugs` / “诊断 X” |
| 测试先行 | `tdd` |
| 审查改动 | `code-review` |
| 设计接口/模块 | `codebase-design` |
| 重构规划 | `request-refactor-plan` |
| 合并冲突 | `resolving-merge-conflicts` |

RimWorld 知识库问题优先使用本地 `ragQuery`；新增知识文档后按 RAG 扩展侧流程重新索引。
