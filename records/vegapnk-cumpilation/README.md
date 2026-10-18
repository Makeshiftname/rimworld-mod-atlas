# Cumpilation — 分析记录

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `Cumpilation`（README 标题 `[NSFW] [WIP] Cumpilation`） |
| packageId | `vegapnk.cumpilation` |
| 作者 | **Vegapnk**（`About.xml` 写 `Vegapnk - 1.6 Rewrite by Telanda`；CHANGELOG 每条都署 `(Commit by @Telanda-DDS)`；`CONTRIBUTING.md` 的 Contributors 段只有一人：**Telanda - Rimworld 1.6 Migration**） |
| 源目录 | `F:\Games\GBL\rimworld\Mods\RJW-体液-精液汇编（Cumpilation）` |
| 上游 | <https://github.com/vegapnk/Cumpilation>（`About.xml` 与 `Manifest.xml` 一致；托管在 GitHub，**不是** gitgud.io） |
| 授权 | 随包 `LICENCE`（**661 行 / 34,452 字节**，正文是 **GNU AGPL-3.0** 全文）。⚠️ 但 `README.md` 的徽章写 `License: GPL3` —— **两者不一致**，见「查出来的问题 · 1」 |
| modVersion | `1.2.6`（`About.xml` 与 `About/Manifest.xml` 一致） |
| 规模 | **512 文件 / 8,193,762 bytes（7.81 MB）** |
| 类型 | **功能型内容 mod**：87 个 Def + 192 个 C# 类型 + 11 个 Harmony 补丁 + 随包完整双版本源码 |
| 支持版本 | `1.5` `1.6`（`LoadFolders.xml` 两组） |
| 硬依赖 | `brrainz.harmony` + `rim.job.world`（`modDependencies`） |
| `loadBefore` | **`Vegapnk.rjw.genes`** —— 同作者的配套 mod 必须排在本 mod 之后加载 |
| `incompatibleWith` | `tory187.rjw.gatheredrjw`、`rjw.bucket` |
| `loadAfter` | `Ludeon.RimWorld`、`Ludeon.RimWorld.Royalty`、`Ludeon.RimWorld.Ideology`、`Ludeon.RimWorld.Biotech`、`brrainz.harmony`、`rim.job.world` |
| 核验深度 | **③ 档**（87 Def / 192 类型 / 双版本 / 多 DLC 条件加载）—— 收录以来工程质量最高的记录之一 |

### 体积分解（按扩展名，全 mod）

| 扩展名 | 文件 | 字节 | 占比 |
|---|---|---|---|
| `.dds` | 26 | 3,625,480 | **44.2%** |
| `.png` | 27 | 2,452,150 | 29.9%（其中 `About/Preview.png` 1,527,348 = 18.6%） |
| `.zstd` | 26 | 919,715 | 11.2% |
| `.cs` | **235** | 447,125 | 5.5%（随包双版本源码） |
| `.xml` | 182 | 363,325 | 4.4% |
| `.dll` | 2 | 236,032 | 2.9% |
| `.ogg` | 1 | 57,071 | 0.7%（`1.6/Sounds/Cumflation/CumflationOverflow.ogg`） |
| 无扩展名 | 1 | 34,452 | 0.4%（`LICENCE`） |
| `.csproj` / `.sln` | 2 / 2 | 23,382 / 1,820 | 0.3% |
| `.md` | 3 | 19,510 | 0.2%（README / CHANGELOG / CONTRIBUTING） |
| `.gitignore` | 3 | 11,416 | 0.1% |
| `.txt` | 2 | 2,284 | 0%（其中 1 个是被停用的 Patch XML） |

**`Common/` 只有贴图**（78 文件 / 5.22 MB，`Textures/` 下的 26 张 × 三格式），不共享任何 Def 或代码。

## 它是什么

把「RJW 的体液系统」做成一套可玩的内容：`About.xml` 的描述列了 9 条，Bukkake、Cumflation、Stuffing、体液作为可消费 Item/Ingredient、体液桶与自动体液桶、随摄入量递进的想法、给 Drugs 加"改体液类型/改体液量"的接口、Oscillation 机制（按使用量增减生殖器内体液量）、以及 Biotech 专属的 Slug（一种基于废包的负面体液）。

### 它是「机制聚合体」，来源在 README 里逐条署名

README 的 Content 一节把每一块的出处写清楚了，这是本 mod 最值得学的地方：

| 功能 | 原作者 / 出处 |
|---|---|
| Cumflation | LicentiaLabs |
| Cum-Stuffed | LicentiaLabs |
| Cum-Item | Ameravashi-Sexperience |
| Cum-bucket | Ameravashi-Sexperience |
| Passive Cum-Cleaning | 想法来自 `rjw-bucket`（Thomas404） |
| Progressive Eat-Thoughts | 部分来自 Ameravashi-Sexperience |
| Gathering | Tory 的 `gathered-rjw`，由 Nil 更新 |
| **Spermatuch & Samenstein** | **Semen Processor（Nalzurin），且仅在 Semen-Processor 未加载时存在** |
| Bukkake | Ed86-Cum |

README 同时**明确承认自己处于 WIP 且冲突面很大**：

> As this is **WIP**, currently there are many things that will break when you use the things taken from other mods. … Consider all mods from which parts are taken potential conflicts.

这解释了为什么只有 2 个 `incompatibleWith` 却是 8 个来源。

### Def 清单（1.6，排除 `Languages/` 与 `Patches/` 后统计）

**87 个具体 Def + 3 个抽象 Def**（1.5 是 86 + 3，差异见下）：

| 类型 | 数量 | |
|---|---|---|
| `HediffDef` | 23 | 蓝球（BlueBalls）、Drained、Wet、Cumflation、Cumstuffed、Bukkake 控制器、Leaking、Slug 系列 |
| `ThoughtDef` | 16 | 含 `CumstuffedEnjoyed`/`CumstuffedNegative`/`GotOverCumflated` 三组正负对照 |
| `ThingDef` | 14 | Cum 资源、Spermatuch/Samenstein、桶与家具、Plug、Cumflation 用药（Galactogogues/Lecithin） |
| `RecordDef` | 10 | 摄入量累计（`RecordDef` 是 Biotech 的记录机制） |
| `JobDef` | 7 | 含 `CleanSelf` / `CleanSelfWithSink` / `OverflowingCumflation` / `VomitFluid` / `Leaking` |
| `RecipeDef` | 3 | 含手术 `Deflate` 与体液资源加工 |
| `WorkGiverDef` / `SpecialThingFilterDef` | 2 / 2 | |
| `ThinkTreeDef` / `TraitDef` / `ThingCategoryDef` | 1 / 1 / 1 | |
| `SoundDef` | 1 | **仅 1.6**：`CumflationOverflow` |

**3 个自定义 Def 类型（mod 自己声明，已在 DLL 中核实存在）**

| XML 根元素 | 数量 | 基类 | 字段（反射得到） |
|---|---|---|---|
| `Cumpilation.Cumflation.StuffingDef` | 3 | `Verse.Def` | `fluid`(`SexFluidDef`) · `resultingStuffedHediff` · `amountOfFluidForFullStuffing` · `canStuffAnimals` · `thoughtThreshold` · `positiveThought` / `neutralThought` / `negativeThought` |
| `Cumpilation.Gathering.FluidGatheringDef` | 2 | `Verse.Def` | `fluidDef` · `thingDef` · `fluidRequiredForOneUnit` · `canProduceMoreThanOne` · `roundUp` · `canBeRetrievedFromFilth` · `filthNecessaryForOneUnit` · `filth` |
| `Cumpilation.Reactions.Fluid_Record_Mapping` | 5 | `Verse.Def` | `fluid` · `numConsumedRecord` · `amountConsumedRecord` |

**外加 1 个来自 RJW 的自定义类型**：`rjw.SexFluidDef` ×1。这个类型在 `RJW_核心_本体\1.6\Assemblies\RJW.dll` 中确实存在，字段为 `filth`、`consumable`、`color`、`consumableFluidRatio`、`ingestThroughAnyOrifice`、`alwaysProduceFilth`、`baseNutrition`、`baseNutritionCost`、`quenchesThirst`、`tags`、`ingestionDoers` —— **本 mod 正是通过扩展 RJW 这个类型来挂载内容的**，与描述里那句 "Fluid-based mechanics for RJW" 对得上。

三个自定义 Def 的设计意图很清楚：`StuffingDef` 把"注入什么液体 → 得到什么 Hediff → 给哪三档想法"做成数据；`FluidGatheringDef` 把"液体 ↔ 可收集物"的换算关系（以及是否向上取整、能否从污渍回收）做成数据；`Fluid_Record_Mapping` 把"液体 → 两条 RecordDef 计数"做成数据。**三张表驱动整条内容管线**，比散落在硬编码里好扩展得多。

### C# 侧（1.6 = 192 个类型）

按命名空间：`Leaking` 40、`Common` 29、`Cumflation` 29、`Bukkake` 28、`Gathering` 20、`Reactions` 17、`Fluids` 13、`Oscillation` 6，其余零散。

框架接入点：**2 个 `Mod` 类 + 2 个 `ModSettings` 类**
- `Cumpilation.Cumpilation_SettingsController : Mod`
- `Cumpilation.Leaking.LeakCum_SettingsController : Mod`
- `Cumpilation.Settings : ModSettings`
- `Cumpilation.Leaking.Settings : ModSettings`

即**两个独立设置页**。另有 `Cumpilation.HarmonyInit`（手工挂载的入口）与 `Cumpilation.ModLog`。

**Harmony 补丁：1.5 有 10 个、1.6 有 12 个属性（11 个类）**

| 补丁 | 作用 |
|---|---|
| `Cumflation.Patch_TransferFluids_Cumflate` / `_Stuff` | 注入体液时触发胀满/填塞 |
| `Bukkake.Patch_TransferFluids_ApplyBukkake` | 同上，Bukkake 分支 |
| `Reactions.Patch_TransferFluid_UpdateRecordAndGiveThoughts` | 记录摄入并给想法 |
| `Reactions.Patches.Patch_IngestMeal_UpdateRecordAndGiveThoughts` | 同上，走进食路径 |
| `Gathering.Patch_CasualSexHelper_FindNearbyBucketToMasturbate` | 找桶 |
| `Gathering.Patch_JobDriverCleaning_TrySpawnItem` | 清洁时产出 |
| `Gathering.Patch_SatisfyPersonal_FillFluidGatherers` | 需求满足时填充收集器 |
| `Oscillation.Patch_OnOrgasm_SpawnHediffs_And_ChangeSeverityOfHediffs` | 高潮时生成/调整 Hediff |
| `Fluids.Slug.Patch_OnDeath_TriggerSlugExplosions` | Slug 死亡爆开 |
| **`Patch_AllowedStuffsFor_noCumRuins`** | **仅 1.6 有** |

**最后一个补丁与 CHANGELOG 1.2.4 精确对应**：

> Replaced `Cumpilation_Samenstein` XML material cost changes with .dll patch to prevent it from being used for creating ruins when map is generated.

即"把 XML 改材料成本"换成"DLL 里改 allowedStuff"，因为前者会被遗迹生成读到。**CHANGELOG 声明的改动在二进制里被独立证实**——这是本轮最扎实的一条交叉验证。

### 跨版本与条件加载

`LoadFolders.xml` 用了我之前**没见过 `IfModNotActive`** 的写法：

```
v1.5 / v1.6:
  Common
  1.x
  [IfModActive="ludeon.rimworld.Biotech"]              1.x/Mods/Biotech
  [IfModActive="ludeon.rimworld.Ideology"]             1.x/Mods/Ideology
  [IfModActive="Dubwise.DubsBadHygiene,Dubwise.DubsBadHygiene.Lite"]  1.x/Mods/DBH
  [IfModNotActive="winderig.processor"]                1.x/Mods/Not-Semen-Processor
```

`IfModNotActive` 是 `IfModActive` 的补集，用来做**互斥加载**——本例正是"Semen Processor 存在时用对方的原料加工，不存在时才用自己的 Spermatuch/Samenstein"，与 README 的出处说明一致。

各条件子树规模（1.5 与 1.6 完全对称）：`Biotech` 9 个 XML、`Ideology` 2 个、`DBH` 1 个、`Not-Semen-Processor` 3 个。

**1.5 vs 1.6 的 Def 差异只有 1 个**：`CumflationOverflow`（`SoundDef`），配 `1.6/Sounds/Cumflation/CumflationOverflow.ogg`（57,071 B）。对应 CHANGELOG **1.2.6 (05-05-2026)**：

> Made Hardcoded deflation sound editable Via XML and chose a more appropriate sound effect. (Thanks Ryufais!)

86 个 Def 两版共享。DLL 侧：1.5 = 116,736 B / 程序集版本 `1.0.0.0`；1.6 = 119,296 B / 程序集版本 **`1.2.6.0`**（跟上了 modVersion）。两者分别绑定 `RJW 1.5.9088.5242` 与 `RJW 1.6.9607.36451`。

> 顺带一个兼容性观察：本机装的 RJW 是 `1.5.9201.31093` / `1.6.9576.22392`，而本 mod 的 1.6 构建绑定的是 **9607.36451（比本机更新）**。Unity 按简单名绑定，同一大版本内不会因此报错，但说明它是在更新的 RJW 上编译的。

## 它是什么 · 查出来的问题

### 1. 许可标注不一致：LICENCE 是 AGPL-3.0，README 徽章是 GPL3

`LICENCE` 首行是 `GNU AFFERO GENERAL PUBLIC LICENSE / Version 3, 19 November 2007`，661 行全文。而 `README.md` 的徽章是：

```
[![License: GPL3](https://img.shields.io/badge/License-GPL3-green.svg)](https://opensource.org/license/gpl-3.0)
```

**AGPL-3.0 与 GPL-3.0 不是同一份许可**（AGPL 多了第 13 条网络服务条款）。对 mod 作者来说差异不大（两者都允许再分发、都要 copyleft），但**发布时对外声称的许可与实际随包文本不一致**，属于需要澄清的合规问题。

按收录区标准：允许再分发（非禁再分发），但**必须原样记录这个不一致**。

### 2. 26 个 `.dds` 占 44.2% 体积，在只支持 1.5/1.6 的情况下基本是死重量

`Common/Textures/` 下是 **26 张贴图 × 3 种格式**（`.dds` + `.dds.zstd` + `.png` = 78 文件）：

| 格式 | 文件 | 字节 | 1.5/1.6 是否读取 |
|---|---|---|---|
| `.dds.zstd` | 26 | 919,715（11.2%） | ✅ 优先读 |
| `.png` | 26 | 924,802（11.3%） | 兜底，zstd 存在时不读 |
| **`.dds`（未压缩）** | 26 | **3,625,480（44.2%）** | **zstd 存在时不读** |

`.dds` 是三者里**最大**的：家具贴图 `autochair_with_cumtank_*` 每张 `.dds` **335,508 B**，而同样的图 `.dds.zstd` 只要 67–107 KB、`.png` 85–135 KB。未压缩 DDS 存的是原始像素，天然比压缩格式大好几倍。

**本 mod 只声明支持 1.5 / 1.6**，而 RimWorld 1.5+ 的贴图解析优先取 `.dds.zstd` —— 所以这 3.6 MB 未压缩 DDS 在其声明支持的全部版本上都不会被读取。删掉它们能把 7.81 MB 压到 4.19 MB（**−46%**），且不影响功能。

### 3. 根目录与 `1.6/Languages/` 有两套重复的 DefInjected，其中一份注释已过期

| 位置 | XML 数 |
|---|---|
| `Languages/ChineseSimplified (简体中文)/` | 38（全是 DefInjected） |
| `1.6/Languages/ChineseSimplified (简体中文)/` | 40（38 DefInjected + 2 Keyed） |
| `1.5/Languages/ChineseSimplified (简体中文)/` | 1（只有 Keyed） |

根目录那 38 个**全部**在 `1.6/Languages/` 里有一份同名副本。两棵树都会加载（根 `Languages/` 总是读，`1.x/Languages/` 经 LoadFolders 读）。

逐字节比对结果：

- **34 个完全相同**
- **3 个只有空白/缩进差异**（`Buildings_Furniture.xml`、`Thoughts_Leaking.xml`、`Thoughts_Social_LikesCumflation.xml`）
- **1 个有实质差异**：`Drug_FluidBuff.xml`（1608 B vs 1584 B）

但**逐条比对键→值映射后，38 个文件的译文全部一致**。第 4 个文件的真实差异只在 **`<!-- EN: ... -->` 注释**上：1.6 那份的英文描述已更新（"…resulting in higher milkproduction."），而**根目录那份的英文注释还停留在旧文案**（"…resulting in higher milk production for ~3 Days."）。

所以这条要如实表述为：**功能上没有影响（中文译文两边相同），属于维护冗余 + 根目录副本的英文注释陈旧**。不是"翻译打架"，我一开始的怀疑（两边值不同）被自己的逐键比对否掉了。

覆盖的 Def 类型共 11 种：HediffDef 9、ThingDef 8、ThoughtDef 8、JobDef 4、RecipeDef 2、RecordDef 2、SpecialThingFilterDef 1、ThingCategoryDef 1、TraitDef 1、WorkGiverDef 1、`rjw.SexFluidDef` 1。

### 4. 两份 Manifest 内容不一致

| 项 | `About.xml` | `About/Manifest.xml`（ModSync Ninja） |
|---|---|---|
| 版本 | 1.2.6 | 1.2.6 ✅ |
| 依赖 | `brrainz.harmony` + `rim.job.world` | **`RimJobWorld` + `HugsLib`** ← 多一个 HugsLib |
| 不兼容 | `tory187.rjw.gatheredrjw`、`rjw.bucket`（**packageId**） | `RJW-LicentiaLabs`、`RJW Bucket`、`Gathered RJW`（**显示名**）← 多一个 LicentiaLabs，且用的是显示名而非 packageId |

HugsLib 那条尤其值得注意：它**只出现在 Manifest 里，没进 `modDependencies`**，所以游戏不会因为缺 HugsLib 而警告；而 HugsLib 本机是装了的。

### 5. 一个用 `.txt` 扩展名停用的 Patch（有意为之，但值得记）

`1.6/Patches/RJW/SexFluid_Cum_Use_Consumable.txt` —— 扩展名是 `.txt`，所以 RimWorld 的补丁加载器**不会读它**。文件里是一段完整的 Patch XML（给 `rjw.SexFluidDef[defName="Cum"]` 加 `<consumable>Cumpilation_Cum</consumable>` 与 `<consumableFluidRatio>0.025</consumableFluidRatio>`，并移除 `<baseNutrition>`），注释写明：

> Discussed in Issue #5 … The base-rjw logic makes it so that all other consumption effects are ignored if a consumable is present. Currently Disabled for reasons.

目标字段 `consumable` / `consumableFluidRatio` / `baseNutrition` 都能在 `rjw.SexFluidDef` 里核实到，所以**停用的原因是逻辑冲突而非字段写错**。改扩展名就能启用——这是作者留给自己的一个开关。

### 6. 工程杂项

- **`.gitignore` 只在根和 `1.5\` 下有，`1.6\` 没有**。而且根 `.gitignore`（4,239 B，标准 VisualStudio 模板）**并不忽略 `*.dll`**；真正管住 DLL 的是 `1.5/Assemblies/.gitignore`（15 B，内容就一行 `Cumpilation.dll`）。这与 CONTRIBUTING 里的"you don't have to commit the `.dll`"对应，但 `1.6` 侧漏了。
- **`csproj` 的 HintPath 极其脆弱**：`..\..\..\..\..\..\Steam\steamapps\workshop\content\294100\2009463077\Current\Assemblies\0Harmony.dll`（往上 6 层才到 Steam 目录），以及 `..\..\..\..\Mods\rjw\1.6\Assemblies\RJW.dll`（往上 4 层到一个名为 `rjw` 的同级目录）。换任何一种目录布局都编不过。没有 `<Publicize>`（与收录区里 C0ffeeRIA 那种做法不同），`LangVersion` 是 `9` 而非 `preview`。
- **`CHANGELOG.md`（312 行）质量很高**：1.2.1 (2025-07-20) 到 1.2.6 (2026-05-05) 每条都有日期、提交者（`@Telanda-DDS`）、分类（Feature/Fix/Change）、社区致谢（`@Ryufais`、`RB`），甚至有 **Known Issues** 一节（1.2.3 里那条"拿着太多食物被报偷窃"还写了"怀疑是 Big & Small 触发而非 Cumpilation 本身，回滚两者都有人报告有效"）。这是 mod 仓库里少见的规范度。
- `CONTRIBUTING.md` 三条硬约束：友好耐心、**代码/提交/素材一律英文**、**图片必须有明确授权归属（如 CC3）**；并规定新特性进 `Dev` 分支、修复进 `Main` 分支。

## 怎么验的

### ① 核验方法（可复现）

| 目标 | 方法 |
|---|---|
| 规模 / 体积 | `Get-ChildItem -Recurse -File` + `[System.IO.File]::ReadAllBytes().Length`，按扩展名汇总 |
| 许可识别 | 直接读 `LICENCE` 首 15 行（不靠文件名猜） |
| Def 全量清点 | Python + ElementTree，脚本 `F:\temp\cump_defs.py`，**排除 `Languages/` 与 `Patches/`** |
| 翻译重复 | 脚本 `F:\temp\cump_trans.py`（比对树结构）+ `F:\temp\cump_wsdiff.py`（逐键→值 + 空白归一化） |
| DLL 反射 | 预载游戏 Managed + `0Harmony.dll` + **`RJW.dll`**（第三个必需，见纠错 2），再 `GetTypes()` |
| 自定义 Def 接口 | 反射取 `StuffingDef` / `FluidGatheringDef` / `Fluid_Record_Mapping` 的字段表 |
| 依赖装况 | Python 逐个 `About.xml` 直系子元素查 packageId |
| 贴图三格式 | 按 stem 分组统计每种格式的文件数与字节 |

### ② 阳性对照

| 结论 | 对照 | 结果 |
|---|---|---|
| 依赖装况表可信 | `vegapnk.cumpilation` 自身必须被扫到 | PASS ✅ |
| DLC「MISSING」是假阴性 | 官方 DLC 的 packageId 在 `Data/<DLC>/About/About.xml`，不在 `Mods/` | 6 个 DLC 全部查到（`Ludeon.RimWorld.Royalty` 等）✅ |
| Def 扫描结果可信 | 1.6 defNames > 0 且与 1.5 的交集 > 0 | 87 / 86，交集 86 ✅ |
| 翻译"内容相同"可信 | 归一化器不能太宽松：34 个原本字节相同的文件必须也归一化后相同 | `norm_same(37) >= byte_same(34)` ✅ |
| 自定义 Def 类存在 | `rjw.SexFluidDef` 必须在 `RJW.dll` 里找到 | FOUND，字段 11 个 ✅ |
| Harmony 计数可信 | 扫描器 `ATTRIBUTE READ ERRORS` 必须为 0 | 0 ✅ |
| XML 全部可解析 | 解析失败要打印而不是吞掉 | parse errors = 0 ✅ |

### ③ 自查纠错（本轮 4 次）

1. **Def 扫描把 DefInjected 当成了 Def，冒出几百个假"Def 类型"。** 我把 `1.6/Languages/` 里的 `<Cumpilation_XXX.label>` 也当成了 `<Defs>` 的根元素，于是根元素类型列表里出现几百条 `.label`。修正方式是排除 `Languages/` 与 `Patches/`（`Patches/` 里的 `Operation` 也不是 Def）。修正后从"几百个类型"降到 **15 个真实 Def 类型**。

2. **PS 脚本里的中文路径被 ANSI 解码成乱码，导致三个自定义 Def 类全部误报 MISSING。** PowerShell 5.1 读 `.ps1` 文件默认按 ANSI，`RJW_核心_本体` 和含全角括号的 mod 目录名全部变成乱码 → `LoadFrom` 抛 `FileNotFoundException` → `GetTypes()` 返回空 → 三个类报 MISSING。**判据是正控同样失败**（`rjw.SexFluidDef` 也 not found）。改成**从命令行传参**（外层用 `-LiteralPath` 处理中文）后一切正常。

3. **反射的 1 个 loader error 也是我的环境问题。** 报 `Could not load file or assembly 'RJW, Version=1.5.9088.5242'`。核实后发现 `F:\Games\GBL\rimworld\Mods\RJW_核心_本体\1.5\Assemblies\RJW.dll` **确实存在**（v=1.5.9201.31093），只是我的探针没预载它。补上预载后 **loader errors = 0**。

4. **DLC 被我的依赖脚本误报为 MISSING。** 脚本只扫 `Mods/*/About/About.xml`，而 6 个官方 DLC 的 `About.xml` 在 `Data/<DLC>/`。误报了三行 `Ludeon.RimWorld.Royalty / Ideology / Biotech MISSING`。改查 `Data/` 后全部确认已装——**这三个 DLC 的条件子树（`Mods/Biotech` 9 XML、`Mods/Ideology` 2 XML）在本机是真实会加载的**。

另外「翻译内容是否真的一致」这一条也走了两步：先按字节判出 4 个不同，再按键→值判出全部一致，最后才定位到差异只在 `<!-- EN: -->` 注释。**三层递进才说清"到底哪里不同"**，只做第一层会得出"译文冲突"的错误结论。

## 可复用结论

1. **判断「贴图格式冗余」要连「支持哪些版本」一起看。** 本 mod 三格式齐全，但只声明 1.5/1.6，而 1.5+ 优先读 `.dds.zstd` —— 于是 26 个未压缩 `.dds`（3.6 MB，占 44.2%）在其声明支持的全部版本上都是死的。反过来，姊妹 mod `3297307747` 没有 zstd，它的 `.dds` 就**是**实际读取格式，不能删。**同一个「有 `.dds`」的事实，在两个 mod 上结论完全相反。**

2. **未压缩 `.dds` 比同名 `.png` 还大，是很好的体积信号。** 本 mod 家具贴图 `.dds` 335 KB / `.png` 135 KB / `.dds.zstd` 68 KB。压缩后的 DDS 通常只有未压缩版的 1/4 到 1/5。看到 `.dds` 单文件几百 KB 而同图 PNG 才一百多 KB，基本可以直接判定 `.dds` 是最冗余的那一份。

3. **`LoadFolders.xml` 支持 `IfModNotActive=`，可用于互斥加载。** 这是 `IfModActive` 的补集。本 mod 用它实现"有 Semen Processor 就用对方的原料加工，没有才用自己的 Spermatuch/Samenstein"——**依赖互斥靠 `LoadFolders` 表达，比在代码里写 `if (ModsConfig.IsActive(...))` 干净**（XML 侧直接不加载，不用做运行时分支）。代价同样是：**条件依赖不给任何提示**（`IfModNotActive` 那条尤其隐蔽，因为它在"依赖不存在"时才生效）。

4. **CHANGELOG 里声明的改动可以用二进制独立验证。** 1.2.4 那条"把 `Cumpilation_Samenstein` 的 XML 材料成本改成 .dll 补丁"，在 1.6 的 DLL 里确实多出 `Patch_AllowedStuffsFor_noCumRuins` 类，而 1.5 的 DLL 没有。**log 与二进制对上是很强的证据链**，反之若 log 说改了而 DLL 里找不到，那就说明改动没生效或被回滚了。

5. **XML 里用自定义 Def 类型做「表驱动」，比散落硬编码好扩展。** 本 mod 的三个自定义 Def（`StuffingDef` / `FluidGatheringDef` / `Fluid_Record_Mapping`）分别描述"液体→Hediff→三档想法"、"液体↔可收集物换算"、"液体→两条记录计数"。**先在反射里把这三个类的字段表读出来，就等于免费拿到了这个 mod 的内容 schema。** 这比通读 192 个类型高效得多。

6. **审 mod 的贴图与代码占比，能一眼判断这个 mod 的性质。** 本 mod `.cs` 235 文件 / 447 KB（5.5%），`.xml` 182 / 363 KB（4.4%），而贴图三件套占 84.9%。**代码量与 Def 量的比例、Def 数与体积的比例，是判断"功能型 vs 内容型"的快捷指标。**

7. **用 `.txt` 扩展名停用一个补丁，是给自己留的开关。** 补丁加载器只读 `.xml`，所以改个扩展名就等于注释掉，但内容、讨论链接（`Discussed in Issue #5`）、停用原因都留在文件里，比注释掉更利于日后恢复。判断一个补丁是否"被有意停用"，先看它的扩展名。

8. **PS 脚本里出现中文/全角字符路径时，改成传参而不是写死在脚本里。** PS 5.1 按 ANSI 读 `.ps1`，中文路径全变乱码 → `FileNotFoundException` → 一连串假阴性。**判据是"正控也一起失败了"** —— 这条比报错信息本身更有用，因为它区分了"路径不存在"和"路径被解码坏了"。

9. **同一份翻译放在两处时，"字节不同"不等于"内容冲突"。** 要分三层看：字节 → 空白归一化 → 逐键→值。本 mod 38 个共享文件里 4 个字节不同，但译文值**全部一致**，差异只在注释与缩进。**先做最贵的那层（逐键→值）再下结论**，否则会把"维护冗余"误报成"翻译打架"。

10. **带 `LICENCE` / `CHANGELOG.md` / `CONTRIBUTING.md` 的 mod 值得多花一点时间读工程文件。** 本轮的许可证不一致、两份 Manifest 不一致、`.gitignore` 漏 `1.6`、CHANGELOG 与二进制的对应关系，全部来自这三份文件——**它们的信息密度远高于 Def 和源码**。本仓库收录的 mod 大多缺这类文件，读到的那些都属于额外收益。

## 修改建议

> 以下全部**未执行**。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。

| 优先级 | 事项 | 依据 |
|---|---|---|
| **P0** | 澄清许可：把 README 徽章从 GPL3 改成 AGPL-3.0，或把 `LICENCE` 换成 GPL-3.0 全文 | 随包 `LICENCE` 是 AGPL-3.0 全文，与 README 徽章不符 |
| **P0** | 删掉 `Common/Textures/` 下 26 个未压缩 `.dds`（3,625,480 B） | 只支持 1.5/1.6，zstd 优先读，`.dds` 永不被读；删后体积 −46% |
| **P1** | 删掉根 `Languages/…/DefInjected/`（38 个文件），只保留 `1.6/Languages/`；或反之只留根、把 1.6 的删掉 | 两套并存；34 个完全重复、3 个仅空白差异、1 个注释过期 |
| **P1** | 同步两份 Manifest：`About.xml` 的 `modDependencies` 补 `UnlimitedHugs.HugsLib`；`incompatibleWith` 统一用 packageId 并补 `RJW-LicentiaLabs` 的真 packageId | 两份清单不一致；HugsLib 缺失无任何提示 |
| **P2** | 删 `1.5/Assemblies/.gitignore`（15 B）并给 `1.6/Assemblies/` 也放一个 | 它只在 1.5 侧，导致 1.6 的 DLL 缺同等的忽略保护 |
| **P2** | 修根 `Languages/…/Drug_FluidBuff.xml` 里过期的 `<!-- EN: -->` 注释 | 英文描述已在 1.6 那份更新，根这份停留在旧文案 |
| **P2** | 把 csproj 的 HintPath 从「往上 6 层找 Steam 目录」改成较稳的相对路径或 MSBuild 属性 | 换任何目录布局都编不过 |
| **P3** | 统一 C# 工程文件：1.5 与 1.6 是否各留一份 `.csproj`/`.sln`（当前共 2+2 个，且 `1.5` 侧多了 `.gitignore` 而 `1.6` 没有） | 配置不对称 |

## 未核实项

- **`.dds` / `.png` 是否真的永不被读**依赖 RimWorld 1.5+ 的贴图解析顺序（`.dds.zstd` → `.dds` → `.png`）。这一条来自本会话早前对姊妹 mod 的推断与本 mod 三格式并存的形态，**未在本机实机验证，也未反编译**。`.dds` 的判断置信度高（三者并存 + 只支持 1.5/1.6），`.png` 的判断置信度较低（某些代码路径可能显式取 `.png`），所以两者未合并成一条结论。
- **本 mod 未在 1.6 实机加载验证**。特别是：`loadBefore="Vegapnk.rjw.genes"` 这条加载顺序契约的实际机制（谁读它、失败会怎样）未追。
- **`Rift`/`RJW-LicentiaLabs` 的真 packageId 未查**。`Manifest.xml` 用的是显示名，我用显示名去查 packageId 索引自然查不到——这是我的查法局限，不是它未装。
- **`CHANGELOG` 里 1.2.3 那条 Known Issue（携带过多食物被判偷窃）是否已解决**未查——1.2.4–1.2.6 的条目里没有对应修复。
- **源文件与素材的完整授权链未逐一核实**。CONTRIBUTING 要求图片"有明确归属（如 CC3）"，README/CONTRIBUTING 署名了 5 个来源仓库，但**没有说明这些来源各自的许可**——把 GPL-3.0 的代码与来源许可未知的贴图打包发布，授权链是否闭合未核。
- **`Common/` 只有贴图这一事实是否是有意设计**未确认（也可能是 Def/代码恰好两版完全相同所以无需共享）。
