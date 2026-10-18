# Misc. Training — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/717575199-MiscTraining/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\717575199\` |

> 本 mod 无需修改。本记录为**留档 + 兼容核验**，
> 核心价值在 §五「跨版本维护策略」与 §七「可复用结论」。
> 与 `修改/美南烛/` 那份不同——那份记录的是**要修的毛病**，这份记录的是**值得学的做法**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 目录名（mod 本体） | `717575199`（Steam 创意工坊 ID 命名） |
| mod 名 | Misc. Training |
| packageId | `Haplo.Miscellaneous.Training` |
| 作者 | Haplo（HaploX1） |
| modVersion | 1.6.5（程序集版本 `1.6.4.0`） |
| 支持版本 | 1.0 – 1.6，**7 套版本目录全部在架** |
| 规模 | 529 文件 / 2.46 MB |
| 源码 | **未随附**（只有编译产物，无 `Source/`） |
| 本地游戏 | RimWorld 1.6.9655.19392 |

### 文件类型分布

| 数量 | 类型 | 说明 |
|---|---|---|
| 364 | `.xml` | Def 与翻译 |
| 74 | `.png` | **贴图源图，保留它是有意的**（见 §六） |
| 72 | `.dds` | 运行时实际读取 |
| 7 | `.dll` | 每个版本目录一个（1.0 → 1.6） |
| 7 | `.ogg` | 音效 |
| 2 | `.pdb` | 调试符号（仅 1.6 有） |
| 1 | `.mdb` | Mono 调试符号 |
| 2 | `.txt` | — |

### 声明的依赖关系

| 声明 | 类型 | 本机状态 | 实际影响 |
|---|---|---|---|
| `loadAfter: Haplo.Miscellaneous.Core` | 排序约定 | **未安装** | **无影响**（见 §二） |
| `incompatibleWith: Haplo.Miscellaneous.TrainingNoTask` | 互斥 | **未安装** | 无 |
| `Patches/Training_CE_Patch.xml` → Combat Extended | 条件补丁 | **CE 未安装** | 补丁空转（见 §二） |

---

## 二、两处容易误判的地方

### 2.1 `loadAfter Haplo.Miscellaneous.Core` 不是硬依赖

Core 未安装，但**不影响 mod 运行**。证据：

`TrainingFacility.dll` 的程序集引用只有四个，无任何 Haplo 程序集：

```
mscorlib              4.0.0.0
Assembly-CSharp       1.6.9340.29816
UnityEngine.CoreModule
System.Core
```

反射出的 26 个公开类型，基类全部是 `Verse.*` / `RimWorld.*`。

→ 所以那条 `loadAfter` 是**排序约定，不是运行时依赖**。
→ 作者刻意用 `loadAfter` 而非 `modDependencies`，正因如此：游戏不会因缺 Core 拒绝加载。
→ **教训**：判断 mod 是否真依赖某物，要看 DLL 的 `GetReferencedAssemblies()`，
   不要看 `About.xml` 的 `<loadAfter>`——后者只是给加载顺序的建议。

> **排查时踩过的坑**：先 grep 到 `2015093322\About\About.xml` 含 `Haplo.Miscellaneous` 就下了
> "Core 已安装"的结论。实际那个目录是 `RWZH.ChinesePack.Miscellaneous`（边缘汉化组的
> Misc. 全系列汉化包，作者 leafzxg），只是它的 `loadAfter` 列表里列了 Core。
> **教训**：确认 packageId 是否存在，必须精确匹配 `<packageId>` 整行，
> 不能靠子串 grep。

### 2.2 CE 补丁在本机不会触发

`1.6/Patches/Training_CE_Patch.xml`：

```xml
<Operation Class="PatchOperationFindMod">
  <mods><li>Combat Extended</li></mods>
  <match Class="PatchOperationSequence">
    <operations>
      <li Class="PatchOperationReplace">
        <xpath>*/JoyGiverDef[defName="PracticeShooting"]/baseChance</xpath>
        <value><baseChance>0.1</baseChance></value>
      </li>
    </operations>
  </match>
</Operation>
```

它把**本 mod 自己的** `JoyGiverDef`（`PracticeShooting`）的 `baseChance` 从 3 压到 0.1。
动机是 CE 自带射击训练，两边同时触发会让殖民者泛滥地泡在靶场。

本机未装 CE → `FindMod` 不匹配 → 整条序列跳过 → `baseChance` 保持 **3**。

> 写法上值得学：用 `PatchOperationFindMod` 包一层做条件补丁，
> 是"给另一个 mod 让路"的标准解法，比无条件 patch 安全得多。

---

## 它是什么

三个建筑：**射击标靶**（`ShootingRangeTarget`）、**格斗假人**（`MartialArtsTarget`）、
**箭靶**（`ArcheryTarget`）。前两个可练技能也可当娱乐，箭靶纯娱乐。

### 3.1 一物三态的 Job 设计（核心机制）

每个建筑派生三个 JobDef：`Joy` / `NonJoy` / `NonJoy_Work`。

| JobDef | joyGainRate | joyDuration | joyXpPerTick |
|---|---|---|---|
| `UseShootingRange`（娱乐） | 1.3 | 4000 | 0.035 |
| `UseShootingRange_NonJoy` | 0.8 | 17000 | 0.044 |
| `UseShootingRange_NonJoy_Work` | **−0.3** | 800 | 0.057 |
| `UseMartialArtsTarget`（娱乐） | 1.1 | 4000 | 0.027 |
| `UseMartialArtsTarget_NonJoy` | 0.9 | 17000 | 0.034 |
| `UseMartialArtsTarget_NonJoy_Work` | **−0.3** | 800 | 0.043 |

设计意图清晰：**列工作时没有快乐收益、时长最短、但技能经验最高**——
刻意做成"干活练级但不享受"，避免玩家无脑把所有人塞进工作标签。

### 3.2 工作标签

`WorkTypeDef` `MiscTraining_CombatTraining`（显示名"训练" / Training，优先级 435），
`WorkGiverDef` 同名，`nonColonistsCanDo=true`，`directOrderable=true`，
需要 `Manipulation` 能力。

**值得记一笔的 workaround**：

```xml
<relevantSkills>
  <li>Shooting</li>
  <!-- <li>Melee</li> BugFix: Ghuls loosing Melee -->
</relevantSkills>
```

作者**故意注释掉 Melee**。原版食尸鬼（Ghul）会因为近战工作项去"训练"而丢失技能。
这是踩坑后写下的注释，也是本 mod 里信息量最高的一行。

> 对照 1.6 核验：`MiscTraining_CombatTraining` 的 `relevantSkills` 只有 `Shooting`，
> 与注释一致，说明 workaround 在 1.6 仍然有效。

### 3.3 建筑参数

| | ShootingRangeTarget | MartialArtsTarget | ArcheryTarget |
|---|---|---|---|
| Beauty | −2 | +2 | −3 |
| MaxHitPoints | 1000 | 1000 | 400 |
| WorkToBuild | 2500 | 4000 | 2500 |
| 主体材料 | 钢 40 | 木 55 | — |
| stuffCategories | Fabric / Leathery | Fabric / Leathery | Metallic / Woody / Stony |
| costStuffCount | 55 | 35 | 70 |
| pathCost | 120 | 120 | 60 |
| 站立距离 | 8–11，宽度 3 | 1–1，宽度 1 | 6–9，宽度 3 |
| joyKind | Gaming_Shooting | Gaming_MartialArts | Gaming_Shooting |

格斗假人**必须贴脸站**（距离固定 1 格），射击标靶需要退后 8–11 格的射击位——
这解释了 C# 里为什么需要 `Utility_PositionFinder` 去算站位。

---

## 四、C# 实现（无源码，靠反射还原）

只发布编译产物。反射 `1.6/Assemblies/TrainingFacility.dll` 得 26 个公开类型：

| 类型 | 基类 | 职责 |
|---|---|---|
| `Building_ShootingRange` | `Verse.Building` | 射击标靶 |
| `Building_MartialArtsTarget` | `Verse.Building` | 格斗假人（含修复开关 Gizmo） |
| `Building_Archery` | `Verse.Building` | 箭靶 |
| `JobDriver_ShootingRange` | `RimWorld.JobDriver_WatchBuilding` | **核心**：`GetToil_ShootAtTarget` / `AttackTarget` / `WatchTickAction` |
| `JobDriver_MartialArtsTarget` | `RimWorld.JobDriver_WatchBuilding` | `GetToil_MeleeFightTarget` / `FightTarget` |
| `JobDriver_Archery` | `RimWorld.JobDriver_WatchBuilding` | 静态 `ShootArrow(Pawn, IntVec3)` |
| `JoyGiver_PracticeShooting` / `JoyGiver_PracticeMartialArts` | `RimWorld.JoyGiver_WatchBuilding` | 娱乐派发 |
| `WorkGiver_Training` | `RimWorld.WorkGiver_Scanner` | 工作标签派发 |
| `PlaceWorker_ShootingRange` / `PlaceWorker_MartialArtsTarget` | `Verse.PlaceWorker` | 幽灵预览 |
| `Graphic_RandomMote` | `Verse.Graphic_Random` | 箭矢 mote |
| `TrainingFacility_Mod` | `Verse.Mod` | 设置界面 |
| `TrainingFacility_ModSettings` | `Verse.ModSettings` | 射击/近战经验倍率 |
| `Utility_PositionFinder` | — | `TryFindWatchBuildingPosition` / `FindAllWatchBuildingCells` |
| `Utility_MaxAllowedTrainingLevel` | — | `GetMaxAllowedTrainingLevel(Pawn)` + `Lerp` |
| `Utility_Hungry` / `Utility_Tired` | — | 饱食度/疲劳提前中断 |

### 从字段名能读出的设计

| 字段 | 推断的设计意图 |
|---|---|
| `skillLevelToPreventFriendlyFire` | 技能阈值以上不打友军 |
| `messageUsedStonesWasShown` | 拿石头当弹药的一次性提示（静态，只弹一次） |
| `restReductionForcedPerTick` | 强制扣休息量 |
| `weaponCheckResult` | 武器检查结果缓存（避免每 tick 重算） |
| `skillGainRateHeavyWeapon` | 重武器单独的经验倍率 |
| `autoRearm` + `CheckAutoRebuild(Map)` + `Kill()` 覆写 | 靶子被打爆后自动重建 |
| `nearbyPawnSearchCountdown` / `nearbyPawnFound` | 邻近单位轮询节流（避免每 tick 扫描） |
| `UpdateInterval`（静态） | 统一的 tick 节流间隔 |

> `JobDriver_*_NonJoy` 只是继承 `JobDriver_*` 的空壳类——
> 差异全在 JobDef 的数值上，C# 侧不重复。

---

## 五、跨版本维护策略（本记录的主要价值）

### 5.1 目录组织

**每个版本目录完全自包含**：

```
1.6/
  Assemblies/  Defs/  Languages/  Patches/  Sounds/  Textures/
```

- **没有 `Common/`**——即使 7 个版本要共享同一批语言文件，也照样各存一份
- **没有 `LoadFolders.xml`**

### 5.2 功能演进

| 版本 | Def 文件数 | 变化 |
|---|---|---|
| 1.0 – 1.2 | 9 | 仅娱乐设施（Joy） |
| 1.3 – 1.6 | 11 | **新增** `WorkTypeDefs/` + `WorkGiverDefs/`，接入工作标签 |
| 1.5 / 1.6 | 11 + `Patches/` | **新增** `Training_CE_Patch.xml` |

程序集体积随版本递增：
28.5 → 31.5 → 31.5 → 39.5 → 41.5 → 45 → **50.5** KB

### 5.3 最值得学的一点：1.5 → 1.6 的适配完全藏在 IL 内部

两项对比的结论：

1. **Def 层**：`1.5\Defs\ThingDefs\TrainingFacility_Buildings.xml` 与 `1.6` 的同名文件
   逐行 diff **完全一致**。
2. **程序集公开面**：1.5 与 1.6 各 26 个公开类型，
   **基类、方法签名、字段全部一致，零增零删零改动**。

→ 也就是说，作者在 1.6 的所有适配都发生在方法体内部，
   对外保持稳定的类型外观。

**为什么这很重要**：mod 之间的 C# 互操作依赖的是公开 API。
公开面稳定 = 别的 mod 跟着升级时不会崩。作者很可能是有意这么设计的。

> 与 `修改/美南烛/` 对比：ASEBI 是模板遗留，字段形状在 1.5/1.6 之间悄悄变了；
> 这个是主动维护，7 个大版本逐个跟上。

---

## 怎么验的

### 核验方法

1. 对 `1.6\Defs` 下全部 Def 引用做交叉引用，对照本机 `Data\` 全量 Def 库
2. 反射 `TrainingFacility.dll`：26 个公开类型的基类、方法、字段全量导出
3. 反射 `Assembly-CSharp.dll` 确认各基类真实存在
4. 反射比对 1.5 与 1.6 两个 DLL 的公开面差异

### 结果：零缺失引用

**Def 引用全部命中**：

`MinifiedThing`、`Light`、`Repair`、`Filth_RubbleBuilding`、`BuildingsJoy`、
`BulletImpact_Metal`、`Steel`、`WoodLog`

**C# 基类全部存在**：

`Verse.Building`、`Verse.PlaceWorker`、`Verse.Graphic_Random`、`Verse.Mod`、
`Verse.ModSettings`、`RimWorld.JobDriver_WatchBuilding`、
`RimWorld.JoyGiver_WatchBuilding`、`RimWorld.WorkGiver_Scanner`

`Gaming_Shooting` / `Gaming_MartialArts` 等是本 mod 自有的 JoyKindDef，不算外部引用。

**结论：与 1.6 完全兼容，无隐患。**

### 汉化

`Languages\ChineseSimplified\Keyed\TrainingFacility.xml` 质量很高，
连设置项的提示文字都译了：

> *此为获得技能经验值的倍率。要增加获得的经验值，请设置为大于 1；要减少则设置为小于 1。*

共 7 语（英/德/法/简中/繁中/俄/巴西葡），简中环境下体验完整。

---

## 七、两处小瑕疵

1. **`.png` 与 `.dds` 双份并存**（74 / 72）。
   但这里 **png 不是冗余**——png 平均约 7 KB、dds 21.5 KB，
   是作者有意保留的**贴图源图**（方便日后改贴图）。
   与 ASEBI 那份（png 280 KB 级、和 dds 内容重复）性质不同。
   真要瘦身应该删 dds，不是删 png。
2. **无 `Source/`**，只发编译产物。调试困难，也无法进仓库的 C# 单测流程。
   对比 ASEBI 连制作教程都随附，这个在"可学习性"上是减分项。

---

## 可复用结论

与具体 mod 无关、可直接用于其他 RimWorld mod 分析：

1. **`loadAfter` ≠ 运行时依赖。** 判定真依赖要看 DLL 的 `GetReferencedAssemblies()`。
   Haplo 用 `loadAfter` 而非 `modDependencies` 是刻意的，好处是缺依赖也能加载。

2. **确认 packageId 是否存在，要精确匹配整行。** 子串 grep 会命中别人的
   `loadAfter` 列表——本记录开头就踩了这个坑。

3. **`PatchOperationFindMod` 是"给别的 mod 让路"的标准写法。**
   本 mod 的 CE 补丁是干净的范例：条件匹配 → 只改自己的值 → 不影响其他环境。

4. **跨版本维护的两种质量分野：**
   - *被动型*（ASEBI）：字段形状在引擎升级中变了，mod 静默失效
   - *主动型*（本 mod）：Def 逐版本跟改，公开 API 保持稳定，适配藏在 IL 内
   **判别方法**：反射新旧两个 DLL 比公开面。公开面一致 = 作者在主动维护。

5. **没有 `Common/` 不代表维护偷懒。** 529 文件里语言文件占了大部分，
   7 份重复的语言文件换来的好处是每个版本目录可以整目录拷贝、不必解冲突。
   对"一次性下载直接用"的工坊 mod 反而更省心。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机验证运行表现*
*本 mod 无授权限制（非 ASEBI 那类禁再分发的 mod）*
