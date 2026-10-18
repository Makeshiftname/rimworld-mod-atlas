# Fortified Features Framework（`3498575851`）— 分析记录

| | |
|---|---|
| 本记录目录 | `records/3498575851-FortifiedFramework/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\3498575851\` |
| mod 名 | Fortified Features Framework |
| packageId | **`AOBA.Framework`**（唯一一个大写开头的） |
| 作者 | AOBA |
| 工坊 ID | `3498575851`（`PublishedFileId.txt` 恰 10 字节 ✅） |
| 程序集版本 | `1.0.0`，构建 commit `8e46d790f5c5afbd19d3b7838077414b8b193c2c` |
| 许可 | **未声明**——`About.xml` 无 `<license>`、目录内无 LICENSE 文件 |
| 支持版本 | 声明 1.5 / 1.6；**但 1.5 是空壳**（见「它是什么 → 1.5 现状」） |
| 作者生态 | 本库共 **16 个 AOBA 前缀 mod**（`Aoba.*` 13 + `AOBA.Framework` + `AOBA.RedMoyo`） |
| 分析日期 | 2026-10-17 |

> 本 mod **无禁再分发声明**，但**也没有任何许可声明**——
> "没说不许"不等于"可以随便用"，转载前需向作者确认。

**它在你库里的位置**：不是"内容 mod"，是**作者自用生态的公共底座**。
它同时带**框架**（788 个类型 / 65 个 Harmony 补丁 / 11 个自定义 Def 类）
与**示范内容**（72 个 Def：机甲舱、绘画作业、炮塔、自动化工单）。
本库实测有 **3 个 mod 依赖它**，全部同作者。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **166 文件 / 7,437,880 字节（7.09 MB）** |
| 结构 | `About/` + `LoadFolders.xml` + `Languages/` + `Textures/` + **`1.5/`（仅 readme）+ `1.6/`**（**用了 LoadFolders.xml**） |
| 类型 | **框架 + 示范内容混合**（自称"commonly used features"） |
| Def 规模 | 21 个 Defs XML / **72 个顶层 Def**（含 14 个自定义 Def） |
| 主 DLL | `1.6/Assemblies/Fortified.dll`，**671,744 字节 / 788 个类型**，全部在 `Fortified` 命名空间 |
| Harmony 补丁 | **65 个类**（含 4 个方法级） |
| 语言 | **ChineseSimplified(25) + ChineseTraditional(25) + English(27)** ✅ 三语 |
| `modDependencies` | `brrainz.harmony` ✅ 已装（`2009463077`） |
| `loadAfter` | `brrainz.harmony` ✅、`Ludeon.RimWorld`（原版虚拟项）、`CETeam.CombatExtended` ❌ 未装 |
| 条件模块 | `1.6/CE/Assemblies/FortifiedCE.dll`（50,176 B），**由 `IfModActive` 条件加载** |
| Multiplayer 桩 | `0MultiplayerAPI.dll` v0.6.0.0 |
| 自定义着色器 | `1.6/AssetBundles/fortified_shaders_{win,mac,linux}` + `.manifest`，内含 **`Assets/Shaders/FF_StandardPaintable.shader`** |
| 是否自带 `0Harmony.dll` | **否** ✅ |

### 目录字节分布

| 目录 | 文件数 | 字节 | 占比 |
|---|---|---|---|
| `Textures/` | 53 | **5,908,057** | **79.4%** |
| `About/` | 4 | 561,506 | 7.5% |
| `Languages/` | 77 | 218,538 | 2.9% |
| `1.6/` | 30 | 749,531 | 10.1% |
| `1.5/` | 1 | 217 | ~0% |

> **79.4% 的体积是贴图**，且其中 **5,034,376 字节是 `.dds`**——
> 与同目录的 `.png` **同内容重复打包**（26 个 `.dds` + 27 个 `.png`）。

---

## 它是什么

一句话：**AOBA 给自己 16 个 mod 用的公共底座**——把"机甲/自动机兵/载具/无人机/绘画/涂装"
这套玩法所需的功能集中到一个 mod，其余 mod 只写内容。

### 1.5 现状：空壳，作者自己写明了

`About.xml` 声明支持 1.5，但 `1.5/` 目录下**只有一个 `readme.txt`（217 字节）**：

> oh, just mention that this mod in 1.5 doesn't really do anything.
> Not loading it doesn't affect your game, but I know you're here because Game told you this is a dependency.
> :3 __AOBA

即：**它挂在那里只是为了满足"别人声明了依赖"的加载校验**，本体什么都不做。
作者提前想到了这一点并主动说明，态度值得肯定。

### LoadFolders.xml：条件加载的教科书用法

```xml
<loadFolders>
  <v1.5><li>/</li><li>1.5</li></v1.5>
  <v1.6>
    <li>/</li>
    <li>1.6</li>
    <li IfModActive="CETeam.CombatExtended,CETeam.CombatExtended_steam">1.6/CE</li>
  </v1.6>
</loadFolders>
```

`1.6/CE` **只有在 CE 激活时才加载**——这就是为什么 Combat Extended 的集成
（`FortifiedCE.dll`）可以放在同一目录里而不让没装 CE 的人崩溃。

**核验**：`FortifiedCE.dll` 引用 `CombatExtended` 程序集，而本库**未装 CE**，
`GetTypes()` 因此返回 **0 个类型**——这是按设计惰性，不是坏包。

> 这也给本仓库 `AGENTS.md` 里"避免用 LoadFolders.xml"的约定提供了一个**反例样本**：
> 它的版本边界是收敛的（根 + `1.6`），且额外那一条是**条件加载**，不是靠 LoadFolders 做版本分发。
> 收录区 §6 待提炼的那条冲突（"弃用 LoadFolders" vs "看是否在版本边界收敛"）可以拿它当第三个样本。

### 四套子系统（从 11 个自定义 Def 类读出来）

反射 `Fortified.dll` 得到 **11 个 `Verse.Def` 派生类**，每个字段都直接说明子系统职责：

**A. 程序化结构/聚落生成（5 个类，`Fortified.Structures`）**

| 类 | 字段 |
|---|---|
| `FFF_StructureDef` | `size` / `elements` / `tags` / `zoneTags` / `baseWeight` / `frontDist` / `disableSuggestedRoof` |
| `FFF_CompoundStructureDef` | `settlementSize` / `centerStructure` / `peripheralStructures` / `roadConfig` / `defenseConfig` / `avoidWater` / `clearArea` |
| `StructureLayoutDef` | `layouts` / **`terrainGrid` / `foundationGrid` / `underGrid` / `tempGrid` / `roofGrid` / `terrainColorGrid`** / `spawnConduits` / `forceGenerateRoof` / `needRoofClearance` / `randomRotation` / `maxSize` / `modRequirements` |
| `SymbolDef` | `thing` / `terrain` / `stuff` / `rotation` / `color` / `pawnKindDef` / `faction` / `thingSetMakerDef` / `fuelPercent` / `powerPercent` / `crateStackMultiplier` / `chanceToContainPawn` / `plantGrowth` |
| `FFF_SettlementDef` | `tags` / `baseWeight` |

> 这是**一整套网格化的地图布局系统**（地形/地基/下层/临时/屋顶/地形色 六个独立网格），
> 与 Odyssey 的 `StructureLayoutDef` 思路相似但是作者自研的独立实现。
> 对应的入口 Def 是 `FFF_SpawnWorldObjects`（`WorldGenStepDef`）与
> `FFF_PrefabGen` / `FFF_AddStartingStructure`（`ScenPartDef`）。

**B. 阵营涂装 / 迷彩系统（4 个类）**

| 类 | 字段 |
|---|---|
| `FFF_CamoDef` | `texPath`（随包 6 张：Army / ArmyDark / Digital / DigitalDark / Hex / Marine） |
| `FFF_OverlayDef` | `texPath` / `multiplyBase` / `applicablePawnKinds` |
| `FFF_PaintDef` | `graphicPath` / `maskPath` |
| `FFF_FactionPaintDef` | `faction` / `pawnKind` / `options` / `color1..3` / `camoDef` / `brightness` / `overlayDef` |

**这一整套靠自定义着色器 `FF_StandardPaintable.shader` 实现**——
通过 AssetBundle 加载，三个平台各一份（win/mac/linux）。相关 Def：`FFF_Camouflage`（Hediff）、
`FFF_Painting` 作业组、`StatDef` 里没有专用项。
配套贴图 `Textures/Things/ExitFacility.*`、`Textures/Things/Building/Linked/Wall/Wall_Atlas_Concrete.*`
都是可涂装面。

**C. 重型装备准入（1 个类）**

`HeavyEquippableDef`：`EquippableBaseBodySize` / `EquippableByRace` / `EquippableWithApparel` /
`EquippableWithHediff` / `EquippableWithGene`

= 按**体型**决定能否装备，并允许用**服装 / 健康状况 / 基因**（Biotech）做加减条件。
随包 8 条：`MountedWeapon`、`AverageHumanCanUse`、`LightAutomatroid` … `UltraHeavyAutomatroid`。
配套 3 个 StatDef：`FFF_MassCarryCapacity`、`FFF_UsableWeapons`、`FFF_HeavyGears`。

**D. 空中支援（1 个类）**

`AirSupportDef`：`comps` / `tempOriginCache` / `originOverridedCache`

### 72 个 Def 的类型分布

| 类型 | 数量 | 举例 |
|---|---|---|
| `JobDef` | **17** | `FFF_DoAutonomousBill`、`FFF_Modification`、`FFF_HackDeactivatedMech`、`FFF_ResurrectMech`、`FFF_SwitchAmmo`、`FFF_PaintMech`、`FFF_HackMechCapsule` |
| `ThingDef` | 11 | `FFF_MechCapsule_Small/Medium/Large/Huge/Colossal`、`FFF_MinifiedTurret`(+2 抽象基)、`FFF_FlareShell` |
| `Fortified.HeavyEquippableDef` | 8 | 见上 |
| `Fortified.FFF_CamoDef` | 6 | 见上 |
| `FleckDef` | 5 | `FFF_Smoke`、`FFF_Fleck_RocketFlame`、`FFF_Fleck_DeflectShell` |
| `EffecterDef` | 4 | `FFF_Effecter_Penetrate_Sabot`、`FFF_LaunchDust_Grenade`、`FFF_Sustainer_JetTrail` |
| `ScenPartDef` | 4 | `FFF_PrefabGen`、`FFF_AddStartingStructure`、`FFF_PlayerPawnsArriveGravship` |
| `StatDef` | 3 | 见上 |
| `WorkGiverDef` | 3 | `FFF_DoAutonomousBill`、`FFF_PaintMechWorkGiver`、`FFF_PaintBuildingWorkGiver` |
| `ConceptDef` | 2 | `FFF_EnvironmentalBill`、`FFF_MechTrade` |
| `DutyDef` | 2 | `FFF_DefendRoomA`、`FFF_ScoutAdvanceA`（Royalty） |
| `ThinkTreeDef` | 2 | `FFF_DroneMain`、`FFF_DroneConstant` |
| 其余 6 类各 1 | 6 | `IncidentDef` / `HediffDef` / `WorldGenStepDef` / `DamageDef` / `DesignationCategoryDef` / `DebugDefs` |

### 一个"有代码有翻译、但内容被注释掉"的功能

`1.6/Defs/TestDefs.xml`（3,592 B）**整个文件被 `<!-- -->` 包住**，0 个生效 Def。
里面是完整的 **Ammo Switch（弹药切换）** 示例：
`Gun_AssaultRifle_AmmoSwitch` + `CompProperties_AmmoSwitch` + `Verb_LaunchProjectile_AmmoSwitch`
+ 抽象基 `FFF_BaseAmmoSwitchBullet` 与两颗子弹 `FFF_Bullet_Rifle` / `FFF_Bullet_Shotgun`。

对应代码在 DLL 里存在（`CompProperties_AmmoSwitch`、`CompProperties_SwitchableAmmo`），
英文翻译 `Keyed/AmmoSwitch.xml`（272 B）也在——**只有 Def 被注释了**。
所以 `TestDefs.xml` 的准确读法是"**示例/待启用模板**"，不是生效内容。

---

## 65 个 Harmony 补丁（1.6 反射实测，按目标归类）

### 机甲 / 自动机兵（最重的一块）

| 补丁 | 目标 |
|---|---|
| `Patch_CanControlMechs` | `Pawn_MechanitorTracker.CanControlMechs` |
| `Patch_MechanitorUtility_CanDraftMech` / `Patch_CanDraftMech` | `MechanitorUtility.CanDraftMech`（两处，一处带优先级 0） |
| `Patch_InMechanitorCommandRange` | `MechanitorUtility.InMechanitorCommandRange` |
| `Patch_IsColonyMechPlayerControlled` / `Patch_IsColonistPlayerControlled` | `Pawn.IsColonyMechPlayerControlled` / `IsColonistPlayerControlled` |
| `Patch_MechInteracte` | `PawnComponentsUtility.AddComponentsForSpawn` |
| `Patch_IsMissingWeapon` / `Patch_MechRepairUtility_GenerateWeapon` | `MechRepairUtility.IsMissingWeapon` / `GenerateWeapon` |
| `Patch_CompOverseerSubject_State` | `CompOverseerSubject.State` |
| `Patch_Bill_ProductionMech_CreateProducts` | `Bill_ProductionMech.CreateProducts` |
| `Patch_PawnWeaponGenerator_TryGenerateWeaponFor` | `PawnWeaponGenerator.TryGenerateWeaponFor` |
| `Patch_PawnGenerator_GeneratePawn` ×2 | `PawnGenerator.GeneratePawn`（**两个不同重载**，含 `PlanetTile` 可空参数） |

### 悬浮 / 浮空单位（"Floating"系列）

`Patch_CostToMoveIntoCell_Floating`（`AI.Pawn_PathFollower.CostToMoveIntoCell`）、
`Patch_Pawn_GetPathContext_Floating`、`Patch_PathGrid_CalculatedCostAt_Floating`（方法级）
—— 让悬浮单位按空中移动逻辑寻路。

### 渲染 / 绘制节点

`Patch_PawnRenderNodeWorker_Carried`（`PostDraw`）+ `…_CanDrawNow`、
`Patch_PawnRenderNodeWorker_Apparel_Body_CanDrawNow` + `…_Head_CanDrawNow`、
`PawnRenderTree_SetupDynamicNodes_Patch`、`PawnRenderTree_ShouldAddNodeToTree_Patch`、
`Patch_Blueprint_Graphic`、`Patch_Thing_FlammableNow`。

### 炮塔与建筑

`Patch_BuildingTurretGun_GetGizmos`、`Patch_CanSetForcedTarget`、`Patch_ThreatDisabled`
（`Building_Turret`）、`Patch_Verb_Shoot_Building_TurretCapacity`、
`Patch_Verb_Shoot_CompCastPushHeat`（两处都在 `Verb_Shoot.TryCastShot`，优先级 0）。

### 生物 / 基因 / 健康

`Patch_AddAndRemoveDynamicComponents`（`PawnComponentsUtility`）、
`Patch_Biocode`（`CompBiocodable.CodeFor`）、`Patch_CanBeInfected`（`MetalhorrorUtility`）、
`Patch_DiseaseContractChanceFactor`（`ImmunityHandler`，**带 3 个 ArgumentType 精确定位重载**）、
`Patch_PregnancyUtility_ApplyBirthOutcome`、`Patch_Pawn_HealthTracker` 类（`Patch_SkillRecord` 等）。

### 界面 / 建筑菜单

`Patch_MainTabWindow_Architect_CacheDesPanels`、`Patch_MainTabWindow_Architect_PreOpen`、
`Patch_ITab_Pawn_Character_IsVisible`、`Patch_Pawn_GetGizmos`（`Pawn_InventoryTracker`）、
`Patch_PawnEquipmentTracker_GetGizmos`、`Patch_CanDropWeapon` + `_Sandy_Detailed_RPG_Inventory`（方法级）。

### 任务 / 事件 / 其他

`Patch_SiegeAsBuilder`（`LordToil_Siege.SetAsBuilder`）、`Patch_IncidentWorkerRaid_TryExecuteWorker`、
`Patch_IncidentWork` + `Patch_IncidentWorkerForDevice`（`IncidentWorker.TryExecute`，两处）、
`Patch_Replace`（`GenSpawn.Spawn`，**7 个参数全指定**）、`Patch_BossgroupEverCallable`、
`MakeNewBill_PostFix`（`BillUtility.MakeNewBill`）、`Patch_RecipeDef_SpecialDisplayStats`、
`Patch_StatWorker_IsDisabledFor`、`Patch_CombinedDisabledWorkTags`、`Patch_ShowDraftGizmo`
+ `Patch_Pawn_DraftController_ShowDraftGizmo`（**两处打同一方法**）、`Patch_FFF_Pawn_ExitMap`、
`Patch_Faction_NaturalGoodwill`、`Patch_Pawn_StyleTracker_CanDesireLookChange`、
`Patch_Pawn_DropAndForbidEverything`、`Patch_GeneratePawnTitle`、`Harmony_Painting`（方法级）、
`ApparelPatch`（方法级）。

> **值得单列的两类重复补丁**：
> `Patch_MechanitorUtility_CanDraftMech` 与 `Patch_CanDraftMech` 都打 `MechanitorUtility.CanDraftMech`；
> `Patch_ShowDraftGizmo` 与 `Patch_Pawn_DraftController_ShowDraftGizmo` 都打 `Pawn_DraftController.ShowDraftGizmo`。
> 有意为之还是历史遗留，从二进制无从判断——记录为事实，不下结论。

> **CE 兼容是双轨的**：除条件模块 `FortifiedCE.dll` 外，主 DLL 里还有一个
> `CombatExtended_Utility_Loadouts_IsItemMechanoidWeapon` 补丁类。
> 本库未装 CE，这两处应当都处于未激活状态（**未实机验证**）。

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse` + `ReadAllBytes().Length` |
| 依赖图 | `[xml]` 解析全库 `About/About.xml`，取 `ModMetaData` **直接子元素** `<packageId>`，检索正文含 `AOBA.Framework` 的节点 |
| Def 全量 | 遍历 `1.6/Defs/**/*.xml`，对每个顶层元素**同时取 `defName` 属性与 `<defName>` 子元素** |
| 自定义 Def 字段 | `GetTypes()` + 读 `BaseType` 与 `GetFields(Public,Instance)`，**只取 `DeclaringType == 该类`** 的自有字段 |
| 补丁目标 | 类级 `GetCustomAttributesData()` 的 `HarmonyPatch` + 方法级 `GetMembers(...).GetCustomAttributesData()` |
| 构建来源 | `AssemblyInformationalVersion`（SDK 写入的 `<版本>+<commit>`） |
| 翻译覆盖 | 按**相对路径**做集合差，而非按词条数 |
| 贴图引用 | 正则抽 `<texPath>` 与 `Textures/` 实际文件对照 |
| 全库副本 | `Get-ChildItem -Recurse -Filter 0MultiplayerAPI.dll` + 逐份 `GetAssemblyName` + `Get-FileHash` |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| packageId 依赖扫描 | `brrainz.harmony` 必须命中 | ✅ |
| defName 提取 | 必须取到 `FFF_MechCapsule_*` 这类**子元素** defName | ✅ |
| `GetTypes()` | 必须存在 `FFF_CamoDef` | ✅（详见纠错 2） |
| 许可证分类 | — | 不适用（**无任何许可文件**） |
| 翻译集合差 | 三语种都必须报出缺失项而非空 | ✅ 各报 3 项 |
| Multiplayer 副本扫描 | 至少应找到 ASF 与本 mod 两份 | ✅ 实得 **81 份** |

### ③ 自查纠错（本轮我的工具错了 2 次）

**1. `defName` 只查属性 → 把 72 个 Def 里绝大多数报成"无 defName"。**
RimWorld 的 XML 里 `defName` 绝大多数是**子元素**（`<defName>FFF_MechCapsule_Large</defName>`），
只有抽象父类用 `Name="..."` **属性**。我第一版脚本只调 `GetAttribute('defName')`，
于是输出里 20 个文件全是 `<无 defName>`——差一步就写成"这个 mod 的 Def 基本没有命名"。
**是靠阳性对照发现的**：抽象类那几个明明取到了 `Name`，与"多数没有 defName"矛盾。
改成"属性 + 子元素都试"后才拿到完整的 72 条清单。

**2. 漏预载 `0Harmony` 导致 `GetTypes()` 部分失败，正控直接 FAIL。**
第一次枚举自定义 Def 时得到 **0 个 Def 派生类**，同时阳性对照 `FFF_CamoDef` 也没找到。
按标准这种"0 不可信"，于是回头核对 `GetReferencedAssemblies()` 的完整清单，
发现少预载了 `0Harmony`（以及 `System.Xml`）。**补齐后 `GetTypes()` 完整成功：788 个类型全出**，
`FFF_CamoDef` 命中，Def 派生类 11 个。
→ 枚举第三方 DLL 前，**按 `GetReferencedAssemblies()` 逐个预载**，不要凭印象挑几个。

### ④ 未核实

- **`DMS_LogisticTerminal` 那批贴图（18 文件 / 3,182,846 字节）的原始作者未知**。
  本 mod 自己的 72 个 Def 里**没有任何一处引用它们**；同名文件也存在于
  `3121742525`（`Aoba.DeadManSwitch.Core`）。即"框架与自家内容 mod 重复打包同一批素材"这一点已确认，
  但它最初来自哪个 mod，本机全库文本扫描太慢（两次尝试均超时），**未查清**。
- **两个重复补丁是有意还是遗留**：只能从二进制看到"同一方法被打两次"，语义判断需读源码（未随包提供）。
- **CE 兼容在未装 CE 时是否真的完全惰性**：未实机验证。
- **`FF_StandardPaintable.shader` 的内容**：本机原版素材被剥掉，且着色器在二进制 AssetBundle 里，未反编译。

---

## 上下游与冲突面

### 谁依赖它

本库实测 **3 个 mod**，全部同作者 AOBA：

| packageId | 工坊目录 | 声明方式 |
|---|---|---|
| `Aoba.Fortress.Neolithic` | 2385960678 | `loadAfter` |
| `Aoba.Fortress.Industrial` | 2561619583 | `loadAfter` + **`modDependenciesByVersion`** |
| `Aoba.DeadManSwitch.Core` | 3121742525 | `loadAfter` + **`modDependenciesByVersion`** |

> 出现了 `modDependenciesByVersion` 这个元素——不是常见的 `modDependencies`。
> 它是"按游戏版本分别声明依赖"的写法，本记录首次见到，语义未深究。

依赖面比 Adaptive Storage Framework（30+ 个外部依赖）窄得多，
**框架属性来自生态规模而非外部采用度**——这是它与 ASF 的本质区别。

### 作者生态：本库共 16 个 AOBA mod

`Aoba.CargoContainer`(+`.Waste`)、`Aoba.DeadManSwitch.{Core,AncientCorps,MobileDragoon,Motorized,Synthetic}`、
`Aoba.Exosuit.Framework`、`Aoba.Fortress.{Frontier,Industrial,Industrial.Citadel,Industrial.Concrete,Medieval,Neolithic}`、
`AOBA.Framework`、`AOBA.RedMoyo`。

### ⚠️ 全库级发现：`0MultiplayerAPI.dll` 有 **81 份副本**

这是本轮最重要的库级发现，**性质与已知的 85 个自带 `0Harmony.dll` 副本完全同类**：

| 指标 | 值 |
|---|---|
| 副本总数 | **81** |
| 不同 SHA256 | **9 种** |
| 不同程序集版本 | **5 个**：v0.1.0.0、v0.2.0.0、v0.3.0.0、v0.5.0.0、v0.6.0.0（**v0.4 缺失**） |
| 覆盖 mod 目录 | 至少 **25 个** mod |
| 同版本不同构建 | 有：v0.1.0.0 存在 **3 种不同哈希**（`FEB8BC28F239` / `0916B1FEE15C` / `56ED25C95249`） |

**决定性证据——已安装的两个 mod 绑定到不同版本**：

| mod | 自身携带的桩 | 主 DLL 绑定的 `0MultiplayerAPI` 版本 |
|---|---|---|
| `3498575851`（本 mod Fortified） | v0.6.0.0 / `863766DF5FD2` | **0.6.0.0** |
| `3033901359`（ASF AdaptiveStorageFramework） | v0.5.0.0 / `4689E799C50D` | **0.5.0.0** |
| `3352894993`（Aoba.Exosuit） | v0.6.0.0 / `863766DF5FD2` | **0.6.0.0** |

即：**两个都装着、且绑定的桩版本不同**。
.NET 按程序集身份（名+版本）加载，两份 `0MultiplayerAPI` 会被当作**不同程序集**各自加载，
于是 `Multiplayer.API.*` 的类型身份在两边不一致——跨 mod 的类型判定/转换存在结构性风险。

⚠️ **我没有实机运行验证这是不是已经在出问题**，只确认了结构性事实。
本轮也**未做任何清理**（用户未授权）。

> 附带一处小事：`dreadbed-a-fleshbeast-tentacle-seedbed-mod-master\1.6\Source\DreadmeldSeedbed\bin\Debug\`
> 里也躺着一份 `0MultiplayerAPI.dll`——**构建输出目录被整个打进了 mod 包**。
> RimWorld 不会加载它，但属于源码树泄漏。

### 体积冗余

| 项 | 字节 | 说明 |
|---|---|---|
| `Textures/` 全目录 | 5,908,057（**79.4%**） | 而这个框架自己的 Def 只引用其中 7 张 png |
| 其中 `.dds` | **5,034,376** | 26 个 `.dds` 与 27 个 `.png` **同内容重复打包** |
| `DMS_LogisticTerminal/` | 3,182,846 | 18 文件，本 mod 无引用，**在 `Aoba.DeadManSwitch.Core` 重复存在** |
| `Textures/UI/` | 434,452 | 18 文件（图标），本 mod 无引用，留给下游 |
| `Textures/Patterns/` | 1,701,910 | 11 文件，**这个是本 mod 自己用的**（6 张迷彩） |

即：**约 5.03 MB（占全 mod 67.6%）是 `.dds`/`.png` 双格式重复**。

---

## 可复用结论

1. **`IfModActive` 条件加载是"把可选依赖放进同一个 mod"的标准解法。**
   本 mod 把 Combat Extended 集成放在 `1.6/CE/`，靠 `LoadFolders.xml` 的
   `IfModActive="CETeam.CombatExtended,CETeam.CombatExtended_steam"` 决定是否加载。
   未装 CE 的人连目录都不会被扫——**零成本、零风险**。
   对照：写成 `<modDependencies>` 就会变成硬依赖，直接挡掉所有没装 CE 的用户。

2. **LoadFolders.xml 不等于"版本分发"。看它是否在版本边界收敛。**
   本 mod 的 loadFolders 是 `/` + `1.6`（收敛）再加一条**条件目录**，
   和"用 LoadFolders 塞 1.3/1.4/1.5 各自资源"（不收敛）不是一回事。
   本仓库 `AGENTS.md` 的"避免用 LoadFolders"与收录区 Harmony 那条的冲突，可以拿它当判据样本。

3. **用"声明支持但不实现"来满足依赖，比让下游报错强得多。**
   本 mod 的 1.5 目录只放一个 readme 说明"这里什么都不做"，
   同时让 1.5 的下游 mod 不会因为"依赖缺失"被游戏拒绝加载。
   这是**依赖契约与功能实现可以分离**的实例。

4. **自定义着色器要走 AssetBundle，且要为三个平台各打一份。**
   `AssetBundles/fortified_shaders_{win,mac,linux}` + 三个 `.manifest`
   （含 `AssetFileHash` / `TypeTreeHash`），manifest 里直接写明资产路径
   `Assets/Shaders/FF_StandardPaintable.shader`。
   **manifest 的 `Assets:` 字段是"这个包到底装了什么"的一手证据**，比猜可靠。

5. **判断"这个 mod 是不是框架"，看有没有自定义 `Verse.Def` 子类。**
   本 mod 11 个自定义 Def 类（结构生成 5 + 涂装 4 + 装备准入 1 + 空中支援 1）
   直接暴露了子系统边界；比读几千行补丁代码快得多。
   其中 `StructureLayoutDef` 的**六个独立网格**（terrain/foundation/under/temp/roof/terrainColor）
   是"程序化地图布局"的典型数据结构。

6. **第三方 DLL 里的功能可能有"代码在、内容被注释掉"的状态。**
   本 mod 的 `TestDefs.xml` 整个被 `<!-- -->` 包住，但对应的
   `CompProperties_AmmoSwitch` / `Verb_LaunchProjectile_AmmoSwitch` 类和英文翻译都在。
   看到 `Test*` 前缀的 Defs 文件要先看有没有被注释——**否则会把"未启用的模板"当成"已生效的内容"**。

7. **"有翻译但没内容"和"有内容但没翻译"是两种不同的缺口，排查时要分开数。**
   本 mod 简中/繁中都缺 `Keyed/AmmoSwitch.xml`（因为 AmmoSwitch 内容被注释掉了），
   简中还缺 `DefInjected/ThingDef/MechCapsule.xml`，繁中缺 `Keyed/FFF_Painting.xml`。
   **按文件相对路径做集合差**才能看清，按词条总数只会得到一个笼统的百分比。

8. **依赖副本问题不止 `0Harmony.dll` 一个。**
   `0MultiplayerAPI.dll` 在本库有 **81 份 / 9 种构建 / 5 个版本**，
   且已安装的 mod 中存在**绑定不同版本**的组合。
   判断这类问题的正确方法是：**读每个主 DLL 的 `GetReferencedAssemblies()` 看它绑定的版本**，
   而不是只看文件名和体积。

9. **`.dds` 与 `.png` 双格式同时打包是常见冗余。**
   本 mod 5.03 MB（占 67.6%）是同内容两种格式。
   RimWorld 两种都能读（策划工具用 `.dds`），但发布时通常只需一种。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **全库 `0MultiplayerAPI.dll` 副本治理** | 81 份 / 9 种构建 / 5 个版本，且已有装好的 mod 绑定不同版本（0.5 vs 0.6）。需先确定保留哪一份，**必须用户授权后再动** |
| 高 | **补许可声明** | `About.xml` 无 `<license>`、目录无 LICENSE。"未声明"不等于"可自由转载" |
| 中 | **`.dds` 去重** | 5.03 MB 同内容双格式，可省约一半贴图体积 |
| 中 | `DMS_LogisticTerminal` 素材定位 | 本 mod 无引用、且在 `Aoba.DeadManSwitch.Core` 重复存在；原始作者待查，确认后再决定是否移除 |
| 低 | `TestDefs.xml` | 建议移到 `Docs/` 或改名标注为示例，避免被当成生效内容 |
| 低 | 两处重复补丁 | `CanDraftMech` 与 `ShowDraftGizmo` 各被打两次，读源码确认是否有意 |
| 低 | CE 双轨兼容 | 主 DLL 与 `1.6/CE` 都有 CE 适配，可考虑收敛到一处 |

---

*2026-10-17 收录。已顺藤摸瓜查依赖图（3 个依赖方 + 16 个同作者 mod）、条件模块、
全库 Multiplayer 桩副本（81 份）、贴图冗余与翻译覆盖。
本轮工具自查纠错 2 次（defName 只查属性；漏预载 0Harmony 致 GetTypes 部分失败），均已留档。*
