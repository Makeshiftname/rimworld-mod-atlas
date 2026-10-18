# mods — 代码样本

`mods/` 保存可运行的 mod 代码与资源，按授权与可发布边界分为：

- [`owned/`](owned/)：仓库主本人原创，可实际维护与发布。
- [`collected/`](collected/)：第三方 mod，仅作学习与本地审计，默认不改动本体。

记录对象的稳定身份写在 [`registry.json`](registry.json)；分析记录在 [`records/`](../records/README.md)，提炼知识在 [`docs/knowledge/`](../docs/knowledge/README.md)。

## 稳定 ID

目录名使用 `<stable-id>`，不再用 `NN-功能-名称` 排序。编号与类型已移到自动生成的 [`docs/knowledge/indexes/mods.md`](../docs/knowledge/indexes/mods.md)，因此删减、重排或补档不会改变引用。

新内容直接放进对应大类；已有旧目录先由 [`tools/kb/migrate_mods.py`](../tools/kb/migrate_mods.py) 扫描并生成映射，确认后才用 `--apply` 一次性迁移。

## 第三方边界

`collected/**` 是只读供应内容。迁移器、链接器、索引器和维护流程都不得修改其正文与资源；`records/` 保存对它做过什么、为什么这么判断。
