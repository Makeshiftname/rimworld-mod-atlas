# Adaptive Simple Storage — 分析记录

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `Adaptive Simple Storage` |
| packageId | `Adaptive.SimpleStorage` |
| 作者 | `vin` —— 与 `收录/3301337278-AdaptiveIdeologyStorage/` **同一作者**（`<authors><li>vin</li></authors>`，复数标签是正确写法） |
| 源目录 | `F:\Games\GBL\rimworld\Mods\3297307747` |
| 工坊 | `3297307747`（`About/PublishedFileId.txt`，10 字节） |
| 授权 | **无**。无 `LICENSE` / `README.md` / `LoadFolders.xml`；`About.xml` 无 `<url>`、无 `<license>`、**无 `modVersion`** |
| 规模 | **279 文件 / 18,279,582 bytes（17.43 MB）** |
| 类型 | 纯 XML 内容包（**零代码**：无 `Assemblies/`），ASF 下游 |
| 声明支持版本 | `1.4` `1.5` `1.6` |
| 实际目录 | 只有 `1.5/`、`About/`、`Textures/`。**无 `1.6/`、无 `LoadFolders.xml`** |
| 硬依赖 | `adaptive.storage.framework`（`modDependencies` 一条，带工坊页 + GitHub 地址）；`loadAfter` 另有 `Ludeon.RimWorld` |
| 依赖是否已装 | ✅ 已装（`F:\Games\GBL\rimworld\Mods\3033901359`，`adaptive.storage.framework`，支持 1.4/1.5/1.6） |
| 核验深度 | **② 档**（21 建筑 / 42 个 XML / 单一机制 / 零代码）+ **下游接口审计** + 与同作者姊妹 mod 的**横向对照** |

### 它自称的血缘（这是本记录最值得记的一件事）

`About.xml` 的 `<description>` 一句话交代了三代移植链：

> An unoffical port of **[JDS] Simple Storage** from **LWM's Deep Storage** to the **Adaptive Storage Framework** using **Phaneron's** retexture and restyle.

即：**LWM Deep Storage（原始 mod）→ [JDS] Simple Storage（裁剪版）→ 移植到 Adaptive Storage Framework（换了机制框架）**，贴图与风格则换成 Phaneron's 的重制版。也就是说这个 mod 同时**换掉了机制后端**（LWM 那套 → ASF 这套）和**美术来源**（→ Phaneron），是"二次移植"而非简单搬运。

## 体积分解

| 项 | 文件 | 字节 | 占比 |
|---|---|---|---|
| `Textures/` | 232 | 17,306,059 | 94.7% |
| └ 其中 **116 个 `.dds`** | 116 | **15,236,500（14.53 MB）** | **88.1%** |
| └ 其中 116 个 `.png` | 116 | 2,069,559（1.97 MB） | 11.3% |
| `About/` | 5 | 912,515 | 5.0%（3 张预览图 911,585 B） |
| `1.5/Defs/StorageBuildings/` | 42 | 61,008 | 0.3% |

**`.dds` 与 `.png` 两套格式一一对应**（stem 集合完全相同，116 = 116），而 `.dds` 占了 88% 体积。注意：**没有 `.dds.zstd`** —— 这与同作者的 `3301337278` 不同（那个是 `.png` + `.dds` + `.dds.zstd` 三件套）。因为本 mod 没有 zstd，**这里的 `.dds` 是 1.5+ 实际会读到的格式，不是死重量**；而 `3301337278` 里 `.dds` 旁边有 zstd，那个 `.dds` 才是冗余的。

`About/` 三个预览图（`Preview.png` 220,112 B、`Preview1.jpg` 253,976 B、`Preview2.jpg` 437,497 B）合计占 5.0%。

## 它是什么

21 个储物建筑 + 21 个外观定义，6 个类别，全部通过 ASF 的抽象父 `AdaptiveStorageBase` 挂载：

| 类别 | 数量 | defName | 容量（声明/实算） |
|---|---|---|---|
| Barrel | 3 | `BarrelA` / `BarrelB` / `BarrelC` | 8 / 24 / 32 ✅ |
| Bundle | 3 | `BundleA` / `BundleB` / `BundleC` | 12 / 48 / 80 ✅ |
| Canister | 2 | `CanisterA` / `CanisterB` | 8 / 32 ✅ |
| Crate | 7 | `CrateA` … `CrateG` | 6 / 12 / **30** / 18 / 32 / 48 / 64 ✅ |
| Metal_Crate | 4 | `MetalCrateA` … `MetalCrateD` | 8 / 40 / 64 / 96 ✅ |
| Pallet_Crate | 2 | `PalletCrateA` / `PalletCrateB` | **8（错，实际 6）** / 32 |

- 每个建筑 = 1 个 `ThingDef`（`ParentName="AdaptiveStorageBase"`）+ 1 个 `AdaptiveStorage.GraphicsDef`（`<targetDef>` 指回它、`<showContainedItems>false</showContainedItems>`）
- **21 个全部用 `AdaptiveStorageBase`，0 个用 `AdaptiveStorageMinifiableBase`** —— 所以 21 个都手工写了 `minifiedDef=MinifiedThing` + `thingCategories=BuildingsFurniture`（ASF 的 `AdaptiveStorageMinifiableBase` 已经内置了这两项）
- 18/21 用 `costStuffCount`（stuff 计价），stuff 分布 `Woody` ×12、`Metallic` ×6
- 研究前置：`ComplexFurniture` ×12、`Machining` ×4、`ComplexClothing` ×3、`BiofuelRefining` ×2 —— 四个都是真实的原版 defName（都在 `Core\Defs\ResearchProjectDefs\`）
- 无 `Languages/` → **零翻译**，21 个建筑名与描述只有英文

## 它是什么 · 查出来的问题

### 1. 只有 1 条容量文案是错的（20/21 正确）

硬写的 `Total Capacity: N` 与 `maxItemsInCell × sizeX × sizeZ` 逐条比对，21 条里 **20 条正确**：

| defName | 声明 | perCell | 格数 | 实际 |
|---|---|---|---|---|
| CrateC | 30 | 15 | 2 | 30 ✅ |
| MetalCrateD | 96 | 16 | 6 | 96 ✅ |
| BundleC | 80 | 20 | 4 | 80 ✅ |
| **PalletCrateA** | **8** | **6** | **1** | **6** ❌ |

**横向对照很有价值**：同作者的 `3301337278`（Adaptive Ideology Storage）实测 **13/27 条容量文案是错的**（`Freight_A` 声明 180 而实际只有 80）。同一个作者的两个 ASF 下游包，**这份的正确率是 20/21，那份是 14/27**。说明这不是作者习惯性缺陷，而是**逐个 mod 单独犯的错**——所以"审计 mod 容量文案"必须逐个 mod 做，不能因为"上一个 mod 的作者很靠谱"就跳过。

顺带：两份 mod 的描述模板完全同源（"Items stored inside will never deteriorate and don't affect the beauty of their surroundings.\n\nTotal Capacity: N\n\nRotate to change appearance."），说明是从同一套模板批量生成的——**批量生成正是这类文案出错的高发场景**。

### 2. 37 个贴图没有任何 Def 引用（占 stem 的 31.9%）

116 个贴图 stem 里，**37 个找不到任何 `texPath` 引用**，全部是 `_m` / `m` 变体：

| 形态 | 数量 | 例子 |
|---|---|---|
| `<texPath>_m`（带下划线） | 2 | `Barrel_C_m`、`Metal_Crate_C_m` |
| `<texPath>_<朝向>m`（**`m` 前无下划线**） | 35 | `Canister_A_eastm`、`Crate_A_northm`、`Pallet_Crate_B_westm` |

两点值得记：

1. **两种拼写不一致**：`Barrel_C_m` / `Metal_Crate_C_m` 有下划线，其余 35 个是把 `m` 直接贴在朝向后（`_eastm`）。同一批贴图里两种约定混用。
2. 这 37 个 stem 共 **36 个文件 / 1.5 MB，占 `Textures/` 的 9.1%**（其中 1 个 stem 缺 `.dds` 或 `.png`，故 37 stem 对应 36 文件）。

它们看起来是**每个朝向 sprite 的"第二版"**（Phaneron 换皮时的原图/替代图）。**是否有某个隐式约定会消费它们，本机无法确认**——所有 Def 的 `texPath` 都没有指向它们，也没有 `_m` 相关的 Def 字段。

### 3. 与同作者姊妹 mod 的一处鲜明对照

两份 mod 都用 ASF 的 `fixedStorageSettings/filter`，但：

| | `3297307747`（本 mod） | `3301337278`（Ideology 版） |
|---|---|---|
| 自己写 `<disallowNotEverStorable>true</disallowNotEverStorable>` 的 Def | **2 / 21**（都在 `CrateC`） | 15 / 27 |
| ASF `EnhanceFixedStorageSettings.xml` 补丁（xpath `[not(disallowNotEverStorable)]`）是否生效 | **对这 20 个生效** | **对这 15 个一条也不命中** |

ASF 那条补丁的设计是"只给没写该字段的 Def 补默认值"。**本 mod 恰好踩在补丁生效的一侧**，所以 20 个 Def 也会拿到 `disallowNotEverStorable=true`；姊妹 mod 则因为自己全写了而完全绕过了它。两边最终行为一致，但走的是相反路径——这也说明**框架补丁与手写字段的交互是"看 xpath 条件"，不是"看框架有没有这条补丁"**。

### 4. 命名一致性

`Canister_B_ThingsDef.xml` 与 `Metal_Crate_D_ThingsDef.xml` 用的是 **`ThingsDef`**（多一个 s），其余 40 个是 `ThingDef`。文件名对 Def 加载无影响，但与姊妹 mod 里同样的 `Barrel_D_ThingsDef.xml` 一起看，说明这是该作者的固定笔误习惯。

### 5. 版本目录：与姊妹 mod 情况完全相同

声明 `1.4 1.5 1.6`，只有 `1.5/Defs/`，无 `1.6/`、无 `LoadFolders.xml`。

我在 `收录/3301337278-AdaptiveIdeologyStorage/README.md` 里已就同一问题做过全库核验，结论直接适用：`Verse.ModContentPack.foldersToLoadDescendingOrder`（"按降序加载的文件夹"字段名）+ `Verse.ModLoadFolders.foldersForVersion` 的按版本字典 + `Verse.LoadFolder.ShouldLoad` 的条件加载模型，三方支持"当前版本 → 更低版本 → Common → 根目录"逐级降级尝试的解读；且本机 1024 份声明支持 1.6 的 mod 中，**370 个既无 `1.6/` 也无 `LoadFolders.xml`，其中 131 个的 `Defs` 在根目录或旧版本目录**。两个 mod 属同一批。

**但仍未反编译 IL 读 `InitLoadFolders()` 的分支逻辑**，所以"极可能正常工作、风险未排除"这个结论对本 mod 同样只到这一步。

## 怎么验的

### ① 核验方法（可复现）

| 目标 | 方法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse -File` + `[System.IO.File]::ReadAllBytes().Length` |
| Def 全量清点 | Python + ElementTree，脚本 `F:\temp\ss_audit.py` |
| 贴图解析 | 同脚本，**按 `graphicClass` 分流**：`Graphic_Single` 查 `<texPath>.png`，`Graphic_Multi` 查 `<texPath>_<朝向>.png` |
| png/dds 对应关系 | 脚本 `os.path.splitext` 剥扩展名后比 stem 集合 |
| 容量核对 | 正则抽 `Total Capacity` / `maxItemsInCell` / `size`，逐条实算 |
| `<building>` 子元素合法性 | 对照已反射确认的 `RimWorld.BuildingProperties` 字段集（见姊妹 mod 记录） |
| ASF 接口 | 直接读 `F:\Games\GBL\rimworld\Mods\3033901359\Defs\ThingDefBase.xml` 与 `About.xml` |
| 框架补丁是否生效 | 读 `F:\Games\GBL\rimworld\Mods\3033901359\Patches\EnhanceFixedStorageSettings.xml` 的 xpath 条件，对照本 mod 各 Def 是否自写该字段 |

### ② 阳性对照

| 结论 | 对照 | 结果 |
|---|---|---|
| png/dds 一一对应 | 两侧 stem 集合都必须非空且完全相同 | 116 = 116，`identical = True` ✅ |
| 贴图引用全部命中 | 脚本内置 `resolved > 0` 判 CONTROL | 42/42 ✅ |
| 容量审计可信 | 脚本内置 `rows > 0` | 21 行 ✅ |
| `<building>` 无非法子元素 | 直系子元素必须全部在 `BuildingProperties` 字段集内 | `unknown = none` ✅ |
| ASF 已装且抽象父存在 | `adaptive.storage.framework` + `Name="AdaptiveStorageBase"` | 都为 True ✅ |
| `.dds` 是真 DDS | 魔数应为 `DDS ` | ✅ |
| 贴图文件总数 | 磁盘实扫 | 232 ✅ |

### ③ 自查纠错（本轮 3 次，全部靠对照/复查抓出）

1. **png/dds 比对没剥扩展名 → 误报 232 条差异。** 我把 `Barrel/Barrel_A_east.png` 和 `Barrel/Barrel_A_east.dds` 当成两个不同字符串直接 `Compare-Object`，结果 **232 行差异 = 全部文件**。剥掉扩展名后两侧 stem 集合**完全一致**。拿 `差异行数 == 文件总数` 当信号才察觉到问题——比"有没有差异"灵敏得多。

2. **把 `ParentName` 当子元素读 → 21 个全部显示 `parent=None`。** 脚本写的是 `el.findtext("ParentName")`，但 `ParentName` 是 **XML 属性**，正确的是 `el.get("ParentName")`。修好后 21 个全是 `AdaptiveStorageBase`。差一步就把"全部建筑都没挂抽象父"写成结论。

3. **未引用贴图统计又栽在路径分隔符上 → 误报 116/116 全未引用。** `os.walk` 出来的 stem 是 `Barrel\Barrel_A_east`（反斜杠），而我拼的引用前缀是 `Barrel/Barrel_A_north`（正斜杠），两者永远不匹配，于是"未被覆盖"全中。归一化后真实数字是 **37**，而不是 116。**这已经是本会话第三次栽在分隔符归一化上了**（前两次：`LegacyAssets` 与 bundle manifest 比对、`Defs/TerrainDefs` 与 `DefInjected/TerrainDef` 配对）。

## 可复用结论

1. **审 mod 时看清 `<description>` 里的血缘声明。** 「X 是 Y 的移植，改用 Z 的贴图」这类自述能直接告诉你它**换掉了什么、保留了什么**。本 mod 三代链（LWM Deep Storage → JDS Simple Storage → ASF + Phaneron）意味着机制后端与美术来源**同时被替换**——这类"二次移植"是最容易出现残留与不一致的地方（这份 mod 的残留就是那 37 个 `_m`/`m` 贴图）。

2. **同一作者的不同 mod，质量要各自实测。** 本轮最有说服力的一组数据：同作者的 `3297307747` 容量文案 **20/21 正确**，`3301337278`（Ideology 版）**14/27 正确**。而且两份的描述**模板完全同源**（同一句 "Total Capacity: N" 批量生成）。**批量生成的文案是高发错区，且同一个作者在不同 mod 上错得不一样。**

3. **`.dds` 是不是死重量，取决于有没有 `.dds.zstd`。** 本 mod 116 `.dds` 占 88% 体积，但因缺 zstd，它们是 1.5+ 实际读取的格式 → 不是冗余。同作者的 `3301337278` 同时带 `.png` + `.dds` + `.dds.zstd`，那个 `.dds` 才是真正没人读的。**判"贴图格式冗余"必须先看三种格式的齐备情况，不能只看"游戏读不读 dds"。**

4. **同名不同后缀的贴图要单独统计"无引用"数量。** 37/116（31.9%）的 stem 是 `_m` / `m` 变体，没有任何 `texPath` 指向它们，占 9.1% 体积。审计贴图时，除了"引用能否解析"（42/42 ✅），还要反查"磁盘上的文件是否都被引用到"——**这两个方向是独立的，前者全绿不代表后者也全绿。**

5. **同一种命名拼写混用（`_m` vs `_eastm`）是美术资产继承下来的信号。** 2 个用 `_m`、35 个用 `_eastm`，来自同一次批量换皮。这类不一致通常意味着资产是从多个来源拼起来的（Phaneron 的重制包 + 原始 mod 的遗留），排查时值得追一下来源。

6. **框架补丁与手写字段的交互，看 xpath 条件不看补丁存不存在。** ASF `EnhanceFixedStorageSettings.xml` 的条件是 `[not(disallowNotEverStorable)]`。同一个作者的两个 mod 一个踩在生效侧（20 个吃到补丁）、一个踩在绕开侧（15 个一条不命中），而两边最终行为一致。**同一框架 + 同一意图 + 两条不同路径 = 一组天然的正反对照，读代码时特别省事。**

7. **有没有 `Languages/` 一眼就能判零翻译**；有没有 `Assemblies/` 一眼就能判零代码。两者都不需要看任何文件内容——所以**第一遍清点目录结构就能确定这个 mod 的分析重点**（本 mod：零代码零翻译 → 重点自然落在贴图与文案，而不是 IL 或源码）。

8. **同一作者的两个 mod 放在同一次收录里对比，是很划算的审计策略。** 姊妹 mod 已经把 ASF 的抽象父、`BuildingProperties` 字段集、`PostInheritanceOperation` 补丁、`Graphic_Multi` 取图约定都验证过了，第二份直接复用，只把精力放在差量上——这就是横向对照省时间的地方。

## 修改建议

> 以下全部**未执行**。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。

| 优先级 | 事项 | 依据 |
|---|---|---|
| **P1** | 修 `PalletCrateA` 描述里的 `Total Capacity: 8` → 实际是 **6**（`maxItemsInCell=6` × 1 格） | 21 条里唯一的容量文案错误 |
| **P1** | 确认那 37 个 `_m` / `m` 贴图是否还有用途；若无，删掉可省 **1.5 MB / 9.1%** | 无任何 Def 引用；两种拼写混用（`_m` 2 个 vs `_eastm` 35 个） |
| **P2** | 补 `Languages/ChineseSimplified/DefInjected/ThingDef/` 覆盖 21 个建筑名与描述 | 目前零翻译 |
| **P2** | 把 `1.5/Defs` 复制为 `1.6/Defs`（当前完全依赖降级回退） | 声明 1.6 却无 1.6 目录，与姊妹 mod 同一风险 |
| **P2** | 改用 ASF 的 `AdaptiveStorageMinifiableBase`，可删掉 21 处手工的 `minifiedDef` + `thingCategories` | 抽象父已内置这两项 |
| **P2** | 21 个 Def 里 21 个重复了 `AdaptiveStorageBase` 已提供的 `ignoreStoredThingsBeauty` / `preventDeteriorationOnTop` | 无害但会掩盖框架默认值变化 |
| **P3** | 统一 `ThingsDef` → `ThingDef` 文件名拼写（`Canister_B_ThingsDef.xml`、`Metal_Crate_D_ThingsDef.xml`） | 与姊妹 mod 同一笔误习惯 |
| **P3** | `About.xml` 补 `modVersion`；补 LICENSE | 目前两项皆无 |

## 未核实项

- **37 个 `_m` / `m` 贴图是否被某个隐式约定消费**，未确认。所有 Def 的 `texPath` 都不指向它们，也没有相关 Def 字段；但我没有穷举 `GraphicData` / `Graphic` 的全部候选命名路径，也没有实机观察加载行为。
- **`1.5/` 单独发给 1.4 用户是否成立**，未验证——本 mod 声明 1.4 但没有 `1.4/` 目录，降级链在 1.4 上的表现与 1.6 未必相同（1.4 时代 ASF 与本 mod 的字段可用性未查）。
- **贴图与美术风格的许可**未查（无 LICENSE）。`About.xml` 明说使用 Phaneron's retexture 与 restyle，但**没有给出 Phaneron 原始贴图包的名字、工坊号或许可条款**——涉及二次改绘的授权链不完整。这与姊妹 mod 的情况相同（两份都缺）。
- **ASF 版本兼容性**：本机装的是支持 1.4/1.5/1.6 的 ASF，但本 mod 是否在**旧版 ASF**（如 1.4 时代）上可用未验。
- **本 mod 未在 1.6 实机加载验证**，所有"能工作"的结论仍是静态推导。
