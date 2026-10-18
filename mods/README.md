# mods — 代码样本

`mods/` 在 Atlas 中只保存本地第三方代码样本；原创生产代码在
[`rimworld-mod-forge`](https://github.com/Makeshiftname/rimworld-mod-forge)。
本地目录按授权与可发布边界分为：

- [`owned/`](owned/)：外部原创代码的登记占位；本地目录不再存放生产代码。
- [`collected/`](collected/)：第三方 mod，仅作学习与本地审计，默认不改动本体。

记录对象的稳定身份写在 [`registry.json`](registry.json)；分析记录在
[`records/`](../records/README.md)，提炼知识在
[`docs/knowledge/`](../docs/knowledge/README.md)。

## 稳定 ID

目录名使用短小写 ASCII `<stable-id>`，不再用 `NN-功能-名称` 排序。
`packageId` 是独立字段和 alias，不要求与 ID 相同；占位 packageId、中文名和
无 packageId 对象必须人工命名。编号与类型已移到自动生成的
[`docs/knowledge/indexes/mods.md`](../docs/knowledge/indexes/mods.md)，因此删减、
重排或补档不会改变引用。

新的第三方样本放进 `collected/`，并在 registry 的 `code` / `record` 中登记。
新的原创或补丁 mod 放进 forge，在 registry 中使用：

```json
"code": {
  "kind": "external",
  "repo": "https://github.com/Makeshiftname/rimworld-mod-forge",
  "path": "mods/owned/<stable-id>",
  "commit": "<固定 SHA>"
}
```

已有旧目录先由 [`tools/kb/migrate_mods.py`](../tools/kb/migrate_mods.py)
生成 plan 和 manifest，确认后才用 `--apply` 一次性迁移；apply 会同步重写
第一方引用。

## 第三方边界

`collected/**` 是只读供应内容。迁移器、链接器、索引器和维护流程都不得修改其正文与资源；`records/` 保存对它做过什么、为什么这么判断。
