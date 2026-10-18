# Glitter Tech Classic（`725576127`）— 分析记录

| | |
|---|---|
| 本记录目录 | `修改/725576127-GlitterTechClassic/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\725576127\` |
| mod 名 / packageId | Glitter Tech Classic / `GT.Sam.GlitterTech` |
| 作者 | Sam |
| 工坊 | https://ludeon.com/forums/index.php?topic=5509.0 |

> 本 mod **无授权限制**，**纯 XML、零 C#、零外部依赖**。
>
> **与前九份记录最大的不同**：这是本库第一个**大型 overhaul mod**——
> 831 文件、195 个 Def、覆盖派系/载具/义体/炮塔/武器/科研/配方/地形。
> 所以本记录的核验方式也变了：从"逐字段人工读"改为**脚本化批量交叉引用**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | 1.0 / 1.1 / 1.2 / **1.5** / **1.6**（**没有 1.3、1.4**） |
| 规模 | 831 文件 / 23.75 MB |
| 结构 | 版本目录 + **根目录共享**（Languages / Sounds / Textures） |
| 依赖 | 无 |
| 语言 | ChineseSimplified / ChineseTraditional / Russian（**无 English**，见 §五） |
| C# | 无 |

| 目录 | 文件数 |
|---|---|
| `1.0` / `1.1` / `1.2` | 各 56 |
| `1.5` / `1.6` | 各 30 |
| `Languages/`（根） | 137 |
| `Sounds/`（根） | 13 |
| `Textures/`（根） | 450 |

> **注意结构变化**：1.2 → 1.5 之间 Def 文件从 56 减到 30（少 26 个）。
> 作者在向新版迁移时**砍掉了部分内容**，不是单纯为新版本新增文件。
> 贴图/音效/语言留在根目录由所有版本共享——这是比前几弹更规范的跨版本写法。

---

## 它是什么

| 分类 | 内容 |
|---|---|
| **派系** | `FactionsGlittertech.xml`：`GTCommando`（隐藏敌对派系，`requiredCountAtGameStart 1`、`maxConfigurableAtWorldCreation 1`、`canStageAttacks`）+ `OrionCo` |
| **载具** | `RacesGlittertech_Tank.xml` + 自定义 `BodyDef` + `ThinkTreeDef` —— **OCTank 坦克是完整可驾驶载具** |
| **义体** | `HediffDefs/BodyParts/*` + `ThingDefs_Items/ItemsGlittertech_Resource_Stuff.xml` —— 可安装/可手术的身体部件 |
| **炮塔与火炮** | `RangedGlittertech_Turrets.xml`（9.5 KB）+ `RangedGlittertech.xml`（18.8 KB）：APB / MRG / EMRG / 自行火炮 |
| **建筑** | 电力、生产、结构、家具、自然地形六类 |
| **科研** | `ResearchProjectGlittertech_advanced.xml`（8.8 KB），17 处引用自有 `GTResearchBase` |
| **交易** | `TraderkindsGlittertech_BlackMarket.xml`（4.4 KB）—— 黑市商人 |
| **其他** | 地形（钛地板等）、制作配方（医疗 + 生产）、工作项、环境音、载具音效 |

内部抽象父类命名很规整：`GTBaseArtillery*` / `GTBaseGun*` / `GTBaseBullet_*` /
`GTBaseTurret` / `GTBaseVehicle` / `GTBodyPartBionic*` / `GTResearchBase` 等。

---

## 三、1.5 → 1.6 的适配：只有 6 个文件，且全部是 Odyssey 真空机制

逐文件 MD5 比对：**24 / 30 完全相同**，只有 6 个不同：

| 文件 | 改动 |
|---|---|
| `ApparelGlittertech_Armor.xml` | 新增 `VacuumResistance` ×2（带 `MayRequire="Ludeon.RimWorld.Odyssey"`） |
| `ItemsGlittertech_Resource_Stuff.xml` | 新增 `isAirtight` ×3 |
| `BuildingsGlittertech_Power.xml` | `soundAmbient` → `soundAmbientProducingPower` |
| `BuildingsGlittertech_Natural.xml` / `_Production.xml` / `_Structure.xml` / `ApparelGlittertech_Armor.xml` | 少量数值调整 |

**核验结论**：

- `VacuumResistance` ✅ 在 1.6 原版被用了 22 次（Odyssey 真空机制）
- `isAirtight` ✅ 原版 18 次
- ⚠️ `soundAmbient` **并未被移除**——1.6 原版里 `soundAmbient` 仍有 8 处、
  `soundAmbientProducingPower` 6 处，**两者共存**。
  所以这一处**不是"字段改名修复"，而是作者主动换成了更精确的"发电中环境音"**。

> 这是本记录里第一次遇到"看着像重命名、实为语义细化"的改动。
> **判断字段是否被移除，必须查原版使用次数，不能只看 mod 换了什么。**

---

## 怎么验的

脚本化批量核验（186 个 `defName`、44 个不同 `ParentName`、66 条 `texPath`）：

| 检查项 | 结果 |
|---|---|
| ParentName 引用（44 个不同值） | ✅ **全部解析**（38 个原版抽象父类 + 17 个自有 + 少量具名 Def） |
| 关键引用字段（researchPrerequisites / recipeMaker / hediffDef / thingDef / body / skeleton / traderKind / workType / building …） | ✅ 20 个 token **全部解析** |
| 贴图引用 59 条（mod 自带） | ✅ 全部命中 |
| 贴图引用 10 条 | 见下 |

那 10 条（`LampStanding`、`RockFlecked_Atlas`、`HealthItem`、`UnfinishedSculpture`、
`Pants/Pants`、`ShieldBelt/ShieldBelt`、`ShirtButton/ShirtButton`、
`Bullet_Big`、`Bullet_Shotgun`、`ShellHighExplosive`）
**全部是原版路径**——已逐条确认 Core / Anomaly 的 Def 正在使用它们，
而本 mod 不重复附带原版素材是**正确做法**。

> **为什么本地验不了**：这个游戏安装**没有原版贴图**——
> `Data\Core\Textures`、`Data\Anomaly\Textures` 等**六个 DLC 目录全部不存在**；
> `Data\Core\Sounds` 也是空的（这也就是为什么 `725130005-PMusic` 的记录里
> 无法给出与原版音频的体积对比）。
> → **本机被剥掉了原版素材**，凡涉及"原版贴图/音频是否存在"的结论都无法本地验证。

### 本次两处自查纠错（都是解析器 bug，不是 mod 问题）

1. **抽象父类正则要求了错误的属性顺序** ——
   我用 `Name="..."[^>]*Abstract="?[Tt]rue` 匹配，结果漏掉了
   `<TerrainDef Abstract="True" ParentName="FloorBase" Name="TileMetalBase">`
   这类 `Abstract` 写在 `Name` 之前的写法，导致 4 个父类被误报为"不存在"。
   → **属性顺序不能假设**，或改用两次独立匹配。
2. **贴图比对只加了 `Textures/` 前缀**，而游戏内路径是 `Core/Textures/...`，
   导致原版路径全部漏判。
   → **跨根目录比对路径时必须分别归一化**，不能共用一个前缀规则。

---

## 五、没有 English 语言包不是问题

`Languages/` 只有简中 / 繁中 / 俄语三种，没有 English。

原因是本 mod 的 Def **在 XML 里直接写英文 `<label>`**
（抽查 `GTCommando` → `<label>Commando Squad</label>`，
description 是完整英文段落）。RimWorld 的 Def 本身即英文原文，
语言包只用于覆盖，所以缺 English 属于正常。

> 另有 13 个 Def 没有 `<label>`，逐个查证后确认**全是 `SoundDef` 与
> `ThinkTreeDef`**（`MatterFab`、`PB`、`Pawn_Vehicle_Death`、`OCTank`）——
> 这两类 Def 本身就没有 label 字段，不是漏写。

---

## 六、一个小观察：`modIconPath` 上的非常规属性

```xml
<modIconPath IgnoreIfNoMatchingField="True">UI/GT</modIconPath>
```

`IgnoreIfNoMatchingField` 不是 `ModMetaData` 的标准字段，RimWorld 会忽略它。
属于作者（或某个打包工具）加的自定义标记，实际不生效，但**也不会报错**。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| — | **无需功能性修改**：字段合法、引用全解析、1.6 适配正确 |
| 低 | 1.3 / 1.4 两个版本无法使用（无对应目录、也没在 `supportedVersions` 声明）。当前已是 1.6，实际无影响；若要补，向作者索取 1.2→1.5 之间砍掉的 26 个文件 |
| 低 | 可清理 `modIconPath` 上那个不生效的 `IgnoreIfNoMatchingField` 属性 |

---

## 可复用结论

1. **大型 overhaul mod 必须脚本化核验。** 195 个 Def 手工读不现实；
   本次用"收集全部 defName → 检查 ParentName / 关键引用字段 / texPath"三段式，
   一次跑完。**只读单个文件会漏掉跨文件引用。**

2. **"字段名变了"要先确认原版是否真的移除。**
   `soundAmbient` 在 1.6 仍有 8 处使用，mod 只是换用了更精确的
   `soundAmbientProducingPower`。**查原版使用次数 > 凭 mod 的改动猜测。**

3. **⚠️ 本机游戏安装被剥掉了原版素材。**
   `Data\{Core,Anomaly,Biotech,Ideology,Royalty,Odyssey}\Textures` **全部不存在**，
   `Data\Core\Sounds` 也为空。
   → **任何"贴图/音频是否存在"的核验在本机都做不了**，
   只能通过"原版 Def 是否引用该路径"来间接确认归属。
   → 这条同样解释了 P-Music 记录里无法与原版音频做体积对比的原因。

4. **缺 1.3/1.4 要区分"故意"和"遗漏"。**
   本 mod 的目录与 `supportedVersions` **声明一致**（都没提 1.3/1.4），
   说明是作者有意的取舍，而不是漏拷目录。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机，原版素材已被剥离）*
*核验方式：脚本化 Def 交叉引用 + 逐文件 MD5 比对 1.5/1.6 + 原版字段使用次数统计*
