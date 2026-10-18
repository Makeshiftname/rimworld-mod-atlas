# Adaptive Storage Framework（`3033901359`）— 分析记录

| | |
|---|---|
| 本记录目录 | `records/3033901359-AdaptiveStorage/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\3033901359\` |
| mod 名 | Adaptive Storage Framework |
| packageId | `adaptive.storage.framework` |
| 作者 | Soul、Phaneron、**bradson**（主开发） |
| 工坊 ID | `3033901359`（`PublishedFileId.txt` 恰 10 字节 ✅） |
| 程序集版本 | `1.2.4`，三版本目录同 commit `40787e9e0746aab12c0bcfb376f67bdeaffd6bdd` |
| 许可 | **混合许可**，见 §授权（不是单一 MIT） |
| 支持版本 | 1.4 / 1.5 / 1.6 |
| 源码 | https://github.com/bbradson/Adaptive-Storage-Framework |
| 分析日期 | 2026-10-17 |

> 本 mod **无禁再分发声明**，MIT 主体可自由取用。
> 但目录内混有 **MPL-2.0** 与 **.NET Foundation** 许可的源码文件，取用时须按 §授权 分档处理。

**它在你库里的位置**：这是本库收录记录里**第一个真正的"地基型" mod**（④ 档）。
它自己不产出任何可玩内容——`Textures/` 里**只有一张图标**，一个建筑/物品都没有。
它的价值完全在于**被别人的 mod 依赖**：本库实测 **30+ 个 mod 在 `About.xml` 里声明依赖它**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **289 文件 / 6,474,153 字节（6.17 MB）** |
| 结构 | `About/` + 顶层 `1.4/ 1.5/ 1.6/` + `Defs/` `Patches/` `Languages/` `Docs/` `Source/` `Textures/`（**无 LoadFolders.xml**） |
| 类型 | **框架 / 库**（基础设施层），无内容产出 |
| 每个版本目录 | **21 文件 = 10 个 DLL + 10 个 PDB** |
| 主 DLL | `AdaptiveStorageFramework.dll` v1.2.4.0，**542,208 字节 / 362 个类型** |
| 语言 | English(**22 词条**) / French(**6 词条**)，**无中文** |
| `modDependencies` | `brrainz.harmony` ✅ 已装（`2009463077`） |
| `loadBefore` | `OskarPotocki.VanillaFactionsExpanded.Core` ✅ 已装（`2023507013`） |
| `loadAfter` | `brrainz.harmony` ✅、`Ludeon.RimWorld`（原版虚拟项）、`rwmt.Multiplayer` ❌ 未装 |
| Harmony 补丁 | **类级 32 个 + 方法级 4 个 = 36 个**（1.6 版反射实测） |
| 自带贴图 | **0 张**（`Textures/` 仅 `ModIcon.dds` + `.png`） |
| 是否自带 `0Harmony.dll` | **否** ✅ |

### 目录字节分布

| 目录 | 文件数 | 字节 | 说明 |
|---|---|---|---|
| `About/` | 6 | 2,045,218 | `Preview.dds`(1.23 MB) + `Preview.png`(807 KB) **同图两种格式并存** |
| `1.4/ 1.5/ 1.6/` | 各 21 | 各约 1.02 MB | 每版 10 DLL + 10 PDB |
| `Source/` | 186 | 1,263,303 | **168 个 `.cs`** + 6 个 `.csproj` + `.sln` + props |
| `Docs/` | 17 | 38,484 | AsciiDoc 文档（Antora 站结构） |
| `Patches/` | 4 | 5,844 | XML patch |
| `Defs/` | 3 | 5,492 | **仅 2 个抽象 ThingDef** + 样式 + Minified |
| `Languages/` | 2 | 4,207 | 英/法 |
| `Textures/` | 2 | 6,888 | 仅图标 |

---

## 它是什么

一句话：**给"深存储/货架"类 mod 提供一套可配置的底层渲染与功能框架**——
一个建筑把 `ParentName` 指向它的抽象 ThingDef，就自动获得"按内容换贴图、逐格摆放物品、
自定义堆叠方式、可调容量/温度"等能力。

### 入口只有两个抽象 ThingDef

`Defs/ThingDefBase.xml` 只定义两个**抽象**父类：

| defName | 父类 | 关键默认值 |
|---|---|---|
| `AdaptiveStorageBase` | `BuildingBase` | `thingClass=AdaptiveStorage.ThingClass`、`drawerType=MapMeshAndRealTime`、`designationCategory=ASFstorage`、`fillPercent=0.4`、`passability=PassThroughOnly`、`inspectorTabs=[ITab_Storage]`、`ignoreStoredThingsBeauty=true` |
| `AdaptiveStorageMinifiableBase` | `AdaptiveStorageBase` | 额外 `minifiedDef=MinifiedThing`、`thingCategories=[BuildingsFurniture]` |

`drawerType=MapMeshAndRealTime` 是整个框架的技术枢纽：
**它把建筑的绘制交给实时渲染层**，从而实现"一格多物品、逐个偏移/缩放/旋转"。
`fillPercent=0.4` 则说明每个格子被切成**子格**布局，物品落在子格上而非整格。

### GraphicsDef：视觉引擎（文档入口）

一个建筑可挂 1 个或多个 `GraphicsDef`，**按内容动态选贴图**：

- `targetDef` / `targetDefs` 绑定建筑（也可用 `Extension.graphics` 反向指定）
- `graphics` / `graphicDatas` 定义贴图，`minimumStackCount` 决定"堆到几个才换图"
- `allowedFilter` / `forbiddenFilter` + `allowedRequirement`
  （`Any / All / Majority / Minority / MajorityOrEqual / MinorityOrEqual / Equal / None / AnyNot / Always / Never`）
  决定这个 GraphicsDef 当前是否可用
- `minimumThingCount` / `minimumAllowedThingCount` / `maximumThingCount` 控制生效区间
- `randomSelectionWeight` 用于**地图生成时**按权重随机挑一个（**6 轮筛选**：先正权重、再反号负权重、再 0、再反向、再 0）
- `stuffFilter` / `buildingFilter`（品质区间）进一步按建材与品质选图
- `useDominantContentColor` / `colorOneSource` / `colorTwoSource`：**用内容物的主色替换贴图颜色**（只认物品自己声明的颜色，不做像素统计）

`itemGraphics` 是**逐子格**的摆放表：`columns` → `c0`/`c1`… → `rows` → `r0`/`r1`…
每格可独立设 `visible`、`drawShadow`、`drawScale`、`rotation`、`stackRotation`、`maxDrawSize`、
`drawOffset`（含东南西北分向偏移）、`stackBehaviour`。

**`stackBehaviour` 四种堆叠方式**是它最实用的部分：

| 值 | 行为 |
|---|---|
| `Default` | 同 def 斜向堆叠 |
| `Circle` | 不同 def 沿圆周排布 |
| `Stack` | 按 `stackOffset`（默认 `(0.11, 0.004054054, 0.24)`）逐层叠 |
| `Weapons` | 武器横排、交替高度 |

### Extension：功能扩展（DefModExtension）

挂在 ThingDef 的 `modExtensions` 上，**全部字段可选**：

- `lockStorageSettingsToStuff` — 用建材替换 `fixedStorageSettings`（做"木架只能放木头"这类限制）
- `maxItemsPerCellByQuality` — **按品质覆盖 `maxItemsInCell`**（ awful 1 → legendary 7）
- `itemStatFactors` / `itemStatOffsets` / `…ByQuality` — 对**格内物品**加 stat 系数/偏移
  （前提：目标 `StatDef` 里必须有 `AdaptiveStorage.StatPart`，通常要 xpath 补）
- `temperature` — **制冷/加热**：`coolingOffset` / `heatingOffset` / `coolingMin` / `heatingMax`，
  自动识别 `CompPowerTrader` / `CompFlickable` / `CompRefuelable` 来决定要不要通电/开关/燃料
- `labelFormat` — `StuffAsNoun`（`Wood pile` 而非 `Wooden pile`）/ `NoStuff`

### 面向玩家的可见改动

- 建筑多一个 **Contents ITab**（`ITab_Storage`），以及**存储组**的 Group ITab
  （`AddITabToLegacyStorages` / `AddITabToStockpileZones` 打在 `Thing.GetInspectTabs` 与 `Zone_Stockpile.GetInspectTabs`）
- 选择行为增强：`PreventSelectionInRect`、`PreventSelectionUnderMouse`、`AdjustSelectionBracketPosition`、
  `AutomaticallyOpenTab`、`CacheZoomAndMousePosition`
- 兼容老存储：把原版 `Building_Storage` 的检视字符串替换掉（`ReplaceLegacyStorageInspectString`）、
  隐藏原版存储 gizmo（`HideStorageGizmos`）、隐藏存物的标签（`HideStoredThingLabels`）
- 神模式下额外出现开发者按钮（`GodModeGizmos`），可现场调 stat——**这些改动不存档**
- 统计项显示：`ThingDef.SpecialDisplayStats` 上挂 stat part（`ThingDefStatDrawEntries`）
- 存档 stat 调优走 **[RIMMSqol]**，框架本身不自带建筑设置菜单

### 存档兼容（`SaveGameCompatibility.dll`，独立程序集）

两个 Harmony 点，其中一个是 **Transpiler**：

- `Verse.BackCompatibility.GetBackCompatibleType` — 跨游戏版本读取旧存档时**重映射类型名**
- `Verse.Thing.ExposeData` 的 **Transpiler + Prefix** — 存档写入/读取时改写 defName、
  建材（`TryGetNewDef` / `TryGetNewStuff` / `TryGetNewType`）

> 这解决的是 ④ 档框架的经典难题：**下游 mod 改了 defName，上游框架必须在读旧档时兜住**。

---

## 36 个 Harmony 补丁（1.6 反射实测，按职责归类）

### A. 渲染与网格（框架本体）

| 补丁 | 目标 | 作用 |
|---|---|---|
| `RegisteredAtThingGridEvent` | `ThingGrid.RegisterInCell` | 登记子格占用 |
| `DeregisteredAtThingGridEvent` | `ThingGrid.DeregisterInCell` | 注销 |
| `HideStoredThingsFromSectionLayerAndOverlayDrawer` | （类级 + 方法级） | 让存物**不参与**地板 section layer 与 overlay |
| `UpdateInvalidHaulablesAndMergeables` | `FilthMonitor.FilthMonitorTick` | 清理失效的可搬运/可合并标记 |

### B. 搬运与容量（性能主张的落点）

| 补丁 | 目标 |
|---|---|
| `StorageLimit` | `GridsUtility.GetMaxItemsAllowedInCell` |
| `PreventStorageLookupFaster` | `StoreUtility.TryFindBestBetterStoreCellForWorker`（**方法级**） |
| `FixMissingValidStackDestinationCheck` | `StoreUtility.NoStorageBlockersIn`（**方法级**） |
| `NotifyItemStackChanged` | `ListerMergeables.Notify_ThingStackChanged` |
| `EnablePackingOnMinify` | `MinifyUtility.MakeMinified` |
| `AdjustThingTemperature` | `Thing.get_AmbientTemperature`（优先级参数） |

### C. UI 与选择

`AddITabToLegacyStorages`、`AddITabToStockpileZones`、`AdjustSelectionBracketPosition`、
`AutomaticallyOpenTab`、`CacheZoomAndMousePosition`、`PreventSelectionInRect`、
`PreventSelectionUnderMouse`、`HideStorageGizmos`、`HideStoredThingLabels`、
`ReplaceLegacyStorageInspectString`、`ThingDefStatDrawEntries`、`StoreUtilityPatches`。

### D. 原版缺陷修补

| 补丁 | 目标 | 作用 |
|---|---|---|
| `FixVanillaVegetarianFilter` | `SpecialThingFilterWorker_Vegetarian.Matches` | 修原版素食过滤器 |
| `ImprovedConfigErrors` | `ThingDef.ConfigErrors` | 更好的配置报错 |
| `RemoveInvalidDefsOnStorageSettingsLoading` | `ThingFilter.ExposeData` | 加载设置时剔除失效 Def |

### E. 存档与 XML（分布在独立程序集里）

| 程序集 | 补丁 | 目标 |
|---|---|---|
| `SaveGameCompatibility.dll` | `BackCompatibilityPatch` / `ExposeDataPatch` | `BackCompatibility.GetBackCompatibleType` / `Thing.ExposeData` |
| `AdaptiveStorageFramework.dll` | `SaveGameCompatibility` | 同上（主程序集另有一份） |
| `PostInheritanceOperation.dll` | `XmlInheritanceResolvePostfix` | **`LoadedModManager.ParseAndProcessXML`（Transpiler）** |
| `DefNameLink.dll` | `DefDatabaseInsertion`（+2 个方法级） | cross-ref 加载与 Def 生成 |

> `XmlInheritanceResolvePostfix` 值得单列：它**给 XML 继承解析过程本身打 Transpiler**，
> 用来挂后继承操作（`PostInheritanceOperation.PatchQueue`）。这是"不改游戏、只改数据管线"的漂亮手法。
>
> 另注意 `BackCompatibility.GetBackCompatibleType` **被两个程序集同时打**——主程序集与
> `SaveGameCompatibility.dll` 各一份。这种重叠在本库并不少见，属于需要盯的重复补丁面。

### F. 可选依赖（`SaveOurShip2`）

`Source/AdaptiveStorage/ModCompatibility/` 下有 8 个文件点名兼容的 mod：
`ActiveMods` / `LWM` / `Multiplayer` / `PerformanceFish` / `SaveOurShip2` / `ToggleableOverlays` /
`ReflectionUtility` / `PackageIDs`。

`PackageIDs.cs` 里写死的 ID 直接可读：

```
adaptive.storage.framework   brrainz.harmony        rwmt.Multiplayer
bs.fishery                   bs.performance         zetrith.prepatcher
Owlchemist.ToggleableOverlays   OskarPotocki.VanillaFactionsExpanded.Core
```

本库安装状态：`zetrith.prepatcher` ✅、`OskarPotocki.VanillaFactionsExpanded.Core` ✅；
`bs.fishery` / `bs.performance` / `rwmt.Multiplayer` / `Owlchemist.ToggleableOverlays` **均未装**。

---

## 十程序集架构：一份 mod，十个 DLL

这是本 mod 最值得学的结构决策。每个 DLL 职责单一，且**命名空间 = 程序集名**：

| 程序集 | 版本 | 类型 | 基类 | 职责 |
|---|---|---|---|---|
| `0MultiplayerAPI.dll` | 0.5.0.0 | 36 | — | **RimWorld Together Multiplayer API 的桩实现**（`IAPI` / `ISynchronizable` / `SyncWorker` / `ISessionManager`…） |
| `1ITransformable.dll` | 1.0.0.0 | 4(+5 系统) | — | **对外公开的接口**：`ITransformable` / `ITransformable<T>` / `RotationAngle` / `TransformData` |
| `AdaptiveStorageFramework.dll` | 1.2.4.0 | 362 | — | 框架主体 |
| `CopyOperation.dll` | 1.0.0.0 | 12 | `PatchOperationPathed` | DefInjected 操作族：`Add` / `Insert` / `Replace` / `Set` / `TryAdd` |
| `PatchOperationSet.dll` | 1.0.0.0 | 6 | `PatchOperationPathed` | `Operation` |
| `PatchOperationTryAdd.dll` | 1.0.0.0 | 6 | `PatchOperationPathed` | `Operation` |
| `GeneratorOperation.dll` | 1.0.0.0 | 3 | `GeneratorBase` | `DefGenerator` / `PatchGenerator` |
| `GeneratorOperationV2.dll` | 1.0.0.0 | 3 | `GeneratorBase` | 同上，另一版 |
| `PostInheritanceOperation.dll` | 1.0.0.0 | 6 | `PatchOperation` | `Patch` / `PatchQueue` + XML 继承解析 Transpiler |
| `DefNameLink.dll` | 1.0.0.0 | 8 | `PatchOperation` | `DefNameLink` 结构 + `DefDatabaseInsertion` |
| `SaveGameCompatibility.dll` | 1.0.0.0 | 7 | `PatchOperation` | `Operation` / `PatchDatabase` + 存档补丁 |

**为什么这么切**：

1. **`0MultiplayerAPI` 是可选依赖的桩**。它把 Multiplayer mod 的 API 面声明出来，
   于是 ASF 能在**不装 Multiplayer** 的情况下编译并运行（未装时 `MP` 落到 `Dummy` 实现）。
   `0` 前缀强制它**最先**加载。
2. **`1ITransformable` 是给第三方存储 mod 用的**。别的存储 mod 只需引用这个小接口程序集
   来实现自定义绘制，**不必引用 542 KB 的框架主体**。`1` 前缀紧随其后。
3. **七个 XML PatchOperation 一家一个程序集**，命名空间各自独立，
   避免 XML 里 `Class="X"` 在多个程序集间产生歧义。

### 跨版本：三个版本目录同 commit，只有两个 DLL 逐版本编译

| DLL | 1.4 | 1.5 | 1.6 |
|---|---|---|---|
| `AdaptiveStorageFramework.dll` | `85aef3cb8d` | `1050dda9c3` | `28daa37ade` |
| `1ITransformable.dll` | `6d25a32c5e` | `97a10e0358` | `598e25338d` |
| 其余 8 个 | **全部相同** | **全部相同** | **全部相同** |

三者 `AssemblyVersion` 同为 `1.2.4`，`AssemblyInformationalVersion` 同为
`1.2.4+40787e9e0746aab12c0bcfb376f67bdeaffd6bdd`——**同一 commit、同一工具链，逐版本各编译一次**。

> 这是"哪些代码真正依赖游戏 API"的精确切分：**碰游戏 API 的两个逐版本编译，
> 纯 XML 操作层与桩层版本无关、一次编译三处复用。**

---

## 授权（§3.2 单独核实：混合许可，不是单一 MIT）

顶层 `LICENSE` 只有一份：**MIT，`Copyright (c) 2023 bradson, Soul, Phaneron`**。
但逐文件统计 168 个 `.cs` 的文件头：

| 许可 | 文件数 | 分布 |
|---|---|---|
| MIT | **137** | `Copyright (c) 2022/2023/2024/2025 bradson` |
| **MPL-2.0** | **30** | 全部在 `AdaptiveStorage/Fishery/`（Collections 15、Pools 6、FunctionPointers 3、其余 6） |
| **.NET Foundation** | **21** | 全部在 `AdaptiveStorage/Fishery/Diagnostics` |
| 无许可头 | 1 | `AdaptiveStorage/Utility/GraphicDataExtensions.cs` |

**`Fishery` 是 bradson 自己写的性能子库**（也是独立 mod `bs.fishery`），
以 **MPL-2.0** 内嵌进本 mod 的 `Source/AdaptiveStorage/Fishery/`。
它带 56 个文件：反射缓存（`Reflection.cs` 21 KB）、对象池（`PooledList` / `PooledStringBuilder`）、
`FunctionPointers`（DynamicMethod 生成）。

**结论（事实陈述，不作法律判断）**：顶层 LICENSE 声明 MIT，但 51/168 个源文件带其它许可头。
取用时须按文件分档；**若只按顶层 LICENSE 判断整包许可，会误判那 51 个文件**。

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse` + `ReadAllBytes().Length`（不信任 KB 化输出） |
| 依赖图（④ 档核心） | `[xml]` 解析全库 1026 个 `About/About.xml`，**取 `ModMetaData` 直接子元素**，检索正文含 `adaptive.storage.framework` 的节点 |
| 类型 / 补丁目标 | `LoadFrom` + `GetTypes()`，前置加载游戏 `Managed` 全部相关程序集与 `0Harmony.dll` |
| 补丁总数 | 同时枚举**类级** `GetCustomAttributesData()` 与**方法级** `GetMembers(...).GetCustomAttributesData()` |
| 卫星 DLL 的真实基类 | 逐类型读 `BaseType.FullName` |
| 跨版本差异 | 逐 DLL `Get-FileHash` SHA256 横向比对 |
| 构建来源 | 读 `AssemblyInformationalVersion`（SDK 自动写入的 `<版本>+<commit>`） |
| 许可 | 逐文件读**前 4 行**，按 MIT / MPL / .NET Foundation 分类，统计目录分布 |
| XML patch | 精读 `Defs/`(3) 与 `Patches/`(4) 全部共 7 个文件 |
| 功能口径 | 读 `Docs/modules/ROOT/pages/` 下作者自述的 AsciiDoc |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| packageId 依赖扫描 | `brrainz.harmony` / `OskarPotocki.VanillaFactionsExpanded.Core` 必须命中 | ✅ |
| `GetTypes()` | 必须列出 `AddITabToStockpileZones` 与 `XmlInheritanceResolvePostfix` | ✅ |
| 类型分类（卫星 DLL） | 必须存在非 `System/Microsoft` 命名空间的类型 | ✅ 每程序集都有 |
| 源码存在性检索 | `namespace AdaptiveStorage` 必须命中 | ✅ **165 处** |
| 语言词条提取 | 英文前几项须为 `ASF_*` 开头 | ✅ `ASF_XStacks` / `ASF_Empty` / `ASF_MapFilled`… |
| 许可分类 | 必须能把 168 个文件分成 >1 类 | ✅ 4 类 |

### ③ 自查纠错（本轮我的工具错了 2 次）

**1. 用 PowerShell 哈希表判 packageId 是否"命中"，等于没判大小写。**
我先查 `OskarPotocki.VanillaFactionsExpanded.Core` 得到"已装"，紧接着查
`oskarpotocki.vanillafactionsexpanded.core` **也**得到"已装"——
因为 **PowerShell 的 `@{}` 是大小写不敏感的**，两个拼法命中同一个键。
差一步就把它写成"VFE 有两个 packageId"。
改用 `[xml]` 直接读 `2023507013/About/About.xml` 的直接子元素，真实值是
`OskarPotocki.VanillaFactionsExpanded.Core`（**混合大小写**）。
顺带查清：`Verse.ModMetaData` 有 `packageIdLowerCase` 字段与 `SamePackageId` 方法，
所以 About.xml 的 `loadBefore` / `loadAfter` **大小写不敏感**——
上一轮 Cherry Picker 记录里那个全小写写法并无问题，我在那边补了说明。

**2. 方法级 Harmony 补丁被异常打断，计数可能偏低。**
枚举方法级 `[HarmonyPatch]` 时，`GetCustomAttributesData()` 对部分方法抛
`TypeLoadException`（`MaybeNullAttribute` / `DoesNotReturnAttribute` 无法从 mscorlib 解析）。
脚本在 `ErrorActionPreference='Continue'` 下继续跑完并给出了 **4 个**，
但**这个 4 可能偏低**。类级计数 **32** 不受此影响。
故本记录写"类级 32 + 方法级 4 = 36，方法级计数可能偏低"，不把它当作精确值。

### ④ 未核实

- **8 个程序集没有随包源码**：`AdaptiveStorage.sln` 只列了 6 个 csproj
  （`AdaptiveStorage.{1.4,1.5,1.6}` 与 `ITransformable.{1.4,1.5,1.6}`）。
  `CopyOperation` / `PatchOperationSet` / `PatchOperationTryAdd` / `GeneratorOperation(V2)` /
  `PostInheritanceOperation` / `DefNameLink` / `SaveGameCompatibility` / `0MultiplayerAPI`
  在 `Source/` 下**按命名空间检索全为 0 命中**。
  README 声称"fully open source"，故推测 GitHub 仓库里有——**本轮未核实**。
- **贴图**：`Textures/` 确实只有图标（`5636B .dds` + `1252B .png`）。
  本机原版素材被剥掉（见 `records/README.md` 提到的环境事实），
  但本 mod 不需要贴图即可核验"它不产出内容"——**这一点是目录清点直接给出的，不受素材缺失影响**。

### ⑤ 顺带发现的一处文档漂移

`info.txt`（9,179 B）是 `GraphicsDef` + `Extension` 的旧版参考，已落后于 `Docs/`：
缺 `contentLabelStyle` / `stuffFilter` / `buildingFilter` / `colorOneSource` / `colorTwoSource`，
且温度上下限仍写作 `NegativeInfinity` / `PositiveInfinity`（`Docs/` 已改为 `-Infinity` / `+Infinity`）。
**以 `Docs/` 为准**。

---

## 上下游与冲突面（④ 档：顺藤摸瓜结果）

### 谁依赖它：本库实测 30+ 个

按 `About.xml` 正文检索 `adaptive.storage.framework`，命中这些 mod
（`D` = 声明为 `modDependencies`，`A` = 列入 `loadAfter`）：

| packageId | 工坊目录 | 声明方式 |
|---|---|---|
| `Adaptive.SimpleStorage` | 3297307747 | D + A |
| `Adaptive.Ideology.Storage` | 3301337278 | D + A |
| `ASF.DeepStorage` | 3373064575 | D + A |
| `Adaptive.PrimitiveStorage` | 3400037215 | D + A |
| `sbz.NeatStorage` | 3416243474 | D + A |
| `sbz.NeatStorageWorkbenchShelf` | 3484671309 | D + A |
| `sbz.NeatStorageFridge` | 3486264784 | D + A |
| `sbz.GravshipStorage` | 3537905298 | D + A |
| `mlmlmlm.bluearchivefurniture` | 3491176484 | D + A |
| `mlmlmlm.bluearchivefurniture3` | 3610152668 | D + A |
| `mlmlmlm.bluearchivefurniture4` | 3685138265 | D + A |
| `vin.warehouse.storage` | 3519963835 | D + A |
| `jdgg.adaptive.cargoholds` | 3536708812 | D + A |
| `ponpeco.PFSF` | 3610234567 | A |
| `NuanKi.AdaptiveStorageGlobalSettings` | 3530785055 | D + A |
| `NuanKi.AdaptiveStorageGlobalSettings.zh` | 3532147963 | D + A |
| `KindSeal.UFLI` | 3651799915 | A |
| `ZH.adaptive.storage.neolithic` | 3050506223 | A |
| `FrozenSnowFox.NoDefaultShelfStorage` | 945085502 | A |
| `ferny.BetterArchitect` | 3563882422 | A |

**注意 `NuanKi.AdaptiveStorageGlobalSettings.zh`（3532147963）已经存在**——
说明这个生态**有中文使用者并已经在做汉化**，只是汉化对象是"全局设置"mod，
**ASF 本身仍无简中**（见「修改建议」）。

### 它依赖谁

- `brrainz.harmony`（唯一硬依赖，本库已装）
- `rwmt.Multiplayer` — **未装**，`0MultiplayerAPI` 桩使其静默降级
- `OskarPotocki.VanillaFactionsExpanded.Core`（`loadBefore`，已装）——
  ASF 要在 VFE 生成 Def 之前把自己挂上

### 自带重复副本检查（④ 档必查）

`bs.fishery`（Fishery 独立 mod）**未安装**——ASF 内部自带 Fishery 源码并编入主 DLL。
**本库不存在"同库两份 Fishery"的重复加载问题** ✅。
`bs.performance`（Performance Fish）亦未装，其优化路径不激活。

### 作者自己声明的冲突面

| 类型 | 内容 |
|---|---|
| **硬不兼容** | Stockpile Stack Limit (Continued) —— 破坏它依赖的"每格多物品"原版功能 |
| **软不兼容** | Recycle This 等 mod 的 Designator 可能在容器内出现，偏移不对且无直接 UI 支持 |
| **明确兼容** | LWM Deep Storage（README 称二者互补）、Multiplayer、Combat Extended、Vanilla Expanded、Pick Up And Haul、各类性能 mod |
| **关于性能** | 声称实现 ASF 的建筑 **tps 优于原版货架**；证据要求"最小 modlist + Dub's Analyzer 对比截图 + hugslib 日志"，否则不予受理 |
| **关于存档** | 框架与"加建筑"的 mod 可随时中途加入；**移除**加建筑的 mod 只有在地图上无遗留建筑（或保留框架）时才安全 |

### 跨生态的一条线索

`PackageIDs.cs` 里点名 **`Owlchemist.ToggleableOverlays`**——
即本库上一轮收录的 Cherry Picker 的作者。作者之间存在互相引用，
说明这不是零散的独立 mod，而是有组织的生态。

---

## 可复用结论

1. **框架型 mod 的分档依据是"有没有人依赖它"，不是文件大小。**
   本 mod 6.17 MB 但零内容产出；判定 ④ 档的信号是
   `packageId` 被 30+ 个 mod 写进 `About.xml`。收录前先扫这张依赖表，能直接决定分析深度。

2. **"一份 mod 拆十个 DLL" 的切分原则：按"谁需要它"和"是否依赖游戏 API"切。**
   - 对外接口单独成小 DLL（`1ITransformable`，9 个类型），
     下游 mod 引用它只需几 KB，而不是拖进 542 KB 主体。
   - 可选依赖做成**桩程序集**（`0MultiplayerAPI`），未安装时静默降级，
     免得把 Multiplayer 变成硬依赖。
   - 纯数据操作（7 个 XML PatchOperation）各自独立程序集 + 同名命名空间，
     避免 XML `Class="X"` 在多程序集间歧义。
   - 编号前缀 `0` `1` 利用 RimWorld **按文件名字母序加载 Assemblies** 来固定顺序。

3. **跨版本维护的最优形态是"同一 commit 编译三次"，并让无关部分复用同一份二进制。**
   本 mod 三版本目录 SHA256 逐 DLL 比对显示：碰游戏 API 的 2 个逐版本编译，
   其余 8 个**三版字节完全相同**。这比"给每个版本分支维护一份"成本低一个量级，
   而且版本差异一目了然。

4. **框架必须自己解决"下游改了 Def，上游还在"的问题。**
   `SaveGameCompatibility.dll` 用 `BackCompatibility.GetBackCompatibleType` 重映射类型，
   再用 `Thing.ExposeData` 的 **Transpiler** 改写 defName / 建材。
   凡是提供 Def 基类的框架，都要预判下游会改名、删 Def。

5. **想扩展 XML 数据管线，不必改游戏：给解析过程打 Transpiler。**
   `XmlInheritanceResolvePostfix` 对 `LoadedModManager.ParseAndProcessXML` 做 IL 级挂钩，
   从而插入后继承操作队列。这是"不改游戏、只改数据管线"的通用手法。

6. **授权要看文件，不能只看顶层 LICENSE。**
   本 mod 顶层写 MIT，168 个源文件里却有 30 个 MPL-2.0、21 个 .NET Foundation。
   MPL-2.0 是**文件级 copyleft**，内嵌子库（Fishery）完全合法，
   但**按顶层 LICENSE 推断整包许可会错**。收录框架型 mod 必查文件头。

7. **可选依赖要做桩，且桩的类型数会暴露作者真正用到了对方多少 API。**
   `0MultiplayerAPI` 声明了 36 个类型（`IAPI`/`ISynchronizable`/`SyncWorker`/`ISessionManager`…）——
   这等于一张"ASF × Multiplayer 的耦合面清单"。要看两个 mod 耦合多深，
   比读它们各自的兼容层代码更直接。

8. **自研性能子库值得单独记账。**
   Fishery 56 文件：反射缓存、`PooledList`/`PooledStringBuilder` 对象池、
   `FunctionPointers`（DynamicMethod 生成）。它是 ASF "tps 优于原版"主张的底座，
   也是判断这套框架技术含量的第一指标。

9. **判断 packageId 是否"已安装"不能用大小写不敏感的哈希表。**
   PowerShell 的 `@{}` 键**大小写不敏感**，用 `[xml]` 查出的
   `OskarPotocki.VanillaFactionsExpanded.Core` 与查询用的全小写拼法都"命中"，
   会凭空造出一个重复 packageId。**永远只取 `ModMetaData` 的直接子元素 `<packageId>`**。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **补简中翻译** | 本体只有 English 22 / French 6 词条。生态里已有 `NuanKi.AdaptiveStorageGlobalSettings.zh`，说明有现成的汉译意愿与流程 |
| 中 | 顶层 LICENSE 补全许可声明 | 建议在 `LICENSE` 里点明 `Fishery/` 为 MPL-2.0、`Fishery/Diagnostics` 为 .NET Foundation 许可，避免下游按 MIT 一刀切 |
| 中 | 补 `GraphicDataExtensions.cs` 的许可头 | 168 个文件中唯一一个无许可头的文件 |
| 低 | 清理 `info.txt` | 已落后于 `Docs/`，字段与数值写法都过时，易误导读者 |
| 低 | `About/` 重复格式 | `Preview.dds`（1.23 MB）+ `Preview.png`（807 KB）并存，占 About 目录的绝大部分字节 |
| 低 | 上游跟进 | 若要改，应基于 commit `40787e9e0746aab12c0bcfb376f67bdeaffd6bdd`（三版本目录同此 commit） |

---

*2026-10-17 收录。④ 档：已顺藤摸瓜查依赖图（30+ 依赖方）、重复副本（无）、兼容层点名 mod 的安装状态。
本轮工具自查纠错 2 次（PowerShell 哈希表大小写不敏感；方法级补丁枚举被 TypeLoadException 打断），均已留档。*
