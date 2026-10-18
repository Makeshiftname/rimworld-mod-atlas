# [sd] Bridges (Continued) — 分析记录

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `[sd] Bridges (Continued)` |
| packageId | `Mlie.SDBridges` |
| 作者 | **Mlie**；原作 **sulusdacors**（工坊 `788610933`），`About.xml` 与 `README.md` 都明写 "Update of sulusdacors mod" |
| 源目录 | `F:\Games\GBL\rimworld\Mods\2036488024` |
| 授权 | **MIT**（`LICENSE.md`，`Copyright (c) 2020 Mlie`，无禁再分发声明）→ 可收录、可再分发 |
| 规模 | **218 文件 / 3,016,871 bytes（2.88 MB）** |
| 类型 | 内容 mod（地形 + 建筑 + 研究 + 配方）+ 少量 C#（PlaceWorker / Building / Job / WorkGiver），**零 Harmony** |
| 支持版本 | `1.0 1.1 1.2 1.3 1.4 1.5 1.6`（`About.xml` 7 项，与 `LoadFolders.xml` 7 组一致） |
| modVersion | `1.6.6`（`About.xml` 与 `About/Manifest.xml` 一致；`About/ModSync.xml` 记 `SaveBreaking=False`） |
| 外部依赖 | **无**。`<modDependencies />` 与 `<loadAfter />` 都是空元素 |
| 全库依赖方 | **0**。全库 1021 个 `About/About.xml` 里只有它自己的 `<packageId>` 命中 `Mlie.SDBridges` |
| 上游 | <https://github.com/emipa606/SDBridges>（`About.xml` 的 `url`、`Manifest.xml` 的 `manifestUri`、`ModSync.xml` 的 Host 三处一致） |
| 核验深度 | **③ 档**（218 文件、7 个版本目录、50 个具体 Def + 6 个抽象 Def） |

**自带的第三方 DLL（两个都是死重量，见「它是什么」）**

| DLL | 字节 | 程序集版本 | 全库副本 | 是否被引用 |
|---|---|---|---|---|
| `1.0\Assemblies\0Harmony.dll` | 113,152 | 1.2.0.1 | 与 `F:\Games\GBL\rimworld\Mods\818773962` 根 `Assemblies\0Harmony.dll` **字节完全相同**（SHA256 前缀均为 `E271D22A7C32BFCA`） | **否** |
| `1.0\Assemblies\ModCheck.dll` | 33,280 | 1.8.0.0 | 全库**仅此 1 份** | **否** |

## 它是什么

一句话：往 RimWorld 的地形系统里塞一整套"能在水面上架桥、能改水成陆"的建筑与地形内容，外加一整套原版没有的 `Bridgeable` 装载规则补丁。**它是一个内容 mod，不是框架**——没有任何其他 mod 依赖它。

### 内容清单（1.6 版本目录，15 个 Def 文件 + 2 个补丁文件）

| 类型 | 数量 | 说明 |
|---|---|---|
| `TerrainDef` | 17 | 8 个正式水面/地面 + 8 个影子地形 + 1 个抽象父 |
| `ThingDef` | 22 | 8 个吊桥（1/2/3/4 格宽 × 上/下）、landbridge/seabridge、pontoonbridge、2 个材料、7 个 terraform 建筑 |
| `RecipeDef` | 10 | 2 组 × 5（抽象 base + 切石台单份/10 份 + 加工台单份/10 份） |
| `ResearchProjectDef` | 3 | bridges(Neolithic,500) → terraforming(Medieval,1000) + drawbridge(Medieval,300) |
| `DesignationCategoryDef` | 1 | `sd_bridges_category_terraform`，`order=187` |
| `JobDef` / `WorkGiverDef` | 1 / 1 | **1.6 新增**，见下 |

具体 defName 共 **50 个**，另有 **6 个抽象 Def**（`FakeWaterBase`、`sd_bridges_bridgeBase`、`sd_bridges_woodbridgeBase`、`sd_bridges_TerraformBase`、`sd_bridges_recipe_make_FoundationMaterial`、`sd_bridges_recipe_make_pontoonbridgepart`）。

### 地形：正向改造 + 影子地形反向还原

`1.6\Defs\TerrainDefs\sd_bridges_TerrainDefs.xml` 的 8 个 TerrainDef 全部 `terrainAffordanceNeeded>Bridgeable`、`fertility=0`：

- **过水**：`sd_bridges_FundamentBase`（WorkToBuild 500，花 15 份基础材料）→ 上面可以架桥或盖 `sd_bridges_platform`（WorkToBuild 9000，25 份材料，承重等同混凝土但贴图更暗）
- **改水**：`sd_bridges_DigUpWater`（5000，生成 `Filth_Dirt`）→ `sd_bridges_ShallowWater` / `sd_bridges_ShallowMovingWater`（各 5000）→ `sd_bridges_DeepWater` / `sd_bridges_ChestDeepMovingWater`（各 **10000**，`passability=Impassable`、`pathCost=300`）
- `sd_bridges_MarshWater`（5000，`pathCost=23`）

配套的 `sd_bridges_fakeTerrainDefs.xml` 是**影子地形**：8 个 `sd_bridges_fakeWater*`/`fakeMud`/`fakeMarsh` 全部继承抽象父 `FakeWaterBase`，而 `FakeWaterBase` 继承原版 `NaturalTerrainBase` 并显式写 `<!-- changed the changeable to true -->` `<changeable>true</changeable>`。用途是把真实水面盖成"可被改造"的地面，从而实现**反向**改造（水 → 地）。

C# 侧对应 `Util_sd_bridges` 的 8 个取值属性 + `IsAquaticTerrain(Map, IntVec3)` + `TrySetTerrain(IntVec3, Map, string)`——数量与 8 个影子 Def 精确对上。

### 1.6 的新东西：吊桥改由 pawn 操作

`1.6\Defs\Jobs\` 是 1.6 才有的目录（1.0–1.5 都没有）：

- `JobDefs.xml`：`sd_bridges_DrawBridge`，`driverClass` = `sd_bridges.JobDriver_DrawBridge`，`reportString` = "using drawbridge."
- `WorkGivers.xml`：`sd_bridges_DrawBridge`，`giverClass` = `sd_bridges.WorkGiver_DrawBridge`，`workType` = **`BasicWorker`**，`priorityInType` = 500，`canBeDoneWhileDrafted=true`

对应 `About.xml` 描述里的 "option to make the drawbridge action be done by a pawn instead of an instant action"，中文 Keyed 里有对应的开关 `sd_bridges.UseJob` / `sd_bridges.UseJobTT`（"小卒需要手动操作吊桥，而不是即时操作"）。

吊桥本体是 **8 个 ThingDef**（`drawbridge` / `doubledrawbridge` / `tripledrawbridge` / `quaddrawbridge` × `_up`/`_down`），`drawSize` 从 (3,4) 到 (6,4)，`size` 从 (1,1)/(1,2) 到 (4,1)/(4,2)，HP 300→1200，`costStuffCount` 100→400，规律严格线性。

### C#：40 个类型，零 Harmony

`1.6\Assemblies\sd_bridges.dll` 展开嵌套类型后共 **40 个类型**，其中 38 个在 `sd_bridges` 命名空间：

- 11 个 `PlaceWorker_*`（每个只实现一个 `AllowsPlacing`）：`drawbridge`/`doubledrawbridge`/`tripledrawbridge`/`quaddrawbridge`、`FundamentBaseNotInDeepWater`、`notonfoundation`、`NotOnShallowWater`/`NotOnShallowMovingWater`、`OnShallowWater`/`OnMovingShallowWater`、`OnFundamentBasis`
- 13 个 `Building_*`：8 个吊桥都派生自 `Building_sd_bridges_basedrawbridge`（`[StaticConstructorOnStartup]`，覆写 `SpawnDrawbridge`/`Destroy`/`ExposeData`/`SpawnSetup`/`GetGizmos`/`SetTerrain`/`DoDustPuff`），另有 `pontoonbridge` 与 6 个 `terraform_*`
- `JobDriver_DrawBridge`（`Verse.AI.JobDriver`）、`WorkGiver_DrawBridge`（`RimWorld.WorkGiver_Scanner`）
- `sd_bridgesMod`（`Verse.Mod`，`SettingsCategory`/`DoSettingsWindowContents`）与 `sd_bridgesSettings`（`Verse.ModSettings`，`ExposeData`）
- `sd_bridges.Textures`（`[StaticConstructorOnStartup]`，方法级枚举显示**无任何 DeclaredOnly 方法**）

**7 个版本的 `sd_bridges.dll` 全部没有一处 Harmony 补丁**——类型级与方法级 Harmony 属性都是 0，且 `GetReferencedAssemblies()` 里从不出现 `0Harmony`。所以 `1.0/Assemblies/` 下那两个 DLL（0Harmony + ModCheck）**没有任何代码引用**，是随上游 sulusdacors mod 一起继承下来的僵尸副本。

`ModCheck.dll` 自己是个版本/依赖预检库（类型有 `ModCheckBase`、`ModCheckNameClass`、`ModCheckLog`，方法有 `LoadModCheckPatches`、`isModCheckPatch`、`IsModLoaded`、`IsModSyncVersion`、`GetModSyncVersionForMod`、`GetVersionFromModSyncXML`、`IsNewestVersion`），编译期引用 `Assembly-CSharp 0.19.6814.14609`（RimWorld 1.0 时代），PDB 路径 `C:\SteamLibrary\steamapps\common\RimWorld\Mods\ModCheck\Source\obj\Release\ModCheck.pdb`。**它能对上本 mod 的 `About/ModSync.xml`，但本 mod 没引用它**——全库也只有这一份 ModCheck。

### 贴图：1.6 改用 Unity AssetBundle

`Assets\AssetBundles\Mlie_SDBridges` 是**真的 UnityFS 包**（魔数 `55 6E 69 74 79 46 53` = `UnityFS`，709,202 bytes），配一份 `ManifestFileVersion` 格式的 `.manifest`（3,317 bytes），列 **31 个资产**，路径形如 `Assets/Data/Mlie.SDBridges/Textures/sd_bridges/...`。

`LegacyAssets\` 下是 **31 张 PNG**（826,866 bytes，未压缩磁盘大小）。把两侧相对路径的分隔符归一化后，**名字集完全一致**——是一次 1:1 的格式迁移，没有增删。`LoadFolders.xml` 因此让 1.0–1.5 加载 `LegacyAssets`、只有 1.6 加载 `Assets`。

### 版本号机制：`VersionFromManifest`

`1.6\Assemblies\VersionFromManifest.dll`（5,120 bytes，`Assembly-CSharp 1.4.8315.26675`）只有 3 个类型：

- `Mlie.VersionFromManifest`：字段 `version` / `identifier` / `manifestUri` / `downloadUri` / `targetVersions` / `suggests` / `incompatibleWith` / `loadBefore` / `loadAfter` / `showCrossPromotions` / `ManifestFileName`；方法 `TryGetManifestFile(ModMetaData, out string)` + `GetVersionFromModMetaData(ModMetaData)`
- `Mlie.Main` + `Mlie.Main+<>c`（静态构造里的 lambda，签名 `Boolean (ModMetaData)`）

1.6 的 `sd_bridges.dll` 的 REF 列表里**确实有 `VersionFromManifest 0.0.0.0`**，所以这套机制是接通的：版本号从 `About/Manifest.xml` 读，显示在设置页（中文 Keyed `sd_bridges.CurrentModVersion` = "已安装 MOD 版本：{0}"）。`sd_bridges.dll` 自己的程序集版本号则是 `0.0.0.0`。

顺带一提：`VersionFromManifest` 的字段里有 `targetVersions`/`suggests`/`showCrossPromotions`，而实际 `Manifest.xml` 一个都没写——helper 支持的 Manifest 键比作者用到的多。

### 原版补丁：`Bridgeable` 装载规则

`Patches\sd_bridges_vanillapatch.xml` 用 28 个 `PatchOperationSequence` 包着 **11 个 `PatchOperationTest` + 11 个 `PatchOperationAdd` + 12 个 `PatchOperationadd`（小写 a）+ 8 个 `PatchOperationRemove`**，给 9 个原版地形加 `Bridgeable`、去掉 `changeable`。`Patches\sd_bridges_biomes.xml`（1.5 起有）再加 2 个。

**`Bridgeable` 是原版 affordance，不是这个 mod 自创的**：`Core\Defs\Misc\TerrainAffordanceDefs\TerrainAffordances.xml` 里 11 个 `TerrainAffordanceDef` 之一就是 `Bridgeable`。

原版 1.6 的实际分布（已递归解析 `ParentName` 链）：

| 状态 | 地形 |
|---|---|
| 自身直接带 `Bridgeable` | `MarshyTerrain`、`Mud`（Core）、`Space`、`ThinIce`（Odyssey） |
| 抽象父类带，`WaterShallowBase` | `ShallowWater`+`WaterproofConduitable`+`Bridgeable`+`Walkable` → 子类 `WaterShallow`、`WaterOceanShallow`、`Marsh` |
| 抽象父类带，`WaterChestDeepBase` | `Bridgeable`+`Walkable` → 子类 `WaterMovingChestDeep` |
| 抽象父类带 `changeable=false` 但无 affordance | `WaterDeepBase` → 子类 `WaterDeep`、`WaterOceanDeep` |
| **本机原版根本不存在** | `WaterMovingDeep`、`BiomesCore_WaterAbyssalDeep`、`BiomesCore_WaterShallowLagoon` |

⚠️ **`WaterMovingChestDeep` 与 `WaterMovingShallow` 各自声明了自己的 `<affordances>`（只有 `<li>MovingFluid</li>`）**，所以它们在"整字段替换"语义下继承不到父类的 `Bridgeable`。而 `WaterMovingDeep` 三个 `BiomesCore_*` 在全 `Data/` 目录 0 命中（对照：同一 grep 方式能命中 `WaterDeepBase`），意味着 `sd_bridges_biomes.xml` 的两个目标是**必然落空的 no-op**。

> **一个值得实机验证的疑点**（两个前提本机都没证实，故只记录不下结论）：
> 对 `WaterShallow` / `WaterOceanShallow` / `WaterMovingShallow` / `Marsh`，补丁走的是"Test(`affordances` 不存在) → Add 空 `<affordances/>` → add `Bridgeable`"。这 4 个在**自己的 XML 里都没有 `<affordances>`**（`Bridgeable` 在抽象父类上）。若 (a) 补丁在继承解析**之前**执行，且 (b) 列表字段是**整字段替换**而非父子合并，那么补丁会给它们建一个只含 `Bridgeable` 的列表，**丢掉父类的 `Walkable`/`ShallowWater`/`WaterproofConduitable`**——表现应是"小 pawn 无法正常走过浅水"。
> 本机 106 个游戏程序集里 `InheritanceResolver` / `ResolveNodes` / `FillInMissingFields` **全部 0 命中**（对照 `LoadedModManager` 在 `Assembly-CSharp` 命中于 offset 7258293），未反编译 IL，无法证实。

### 翻译：5 语种，机翻，且漏了招牌功能

| 语种 | DefInjected 条目 | 覆盖 defName | label+description 齐全 | Keyed 文件 |
|---|---|---|---|---|
| ChineseSimplified | 101 | 43 / 50 | 39 | 2 |
| English | 0 | 0 | 0 | 2 |
| French | 101 | 43 / 50 | 39 | 2 |
| German | 101 | 43 / 50 | 39 | 2 |
| Russian | 101 | 43 / 50 | 39 | 2 |

CS / FR / DE / RU 的覆盖 defName 集合**完全相同**（`identical=True`），说明是同一批译文分发到 4 个语言目录。English 无 DefInjected（源语言，label 直接写在 Def XML 里），只有 2 个 Keyed。

中文翻译文件首行注释写明机翻来源：`<!--The following translations were generated by https://www.deepl.com/-->`。

**4 语种一致的翻译缺口**：

1. `sd_bridges_tripledrawbridge_up/down`、`sd_bridges_quaddrawbridge_up/down` —— 4 个 ThingDef 没有任何 `.label`/`.description`。直接读了 `Languages\ChineseSimplified\DefInjected\ThingDef\sd_bridges_ThingDefs_drawbridge.xml`，里面只有 `drawbridge_up/down` 与 `doubledrawbridge_up/down` 共 4 个。**即 mod 宣传的"3 格/4 格宽吊桥"这个 1.6 招牌功能，游戏里显示英文。**
2. `sd_bridges_DrawBridge`（WorkGiverDef）—— **5 个语种都没有 `DefInjected/WorkGiverDef/` 目录**，所以它的 `label`("use drawbridges") / `verb` / `gerund` 全部未本地化。
3. `sd_bridges_recipe_make_FoundationMaterial` / `..._make_pontoonbridgepart` 两个**抽象**父 RecipeDef 无 DefInjected —— 但抽象父不进 Def 表，不算真缺口。

## 跨版本工程

**`LoadFolders.xml` 的共享目录在版本边界没有收敛**：

```
v1.0 ~ v1.5 :  /  +  1.x  +  LegacyAssets
v1.6         :  /  +  1.6  +  Assets
```

1.0–1.5 六个版本共用 `LegacyAssets`（827 KB PNG），到 1.6 换成 `Assets`（AssetBundle）。名字在边界处切换，旧版本仍要拖着那 827 KB。这正好是收录区标准 §6 记的那条待提炼项需要的**反例样本**（"LoadFolders 用得好不好取决于是否在版本边界收敛" vs "仓库倾向弃用 LoadFolders"）。

**各版本目录差异**：

| 版本 | 文件数 | 字节 | 相对上一版的变化 |
|---|---|---|---|
| 1.0 | 20 | 254,164 | 基线；多 3 个补丁（vanillapatch / `_buildableterrain` / `_grandrivers`）+ `ResearchTabs` + Harmony + ModCheck |
| 1.1 | 16 | 85,994 | 删掉 `_grandrivers`、`_buildableterrain`、`ResearchTabs`；删 Harmony + ModCheck |
| 1.2 | 16 | 93,290 | — |
| 1.3 | 15 | 91,621 | 删 `ResearchTabs`（1.3 起彻底没有） |
| 1.4 | 15 | 92,800 | — |
| 1.5 | 16 | 87,665 | 加 `Patches\sd_bridges_biomes.xml` |
| 1.6 | 19 | 110,621 | 加 `Defs\Jobs\`（JobDefs + WorkGivers）+ `VersionFromManifest.dll` |

**程序集版本号一路没维护**：1.0/1.1/1.2 都是 `1.0.6881.34783`，1.3/1.4/1.5 都是 `1.0.0.0`，1.6 退化成 `0.0.0.0`。7 个 `sd_bridges.dll` 的 SHA256 前 8 位两两不同（不是同一份二进制复用），但 1.1 与 1.2 版本号相同且大小都是 32,768 bytes。

## 怎么验的

### ① 核验方法（可复现）

| 目标 | 方法 |
|---|---|
| 规模 | `Get-ChildItem -Recurse -File` 后逐个 `[System.IO.File]::ReadAllBytes().Length`（不信 KB 化列表） |
| DLL 版本 | `[System.Reflection.AssemblyName]::GetAssemblyName()`；DLL 是否同一份用 `Get-FileHash -Algorithm SHA256` |
| 类型表 | 每版本**独立进程**跑反射脚本：预载 `RimWorldWin64_Data\Managed` 全部 106 个 DLL + `Mods\2009463077\Current\Assemblies\0Harmony.dll`，再 `Assembly.LoadFrom` 目标，`GetTypes()` 并吃 `ReflectionTypeLoadException.Types` 取部分类型 |
| Def 清单 / 翻译覆盖 | Python + `xml.etree.ElementTree`，脚本落 `F:\temp\sdb_inventory.py` 与 `F:\temp\sdb_trans.py` |
| 原版地形状态 | Python 递归解析 `ParentName` 链，脚本落 `F:\temp\sdb_vanilla_terrain2.py` |
| 依赖扇出 | `grep` 工具全库扫 `Mlie.SDBridges`（ripgrep，不用 `Get-ChildItem -Recurse`，后者会超时） |
| AssetBundle | 读前 8 字节魔数 + 解析 `.manifest` 的 `Assets:` 列表 |

### ② 阳性对照（每条"0 命中"都配了对照）

| 结论 | 对照 | 结果 |
|---|---|---|
| Assembly-CSharp 无 `0Harmony` 字面量 | 同法扫 `LoadedModManager` / `ModDdsLoader` | 各命中 2，还捞到源码路径 token `9\Assets\Scripts\Verse\Mods\ModContent\Dds\ModDdsLoader.cs` ✅ |
| 全 106 个 Managed DLL 无 `0Harmony` | `Assembly-CSharp` 的 `LoadedModManager` | 命中 offset 7258293 ✅ |
| sd_bridges.dll 零 Harmony | **Cherry Picker 1.6**（`F:\Games\GBL\rimworld\Mods\3521312241\1.6\Assemblies\CherryPicker.dll`，已知带 6 个补丁） | 同一扫描器报出 **7 处** Harmony 属性（6 个 `Patch_*` + `Patch_Wear` 上的 `HarmonyPriority`）✅ |
| `Bridgeable` 是原版 affordance | `TerrainAffordances.xml` 应含 11 个 `TerrainAffordanceDef` 且含 `Bridgeable` | 11 个，含 ✅ |
| 地形继承解析正确 | `MarshyTerrain`/`Mud`/`Space`/`ThinIce` 4 个已知直持者必须 True | 全 True ✅ |
| `BiomesCore_*` 不存在 | 同一 grep 方式找 `WaterDeepBase` | 命中 ✅（说明不是工具坏了） |
| 中文翻译覆盖非零 | CS 必须报 >0 覆盖 defName | 43 ✅ |
| `InheritanceResolver` 缺失是真阴性 | `ParentName` / `PatchOperationFindMod` 必须命中 | 分别命中 offset 12793203 / 7259439 ✅ |
| bundle 与 LegacyAssets 一一对应 | 两侧各 31 条且名字集相同 | 31 = 31，归一化后 `IDENTICAL` ✅ |

### ③ 自查纠错（本轮 5 次，全部靠对照抓出来）

1. **后缀正则漏了 `RegexOptions.Multiline`**。`[regex]::Matches($bigString, [regex]::Escape($n)+'$')` 里 `$` 只锚到整段 15 MB 输入的**末尾**，等于在找"文件最后一个 token 正好等于该名"。第一次扫 `0Harmony`/`HarmonyLib`/`ModCheck`/`VersionFromManifest` 全报 0，就是这个假阴性。作废重做为"按 NUL 切分后逐 token 比对"。

2. **Harmony 检测器假阴性，连修两版才对**。第一版扫描器把 **Cherry Picker 1.6** 报成"0 处 Harmony 补丁"——而它是已知用 Harmony 的 mod。根因两层：(a) **Harmony 不在游戏 `Managed` 目录**（它在 `Mods\2009463077\Current\Assemblies\0Harmony.dll`），不预载时 `HarmonyLib.*` 属性类型解析不了，`CustomAttributeData.ToString()` 抛异常，而我的 `try/catch` 把它吞了；(b) 即使预载了 Harmony（第二轮验证 `HarmonyLib.HarmonyPatch` 确实可解析），`ToString()` 仍是脆路径。改用 `AttributeType.FullName` + **显式统计并打印属性读取异常**后才稳定。**在阳性对照通过之前，那个 0 一律不算数。**

3. **Def 继承链漏算，结论直接翻转**。第一版只看每个 TerrainDef 自己的 `<affordances>`，报 `WaterShallow` 的 `Bridgeable=False`——但 `grep` 在 `Core\Defs\TerrainDefs\Terrain_Water.xml` 的 80/109 行明明命中 `<li>Bridgeable</li>`，那两行在**抽象父类** `WaterChestDeepBase` / `WaterShallowBase` 上。改成递归解析 `ParentName` 后结论反转。

4. **翻译覆盖按文件夹映射全灭**。第一版配对 `Defs\TerrainDefs\x.xml ↔ DefInjected\TerrainDef\x.xml`，4 语种全报"覆盖 0/50"，可简中明明有 101 条条目。根因正是收录区标准早就写着的「DefInjected 文件夹名只是装饰，Def 类型取自元素名」——`TerrainDefs`(复数) vs `TerrainDef`(单数)。改成按 **defName 求交**后：CS/FR/DE/RU 各覆盖 43/50 且四者集合完全相同。

5. **`Compare-Object` 报出 31 条假差异**。拿 `LegacyAssets` 的相对路径（`\`，PowerShell 生成）和 bundle manifest 里的（`/`，Unity 生成）直接比，全部报不等。归一化分隔符后完全一致——**不是内容差异，是我没归一化**。

另有一处工具可用性问题记一笔：`rg` 不在本机 PowerShell 的 PATH 上，命令里调 `rg` 会报 `CommandNotFoundException`；内容搜索一律走 `grep` 工具（内含 ripgrep）。

## 可复用结论

1. **「自带公共库 DLL」不等于「真的依赖它」，必须逐个核对引用方**。`1.0\Assemblies\0Harmony.dll` 与 `F:\Games\GBL\rimworld\Mods\818773962` 的那份**字节完全相同**（同为 v1.2.0.1），但本 mod 7 个版本的 DLL 无一引用 Harmony。所以「全库 N 份重复 Harmony」这种计数，**不能把继承自上游的僵尸副本算成真实冲突源**——必须配 `GetReferencedAssemblies()` + Harmony 属性扫描双重确认。

2. **查"某 DLL 是否用了 Harmony"要三件事同时成立**：(a) 预载 `Mods\*\Assemblies\0Harmony.dll`（**游戏 `Managed` 目录里没有它**，这是最容易漏的一步）；(b) 用 `AttributeType.FullName` 而不是 `ToString()`；(c) **拿一个已知带补丁的 DLL 做阳性对照**。第 (c) 条最关键——我的扫描器连续两版在已知样例上返 0，没有对照就会把"工具坏了"写成"这个 mod 没用 Harmony"。

3. **RimWorld 并没有"按文件名跳过 `0Harmony.dll`"的硬编码**。106 个游戏程序集全扫，`0Harmony` 字面量 0 命中（对照 `LoadedModManager` 命中）。所以"重复的 `0Harmony.dll` 会被加载器跳过"这个流传说法**本机无法证实**，机制更可能是按已加载程序集的**简单名**去重。没反编译 IL，别当定论。

4. **判断"某个 Def 补丁还有没有必要"，必须先解析 `ParentName` 继承链，并严格区分"自己 XML 里写了"与"继承来的"**。只看单层字段会同时产生两个方向的错误结论——本轮就把 `WaterShallow` 的 `Bridgeable` 判反了一次。

5. **补丁目标可能整批不存在**。`sd_bridges_biomes.xml` 打的两个 `BiomesCore_*` 在全 `Data/` 0 命中，是必然落空的 no-op。写补丁时把"目标 defName 在原版是否存在"当阳性对照，比数补丁条数有意义得多。

6. **`specialDesignatorClasses` 挂 `Designator_RemoveFloor` 是个可复用的省事写法**。`sd_bridges_category_terraform` 里列了 `Designator_Cancel` + `Designator_SmoothSurface` + `Designator_RemoveFloor`；terraform 类 mod 只要把自己的 TerrainDef 的 `designationCategory` 指到同一个分类，就能白拿"移除地板"这个原版工具，把玩家造出来的假地形一键还原成原版地形，不用自己写移除逻辑。本 mod 的影子地形体系正是靠这条闭环。

7. **`VersionFromManifest` 模式值得抄**：程序集版本号一旦被 csproj 绑死就很难看，让版本号改从 `About/Manifest.xml` 读、再与 ModSync Ninja 的 `<Version>` 对齐，并由 mod 主程序集 **REF** 那个 helper DLL（本 mod 1.6 的 REF 列表里确有 `VersionFromManifest 0.0.0.0`）。附带一条：它的 REF 写的是 `Assembly-CSharp 1.4.8315.26675`，在 1.6 上照跑——Unity 按**简单名**绑定，同大版本内的小版本号差异不会炸。

8. **LoadFolders 的共享目录要在版本边界收敛**。本 mod 1.0–1.5 共用 `LegacyAssets`、1.6 切成 `Assets`，边界处换了名，旧版本仍拖 827 KB PNG。这为收录区标准 §6 那条待提炼项提供了反例样本。判断一个 mod 的 LoadFolders 用得好不好，看它"跨版本的共享目录名是否只在一个地方变更"。

9. **机翻痕迹可查、且多语种漏同一批**。翻译文件首行注释会写 `generated by https://www.deepl.com/`。本 mod 4 个语种的覆盖 defName 集合完全一致（同一批机翻再分发），且**都漏了同一批新 Def**——所以"某语种翻译质量如何"和"翻译是否跟上了新功能"是两个独立问题，得分别查。

## 修改建议

> 以下全部**未执行**。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。

| 优先级 | 事项 | 依据 |
|---|---|---|
| **P0** | 实机验证"补丁抹掉 `WaterShallow` 父类 affordances"的疑点 | 最低成本验证：开一个 1.6 存档放到浅水上，看小 pawn 能否正常走过去。若能走通，说明两个前提中至少有一个不成立，疑点作废 |
| **P0** | 给 4 语种补 `sd_bridges_{triple,quad}drawbridge_{up,down}` 的 `.label`/`.description`，并新建 `DefInjected/WorkGiverDef/` 补 WorkGiverDef 的 `label`/`verb`/`gerund` | 已逐文件确认：招牌功能 3/4 格宽吊桥 + Job 层入口在 4 语种里都显示英文 |
| **P1** | 删 `1.0\Assemblies\0Harmony.dll`（113,152 B）与 `ModCheck.dll`（33,280 B） | 7 个版本零引用，省 146 KB，并少一个"全库重复 Harmony"的计数源。**须用户明确同意才动 Mods 目录** |
| **P1** | 给 `sd_bridges_biomes.xml` 的两个 `BiomesCore_*` 目标加前置判断 | 目标在本机 1.6 不存在，是必然失败的补丁操作，会在 `Player.log` 里留噪音 |
| **P2** | 把 12 处 `PatchOperationadd`（小写 a）统一成 `PatchOperationAdd` | 类名匹配大小写敏感性未验证，统一写法消除风险 |
| **P2** | 恢复 `sd_bridges.dll` 的程序集版本号 | 7 版只有 3 个值、末版退化成 `0.0.0.0`，靠程序集版本号定位版本会失灵（`VersionFromManifest` 只补了设置页显示） |

## 未核实项

- **列表字段继承是"整字段替换"还是"父子合并"**。本机 106 个程序集里 `InheritanceResolver` / `ResolveNodes` / `FillInMissingFields` / `DirectlyInheritsFrom` 全部 0 命中（对照 `ParentName`、`PatchOperationFindMod` 命中），未反编译 IL。仅据原版两处 `WaterMoving*` 的设计意图（moving water 不该 Walkable）**推断**为替换，故 P0 那条疑点的两个前提都没坐实。
- **`sd_bridges.Textures` 这个 `[StaticConstructorOnStartup]` 空标记类具体做什么**。C# 的 ASCII 与 UTF-16 两个堆都搜不到 `AssetBundle` / `Mlie_SDBridges` / `LoadFromFile`；方法级枚举显示它无 DeclaredOnly 方法。推测 bundle 由 RimWorld 自己扫描 `AssetBundles/` 加载，该类只负责触发 mod 程序集初始化——未实机验证。
- **12 处 `PatchOperationadd`（小写 a）在游戏里是否真被解析**。RimWorld 的类名匹配是否大小写不敏感未验证。
- **贴图素材的原始作者与授权**。`LICENSE.md` 只有一份 MIT，但贴图沿用 sulusdacors mod，未见单独的素材授权条款。
- **1.6 的实际加载**。`1.6\Assemblies\sd_bridges.dll` 编译时引用 `Assembly-CSharp 1.6.9371.18214`，本机实际是 1.6.9655.19392（同为 1.6，Unity 按简单名绑定应无碍），但未实机验证。
- **`1.5` / `1.6` 的 `sd_bridges_biomes.xml` 历史上服务于哪个版本**。`BiomesCore_*` 前缀在本机 1.6 全无，但无法判断它是"旧 DLC 内容的残留"还是"尚未随 DLC 上线的预留"。
