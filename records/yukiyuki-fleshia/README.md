# FLESHIA / 弗莱西雅 — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/6弗莱西雅/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\6弗莱西雅\` |
| mod 名 / packageId | FLESHIA / `yukiyuki.FLESHIA` |
| 作者 | yukiyuki |
| 工坊 | https://steamcommunity.com/sharedfiles/filedetails/?id=3459970098 |

> **⚠️ 禁再分发**。本目录只存结论，不收录 Def 原文与贴图。
> 系列基线问题清单见 `修改/美南烛/README.md`，此处只列本弹独有部分。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | **仅 1.6**（全系列最窄，也最诚实） |
| 结构 | `LoadFolders.xml` + `Common/` + `1.6/` —— **系列里第一个用 LoadFolders 的** |
| 规模 | 36 文件 / 3.25 MB |
| **硬依赖** | `OskarPotocki.VanillaFactionsExpanded.Core`（VEF 框架）—— 已声明 |
| 依赖状态 | ✅ 已装（`2023507013`） |
| 语言 | ⚠️ **只有 `Languages\English\`**，无简中 |

```
LoadFolders.xml                                          ← 新增
1.6/Assemblies/Yukiyuki.dll        6.0 KB               ← 系列第一个 C# 程序集
1.6/Defs/AbilityDef/AbilityDef.xml 3.9 KB               ← 新增，凝血技能
1.6/Defs/MVCF/SM_MVCF.ModDef.xml
1.6/Defs/Projectiles/Projectile_Animal.xml               ← liquid 弹丸
1.6/Defs/SoundDefs/SoundDef.xml
1.6/Defs/ThingDefs_Races/Races_Animal_FLESHIA.xml
Common/Sounds/SE/liquid.mp3
Common/Textures/AnimalProjectile/liquid.dds.zstd
Common/Textures/Things/Mote/Blood/Spatter.dds.zstd       ← 新增，血迹 fleck
Common/Textures/Things/Pawn/Animal/FLESHIA_*   8 组双份
Common/Textures/UI/Abilities/FS_Aggregation_Icon.dds.zstd
Languages/English/DefInjected/…（4 个 Unknown.xml）
```

描述：*"攻撃や保護のため常時使用する体液を補うため多めのエサを必要とします"*——
体液是它的弹药与凝血媒介，所以**饿得快**。

---

## 二、`LoadFolders.xml`（系列首次）

```xml
<loadFolders>
  <v1.6>
    <li>/</li>
    <li>Common</li>
    <li>1.6</li>
  </v1.6>
</loadFolders>
```

只声明 1.6，加载根目录 + `Common` + `1.6`。因为没有其他版本条目，
**加载顺序上不会出现重复**：根目录的 `Languages/` 提供英文，
`Common/` 提供贴图音效，`1.6/` 提供 Def 与 DLL。

> **与本仓库约定冲突**：仓库 `AGENTS.md` 写明"**避免用 LoadFolders.xml**"。
> 这里是系列里唯一用到的一次。若要把本 mod 收进仓库，需先决定是改造成
> 纯版本目录（只保留 `1.6/`，去掉 LoadFolders）还是在约定里开例外。

---

## 三、`Yukiyuki.dll` —— 系列第一个 C# 程序集

反射结果：程序集 `Yukiyuki 1.0.0.0`，**只引用 3 个程序集**
（`mscorlib` / `Assembly-CSharp` / `UnityEngine.CoreModule`），共 5 个类型，
其中 3 个是编译器生成的属性，**真正的手写代码只有 2 个类**：

```csharp
Yukiyuki.CompAbilityEffect_Aggregation : RimWorld.CompAbilityEffect
    void   Apply()
    bool   Valid()

Yukiyuki.CompProperties_AbilityAggregation : RimWorld.CompProperties_AbilityEffect
    FloatRange tendQualityRange
    HediffDef  postAggregationHediffDef
```

依赖干净、代码量极小——**只为凝血技能写了一个 AbilityEffect**。
这比前几弹"抄 Odyssey 的 TrainableDef"要克制得多，是值得肯定的写法。

---

## 它是什么

描述里的 *"体液を使用した凝血能力"*。用 `CompAbilityEffect` 实现——
比 Harmony 补丁轻得多，不碰游戏逻辑。

| 项 | 值 |
|---|---|
| verbClass | `Verb_CastAbilityTouch`（`AbilityTouchBase` 父类，**Anomaly 原版**，非 VEF） |
| jobDef | `CastAbilityOnThingMelee`（Core ✅） |
| 施法时间 | 1s |
| 冷却 | **160000~180000 ticks ≈ 2.2~2.5 RimWorld 天** |
| 治疗质量 | `tendQualityRange 0.4~0.8` |
| 能力要求 | `Manipulation`（`CompProperties_AbilityRequiresCapacity`） |
| 目标 | 人 ✅ 动物 ✅ / 自身 ❌ 建筑 ❌ 机械体 ❌ |
| `casterMustBeCapableOfViolence` | **false**（友方治疗，不算暴力行为） |
| `stunTargetWhileCasting` | true（施法期间定住目标） |

配套三件套：

- `FS_BleedAggregation`（EffecterDef）：两层 `SubEffecter_SprayerContinuous` 持续喷血粒子
- `FS_Blood`（FleckDef）：`ParentName="FleckBase_Thrown"` ✅（Core 原版）
  → `Things/Mote/Blood/Spatter` ✅ 本 mod 确实带了贴图
- `FS_Mote_Stencil`（ThingDef）：`ParentName="MoteBase"` ✅，
  用 `Graphic_PawnBodySilhouette` + `PawnSilhouetteStencil` shader 做目标剪影

> **XML 只设了 `tendQualityRange`，没设 `postAggregationHediffDef`。**
> 后者是可选的（HediffDef 可为 null），所以不是 bug，但意味着凝血后
> 不会附加额外的长期状态。

---

## 五、⚠️ 一张缺失的贴图

`FS_Mote_Stencil` 的 graphicData 写的是：

```xml
<texPath>Things/Mote/Transparent</texPath>
```

但本 mod 的 `Common\Textures\Things\Mote\` 下**只有 `Blood\Spatter.*`**，
**没有 `Transparent.*`**。

→ 施法时的目标剪影贴图**解析不到**，游戏会回退到默认贴图或报错。
这是本弹唯一实际缺失的资源。

修法二选一：补一张 `Things/Mote/Transparent.dds(.zstd)`，
或把 `texPath` 改成 `Things/Mote/Blood/Spatter`（若作者本意就是用那张）。

---

## 怎么验的

指纹扫描：`wildBiomes=YES` · **`trainableTags=no`** · `canArriveManhunter=YES` ·
`verbs=YES` · `nameOnTameChance=YES`

**进步**：`<trainableTags>` **被删掉了**——全系列第一次。
说明作者在逐步清理模板遗留。

仍然存在：

1. **`<wildBiomes>` 扁平写法静默失效**
2. **`<canArriveManhunter/>` 空标签**
3. **`nameOnTameChance` 1** —— 模板说明书建议 ≤0.9（第 3、5 弹也犯）
4. **MVCF.ModDef `MVSM` 第三处重复**（第 3、5、6 弹），且 **MVCF 仍未安装**
   → `<verbs>` 远程攻击很可能不工作（`FS_Aggregation` 是 Ability，不受影响）
5. **`.png` + `.dds.zstd` 双份** —— 8 组 + 2 张零散，约 **1.8 MB 冗余**
6. ~~**`PublishedFileId.txt` 0 字节**~~ —— **撤销**：实测为 `3459970098`（10 字节，正常）
7. **无 TrainableDef 抄件** —— 本弹没抄 Attack/Comfort/Dig/Forage，
   凝血走 Ability 路线。**这是本系列最干净的一处**

---

## 七、语言文件的一个小坑

`Languages\English\` 下 4 个翻译文件的文件名全是 **`Unknown.xml`**
（`MVCF.ModDef\Unknown.xml`、`PawnKindDef\Unknown.xml` 等）。

这是翻译工具在 Def 类型无法识别时生成的占位名——说明**翻译工具当时不认识
`Yukiyuki.CompProperties_AbilityAggregation` 这种自定义 Def 类型**。
对英文本身无害，但简体中文包（`ChinesePack.yukiyuki.animalgirls`）
很可能同样没能翻译到凝血技能相关的字段。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| 高 | **补 `Things/Mote/Transparent` 贴图**，或改 `FS_Mote_Stencil` 的 `texPath` |
| 高 | 装 MVCF / 补依赖声明（与第 3、5 弹同） |
| 高 | 重写 `<wildBiomes>` |
| 中 | `<canArriveManhunter/>` 显式写 `true` |
| 中 | `nameOnTameChance` 1 → ≤0.9 |
| 中 | 简中环境下凝血技能的 description 是中英混排（`"Aggregation the bleed to stop the bleeding of a designated colonist(指定した対象を凝血させます)"`），建议补 `Languages/ChineseSimplified` |
| 低 | 三个 `MVSM` 重复 Def 改唯一 defName |
| 低 | ~~补 `PublishedFileId.txt`~~ —— **撤销**；删冗余 `.png`（约省 1.8 MB） |

---

## 可复用结论

1. **想给动物加技能，`CompAbilityEffect` + `CompProperties_*` 比 Harmony 补丁更轻。**
   本弹 6 KB 的 DLL 只改技能效果，不碰任何游戏逻辑，是很克制的扩展方式。
   结构：`<li Class="Yukiyuki.CompProperties_X">` 挂到 `AbilityDef.comps`。

2. **凝血类治疗能力用 `CompProperties_AbilityRequiresCapacity` 挂能力门槛**
   （本例 Manipulation），并把 `casterMustBeCapableOfViolence` 设 false，
   这样友方治疗不会让 AI 判定为暴力行为。

3. **翻译工具对自定义 Def 类型会生成 `Unknown.xml`。**
   看到文件名是 `Unknown.xml` 的 DefInjected 文件，说明翻译器不认那个 Def 类型，
   对应字段很可能没被翻译。

4. **作者在逐步清理模板遗留**：`trainableTags` 从第 1/2/3/4/5 弹都有，
   到第 6 弹被删除。**批量分析必须逐弹扫指纹**，不能按前几弹推断。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），凝血技能未在游戏内实机验证*
