# RimJobWorld（RJW）— 分析记录

| | |
|---|---|
| 本记录目录 | `收录/RJW_核心_本体/`（收录目录名直接用源目录名——它是**用户自命名的中文目录**，非工坊 ID） |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\RJW_核心_本体\` |
| mod 名 | RimJobWorld |
| packageId | **`rim.job.world`** |
| 作者 | Ed86（`LICENSE` 版权行为 **semigimp 2017**，见「授权」） |
| 版本 | **6.1.2**（`<modVersion>`） |
| 许可 | MIT，`Copyright (c) 2017 semigimp` |
| 支持版本 | 1.1 / 1.2 / 1.3 / 1.4 / 1.5 / 1.6（6 个版本目录，各含完整副本） |
| 源码 | https://gitgud.io/Ed86/rjw（自建 GitLab） |
| 语言 | **11 个语种**（简中 223 文件 / 繁中 234 文件最全） |
| 分析日期 | 2026-10-17 |

> **本 mod 是成人向（18+）内容框架**，仓库与工坊页均明示。
> 本记录只做**技术分析**（结构、规模、依赖、跨版本工程），不评价内容取向。

**它在你库里的位置**：**收录记录里规模最大、依赖扇出最广的一个**——
**12,477 文件 / 66.9 MB**，本库实测 **74 个 mod 依赖它或排在它之后**。
此前最大是 Adaptive Storage Framework（6.47 MB / 30+ 依赖方），本 mod 约为其 **10 倍体积、2.5 倍依赖面**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **12,477 文件 / 70,156,865 字节（66.9 MB）** |
| 结构 | 顶层 `1.1/`–`1.6/` + `About/` + **`ci/`（GitLab CI）** + **`Deploy/`（部署脚本）** + **完整 git 仓库文件**（`.gitignore` `.gitattributes` `.gitlab-ci.yml` `CONTRIBUTING.md` `RELEASING.md` `changelog.txt` `todo or not todo.txt` `known_bugs.txt`） |
| `LoadFolders.xml` | **没有** ✅ 用 RimWorld 原生顶层数字版本目录 |
| 主 DLL（1.6） | `RJW.dll` **775,680 字节 / 920 个类型**（567 个非编译器生成，全部在 `rjw` 命名空间） |
| Def 规模（1.6） | 223 个 XML / **867 个顶层 Def / 49 种类型，其中 17 种是自定义 `rjw.*`** |
| 自定义 Def 类（代码里） | **17 个**，全部继承自某个 `Verse.Def` 派生类 |
| 语言 | 11 语种；**English 只有 10 个文件**（英文即源语言，label 直接写在 `Defs/` 里） |
| `modDependencies` | `brrainz.harmony` ✅ 已装 |
| `modDependenciesByVersion` | **只覆盖 v1.1–v1.4**，这四版额外要求 `UnlimitedHugs.HugsLib` |
| `loadAfter` | `UnlimitedHugs.HugsLib`、`brrainz.harmony` |
| `incompatibleWith` | **7 个 mod**（均附 HTML 注释说明原因） |
| 是否自带 `0Harmony.dll` | **否** ✅ |
| 版本目录累积 | 1.1(1632 文件/10.7 MB) → 1.6(2721 文件/13.2 MB)，**六份全量副本共约 69.6 MB** |

### 1.6 单版本目录构成

| 目录 | 文件数 | 字节 | 说明 |
|---|---|---|---|
| `Textures/` | 215 | 6,015,243 | 最大单项 |
| `Languages/` | 1,886 | 3,317,169 | 11 语种 |
| **`Source/`** | **364** | **1,674,943** | **完整 C# 源码**（27 个子目录） |
| `Assemblies/` | 4 | 1,061,636 | `RJW.dll` + PDB + `0MultiplayerAPI.dll` + `0PrepatcherAPI.dll` |
| `Sounds/` | 2 | 571,082 | |
| `Defs/` | 228 | 544,214 | 33 个语义子目录 |
| `Patches/` | 21 | 32,111 | |
| `.vscode/` | 1 | 150 | **IDE 配置也打包了** |

---

## 它是什么

作者自述（README / About.xml 一致）：*"An adult oriented modding framework"*——
**不是单一玩法 mod，而是一套"给别的 mod 用的成人向玩法框架"**。

### 一、867 个 Def 的类型分布（1.6，实测 223 文件全部解析成功、0 失败）

| 类型 | 数量 | 类型 | 数量 |
|---|---|---|---|
| `RecipeDef` | **121** | `BodyPartDef` | 6 |
| `ThoughtDef` | **96** | `StatDef` | 6 |
| `RulePackDef` | **90** | `ApparelLayerDef` | 6 |
| `InteractionDef` | **87** | `TraitDef` | 4 |
| `rjw.HediffDef_SexPart` | **79** | `PawnTableDef` | 4 |
| `ThingDef` | **78** | `BodyPartGroupDef` | 3 |
| `rjw.RacePartDef` | **62** | 其余 15 种 | 各 1–2 |
| `HediffDef` | 46 | | |
| `JobDef` | 26 | | |
| `rjw.RaceGroupDef` | 23 | | |
| `RecordDef` | 20 | | |
| `PawnRelationDef` | 16 | | |
| `ThinkTreeDef` | 12 | | |
| `BackstoryDef` / `PawnColumnDef` / `rjw.RaceTagDef` | 各 9 | | |
| `rjw.SexFluidDef` | 7 | | |

**规模上的两条主线**：一条是 **87 个 `InteractionDef` + 121 个 `RecipeDef` + 96 个 `ThoughtDef`**
（互动 / 制作 / 心情，是它玩法密度的来源）；另一条是
**79 个 `rjw.HediffDef_SexPart` + 62 个 `rjw.RacePartDef` + 23 个 `rjw.RaceGroupDef`**
（身体部位 / 种族适配 / 种族组，是"给第三方种族 mod 接入"的那层）。

### 二、17 个自定义 `rjw.*` Def 类型（逐个核对过基类）

| 类型 | 基类 | XML 里出现次数 |
|---|---|---|
| `rjw.RacePartDef` | `Verse.Def` | 62 |
| `rjw.RaceGroupDef` | `Verse.Def` | 23 |
| `rjw.RaceTagDef` | `Verse.Def` | 9 |
| `rjw.SexFluidDef` | `Verse.Def` | 7 |
| `rjw.PartSizeConfigDef` | `Verse.Def` | 6 |
| `rjw.MiscTranslationDef` | `Verse.Def` | 6 |
| `rjw.StringListDef` | `Verse.Def` | 4 |
| `rjw.AgeConfigDef` | `Verse.Def` | 1 |
| `rjw.BraSizeConfigDef` | `Verse.Def` | 1 |
| `rjw.config` | `Verse.Def` | 1 |
| `rjw.HediffDef_SexPart` | **`Verse.HediffDef`** | 79 |
| `rjw.SexualMentalStateDef` | **`Verse.MentalStateDef`** | 2 |
| `rjw.SexualMentalBreakDef` | **`Verse.MentalBreakDef`** | 2 |
| `rjw.bondage_gear_def` | **`Verse.ThingDef`** | 2 |
| `rjw.force_off_gear_def` | **`Verse.RecipeDef`** | 1 |
| `rjw.HediffDef_InsectEgg` | **`rjw.HediffDef_EnemyImplants`**（RJW 自己的中间基类） | 2 |
| `rjw.HediffDef_MechImplants` | **`rjw.HediffDef_EnemyImplants`** | 2 |

`RacePartDef` / `RaceGroupDef` / `RaceTagDef` 这三个是**核心接口**——
它们让第三方种族 mod 声明"我这个种族支持哪些身体部位/分组/标签"，
RJW 据此做适配。这是它作为"框架"的主要抓手。

> 命名不统一值得一提：多数是 PascalCase，但混进了两个 **snake_case**
> （`bondage_gear_def`、`force_off_gear_def`）——看起来是后期补的、没跟上命名规范。

### 三、21 个 Patches：按需补丁与兼容层

命名本身就说明了分类（前缀 `0` 用于强制提前加载）：

| 类别 | 文件 |
|---|---|
| DLC 兼容 | `0Biotech_Babyfood.xml`、`0Royalty_Hediffs.xml` |
| 框架兼容 | `CEbulk_patch.xml`、`VanillaPsycastsExpanded.xml`、`FacialAnimation_compatibility.xml`、`CnP_compatibility.xml`、`ModdedTraits_compatibility.xml` |
| 身体部位注入 | `BodyParts_Animals.xml`、`BodyParts_Humanoid.xml`、**`BodyParts_Mechanoid.xml.b`** |
| AI 行为 | `Duty_AiRapeEnemy.xml`、`Duty_AIRapePrisoner.xml`、`MentalStateCritical_AiRandomRape.xml` |
| 其它 | `Animetree_Meditation.xml`、`Recipes_Animals.xml`、`Recipes_PegArm_Human.xml`、`TalkTopics_Sex.xml`、`Thought_Masochist.xml`、`Thought_Necro.xml`、`Thought_Nymph.xml`、`PawnRelations_Humanlike.xml` |

> **`BodyParts_Mechanoid.xml.b` 的 `.b` 后缀是有意为之**：
> RimWorld 只加载 `.xml`，改扩展名就是"保留但不加载"的标准手法
> （对照：跟本记录同名收录的 `GLitterTech` 等 mod 也常用）。这是一条值得学的发布技巧。

### 四、Source/ 里除了源码还有什么

`1.6/Source/` 27 个子目录（`Modules` 123 文件最大，`Common` 53、`Harmony` 26、
`JobDrivers` 25、`RJWTab` 18、`ThinkTreeNodes` 18、`Hediffs` 18…），
外加几个有意思的文件：

| 文件 | 字节 | 说明 |
|---|---|---|
| **`partsgenerator.xlsx`** | 18,894 | **用 Excel 生成 62 个 `RacePartDef`** |
| **`spawn requestgenerator.xlsx`** | 14,056 | 同上，生成互动/生成请求类 Def |
| `containerized-build.sh` | 403 | 容器化构建 |
| `prepare-release.sh` | 794 | 发布脚本 |
| `packages.lock.json` | 2,214 | .NET 包锁定 |
| **`0trash/modpackages/`** | 2 文件 | 见下 |

> **两个 `.xlsx` 生成器很值得注意**：这是"用表格批量产出上百个结构化 Def"的实际做法，
> 62 个 `RacePartDef` + 87 个 `InteractionDef` 这种量级手写不现实。

### 五、`0trash`：两个被继承的老框架

`1.6/Source/0trash/modpackages/` 下**只剩 2 个文件**：

```
Psychology.2018-11-18/Assemblies/Psychology.dll   (189,440 B)
SYR.Individuality.1.1.7/1.1/Assemblies/SyrTraits.dll (53,248 B)
```

而 **1.6 的 `RJW.dll` 确实硬引用这两个程序集**：

```
引用程序集: 0Harmony 2.4.2.0, Assembly-CSharp 1.6.9438.37837,
            0MultiplayerAPI 0.6.0.0, 0PrepatcherAPI 1.2.0.0,
            SyrTraits 1.0.0.0, Psychology 18.11.18.0, + UnityEngine 三件套
```

RJW 的血统来自 **RimWorldChildren（作者 semigimp）**，而那个 mod 建在
SYR.Individuality 与 Psychology 之上——`LICENSE` 里是 semigimp 的版权行，
`0trash` 里留着这两个前身框架的 DLL，**线索完全吻合**。

> ⚠️ **但这两个 DLL 不在 `Assemblies/` 里**，所以游戏不会加载它们。
> 我实测 `GetTypes()` **完整成功（920 个类型，零加载失败）**，
> 说明**没有任何类型的签名（基类/字段）依赖它们**——
> 引用只存在于方法体里（多半是有保护条件的可选集成）。
> 是否会在某些代码路径上炸，**未实机验证**。

### 六、跨版本：一个值得单独记的依赖断点

`About.xml` 同时写了两种依赖声明：

- `<modDependencies>`：只有 `brrainz.harmony`（**适用于 1.5 / 1.6**）
- `<modDependenciesByVersion>`：**只覆盖 `<v1.1>`–`<v1.4>`**，这四版额外要求 `UnlimitedHugs.HugsLib`

README 的 Requirements 一节也印证：*"Hugslib (**for RimWorld 1.0 - 1.4**)"*。

即：**HugsLib 依赖在 1.5 处被切断了**。
结合上一轮收录 `818773962` 的结论（HugsLib 本体支持 1.0–1.6）——
**是 RJW 先不再需要 HugsLib，不是 HugsLib 停了**。

六个版本的 `RJW.dll` 逐版不同且单调增长：

| 版本 | 字节 |
|---|---|
| 1.1 | 540,160 |
| 1.2 | 575,488 |
| 1.3 | 632,320 |
| 1.4 | 700,416 |
| 1.5 | 722,944 |
| 1.6 | 775,680 |

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 | `Get-ChildItem -Recurse` + `ReadAllBytes().Length`，分目录与分版本统计 |
| 是否有 LoadFolders | `Get-ChildItem -Recurse -Filter LoadFolders.xml`（0 命中） |
| Def 全量 | 遍历 1.6 的 223 个 XML 逐个 `[xml]` 解析，按根元素 `LocalName` 分组计数，**并统计解析失败数** |
| 自定义 Def 类型 | 反射 `RJW.dll` 取全部 567 个非编译器生成类型的 `BaseType.FullName` |
| XML↔代码对应 | 把 XML 里出现的 17 个 `rjw.*` 根元素名**逐个回查程序集类型**，取其基类 |
| 依赖扇出 | `[xml]` 解析全库 `About/About.xml`，取直接子元素 `<packageId>`，检索正文含 `rim.job.world` 的节点 |
| 不兼容项安装状态 | 同上扫描，查 7 个 `incompatibleWith` 的 packageId |
| 跨版本 | 逐版本 `Get-FileHash` + `GetReferencedAssemblies()` |
| 授权 | 读 `LICENSE`（21 行） |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| Def 批扫 | `ThingDef` 必须出现在类型统计里 | ✅ 78 个 |
| Def 批扫的解析能力 | 必须报出 0 失败 | ✅ **223/223 成功，0 失败** |
| `GetTypes()` | 必须存在 `rjw.RacePartDef` | ✅ |
| XML↔类型对照 | 17 个根元素必须逐个命中 | ✅ **17/17 全部命中** |
| 依赖扫描 | `brrainz.harmony` 必须命中 | ✅ |
| `GetTypes()` 完整性 | 不预载 `Psychology`/`SyrTraits` 时仍须成功 | ✅ 920/920 |

### ③ 自查纠错（本轮我的工具错了 1 次）

**自定义 Def 类数从"10 个"改成"17 个"——是我的过滤器写窄了。**
我用 `BaseType.FullName -match 'Verse\.Def$|Verse\.Def`1$'` 找自定义 Def，
只匹配**直接**派生自 `Verse.Def` / `Verse.Def<T>` 的，得到 10 个。
而 XML 里实际有 **17 个** `rjw.*` 根元素——差的 7 个派生自**中间** Def 子类
（`Verse.HediffDef`、`Verse.MentalStateDef`、`Verse.MentalBreakDef`、`Verse.ThingDef`、
`Verse.RecipeDef`，以及 RJW 自己的 `rjw.HediffDef_EnemyImplants`）。
逐个回查后确认 **17/17 全部命中**。
→ **按"基类全名匹配某个类型"筛派生关系时，必须覆盖完整继承链**，不能只看直接基类。

（另：读取 `.vscode` 配置时用了 `ReadAllText("$r/1.6/.vscode/*")`，
被 .NET 当成非法路径字符抛异常——改用 `Get-ChildItem` 逐个读即可。）

### ④ 未核实

- **`Psychology` / `SyrTraits` 的可选集成在未装这两个 mod 时是否安全**：
  已证"没有任何类型签名依赖它们"（`GetTypes()` 在不预载它们时完整成功），
  但**方法体里的调用路径是否都有保护条件，未实机验证**。
- **`RJW.dll` 的 920 个类型里 Harmony 补丁的具体目标**：本次未逐一列出
  （`Source/Harmony/` 有 26 个文件可作为下次的入口）。
- **`modulesgenerator.xlsx` 之外的 121 个 `RecipeDef` / 87 个 `InteractionDef` 生成方式**：
  观察到有 `.xlsx` 生成器，但未验证它覆盖哪些 Def。
- **74 个依赖方的清单只列了前 40 个**（全量可复现）。
- **1.1–1.4 的 `Source/` 与 1.6 的差异**未逐一比对（各版本 3632–2721 文件，量太大）。

---

## 上下游与冲突面

### 依赖扇出：**74 个 mod**（收录记录之最）

全库扫描命中 **136 处**引用，涉及 **74 个不同 mod**：

| 声明方式 | 次数 |
|---|---|
| `loadAfter` | 69 |
| `modDependencies` | 61 |
| `packageId`（自身） | 5 |
| `incompatibleWith` | 1 |

依赖方里能看到完整的 RJW 生态分层（同作者的 `Ed86.rjwinsects`、
`Euclidean.FantasyRaces`、一整族 `archersaiter.rjw.*` / `c0ffee.rjw.*` / `ElToro.rjw.*` /
`moth.rjw.*` / `lw.rjw.*`），也有第三方依赖
（`LustLicentiaSerums.RJWLabs`、`Nekonomicon.Latex`、`Abscon.privacy.please`…）。

### `incompatibleWith`：7 项，**本库一个都没装**

作者给每一项都写了原因注释，这在 mod 里不常见：

| packageId | 作者写的原因（原文注释） |
|---|---|
| `gregorycurrie.AnimalGenetics` | Breaks CompHatcher.Hatch preventing eggs hatching |
| `Dalrae.GaramRaceAddon` | Hijacks pawn generator fucking up pawn genders and who knows what else |
| `IGNI.LostForest` | Intentionally breaks rjw jobs, hijacks storyteller to call raids… |
| `Sierra.RT.MedievalTalents` | Breaks pawn generator/pregnancies, causes pregnancies to instafail |
| `com.yayo.raceQuestPawn` | Breaks pawn generator/pregnancies, wrong children outcome |
| `mlie.realfactionguest` | Same issue as above; different packageID, same mod |
| `Xenofell.HermaphroditeGene` | **Transpiles same function(s) as RJW** |

**实测结果：7 个全部未安装** → 本库当前**没有触发任何一条声明的不兼容**。
最后一条特别值得注意：**Harmony Transpiler 目标撞车**是这类框架的典型冲突模式。

### 自带重复副本

- **自带 `0MultiplayerAPI.dll` v0.6.0.0（23,552 B）** ——
  即上一轮收录 `3498575851` 时统计的**全库 81 份 Multiplayer 桩**里的最新版本之一
  （SHA `863766DF5FD2`，与 ASF 的 0.5 版不同代）。
- **自带 `0PrepatcherAPI.dll` v1.2.0.0（1.5/1.6 才有）** —— Prepatcher（VS 合并工具）兼容。
- 不自带 `0Harmony.dll` ✅

### 作者自己承认的两个部署坑

README 与 `About.xml` 都点了出来：

1. **更新必须手动清干净旧版本文件** ——
   *"if updating, delete all files from previous RJW versions"*。
   因为六个版本目录各自是全量副本，RimWorld 只按当前版本加载，
   残留的旧版本 DLL 不会自动清理。本包实测 **69.6 MB 里 99% 是六份副本**。
2. **RimSort 等排序工具不认 RJW 的加载顺序要求** ——
   *"Tools like RimSort may not respect that RimJobWorld and its submods should be
   loaded after everything else. You have to manually add them to the bottom of your Load Order."*
   期望顺序：Core → HugsLib → 其它 mod → **RJW → RJW 的附属 mod** → 性能 mod。

### 作者自曝的已知缺陷（`known_bugs.txt`，共 3 条）

三条都写得直接（且带粗口），分别是：跨性别转换时的 Thought 链偶尔丢失；
未治疗的性病会导致叫床 job 被取消并刷屏；
"Genital helper"用 `has_<x>` 方法做**运行时正则搜索**，且不处理后加的动物器官。

---

## 可复用结论

1. **多版本目录的代价是"乘以版本数"，不是"取最大那个"。**
   本 mod 六份全量副本共 **69.6 MB**，而 1.6 单份只有 13.2 MB。
   跨版本支持做得好不好，先算这个乘数——**这是评估一个 mod 能否进库的成本项**。

2. **`modDependenciesByVersion` 是做"依赖随版本增删"的正确工具。**
   本 mod 在 `<v1.1>`–`<v1.4>` 四段里额外要求 HugsLib，`<v1.5>`/`<v1.6>` 不再要求。
   这一点从 `<modDependencies>`（全版本）+ `<modDependenciesByVersion>`（按版本覆盖）两段并存的写法表达，
   README 也同步说明。**依赖关系的演进不该靠发版说明写在别处。**

3. **`incompatibleWith` 值得逐条写原因注释。**
   本 mod 7 条不兼容全部带 HTML 注释，其中 *"Transpiles same function(s) as RJW"*
   一句就点明了 Harmony 补丁撞车这一具体机制——
   比只列 packageId 有用得多，也帮别人自己判断。

4. **"继承来的旧框架"会留下可追溯的痕迹。**
   `LICENSE` 写的是 semigimp 2017（本仓库无 LICENSE 或与作者不符），
   `0trash/modpackages/` 里躺着前身框架 `Psychology.dll` 与 `SyrTraits.dll`，
   而 `RJW.dll` 确实硬引用这两个程序集——**三条线索互相印证出了血统**。
   但遗留 DLL **不在 `Assemblies/`**，游戏不会加载；
   且 `GetTypes()` 在不预载它们时完整成功，说明引用只在方法体里。

5. **表格生成器是批量产出结构化 Def 的实用手段。**
   `partsgenerator.xlsx`（18.9 KB）+ `spawn requestgenerator.xlsx`（14 KB）
   放在 `Source/` 里——62 个 `RacePartDef` / 87 个 `InteractionDef` 这个量级，
   手写不现实也难维护。**把生成器跟产物一起发布**，让接手的人能改表格而不是改 XML。

6. **改扩展名是"保留但不加载"的标准手法。**
   `BodyParts_Mechanoid.xml.b` —— RimWorld 只扫 `.xml`，
   所以把文件留着、扩展名改掉，就等于保留历史方案而不生效。
   比删掉好（可回退），比留着 `.xml` 好（不误加载）。

7. **把整个 git 仓库 + CI 配置一起发布，是"可追溯"的极致做法。**
   本 mod 打包了 `.gitignore` `.gitattributes` `.gitlab-ci.yml` `ci/check_merge_request.sh`、
   `Deploy/Deploy.{ps1,sh,bat}`、`CONTRIBUTING.md`（含"TABS not SPACES"这类约定）、
   `RELEASING.md`、`changelog.txt`（**175 KB**）、`todo or not todo.txt`、`known_bugs.txt`。
   对使用者来说是噪声，对愿意 fork 的人是完整上下文。
   代价是体积与信息暴露（仓库地址、CI、内部脚本）。

8. **依赖扇出是这个库衡量"谁在给生态托底"的最好指标。**
   本轮实测：**RJW 74 → ASF 30+ → HugsLib 27 → XML Extensions 17 → Adaptive 系 3**。
   这条序列比"文件数/体积"更能反映一个 mod 在生态里的位置——
   因为它回答的是"装它之后，会连带装起多少东西"。

9. **判断"自带某公共库副本"时，要看主 DLL 实际绑定的版本，不是文件名。**
   本 mod 自带 `0MultiplayerAPI.dll` v0.6.0.0，而 ASF 自带 v0.5.0.0——
   同一份 Multiplayer 桩在本库里存在多个版本，且已安装的 mod 绑定不同版本。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **磁盘占用** | 六份全量版本副本共 69.6 MB，而实际只用得上 13.2 MB。**若确认只用 1.6，可清理 1.1–1.5 省约 56 MB**。这属于改用户游戏目录，**必须用户明确授权** |
| 高 | **`Psychology` / `SyrTraits` 的可选集成** | 主 DLL 硬引用这两个程序集但未随包提供；已证类型签名不依赖，仍建议实机验证相关代码路径 |
| 中 | `known_bugs.txt` 提到的 `has_<x>` 运行时正则 | 若要用到身体部位相关功能，这是明确的性能隐患 |
| 中 | 排序工具不认加载顺序 | README 明确要求手动把 RJW 及其附属排到最后。若用 RimSort 需人工干预 |
| 低 | snake_case 混入命名 | `bondage_gear_def`、`force_off_gear_def` 与其余 PascalCase 不一致 |
| 低 | 精简发布内容 | 若不需要贡献，`ci/` `Deploy/` `.vscode/` `CONTRIBUTING.md` 等可从工坊包里排除 |

---

*2026-10-17 收录。③ 档（12,477 文件 / 867 Def）＋ 依赖扇出分析。
223 个 Def XML 全部解析成功（0 失败）；17 个自定义 Def 类型的基类逐个核对；
74 个依赖方与 7 个不兼容项安装状态全部实测。
本轮工具自查纠错 1 次（派生关系过滤器只看直接基类，把 17 个自定义 Def 少报成 10 个），已留档。*
