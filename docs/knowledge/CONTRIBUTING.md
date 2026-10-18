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

1. **生成/手写分离**：`indexes/mods.md` 的自动区间由 `scan_mods.py` 重写；
   `MANUAL` 区间人工维护，脚本永不覆盖。
2. **知识分层**：单 mod 事实和未审核推断留在 `records/`；只有跨 mod、已复核的结论才进入 `guides/reference/mechanics`。
3. **稳定 ID**：目录、记录和知识页引用使用 `mods/registry.json` 登记的稳定 ID；编号只用于生成旧索引的显示与排序。
4. **链接相对所在文件解析**：迁移后优先用注册表 ID 或脚本生成的相对路径，不手写旧编号。

## 更新场景

### A. 新增代码样本

1. 放进 `mods/owned/<stable-id>/` 或 `mods/collected/<stable-id>/`。
2. 在 `mods/registry.json` 登记 packageId、类别、作者、授权和别名。
3. 运行 `python tools/kb/scan_mods.py`。
4. 运行 `python tools/kb/scan_records.py --check` 与 `python tools/kb/check_all.py`。

### B. 新增或修改分析记录

1. 先读 [`records/STANDARD.md`](../../records/STANDARD.md)。
2. 在 `records/<stable-id>/` 更新 `README.md` 与 `record.json`。
3. 运行 `python tools/kb/scan_records.py`。
4. 若产生已审核的跨 mod 结论，按 `STANDARD.md` 的提炼规则写入知识页并登记
   `record.json.distilled_to`。
5. 运行 `python tools/kb/check_all.py`。

### C. 修改知识页

1. 确认结论适用于跨 mod 场景，并保留来源 ID 或记录链接。
2. 只改对应层：实操 → `guides/`；参考手册 → `reference/`；机制手册 → `mechanics/`；外部来源 → `sources/`。
3. 运行 `python tools/kb/check_all.py`。

### D. 迁移旧 `收集/`、`自建/` 到 `mods/`

1. 运行 `python tools/kb/migrate_mods.py` 查看 dry-run。
2. 确认目标路径无冲突后运行 `python tools/kb/migrate_mods.py --apply`。
3. 运行 `python tools/kb/scan_mods.py` 和 `python tools/kb/check_all.py`。

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
