# Handoff — RimWorld mod 收录与分析记录

> 接手的 agent：**先读 `收录/README.md`**，那是本系统的标准本体（术语 / 命名规则 /
> 四档深度 / 模板必答内容 / 阳性对照纪律 / 索引表）。本文只讲"现在到哪了、接下来做什么"，
> 不重复标准里的内容。

**生成时间**：2026-10-17 08:57（Asia/Shanghai）
**分支**：`main`，工作区有未提交内容（见 §4）

---

## 1. 用户是谁、要什么

用户在 `F:\Git Repository\rimworld-RimModNotes` 维护一个 RimWorld mod 学习仓库。
本机 `F:\Games\GBL\rimworld\Mods` 下有 **1021 个 mod**，他会挑其中自己喜欢的、
觉得有意义的，逐个点名要求"分析并记录"。

**用户的核心工作方式（重要，容易踩）**：

> 他**现在不做任何修改**。先收录分析，**改是后面的事，而且由他明确触发**。

本轮访谈里我反复推销"要不要一次性把六弹模板改掉 / 清掉 85 个重复 Harmony"，
**全部被推迟**。他明确纠正：*"我暂时不想更改…后续需要时再针对性修改"*。
**不要再主动提议批量改动，也不要替他动 `F:\Games\GBL\rimworld\Mods` 里的任何文件。**

同理，`docs/knowledge/` 的提炼（把记录里的通用结论沉淀成主题笔记）
**由用户口头触发**，不设固定批次、不自动做。

---

## 2. 已经建好的东西

### `收录/` —— 分析记录区（原名 `修改/`，2026-10-17 改名）

| 路径 | 内容 |
|---|---|
| `收录/README.md` | **标准本体**。术语表、目录命名规则、四档核验深度、记录模板必答内容、阳性对照纪律、提炼约定、12 条索引表 |
| `收录/<mod目录>/README.md` | 12 份分析记录 |
| `tools/kb/check_records.py` | 收录区专属门禁（见 §3） |

**记录的四个必答锚点**（章节标题固定、不加编号）：
`## 身份卡` / `## 它是什么` / `## 怎么验的` / `## 可复用结论`；
`## 修改建议` 可选，没有就整节删掉。

### 12 份现有记录

| 目录 | mod | 类型 | 有待办 |
|---|---|---|---|
| `美南烛/` | yukiyuki.ASEBI | 种族（模板 #1） | ✅ |
| `2 雪绒兽/` | yukiyuki.BORUM | 种族（模板 #2） | ✅ |
| `3 素心和葬歌/` | yukiyuki.SANKAandSOSIN | 种族 + 远程攻击 + MVCF | ✅ |
| `4 八重律/` | yukiyuki.YAEMU | 种族（模板 #4） | ✅ |
| `5 阿比斯/` | yukiyuki.ABYSS | 种族 + 任务链 + VEF | ✅ |
| `6弗莱西雅/` | yukiyuki.FLESHIA | 种族 + C# 技能 + LoadFolders | ✅ |
| `1~11岁美狐贴图修正/` | Fix.Miho.VisualPatch | 贴图修正（fork 架构） | ✅ |
| `717575199-MiscTraining/` | Haplo.Miscellaneous.Training | 跨版本维护范本 | — |
| `725130005-PMusic/` | Peppsen.PMusic | 纯内容（音乐） | — |
| `725576127-GlitterTechClassic/` | GT.Sam.GlitterTech | overhaul（195 Def） | — |
| `2009463077-Harmony/` | brrainz.harmony | 基础设施（MIT） | ✅ 全库级 |
| `3652938473-FasterGameLoading/` | Taranchuk.FasterGameLoading | 性能层 | — |

每份记录里的**具体结论不要重读**，按需打开对应文件即可。

---

## 3. 门禁

```bash
python tools/kb/check_records.py        # 收录区专属，exit 0 = 通过
python tools/kb/check_repo_hygiene.py   # 仓库既有卫生门槛
python tools/kb/check_links.py          # 链接检查
```

三个当前都是 exit 0、零警告。

**`check_records.py` 查四项**：四锚点齐全 / 收录目录名对得上 Mods 源目录（支持
`工坊ID-可读名` 与 `DIR_ALIASES` 显式对照）/ 记录里出现的 Mods 绝对路径真实存在 /
索引表覆盖全部记录。

⚠️ **`check_links.py` 不覆盖 `收录/`**——它只扫 `AGENTS.md` + `docs/knowledge/*.md` +
`mod-index.md`。报"门禁通过"时别把它算进去。

⚠️ 脚本已做过**反向测试**（破坏一个锚点 → 确认 exit 1 并精确报错 → 恢复 → exit 0，
md5 与操作前一致）。如果以后有人改了它，记得重做这个测试。

---

## 4. 未提交的工作区状态

```
?? tools/kb/check_records.py
?? 收录/
```

用户**没有要求提交**。要不要 commit 需要先问。

---

## 5. 接下来最可能做的事

1. **继续收录新 mod** —— 用户会点名 `F:\Games\GBL\rimworld\Mods\<目录>`，按
   `收录/README.md` 的四档深度分析，写进 `收录/<mod目录>/README.md`，
   跑 `check_records.py`，最后更新 `收录/README.md` §7 索引表。
2. **用户说"提炼"时** —— 把手上攒的记录里的跨 mod 通用结论批量沉淀进
   `docs/knowledge/*.md`，并清理两边打架的说法。
   **已知待提炼项**（都在 `收录/README.md` §6）：
   - `docs/knowledge/cross-version-structure.md:34` 写"弃用 LoadFolders"，
     与 Harmony 那份记录的结论冲突（后者认为取决于**是否在版本边界收敛**）
   - `docs/knowledge/README.md` 与 `AGENTS.md` 的 mod 计数（"83 个 / 收集 82"）已过期
3. **用户说"改 XX"时** —— 才动对应 mod 的 Def。改动前先看该记录里的「修改建议」。

---

## 6. 环境事实（会反复用到，别重新踩）

| 事实 | 影响 |
|---|---|
| 本机游戏版本 | RimWorld **1.6.9655.19392**，含 Core + Ideology + Anomaly + Biotech + Royalty + **Odyssey** |
| **原版素材被剥掉** | `Data\{六个 DLC}\Textures` **全部不存在**，`Data\Core\Sounds` 为空。凡"贴图/音频是否存在"的核验**在本机做不了**，只能用"原版 Def 是否引用该路径"间接判断归属 |
| Mods 数量 | **1021 个**，且有 **2 组重复 packageId**（`fxz.Ratkin.FacialAnimation`、`stm.ShellaBackgrounds` 各占两个目录） |
| **85 个 mod 自带会被加载的 `0Harmony.dll`**（196 份） | 与官方 Harmony mod 并存，是全库最大的结构性隐患。尚未清理，用户未授权 |
| Mods 目录命名有两种风格 | 用户自命名带序号（`1 美南烛`）/ 工坊 ID（`717575199`）。收录目录名规则见标准 §2 |
| 六弹 yukiyuki 系列 | `1`–`6` 正好是同作者 `yukiyuki.*` 的全六弹 + 一个汉化包 `ChinesePack.yukiyuki.animalgirls`。它们**禁止再分发**，收录区只存结论不存 Def 原文 |

---

## 7. 方法论纪律（已写进 `收录/README.md` §5，这里只列结论）

本轮我的核验工具出过 **4 次错**，每次都差点给出方向相反的结论，全靠对照发现。
接手后请先读那段，重点是这三条：

1. **任何"扫描/正则/grep 得出的 0 命中或全缺失"结论，必须先证明同一个工具能在已知有效的样例上命中**，否则 0 不可信。
2. **报"文件是空的"之前读字节数**，不要看 KB 化的列表输出（10 字节会显示成 `0`）。
3. **自查纠错要写进记录的「怎么验的」，不要悄悄改掉结论了事** —— 留着才能防止后人重走。

---

## 8. Suggested skills

| Skill | 什么时候用 |
|---|---|
| （无） | **常规收录新 mod 不需要任何 skill**，直接按 `收录/README.md` 走四档深度即可 |
| `grill-with-docs` | 用户对收录区的规则/结构/标准提出异议时，用它拷问并把结论落回 `收录/README.md` |
| `research` | 需要查 rimworldwiki / 官方文档等外部一手资料时（用户说"研究/调研 X"） |
| `diagnosing-bugs` | 用户报告游戏报错、崩溃、mod 不生效时 |
| `code-review` | 用户要对改动做审查时 |
| `domain-modeling` | 收录区的术语体系（收录 / 记录 / 提炼 / 阳性对照…）需要增删时 |

---

## 9. 给接手 agent 的三条提醒

1. **别主动提议修改 mod。** 用户明确说过现在不改。所有改动必须等他触发。
2. **写记录前先跑 `check_records.py` 看现状**，写完再跑一次；别报告"门禁通过"却没跑收录区那一项。
3. **本仓库的历史文档有陈旧数字**（AGENTS.md 的 mod 计数、kb_common 里写死的
   `CATEGORY_DIRS = ("自建", "收集")` 不含 `收录`）。引用前先实测。

---

*本文档只做交接，不重复 `收录/README.md` 与各份记录里的内容。*
