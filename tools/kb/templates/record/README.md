# 记录模板

记录分两档，分别从对应子目录复制：

- `initial/`：初步分析。用于快速分流，不写可复用结论或修改建议，不能提炼。
- `deep/`：深度分析。用于支撑修改、发布、兼容性/许可判断和知识提炼。

把整个子目录复制到 `records/<stable-id>/`，再修改 `record.json` 的
`id`、`package_id`、`display_name` 等字段。不要把模板目录本身放进
`records/`，记录扫描器会把那里的每个目录当成真实记录。

完整契约见 [`records/STANDARD.md`](../../../../records/STANDARD.md)。
