# RimWorld Modding 学习库

个人 RimWorld modding 学习作品集。仓库把**可运行代码样本**、**单 mod 分析记录**和**跨 mod 提炼知识**分开保存，避免路径越积越深、结论到处重复。

## 从这里开始

- 我要做某个 modding 任务 → [`docs/knowledge/README.md`](docs/knowledge/README.md)
- 我要看某个 mod 的分析 → [`records/README.md`](records/README.md)
- 我是 Agent，要开始分析一个 mod → [`records/AGENT_WORKFLOW.md`](records/AGENT_WORKFLOW.md)
- 我要找可运行代码样本 → [`mods/README.md`](mods/README.md)
- 我想了解目录职责与扩展规则 → [`ARCHITECTURE.md`](ARCHITECTURE.md)
- 我想看当前迁移阶段与阻断 → [`docs/STATUS.md`](docs/STATUS.md)

## 当前状态

`mods/` 目标结构、schema v3 稳定 ID 注册表与带引用重写的迁移器已经就位；
现有 `收集/`、`自建/` 代码样本暂时保留原位，等删减完成后按架构文档一次性迁入
`mods/`。

## 常用门禁

```powershell
python tools/kb/check_all.py
```

学习资源与工具说明分别在 [`docs/knowledge/sources/`](docs/knowledge/sources/) 与 [`tools/kb/README.md`](tools/kb/README.md)。

## 许可

`自建/` 与未来 `mods/owned/` 下的原创 mod 使用 [MIT 许可](LICENSE)。`收集/` 与未来 `mods/collected/` 下的第三方 mod 保留各自许可，仅供本地学习，不擅自再发布。
