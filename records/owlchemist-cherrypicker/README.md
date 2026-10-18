# Cherry Picker（`3521312241`）— 分析记录

| | |
|---|---|
| 本记录目录 | `records/3521312241-CherryPicker/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\3521312241\` |
| mod 名 | Cherry Picker |
| packageId | `Owlchemist.CherryPicker` |
| 作者 | Owlchemist |
| 工坊 ID | `3521312241`（`PublishedFileId.txt` 恰 10 字节，无 BOM 无换行 ✅） |
| 许可 | **MIT**（见下方授权说明） |
| 支持版本 | 1.3 / 1.4 / 1.5 / 1.6（`About.xml` 四项全列） |
| 源码 | https://github.com/Owlchemist/cherry-picker |
| 分析日期 | 2026-10-17 |

> 本 mod **无禁再分发声明**，收录区可存其结论与 Def 细节。

**它在你库里的位置**：全库 **1021 个 mod** 里，它属于"没有它就难受、有了它就不必为某个 mod 单独写 patch"的那一类。
它的存在意味着**你可以对任意 mod 做逐 Def 粒度的减法**，而不必为每个不想要的东西写一次 `PatchOperationRemove`。
本记录因此**不分析某个内容 mod**，只分析这个"减法工具"本身。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **12 文件 / 324,306 字节（316.7 KB）** |
| 主体 | 4 个版本的 DLL 合计 228,864 字节 + 1 个 PDB（34,184） |
| 结构 | `About/` + 顶层 `1.3/ 1.4/ 1.5/ 1.6/` + `Languages/`（**RimWorld 原生版本目录，未用 LoadFolders.xml**） |
| 类型 | **纯 C# 工具 / 框架**——不产出任何 Def，**一个 XML 都没有** |
| 语言 | English(54) / Russian(53) / Japanese(4)，**无简中** |
| `modDependencies` | `brrainz.harmony` ✅ 已装（目录 `2009463077`） |
| `loadBefore` | `oskarpotocki.vanillafactionsexpanded.core` ✅ 已装（`2023507013`）——**该 mod 实际的 packageId 是混合大小写 `OskarPotocki.VanillaFactionsExpanded.Core`；About.xml 的加载顺序匹配大小写不敏感，故此处写法无害**；`vinalx.researchpalforked`、`owlchemist.researchpowl`、`antaioz.modmedicinepatch` ❌ 未装 |
| `loadAfter` | `mlie.clothingsorter` ❌ 未装 |
| 引用程序集（1.6） | `0Harmony 2.3.6.0`、`Assembly-CSharp 1.6.9320.31385`、`UnityEngine.CoreModule / TextRenderingModule / IMGUIModule`、`System`、`System.Core`、`mscorlib` |
| 是否自带 `0Harmony.dll` | **否** ✅（与全库 85 个自带副本的 mod 相反） |

```
About/About.xml (1128B) + About/Preview.png (43641B) + About/PublishedFileId.txt (10B)
1.3/Assemblies/CherryPicker.dll   46080B   SHA256 53abbef5…
1.4/Assemblies/CherryPicker.dll   59904B   SHA256 76a72442…
1.5/Assemblies/CherryPicker.dll   62976B   SHA256 d21f579a…  + CherryPicker.pdb (34184B)
1.6/Assemblies/CherryPicker.dll   59904B   SHA256 4f4ab849…
Languages/English/Keyed/owlchemist.cherrypicker.xml   (6452B)
Languages/Japanese/LanguageInfo.xml (354B) + Keyed/… (585B)
Languages/Russian/Keyed/owlchemist.cherrypicker.xml  (9088B)
```

**授权说明（§3.2 单独核实）**：
- `About.xml` **没有** `<license>` 字段，**工坊分发的目录里没有任何 LICENSE 文件**。
- 许可证只存在于 GitHub 仓库：MIT。但其版权行写的是 `Copyright (c) 2020 jptrrs`，
  **不是 Owlchemist**——像是 fork / 沿用模板未改。因此不能仅凭 LICENSE 断言工坊版本的授权归属。

---

## 它是什么

一句话：**在 mod 设置页里把任意 mod 的任意 Def 逐条勾掉**。勾掉的 Def 仍留在 `DefDatabase` 里
（避免其他 mod 引用它时报错），但**所有指向它的引用都被切断**，于是它不再出现在任何地方。

### 四类"切断"手段

| 手段 | 做法 | 例子 |
|---|---|---|
| **数值归零** | 把权重/概率/间隔改成永不可能命中的值 | `IncidentDef.baseChance=0` + `earliestDay=int.MaxValue`；`WeatherDef.temperatureRange=(-999,-998)`；`AbilityDef.level=int.MaxValue`；`PawnKindDef.combatPower=float.MaxValue` |
| **集合摘除** | `Clear()` / `RemoveAll()` 清掉标签、前置、过滤器 | `thingCategories.Clear()`、`researchPrerequisites.RemoveAll(…)`、`costList.RemoveAll(…)` |
| **真删** | 对"删了没人会引用"的类型直接 `DefDatabase<T>.Remove` | `TraitDef`、`HairDef`、`BeardDef`、`TattooDef`、`MemeDef`、`BackstoryDef`、`RitualPatternDef`、`GeneDef`、`XenotypeDef` |
| **反向下推** | 被移除项是别人的前置时，把它的前置**补给依赖它的项目** | 移除研究 A 后，所有以 A 为前置的研究自动继承 A 的前置，避免变成不可达 |

> 「反向下推」是最见功力的一处：单纯删掉前置会让整条研究链锁死，作者选择**重连**而不是**留坑**。

### 处理范围（1.6 源码实测）

`Setup()` 用一条长 `Concat` 收集 **45 个核心 Def 类型**，再追加 4 类特殊来源：

- `DefList` —— 它自己定义的一种 Def（见下）
- VFE Ancients 的 `PowerDef`（`vanillaexpanded.vfea`）
- VFE 的 `AbilityDef`（`oskarpotocki.vanillafactionsexpanded.core`）——**只取带 VanillaPsycastsExpanded 扩展的那些**
- VPE 的 `PsycasterPathDef`（`vanillaexpanded.vpsycastse`）

45 类清单：ThingDef、ResearchProjectDef、BodyTypeDef、FactionDef、PawnKindDef、QuestScriptDef、
TerrainDef、RecipeDef、TraitDef、DesignationCategoryDef、ThingStyleDef、IncidentDef、HediffDef、
ThoughtDef、TraderKindDef、GatheringDef、WorkTypeDef、MemeDef、PreceptDef、RitualPatternDef、
HairDef、TattooDef、BeardDef、RaidStrategyDef、MainButtonDef、AbilityDef、BiomeDef、MentalBreakDef、
SpecialThingFilterDef、GenStepDef、InspirationDef、StorytellerDef、ScenarioDef、DesignationDef、
PawnsArrivalModeDef、GeneDef、XenotypeDef、BackstoryDef、WeatherDef、ScatterableDef、
RaidAgeRestrictionDef、WeaponTraitDef、RulePackDef、InteractionDef、DefList。

### 六个 Harmony 补丁（**1.6 DLL 反射实测**，非源码推断）

| 补丁类 | 目标 | 手法 | 为什么需要 |
|---|---|---|---|
| `Patch_Wear` | `Pawn_ApparelTracker.Wear` | Prefix，`HarmonyPriority(800)` = First | 有些 mod 用 **C# 直接给人穿装备**生成pawn，绕过所有过滤器 |
| `Patch_QuestUtility` | `QuestUtility.SendLetterQuestAvailable` | Prefix | 同上——**C# 塞任务** |
| `Patch_QuestManager` | `QuestManager.Add` | Prefix | 同上 |
| `Patch_Pawn_HealthTracker_AddHediff` | `Pawn_HealthTracker.AddHediff`（显式指定 4 参重载） | Prefix | Hediff 的移除**只能靠运行时拦截** |
| `Patch_IsDebugSpawnable` | `DebugThingPlaceHelper.IsDebugSpawnable` | Postfix | 让 devmode 生成器也知道 Def 已被移除 |
| `Patch_MainMenuDrawer_MainMenuOnGUI` | `MainMenuDrawer.MainMenuOnGUI` | Postfix | 回到主菜单后**跑第二遍**，抓运行时才生成的 Def，完事把补丁自己卸掉 |

外加一个**按需安装**的补丁：`ThingDef.IsStuff` 的 getter **Transpiler**——
只有当"被移除的东西里含 Stuff（衣料）"时才装（`filteredStuff` 标志），装后用 `patchLedger` 防重复。

> `DynamicPatches` 类上的 `[HarmonyPatch]` 属性是**注释掉的**，源码里那处 Transpiler 定义之上留着注释行。
> 不是遗漏——它由 `ProcessList()` 末尾**手动** `_harmony.Patch(…, transpiler:)` 装上，属条件启用。

### 三个特殊处理

- **HediffDef**：`RemoveDef` 里 `break;` **什么都不做**，注释写明
  `// Do nothing, this can only be handled via harmony interception`。疾病无法从静态引用切断，只能在 `AddHediff` 拦。
- **InteractionDef**：换掉 worker 实例为 `InteractionWorker_Dummy`，
  它的 `RandomSelectionWeight` 直接 `return 0f`——"交互还在，但被选中的概率是 0"。
- **Apparel（服装）**：`reloadRequired = true`。服装的标签一改就会影响已有 pawn 的着装缓存，
  只能提示**重载存档**。

### 两级提示，区分得很清楚

| 提示 | 触发条件 | 含义 |
|---|---|---|
| `CherryPicker.ReloadRequired` | 移除**服装**、`DesignationCategoryDef`（游戏中） | **重载存档**即可，不用重启游戏 |
| `CherryPicker.RestartRequired` | `TryRestoreDef` 对该类型**没有还原分支**，只能重启 | 反向取消移除时触发 |

> 这是"可逆性设计"的教科书写法：**每一类 Def 都要回答"改回来要花多大代价"**，
> 并把代价直接告诉用户，而不是默默重启或默默要求重载。

### `DefList`：给别的 mod 作者用的"预设清单"

它自定义了一个 `DefList : Def { public List<string> defs; }`。
**别的 mod 作者**可以定义这种 Def，装一批 defName，用户在 Cherry Picker 里勾一下 `DefList` 那一行，
就会**批量**把清单里的 def 加进/移出移除列表。英文说明原文：

> This is a proprietary Cherry Picker def. Mod authors can create these defLists for their mods
> to create preset lists of defs that users can add/remove.

### 设置存储

`ModSettings_CherryPicker.allRemovedDefs` 是个 `HashSet<string>`，Scribe 键名 `keys`。
键的格式由 `DefUtility.ToKey()` 生成：**`Def类型名/defName/命名空间`**。

带命名空间是必需的——第三方 mod 的 `AbilityDef` 和原版的 `AbilityDef` 同名不同类，
只存 `AbilityDef/Foo` 会撞车。`ToType()` 反向解析时也按 `Verse.` → `RimWorld.` → 已缓存程序集 → 原版程序集的顺序找。

> ⚠️ **设置文件的磁盘位置本机无法核实**：全 `F:\Games\GBL\rimworld\` 递归找不到任何 `.cfg`，
> `%USERPROFILE%\AppData\LocalLow` 下也没有 Ludeon 目录（游戏在本机未产生过用户数据）。
> 源码侧只能确认它用 `ModSettings` + `HashSet<string>`，落盘路径未验证，不作断言。

### 界面

三个筛选器（**Def 类型**下拉 / **内容包**下拉 / 搜索框）+ 逐行复选框列表，行高固定 22px，
隔行浅色高亮，鼠标悬停变亮，Tooltip 显示 `Type / Mod / Def / Filename`。
列表用**虚拟滚动**——只绘制 `scrollPos` 可视范围内的行（`DrawList` 里那个 `cellPosition` 判断）。

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 / 文件清单 | `Get-ChildItem -Recurse` + `[System.IO.File]::ReadAllBytes().Length`（不用 KB 化输出） |
| 依赖与加载顺序安装状态 | `[xml]` 解析全部 1021 个 `About/About.xml`，**只取 `ModMetaData` 的直接子元素 `<packageId>`** |
| 1.6 的类型 / 补丁目标 | `Assembly.LoadFrom` + `GetTypes()`，前置 `LoadFrom` 游戏 `Managed` 与 Harmony 的 `0Harmony.dll` |
| 1.4↔1.6 引用了哪些 Def 类型 | 提取 DLL 的 **#Strings 元数据堆**（ASCII 连续段），正则 `^[A-Za-z_]\w*Def$` 过滤后做集合差 |
| 第三方 mod 集成标识 | 提取 **#US 字面量堆（UTF-16）**——`AccessTools.TypeByName("…")` 的参数只存在于这里 |
| 实现手法 | `git clone --depth 1` 源码仓库 + 读全部 6 个 `.cs` |
| 1.6 真实源码 | 从 DLL 的 `AssemblyInformationalVersion` 读出 commit `7e77b7fd…`，再 `git fetch --depth 1 origin <sha>` 定点抓取 |

> 关键手法：**.NET SDK 会把构建时的 git commit 自动写进 `AssemblyInformationalVersion`**
> （格式 `<Version>+<commit>`）。这是"从二进制反查源码"最省事的入口——
> 本例中 `1.6+7e77b7fdba2daa472a5b7c2b35ac17c149dffa99` 直接指向了产物源码。

### ② 阳性对照（每条结论都配了能证明工具本身有效的样例）

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| XML packageId 解析 | `brrainz.harmony` 必须命中 | ✅ 命中，且顺带扫出全库 1026 个 packageId |
| #Strings ASCII 提取 | `QuestScriptDef` 必须命中 | ✅ 命中（否则"66 个 Def 名"的结论作废） |
| #US UTF-16 提取 | `CherryPicker.ReloadRequired` 必须命中 | ✅ 命中 |
| Keyed 翻译词条提取 | `CherryPicker.RestartHeader` 必须命中 | ✅ 命中 |
| `GetTypes()` | 必须列出带 `[HarmonyPatch]` 的类 | ✅ 28 个类型中 6 个带补丁 |
| 后缀匹配 | `WeatherDef` / `InteractionDef` 必须**独立**出现（对照组） | ✅ 独立出现，说明并非全部靠共享 |
| Odyssey Def 类提取 | Core Defs 里必须能解析出 `ThingDef` | ✅ 命中 |

### ③ 自查纠错（本轮我自己的工具错了 5 次）

**1. 把 Keyed 翻译统计成 0 条**
我按 DefInjected 的格式去找 `<li defName="…">`，而 Keyed 文件的形态是
`<LanguageData><CherryPicker.Xxx>文本</CherryPicker.Xxx></LanguageData>`——**元素名就是 key**。
结果三个语种全报 0 条。差一步就写下"该 mod 几乎没有翻译"。
改对形态后实际是 English 54 / Russian 53 / Japanese 4。

**2. `$hashtable` 初始化写在了 `if` 分支里，导致统计结果自相矛盾**
统计脚本里 `$other=@{}` 落在了 `if` 分支，导致后面两次赋值静默失败，
报出"俄语缺失 1 条"这种一眼就不可能的数字。**发现方式是数字本身不合理**，不是靠复算。
重写后确认俄语只缺 1 条、日语缺 50 条。

**3. `git clone` 明明成功了却被判为失败**
git 把 clone 进度写到 **stderr**，PS 5.1 在 `$ErrorActionPreference='Stop'` 下把 stderr 当终止性错误。
当时正准备改用其它方式下载源码——**先 `Test-Path` 才发现仓库其实已经在盘上**。
凡是会往 stderr 写进度的原生命令（`git clone`/`git fetch`/`curl`）都要先摘掉 `Stop`。

**4. 元数据堆的**后缀共享**造成假阴性**
比对源码与二进制时，`TraitDef` 和 `RulePackDef` 报"在 1.6 DLL 里找不到"，
差点据此写成"1.6 版本删掉了这两类处理"。实际原因是 .NET 的 **#Strings 堆做后缀共享**：
`TraitDef` 只作为 `WeaponTraitDef` 内部的一个后缀存在（`RulePackDef` 藏在 `processRulePackDef` 里），
我的提取器按 0x00 切分，看到的只有外层那个更长的字符串。
改用**后缀匹配**（`regex Escape + '$'`）后 45 个类型全部命中。

**5. 只扫 ASCII 堆，把第三方 mod 集成全判成"未命中"**
`VanillaPsycastsExpanded.PawnKindAbilityExtension_Psycasts`、`VEF.Abilities`、
`vanillaexpanded.vfea` 等在 `AccessTools.TypeByName("…")` 里是**字符串字面量**，
存在 **#US 堆、UTF-16 编码**，ASCII 提取器一个都看不见。
补了 UTF-16 提取后 101 条字面量全部读出——**第三方集成一直都在**，
差一步就写成"1.6 版砍掉了 VPE/VFE 支持"。

**6.（2026-10-17 收录 `3033901359` 时回头发现）用大小写不敏感的哈希表判 packageId，等于没判。**
上面这张「依赖/加载顺序」表里，`oskarpotocki.vanillafactionsexpanded.core` 一栏写的是
**本 mod 自己声明的拼法**，而 VFE 的真实 packageId 是混合大小写
`OskarPotocki.VanillaFactionsExpanded.Core`（直接读 `2023507013/About/About.xml` 的
`ModMetaData` 直接子元素确认）。当时我用 PowerShell 的 `@{}` 查"是否已装"，
两种拼法都返回命中——因为 **PS 哈希表键大小写不敏感**，这掩盖了拼写差异。
结论本身（已装、未装）没错，**错在证据链**。
后续核对：`Verse.ModMetaData` 同时有 `packageIdLowerCase` 字段与 `SamePackageId` 方法，
故 About.xml 的 `loadBefore` / `loadAfter` **大小写不敏感**，全小写写法不构成 bug。
→ 查"某 packageId 是否安装"一律走 `[xml]` 直系子元素，别用哈希表。

### ④ 一处未核实

**设置文件（`ModSettings`）的落盘位置**在本机无法核实，原因见「它是什么 → 设置存储」。
我尝试过两条路：全游戏目录递归找 `.cfg`（0 命中）、`LocalLow` 下找 Ludeon 目录（不存在）。
另一条路是解 `Verse.ModSettings.Write()` 的 IL 取路径字面量，
但 `MethodBody` 的 token 解析在本机失败（`ResolveMember` 全部解析不了），**没有硬猜**。

---

## 上下游与冲突面

**它要求 Harmony，但没有自己带一份** ✅ —— 与全库 85 个自带 `0Harmony.dll` 副本的 mod 不同。
依赖唯一的 `brrainz.harmony` 在本库已装（目录 `2009463077`，`Current/Assemblies/0Harmony.dll` 为 2.4.1.0）。

**加载顺序是它的功能的一部分**，不是形式：
`loadBefore` 列的四个 mod 是"会在加载期生成 Def、且 Cherry Picker 要在它们之前把这些 Def 摘掉"的对象。
本库里 VFE Core 已装（其余三个未装），这条顺序声明是**真实生效**的。

**跨版本约定值得学**：仓库根目录**就是 mod 目录**（`About/` 与 `1.3/`–`1.6/` 平级），
`CherryPicker.csproj` 的 `OutputPath` 在 1.6 版改成 `..\1.6\Assemblies\`，直接编译进版本目录。
**没有 LoadFolders.xml**——用的是 RimWorld 原生的顶层数字版本目录机制。

**源码仓库与工坊产物不同步**（重要）：

| | 仓库 `master` | 仓库 commit `7e77b7f` | 工坊安装版 |
|---|---|---|---|
| 日期 | 2023-05-30 | **2025-07-11** | — |
| 预编译产物 | 仅 1.3 / 1.4 | 1.3 / 1.4 / 1.5 / 1.6 | 1.3 / 1.4 / 1.5 / 1.6 |
| 与安装版 1.5 | — | **SHA256 完全一致** ✅ | — |
| 与安装版 1.6 | — | 61440B / `4da68baf…` | 59904B / `4f4ab849…` ❌ |

即：**`master` 分支停在 2023 年、只到 1.4，而工坊发的 1.5/1.6 来自 master 之外的 commit `7e77b7f`
（提交信息："Fixing null reference exception on mech hive filth"）**。
`ls-remote` 显示该仓库只有 `master` 一个分支，但按 SHA 定点 fetch 却成功了——
说明这些提交在服务器上可达却不属于任何公开分支。
安装版 1.6 与该 commit 的 1.6 二进制**不同大小但同 commit 号**，属同源不同工具链的产物。

**1.4 → 1.6 的真实代码改动只有 3 处**（源码 diff 全文核实）：

| 改动 | 原因 |
|---|---|
| `assemblyName:"VFECore"` → `"VEF"`，`nameSpace:"VFECore.Abilities"` → `"VEF.Abilities"` | VFE 改了程序集名与命名空间 |
| `thingDef.race.wildness = 1f` → `thingDef.SetStatBaseValue(StatDefOf.Wildness, 1f)` | 1.5 的 stat 重构把 wildness 变成了 StatDef |
| `scatterGroup.things.RemoveAll(…)` → `scatterGroup.things?.RemoveAll(…)` | **就是那次提交的名字**：mech hive filth 的空引用 |
| csproj：`Krafs.Rimworld.Ref` `1.4.*` → `1.6.4515-beta`，`OutputPath` 改到版本目录 | 构建适配 |

**没有新增任何 Def 类型。** 这与二进制侧的独立结论一致：
1.4 与 1.6 的 `*Def` 名集合**完全相同**（66 个，无增无减；用后缀匹配复核过）。

---

## 可复用结论

1. **"伪移除"是给别人的 Def 做减法时唯一安全的默认姿势。**
   直接 `DefDatabase<T>.Remove` 会让所有指向它的引用变成 null，炸在别人代码里；
   保留 Def、只切引用，则爆炸面收敛在本 mod 内部。
   代价是要为每类 Def 手写"怎么切"——Cherry Picker 为此写了 550 行 `switch`。

2. **删掉一个"前置"时，要决定后继者的命运。**
   研究链和灵能前置都是 DAG，删中间节点会让下游全部不可达。
   Cherry Picker 选的是**把被删节点的前置下推给下游**（`prerequisites.AddRange(...)`）——
   这是图论里的"路径合并"，通用：任何"可被多节点引用的能力/前置"都该这么处理。

3. **可逆性要按类型分级并主动告知。**
   值被改成 0 的可以改回来；`DefDatabase.Remove` 的能 `Add` 回来；
   两者都不行的只能重启。把这三档映射到"静默 / 提示重载 / 提示重启"三种 UI 行为，
   比"一律要求重启"友好得多，也比"默默重启"诚实。

4. **过滤器永远拦不住 C#，所以补 C# 补丁。**
   Cherry Picker 清空了 Def 的全部标签与权重，但作者仍为"用 C# 直接穿装备 / 直接塞任务 / 直接加 Hediff"
   这三条路径各加了一个 Harmony Prefix。**XML 层做完不等于完事**——
   凡是别的 mod 会用代码直接调用的入口，都要用 Harmony 再兜一层。

5. **从二进制反查源码：`AssemblyInformationalVersion` 是最短路径。**
   .NET SDK 默认把 `<Version>+<git commit>` 写进程序集属性。
   读它 → 按 SHA `git fetch --depth 1 origin <sha>` → 拿到产物对应的确切源码，
   比"clone 默认分支然后猜版本"精确得多（本例就靠它发现了 master 落后两年）。

6. **判断"某类 Def 支不支持"要看 `Setup()` 的 `Concat` 链，不要看 `RemoveDef` 的 `switch`。**
   `switch` 里有分支 ≠ 用户能勾到；只有进了 `allDefs` 的才出现在界面上。
   本 mod 有 45 类进 `allDefs`，而 Odyssey 用到的 94 种 Def 类里有 **69 种不在其中**
   （含 `GameConditionDef`、`SitePartDef`、`WorldObjectDef`、`TileMutatorDef`、
   `ManeuverDef`、`DutyDef`、`GravshipComponentTypeDef`、`ToolCapacityDef`、
   `WeaponCategoryDef`、`TrainableDef` 等**用户可见**的类型）。
   基础设施类（`EffecterDef`、`ShaderTypeDef`、`ThinkTreeDef`、`JobDef` 等）不处理是合理的。

7. **做二进制元数据差分时，两个堆都要扫，且要考虑后缀共享。**
   #Strings（ASCII）放类型名/成员名——但**后缀共享**会让短名字藏在长名字里（`TraitDef` ⊂ `WeaponTraitDef`）；
   #US（UTF-16）放字符串字面量——`AccessTools.TypeByName("…")` 的参数**只**在这里。
   两者都用"按 0x00 切分"的朴素脚本，会同时产生**假阴性**和**假阴性**，
   而且两次都指向"某个功能被删了"这种方向相反的错误结论。

8. **加载顺序声明里，`loadBefore` 和 `loadAfter` 反映的是功能角色，不是偏好。**
   凡是"在加载期修改全局 Def 数据库"的 mod，必须 `loadBefore` 那些会生成 Def 的 mod；
   凡是"给别人的结果加工"的，才用 `loadAfter`。
   本仓库 `AGENTS.md` 约定"patch 第三方 mod 时其 packageId 写 `<loadAfter>`"——
   Cherry Picker 是个**反例**：它不是 patch 某个 mod，而是要在所有人之前动数据库。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **补简中翻译** | 现有 English 54 / Russian 53 / Japanese **4** 条，**中文完全缺失**。54 条里绝大多数是 `CherryPicker.<DefType>.Desc` 说明文本，格式统一、翻译量小 |
| 中 | **Odyssey 覆盖缺口** | Odyssey 的 94 种 Def 类中 69 种未处理，其中 `GameConditionDef`、`SitePartDef`、`WorldObjectDef`、`TileMutatorDef`、`ManeuverDef`、`DutyDef`、`GravshipComponentTypeDef` 是玩家会遇到的 |
| 低 | `Author` 元数据 | 若自制补丁版，可考虑补 `<modDependencies>` 之外的自述信息 |
| 低 | 上游同步 | 上游 `master` 落后两年且不含 1.5/1.6；本机若有改动需求，应基于 commit `7e77b7f` 而非 master |

---

*2026-10-17 收录。核验脚本与阳性对照见「怎么验的」；本轮工具自查纠错 5 次，均已留档。*
