# RimWorld Modding 学习库

个人 RimWorld modding 学习作品集。仓库把**可运行代码样本**、**单 mod 分析记录**和**跨 mod 提炼知识**分开保存，避免路径越积越深、结论到处重复。

## 从这里开始

- 我要做某个 modding 任务 → [`docs/knowledge/README.md`](docs/knowledge/README.md)
- 我要看某个 mod 的分析 → [`records/README.md`](records/README.md)
- 我是 Agent，要开始分析一个 mod → [`records/AGENT_WORKFLOW.md`](records/AGENT_WORKFLOW.md)
- 我要找可运行代码样本 → [`mods/README.md`](mods/README.md)
- 我要开发原创或补丁 mod → [`rimworld-mod-forge`](https://github.com/Makeshiftname/rimworld-mod-forge)
- 我想了解目录职责与扩展规则 → [`ARCHITECTURE.md`](ARCHITECTURE.md)
- 我想看当前迁移阶段与阻断 → [`docs/STATUS.md`](docs/STATUS.md)

## 当前状态

`mods/registry.json` 已升级为 schema v4：本地代码样本使用 `code.kind: local`，
生产代码可以直接登记为另一个仓库中的 `code.kind: external`。
原 `自建/01-xml-RimTalkPersonaTraits` 草稿已迁入
[`rimworld-mod-forge`](https://github.com/Makeshiftname/rimworld-mod-forge)，
Atlas 不再保留该草稿的生产代码，只保留稳定 ID、记录和知识索引。现有 86 个 `收集/` 代码样本仍在原位，
等删减完成后按架构文档一次性迁入 `mods/collected/`。

## 常用门禁

```powershell
python tools/kb/check_all.py
```

学习资源与工具说明分别在 [`docs/knowledge/sources/`](docs/knowledge/sources/) 与 [`tools/kb/README.md`](tools/kb/README.md)。

## 许可

本仓库混合了第三方代码、原创分析记录和知识文档，不能用一个许可证一概而论。
具体边界见 [`docs/LICENSING.md`](docs/LICENSING.md)。第三方样本保留各自许可，
仅供学习与本地审计；Makeshiftname 的原创生产 mod 位于
`rimworld-mod-forge`，使用该仓库自己的 MIT 许可。
