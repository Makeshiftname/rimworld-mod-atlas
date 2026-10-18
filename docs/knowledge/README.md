# RimWorld Mod 知识库

这里是**经审核后提炼**的跨 mod 知识。单个 mod 的调查过程、原始证据和修改建议不放在这里，而在仓库根目录的 [`records/`](../../records/README.md)；可运行代码样本在 [`mods/`](../../mods/README.md)。

## 先按任务找

| 我想做什么 | 去哪里 |
|---|---|
| 给原版或第三方功能打补丁 | [guides/harmony-patching.md](guides/harmony-patching.md) |
| 画窗口、加切换栏图标、用 Widgets | [guides/ui-and-windows.md](guides/ui-and-windows.md) |
| 写每 tick 逻辑、GameComponent、存档 | [guides/game-and-world-components.md](guides/game-and-world-components.md) |
| 改 Defs、PatchOperation、纯 XML | [guides/xml-defs-and-patches.md](guides/xml-defs-and-patches.md) |
| 翻译 / Languages 结构 | [guides/translations-localization.md](guides/translations-localization.md) |
| 设计跨版本目录、Common/ | [guides/cross-version-structure.md](guides/cross-version-structure.md) |
| 写静态白盒测试和验收门禁 | [guides/testing-and-validation.md](guides/testing-and-validation.md) |
| 排查卡顿与 GUI 性能 | [guides/performance-and-gui.md](guides/performance-and-gui.md) |
| 新建 C# mod 骨架、日志模板 | [guides/project-templates.md](guides/project-templates.md) |
| 发布、软链接、工坊版权红线 | [guides/publishing-and-release.md](guides/publishing-and-release.md) |
| 静态审计一个 mod 的依赖、程序集、翻译、贴图、多版本 | [guides/mod-static-audit.md](guides/mod-static-audit.md) |
| 查某个 mod 的具体分析记录 | [../indexes/mods.md](indexes/mods.md) + [`records/`](../../records/README.md) |

## 四层内容

- **guides/**：从本仓库实际代码与调查记录中提炼的实操方法，回答“在这里怎么做”。
- **reference/**：蒸馏 rimworldwiki Modding Tutorials vetted 区，回答“这个字段/流程完整是什么”。
- **mechanics/**：从本地游戏 Defs + 官方简中译文整理的机制手册，回答“游戏系统本身由什么构成”。
- **sources/**：外部来源索引、抓取与校验规则，说明知识从哪里来。

## 索引与数据

- [`indexes/mods.md`](indexes/mods.md)：全部代码样本的元数据表 + 人工维护的学习要点。
- [`indexes/mods.json`](indexes/mods.json)：机器可读索引。
- [`../records/index.json`](../../records/index.json)：分析记录索引。
- [`../../mods/registry.json`](../../mods/registry.json)：稳定 ID、packageId、旧路径与别名注册表。

## 维护

- 目录职责、提炼规则和新内容放置位置：[`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)。
- 新增/修改 mod 的流程与验收门槛：[CONTRIBUTING.md](CONTRIBUTING.md)。
- 工具链说明：[tools/kb/README.md](../../tools/kb/README.md)。

## 内容边界

`guides/reference/mechanics` 只接收**审核后的通用结论**。如果结论只适用于某一 mod，或还带有未验证的推断，保留在 `records/<id>/`；提炼时在知识页和被引用的记录之间保留稳定 ID 链接。
