# Adaptive Ideology Storage — 分析记录

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `Adaptive Ideology Storage` |
| packageId | `Adaptive.Ideology.Storage` |
| 作者 | `vin` —— `About.xml` 写 `<authors><li>vin</li></authors>`（**复数标签是正确写法**，见「怎么验的」纠错 4） |
| 源目录 | `F:\Games\GBL\rimworld\Mods\3301337278` |
| 工坊 | `PublishedFileId.txt` = `3301337278`（10 字节） |
| 授权 | **无**。无 `LICENSE` / `LICENSE.md` / `README.md` / `CHANGELOG.md`，`About.xml` 也无 `<url>`、无 `<license>`、**无 `modVersion`** → 默认保留所有权利 |
| 规模 | **432 文件 / 42,257,745 bytes（40.3 MB）** |
| 类型 | 纯 XML 内容包（**零代码**：整个 mod 无 `Assemblies/`） |
| 声明支持版本 | `1.4` `1.5` `1.6` |
| 实际目录 | 只有 `1.5/`、`About/`、`Textures/`。**无 `1.6/`、无 `LoadFolders.xml`** |
| 硬依赖 | `Ludeon.RimWorld.Ideology` + `adaptive.storage.framework`（`<modDependencies>` 两条，都写了工坊/下载地址） |
| `loadAfter` | `Ludeon.RimWorld`、`Ludeon.RimWorld.Ideology`、`adaptive.storage.framework` |
| 依赖是否已装 | **均已装**。Ideology 在本机 6 个 DLC 内；ASF = `F:\Games\GBL\rimworld\Mods\3033901359`（`adaptive.storage.framework`，支持 1.4/1.5/1.6） |
| 核验深度 | **② 档**（54 个 XML、单一机制、零代码）+ 一节**下游接口审计**（逐字段对着 ASF 与原版运行时类型验） |

### 体积分解（关键）

| 目录 | 文件 | 字节 | 占比 |
|---|---|---|---|
| `Textures/` | 372 | 39,788,757 | 94.2% |
| └ 其中 **`.dds`** | 186 | **35,966,568（34.3 MB）** | **85.1%（全 mod）** |
| └ 其中 `.png` | 186 | 3,822,189（3.65 MB） | 9.1% |
| `About/` | 6 | 2,328,727 | 5.5%（其中 4 张预览图 2,327,628 B） |
| `1.5/Defs/StorageBuildings/` | 54 | 140,261 | 0.3% |

**34.3 MB 的 `.dds` 是纯死重量**：RimWorld 只读 PNG，本 mod 的 Def 里没有任何一处引用 `.dds`（`texPath` 一律不带扩展名），也没有 DDS 加载配置。抽样确认它们是真实 DDS 文件（魔数 `44 44 53 20` = `DDS `），只是原美术的源文件被打包进来了。

## 它是什么

一句话：把「Ideology 的储物家具」这一类东西接进 **Adaptive Storage Framework（ASF）**，让它们变成真能装东西的储物建筑。**纯 XML，零代码**——它做的是**内容**，不是机制；机制全部来自 ASF 与原版。

### 内容量

| 项 | 数量 |
|---|---|
| `ThingDef` | **27**（全部 `ParentName="AdaptiveStorageBase"`） |
| `AdaptiveStorage.GraphicsDef` | **82**（其中 7 个抽象父） |
| Def 文件 | 54，分布在 11 个类别目录 |

27 个建筑：Barrel×4、Bundle×1、Canister×4、Chunk×2、Container×2、Crate×5、Cylinder×1、Freight×2、LockerBank×3、MealCrate×2、RustedToolbox×1。

82 个 GraphicsDef 里两组是"外观随内容变"的看点：

- **MealCrate A/B 各 22 个**：按存货切换贴图。`requiredThingDefs` 指定 `MealSimple` / `MealFine` / `MealNutrientPaste` / `MealLavish` / `MealSurvival` 等 6 类 × 简单/精细/奢华/生存 4 等级，外加 `allowedFilter` 里带 `MayRequire="Ludeon.RimWorld.Ideology"` 的 `<li>AllowVegetarian</li>` / `<li>AllowCarnivore</li>` 特化过滤器——于是**素食者餐食 / 荤食者餐食 / 纯肉 / 纯蔬**各有独立外观。每个变体再用 `minimumStackCount`（1 / 3）叠出半满与全满两个 sprite，用 `randomSelectionWeight`（0 或 15）控制同级命中时的取舍，用 `maximumThingCount=0` 表示"空箱"状态。
- **Freight A/B 各 4 个**：Base + Steel / Plasteel / Uranium 三种盖布，靠 `onlyAllowRequiredThingDefs=true` + `requiredThingDefs` 限定该变体只在存了对应材料时出现。

### 与 ASF 的接口（**全部核对通过**）

1. **抽象父** `AdaptiveStorageBase` —— 存在于 `F:\Games\GBL\rimworld\Mods\3033901359\Defs\ThingDefBase.xml:3`，`ParentName="BuildingBase"`、`thingClass=AdaptiveStorage.ThingClass`、`designationCategory=ASFstorage`、`inspectorTabs=ITab_Storage`、`blueprintClass=Blueprint_Storage`。27 个下游 Def 全部正确引用。

2. **自定义 Def 类型** `AdaptiveStorage.GraphicsDef` —— 存在于 `AdaptiveStorageFramework.dll`（类型 token `.AdaptiveStorage.GraphicsDef+<ConfigErrors>d__66`）。

3. **`<building>` 内的 5 个字段** —— 逐一对着运行时反射验证，**全部是原版 `RimWorld.BuildingProperties` 的真实字段**，不是 ASF 注入的私有字段：

   | 字段 | 类型 |
   |---|---|
   | `maxItemsInCell` | `System.Int32` |
   | `fixedStorageSettings` | `RimWorld.StorageSettings` |
   | `defaultStorageSettings` | `RimWorld.StorageSettings` |
   | `preventDeteriorationOnTop` | `System.Boolean` |
   | `ignoreStoredThingsBeauty` | `System.Boolean` |

   （顺带确认同类型上 `storageGroupTag`:String、`blueprintClass`:Type 也存在。）

4. **27 个 Def 里 15 个带 `<fixedStorageSettings><filter>`**，分别限定 `Chunks` / `FoodMeals` / `Weapons`+`Apparel` 等类别，并带 `disallowNotEverStorable=true`。

5. 研究前置 4 个**全部是真实原版 defName**：`Machining`×11、`ComplexFurniture`×11、`BiofuelRefining`×9、`ComplexClothing`×1，都能在 `Core\Defs\ResearchProjectDefs\` 里查到。

### 贴图

146 个不重复的 `texPath`/`uiIconPath` 引用，**146/146 全部命中实际文件，0 缺失**。其中 126 个 `Graphic_Single`（`<texPath>.png`），20 个 `Graphic_Multi`（按 `<texPath>_<朝向>.png`）。`Graphic_Multi` 的朝向齐备度分布：四向齐全 6 个、只有 east/south 10 个、三向 4 个——不必四向都做，`Verse.Graphic_Multi` 有 `MatSingle` 兜底。

## 它是什么 · 查出来的问题

### 1. 13/27 的 "Total Capacity" 与实际容量对不上（最主要发现）

`description` 里硬写的 `Total Capacity: N` 与 `maxItemsInCell × sizeX × sizeZ` 实算逐条比对：

| defName | 声明 | perCell | 格数 | 实际 | 结论 |
|---|---|---|---|---|---|
| BarrelD / E / F / G | 2 | 3 | 1 | **3** | ❌ |
| CanisterC / D / E / F | 48 | 9 | 6 | **54** | ❌ |
| ChunkA / B | 80 | 12 | 10 | **120** | ❌ |
| Freight_A / B | 180 | 8 | 10 | **80** | ❌ |
| asf_rustedtoolbox | 8 | 5 | 2 | **10** | ❌ |
| Bundle_D | 24 | 6 | 4 | 24 | ✅ |
| ContainerC / D | 180 | 12 | 15 | 180 | ✅ |
| CrateH / I / J / K / L | 3/3/2/1/4 | 同左 | 1 | 同左 | ✅ |
| CylinderA | 12 | 6 | 2 | 12 | ✅ |
| LockerBank_1x1z / 1x2z / 1x3z | 6/24/36 | 6/12/12 | 1/2/3 | 6/24/36 | ✅ |
| MealCrate_A / B | 32 / 8 | 8 / 8 | 4 / 1 | 32 / 8 | ✅ |

**合计 27 条，14 对 13 错。** 两点值得注意：

- `Freight_A/B` 声明 **180** 而实际只有 **80**，而 `ContainerC/D` 声明的恰好也是 180 且实际正好 180 —— Freight 的数字**疑似从 Container 复制粘贴**而来。
- ASF 本身就提供了带占位符的 Keyed 字符串
  `ASF_StorageCapacityDescriptionStacksPerCell`：
  "…`{sizeX}` * `{sizeZ}` cells with a maximum capacity of `{maxItemsInCell}` stacks per cell."
  也就是说**框架本来就会算这个数**，硬写反而放弃了自动同步——上游一旦调 `maxItemsInCell`，文案就静默过期，且没有任何机制会提醒。

### 2. LockerBank 三个 Def 的 `<label>` 直接等于 `<defName>`

`LockerBank_1x1z` / `LockerBank_1x2z` / `LockerBank_1x3z` 的 `<label>` 写的就是内部标识符本身（读原文确认，如 `<label>LockerBank_1x1z</label>`）。其他 24 个 Def 都有正常可读名（`Barrel D`、`Meal Crate A`…）。玩家在建造菜单里会看到 `LockerBank_1x1z`。

### 3. LockerBank 描述有重复词

`1x1LockerBank_Thingdef.xml:16`：`don't affect the beauty of their surroundingssurroundings.` —— `surroundings` 重复两次（其余 26 条描述都正常）。

### 4. 零翻译

**没有 `Languages/` 目录**。27 个建筑的名字与描述只有英文。Keyed 也没有——不过 ASF 自己的容量说明 Keyed 是英文默认，缺 `Languages` 只影响本 mod 自己的 27 条文案。

### 5. 声明 1.6 却只发 `1.5/`

`About.xml` 的 `<supportedVersions>` 写 `1.4 1.5 1.6`，但只存在 `1.5/Defs/`，既无 `1.6/` 也无 `LoadFolders.xml`。它在 1.6 上大概率仍能工作（见下节），但作者并未在 1.6 目录上做过任何适配。

### 6. 34.3 MB `.dds` 死重量（见「身份卡」体积分解）

## 跨版本工程：只有 `1.5/` 到底行不行

这是本 mod 最需要交代的技术问题。本机能查到的全部证据：

**类型模型（反射 `Assembly-CSharp` 1.6.9655.19392）**

| 类型 | 关键成员 |
|---|---|
| `Verse.ModContentPack` | 字段 `List<string> foldersToLoadDescendingOrder`；方法 `InitLoadFolders()`、`<InitLoadFolders>g__AddFolders\|58_0(List<string>)`、`LoadDefs` / `LoadPatches` / `GetAllFilesForMod` |
| `Verse.ModLoadFolders` | 字段 `defaultVersionName`、`Dictionary<string, List<LoadFolder>> foldersForVersion`；方法 `FoldersForVersion(string)`、`DefinedVersions()`、`GetIssueList(ModMetaData)` |
| `Verse.LoadFolder` | 字段 `folderName`、`requiredAllOfPackageIds`、`requiredAnyOfPackageIds`、`disallowedAnyOfPackageIds`；属性 `ShouldLoad` |

字段名 **`foldersToLoadDescendingOrder`**（"按降序加载的文件夹"）与 `foldersForVersion` 这个按版本字符串索引的字典，共同支持"**当前版本 → 更低版本 → Common → 根目录**逐级降级尝试"这一解读；`LoadFolder` 的三个 packageId 列表说明条目还可以按其它 mod 的存在与否条件加载（这正是 `LoadFolders.xml` 的能力）。

**全库实证**：1021 个 mod 里 **1024 份 `About.xml` 声明支持 1.6**（含重复 packageId 的目录），其中：

| 情形 | 数量 |
|---|---|
| 有 `1.6/` 目录 | 569 |
| 无 `1.6/` 且无 `LoadFolders.xml` | **370** |
| └ 其中 Defs 在根目录或某个旧版本目录里 | **131**（本 mod 属于这一类） |
| └ 其中任何位置都找不到 Defs | 239 |

131 个 mod 与本 mod 处于**完全相同**的布局。若"没有 `1.6/` 就完全不加载"，这 131 个会同时失效——那是灾难级、用户当天就会报的问题。所以降级回退几乎必然存在。

**但要说清楚没证实的部分**：我没有反编译 `InitLoadFolders()` 的 IL，读不到它的实际分支顺序；也没实机启动游戏。所以严格表述是——**极可能在 1.6 正常工作（因为 131 个同布局 mod 共用这一模式），但"1.6 未适配"这一风险无法从本机排除**：若 1.6 改了 `AdaptiveStorage.GraphicsDef` 或 `BuildingProperties` 的字段，本 mod 会静默失配，而 `<supportedVersions>` 仍会让模组管理器把它当兼容。

### 顺带：ASF 的 XPath 补丁对本 mod 不生效

`F:\Games\GBL\rimworld\Mods\3033901359\Patches\EnhanceFixedStorageSettings.xml` 用 `PostInheritanceOperation.Patch` 包一条 `PatchOperationAdd`，xpath 条件是
`Defs/ThingDef[thingClass="AdaptiveStorage.ThingClass"]/building/fixedStorageSettings/filter[not(disallowNotEverStorable)]` —— 只给"**没写**该字段的" Def 补 `<disallowNotEverStorable>true</disallowNotEverStorable>`。本 mod 15 个带 filter 的 Def **全部自己写了**这一行，所以值相同、结果无差别，但那条补丁对它们一条也没命中。判断"框架某条补丁对我有没有生效"必须看 xpath 条件，不能只看框架有没有这条补丁。

## 它是什么 · 两处冗余（无害但值得知道）

1. **重复声明抽象父已有的字段**：`AdaptiveStorageBase`（`Defs\ThingDefBase.xml:22-23`）已经写了 `<ignoreStoredThingsBeauty>true</ignoreStoredThingsBeauty>` 和 `<preventDeteriorationOnTop>true</preventDeteriorationOnTop>`，本 mod **27 个 Def 全部又写了一遍**。
2. **没用更省事的抽象父**：ASF 还提供 `AdaptiveStorageMinifiableBase`（已含 `minifiedDef=MinifiedThing` + `thingCategories=BuildingsFurniture`），本 mod 27 个 Def **全部用 `AdaptiveStorageBase`**，并手工重复那两行。

这两点合起来说明作者大概率没细读 ASF 的 `ThingDefBase.xml`——不影响运行，但让 mod 与框架的耦合更脆（框架改了默认值，这个 mod 不会跟着变）。

## 怎么验的

### ① 核验方法（可复现）

| 目标 | 方法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse -File` 后逐个 `[System.IO.File]::ReadAllBytes().Length`（不信 KB 化列表） |
| packageId / 依赖 | `xml.etree` 或 `[xml]` 取 `ModMetaData` **直接子元素**，不用 PS `@{}`（键大小写不敏感会造出假冲突） |
| Def 全量清点 | Python + ElementTree，落 `F:\temp\ais_inventory.py` |
| `<building>` 字段合法性 | 预载全部 106 个 Managed DLL 后反射 `RimWorld.BuildingProperties` 的 `DeclaredOnly` 字段 |
| `Graphic_Multi` 取图约定 | 反射 `Verse.Graphic_Multi` 的属性 + 在 Assembly-CSharp 的 ASCII/UTF-16 两堆做 `IndexOf` 探字面量 |
| 容量一致性 | Python 正则抽取 `Total Capacity` 与 `maxItemsInCell`/`size`，脚本落 `F:\temp\ais_capacity.py` |
| 贴图解析 | Python，脚本落 `F:\temp\ais_tex2.py`（按 `Graphic_Single` / `Graphic_Multi` 分别解析） |
| 库级普查 | PowerShell 遍历（`Get-ChildItem -Recurse` 会超时，内容搜索一律走 `grep` 工具） |

### ② 阳性对照

| 结论 | 对照 | 结果 |
|---|---|---|
| 贴图 146/146 命中 | 审计脚本内置：命中数为 0 则判 CONTROL FAILED | 146 ✅ |
| 5 个 `<building>` 字段真实存在 | `RimWorld.BuildingProperties` 的 `isEdifice`/`isInert`/`repairable`/`paintable` 等 180+ 字段全部列出 | ✅（我原先挑的 `deconstructible`/`passability`/`fillPercent` 其实**不在** `BuildingProperties` 上——正控选错的是对照，不是被测对象） |
| `Graphic_Multi` 不走 `_Atlas` | `_Atlas` 的 `IndexOf` 在 ASCII 与 UTF-16 两堆都应能命中（若该约定存在） | 都 -1，而对照 `Graphic_Single` 命中 7281205 → 证明是真阴性 ✅ |
| 27 条描述含字面 `\n` 是否异常 | 原版 `Core\Defs` 里搜 `\n` | 8 个 `BackstoryDefs` 命中 → 原版也有此写法，**不能据此判缺陷** ✅ |
| 4 个研究前置真实 | 同法找 `WoodBench` | `WoodBench` 在 Core Defs 里不存在（正控选错）；改用 4 个研究项本身逐个查，全部 FOUND ✅ |
| 类型名 `RimWorld.BuildingProperties` | `Verse.Building` 必须能找到 | 找到 ✅ |

### ③ 自查纠错（本轮 4 次）

1. **贴图审计报了 40 条假「缺失」**，而且纠正过程自己绕了两圈。第一版只探 `Textures/<texPath>.png`，把 20 个 `Graphic_Multi` 目标 × 2 处引用全判成缺失。实际上这些资源是**按朝向命名**的（`Textures\Barrel\Barrel_D_north.png` 等）。纠正时我先假设 RimWorld 需要 `<texPath>_Atlas.png`——但本 mod 里 **0/20** 有 `_Atlas`，于是去全库抽样 651 个 `Graphic_Multi` 的 texPath，结果 563 个无法解析（**样本被污染**：多数 1.5+ mod 已改用 AssetBundle 而非散图），差点就此得出"全库都这样所以没问题"的荒谬结论。最后靠反射 `Verse.Graphic_Multi`（属性 `MatNorth`/`MatSouth`/`MatEast`/`MatWest`/`MatSingle`）+ `_Atlas` 在两个堆里都 `IndexOf = -1` 才定案。修正后 **146/146 全部命中**。

2. **类型名猜错，导致字段审计全军覆没**。`$asm.GetType('Verse.BuildingProperties')` 返回 `null`，于是那 5 个 ASF 字段全被报成 `absent` —— 差一步就写成"这 mod 在往 `<building>` 里写不存在的字段，装载必报错"。真名是 **`RimWorld.BuildingProperties`**（`Verse` 命名空间下没有这个类型）。这与我在 `2898044088` 那轮踩过的 `Verse.XenotypeDef` → `RimWorld.XenotypeDef` 是同一类命名空间陷阱。

3. **反射脚本里写了 `[System.Reflection.AppDomain]`** —— 这个类型不存在，PS 直接 `Unable to find type`，导致全程序集类型搜索**整体静默失效**（只输出三条 `NOT FOUND`，看起来像"这些类型都不存在"）。正确写法是 `[System.AppDomain]::CurrentDomain`。

4. **差点把 `<authors>` 记成笔误**。看到 `<authors><li>vin</li></authors>` 时我准备按"应为 `<author>`"写进缺陷表。反射 `Verse.ModMetaData` 后发现它的属性就叫 **`Authors`（`IEnumerable`）** 和 **`AuthorsString`**——**复数写法是正确的**。差一步就凭空造出一条假缺陷。

## 可复用结论

1. **审计"纯 XML 下游 mod"要逐字段对着目标框架的运行时类型验，不能读一遍觉得合理就过。** 本轮最大的收获是这个方向的反面结论：ASF 这类框架**没有**用私有字段污染 `<building>`，下游直接写原版 `RimWorld.BuildingProperties` 的字段即可（`maxItemsInCell`、`fixedStorageSettings` 等全是原版字段）。所以"下游 mod 写了框架的私有字段"这个怀疑，**必须反射证伪，不能靠猜**。

2. **`Verse` vs `RimWorld` 命名空间必须反射确认。** `BuildingProperties`、`XenotypeDef` 这类"看起来像 Verse"的核心类型实际都在 `RimWorld`。凭直觉写 `Verse.X` 会让 `GetType` 返回 `null`，而 `null` 上调 `GetField` 会一路抛异常——若外面套了 `try/catch`，就变成一串**可信度为零的假阴性**。这个坑我已经在两个不同 mod 上各踩一次。

3. **看到"疑似笔误"先反射属性名再下结论。** `<authors>` 复数是对的（`ModMetaData.Authors`）。收录区标准要求的"如实标注、不硬猜"，反过来也适用于别急着报 bug。

4. **框架的抽象父可能已经给了你想要的默认值；重复声明无害但会掩盖差异。** 本 mod 27 个 Def 全部重复了 ASF 抽象父里已有的两个 `true` 字段，而且没用 ASF 提供的更省事的 `AdaptiveStorageMinifiableBase`。判"这个 mod 与框架耦合得脆不脆"，看它有没有在手工重复框架已经做过的事。

5. **判断"框架某条补丁对我有没有生效"要看 xpath 条件。** ASF 用 `[not(disallowNotEverStorable)]` 只补默认值；本 mod 自己写了该字段，那 15 个 Def 一条也没命中该补丁。框架有补丁 ≠ 你的 Def 吃到补丁。

6. **把可计算的数字硬写进描述 = 迟早对不上，而且没有任何机制会提醒你。** 本 mod 13/27 的 "Total Capacity" 与实算不符，而 ASF 本来就提供了带 `{sizeX}`/`{sizeZ}`/`{maxItemsInCell}` 占位符的 Keyed 字符串。同类数字还有 HP / 建造工时 / 材料成本——凡是"上游一改就过期"的文案，都该用框架的计算机制或至少留 TODO。

7. **`Graphic_Multi` 按 `<texPath>_<朝向>.png` 取图**——不是 `<texPath>.png`，也不是 `<texPath>_Atlas.png`。`Verse.Graphic_Multi` 暴露 `MatNorth`/`MatSouth`/`MatEast`/`MatWest`/`MatSingle` 五个材质属性，且 `_Atlas` 这个字面量在 Assembly-CSharp 的 ASCII 与 UTF-16 两堆里都不存在。做 mod 资源审计时 `texPath` 必须当**前缀**解析，并单独统计每种朝向齐不齐（本 mod：四向 6 个、两向 10 个、三向 4 个，不必一致）。

8. **审计 mod 体积先按扩展名切分。** 本 mod 85.1% 的体积是 186 个游戏根本不读的 `.dds`（34.3 MB）。一眼可见的死重量，藏在"40.3 MB"这个总数里完全看不出来。

9. **"声明支持 X 却只发 X-1 目录"是广泛存在的模式，不要默认它是 bug。** 本机 1024 份声明 1.6 的 mod 里，370 个既无 `1.6/` 也无 `LoadFolders.xml`，其中 131 个的 Defs 在根目录或旧版本目录。`Verse.ModContentPack.foldersToLoadDescendingOrder` 这个字段名 + `Verse.ModLoadFolders.foldersForVersion` 的字典结构 + `Verse.LoadFolder.ShouldLoad` 的条件加载模型，三方共同支持"逐版本降级尝试"的解读。这个模式既然被 131 个 mod 共用，就不该当成缺陷——但**也不能**在没反编译 IL 的情况下断言它一定工作。想彻底确定，最省事的办法还是开一次游戏看建筑有没有出现。

10. **抽样的样本可能被"素材已迁到 AssetBundle"污染。** 我第一次试图用全库 651 个 `Graphic_Multi` 引用来推断约定，结果 563 个无法解析（因为 1.5+ 的 mod 普遍不再随包散图）。用 mod 库推约定时，要先确认抽样对象的素材确实在 `Textures/` 里。

## 修改建议

> 以下全部**未执行**。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。

| 优先级 | 事项 | 依据 |
|---|---|---|
| **P0** | 修正 13 个建筑描述里的 "Total Capacity"（Barrel×4、Canister×4、Chunk×2、Freight×2、RustedToolbox）；或改用 ASF 的 `ASF_StorageCapacityDescriptionStacksPerCell` 占位符机制，让数值自动跟随 `maxItemsInCell` | 逐条实算表见「它是什么 · 查出来的问题 · 1」 |
| **P0** | LockerBank 三个 Def 的 `<label>` 从 `LockerBank_1x1z` 改成可读名（如 `1×1 Locker Bank`） | 建造菜单现在显示内部标识符 |
| **P1** | 修 `1x1LockerBank_Thingdef.xml:16` 的 `surroundingssurroundings` 重复词 | 27 条描述里独此一处 |
| **P1** | 删掉 186 个 `.dds`（省 34.3 MB，体积降约 85%） | 无任何 Def 引用；RimWorld 只读 PNG |
| **P1** | 补 `Languages/ChineseSimplified/DefInjected/ThingDef/`，覆盖 27 个建筑名与描述 | 目前零翻译 |
| **P2** | 把 `1.5/Defs` 复制为 `1.6/Defs`（当前完全依赖降级回退） | 声明了 1.6 却无 1.6 目录；一旦框架字段变更会静默失配 |
| **P2** | 改用 `AdaptiveStorageMinifiableBase`，并删掉与抽象父重复的 `ignoreStoredThingsBeauty` / `preventDeteriorationOnTop` / `minifiedDef` / `thingCategories` 四行 | ASF 抽象父已提供全部四项 |
| **P2** | 补 `modVersion` 与 `<url>`；若允许，补 LICENSE 文件 | 目前四项全缺 |

## 未核实项

- **`Verse.ModContentPack.InitLoadFolders()` 的实际目录顺序**。未反编译 IL。降级回退机制有"字段名 + 类型模型 + 131 个同布局 mod"三方支撑，但分支逻辑没读到。
- **本 mod 未在 1.6 实机加载验证**。所有"能工作"的结论都是静态推导。
- **27 条描述里的字面 `\n` 是否会原样显示在游戏 UI 上**。原版 `BackstoryDefs` 里也有 `\n`（已搜到 8 个文件），但 ThingDef 描述是否惯例如此、以及 RimWorld 在读取非翻译字段时是否解 `\n`，未实机验证——**不能据此判为缺陷**。
- **素材（186 PNG + 186 DDS）的原始作者与授权**。无 LICENSE 文件，`About.xml` 的 `<description>` 也未提素材来源或是否取自 Ideology 原版家具再加工。考虑到它做的是"Ideology 家具 + ASF 改造"，贴图很可能大量取自 Ideology DLC 原版资源再加工——**若如此，涉及 DLC 素材的再分发授权**。未核实。
- **ASF 的 `AdaptiveStorage.GraphicsDef` 是否还有本 mod 未用到的字段**（例如 `maximumThingCount` 之外的全局外观覆盖）。未逐字段枚举该 Def 类的字段清单。
