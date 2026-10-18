# 分析一个 mod：Agent 操作流程

> 接手 Agent 先读本页，再按需要读 [`STANDARD.md`](STANDARD.md)。

> 用户可以直接说：**读 `records/AGENT_WORKFLOW.md`，按其中流程分析 `<mod>`，档位 `<initial/deep>`。**

## 1. 开工前先确认四件事

1. **目标 mod 在哪里**：游戏 `Mods` 目录下的实际目录名，或仓库内的代码样本路径。
2. **稳定 ID 是什么**：先查 [`mods/registry.json`](../mods/registry.json)，不要临时拼目录名。
3. **用哪一档**：`initial` 或 `deep`。用户没指定时默认 `initial`。
4. **这次分析的范围**：至少覆盖身份、来源、许可、版本、依赖和明显结构；不要无差别读取整个仓库。

如果缺少的信息会改变分析范围，先问用户；否则从注册表、`About.xml` 和目录结构自行确认。

## 2. 选档

| 档 | 什么时候用 | 不能做什么 |
|---|---|---|
| `initial` | 第一次接触、判断是否值得继续、快速分流 | 不写可复用结论和修改建议；不能提炼 |
| `deep` | 要打补丁、发布、做兼容性/安全/许可判断，或 mod 是基础设施/高风险对象 | 不能把未核验推断写成事实 |

用户明确要求深挖、任务本身是修改/发布、或 mod 被大量依赖时，可以直接用 `deep`，不必先写一份 `initial`。

## 3. 确认身份与注册表

先查是否已登记：

```powershell
rg -n '"package_id": "作者.packageId"' mods/registry.json
```

如果还没有登记，在 `mods/registry.json` 增加条目。只有分析记录、没有本地代码样本时：

```json
{
  "id": "example-mod",
  "origin": "collected",
  "package_id": "author.example",
  "display_name": "Example Mod",
  "aliases": [],
  "code": null,
  "record": {
    "legacy_paths": [],
    "path": "records/example-mod"
  },
  "type": "unknown"
}
```

如果仓库里有代码样本，再补：

```json
"code": {
  "legacy_paths": ["收集/01-standalone-Example"],
  "target_path": "mods/collected/example-mod"
}
```

规则：

- `id` 是小写 ASCII slug，登记后不再改名；旧名放进 `aliases`。
- `source_dir` 写游戏 `Mods` 目录下的**实际目录名**，不是显示名或旧编号。
- 第三方 mod 的 `origin` 用 `collected`；仓库主原创用 `owned`。

## 4. 建记录目录

按档位复制整个模板目录：

```text
initial -> tools/kb/templates/record/initial/
deep    -> tools/kb/templates/record/deep/
```

目标：

```text
records/<stable-id>/README.md
records/<stable-id>/record.json
```

`record.json` 至少填好：

- `schema_version: 3`
- `id` / `package_id` / `display_name`
- `origin` / `authors` / `license`
- `source_dir`
- `analysis_tier: initial | deep`
- `status: analyzed`

作者证据放 `author_evidence`，许可链和例外放 `license_notes`；不要只把说明堆进 `authors` 或 `license`。

## 5. 执行分析

### 初步分析

必须使用四节：

```text
身份卡 / 它是什么 / 初步核验 / 下一步
```

`初步核验` 必须包含：

```text
### 已核验
### 未核验
```

底线：

- 没有阳性对照时，否定性结论只能写“未核验”，不能写“缺失 / 不存在 / 0 命中”。
- 禁止 `## 可复用结论`、`## 修改建议` 和非空 `distilled_to`。
- 修改方向只能放在 `下一步` 里作为待验证问题。

### 深度分析

必须保留四锚点：

```text
身份卡 / 它是什么 / 怎么验的 / 可复用结论
```

`怎么验的` 应写：

```text
### 范围
### 方法
### 阳性对照    ← 出现 0 命中/缺失/不存在时
### 自查纠错    ← 工具犯错或被纠正时
### 未核验
```

底线：

- 方法写清路径/命令/工具/版本；运行时结论写游戏版本和运行条件。
- 多版本 mod 写版本矩阵；依赖区分 `modDependencies`、`loadAfter` 和代码/程序集引用。
- `可复用结论` 每条标 `[已确认]`、`[推断]` 或 `[未核验]`。
- 只有 `status: analyzed` 才能写 `distilled_to`；用户没有明确说“提炼”时，不要改 `docs/knowledge/`。

## 6. 只读边界

分析第三方 mod 时，**不修改**它的：

- `About/About.xml`、C#、Defs、Patches、Languages、贴图和其他资源；
- 也不要把第三方内容复制进分析记录正文，除非是必要的字段名、数值或短引用。

分析任务只写 `records/<stable-id>/` 和必要的 `mods/registry.json` 条目；除非用户明确要求，否则不改代码、`mods/collected/` 或 `收集/`。

## 7. 收尾验证

在仓库根目录运行：

```powershell
python tools/kb/scan_records.py
python tools/kb/check_all.py
```

如果要验证来源目录存在，先设置：

```powershell
$env:RIMWORLD_MODS_DIR = 'F:\Games\GBL\rimworld\Mods'
```

`check_all.py` 失败时，修记录或元数据，不要为了通过而放宽校验器。

## 8. 可直接复制的任务提示词

### 初步分析

```text
读 records/AGENT_WORKFLOW.md 和 records/STANDARD.md，按 initial 档分析 <mod 名称>。

工作目录：F:\Git Repository\rimworld-RimModNotes-worktrees\refactor
稳定 ID：<stable-id>
来源目录：<RIMWORLD_MODS_DIR 下的实际目录名，或仓库内路径>

要求：
- 使用 tools/kb/templates/record/initial/
- 写入 records/<stable-id>/README.md 和 record.json
- 必须有 身份卡 / 它是什么 / 初步核验 / 下一步
- 初步核验必须包含 ### 已核验 和 ### 未核验
- 没有阳性对照时，否定性结论只能写“未核验”
- 禁止 ## 可复用结论、## 修改建议、非空 distilled_to
- 不修改第三方 mod 本体
- 完成后运行 python tools/kb/scan_records.py 和 python tools/kb/check_all.py
```

### 深度分析

```text
读 records/AGENT_WORKFLOW.md 和 records/STANDARD.md，按 deep 档分析 <mod 名称>。

工作目录：F:\Git Repository\rimworld-RimModNotes-worktrees\refactor
稳定 ID：<stable-id>
来源目录：<RIMWORLD_MODS_DIR 下的实际目录名，或仓库内路径>

要求：
- 使用 tools/kb/templates/record/deep/
- 写入 records/<stable-id>/README.md 和 record.json
- 必须有 身份卡 / 它是什么 / 怎么验的 / 可复用结论
- 怎么验的要写 ### 范围 和 ### 未核验；条件性写 ### 阳性对照 / ### 自查纠错
- 可复用结论每条标 [已确认] / [推断] / [未核验]
- 只有 status: analyzed 才能写 distilled_to；没有明确要求提炼就不要动 docs/knowledge
- 不修改第三方 mod 本体
- 完成后运行 python tools/kb/scan_records.py 和 python tools/kb/check_all.py
```

## 9. 交接时回报什么

完成后向用户回报：

1. 档位与稳定 ID；
2. 改了哪些文件；
3. `check_all.py` 结果；
4. 仍然 `未核验` 的关键结论；
5. 是否建议升级为深度分析。

不要只回报“分析完成”。下一位 Agent 需要知道哪些结论已经确认、哪些仍然只是线索。
