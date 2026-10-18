# ABYSS / 阿比斯 — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/5 阿比斯/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\5 阿比斯\` |
| mod 名 / packageId | ABYSS / `yukiyuki.ABYSS` |
| 作者 | yukiyuki |
| 工坊 | https://steamcommunity.com/sharedfiles/filedetails/?id=3460293910 |

> **⚠️ 禁再分发**。本目录只存结论，不收录 Def 原文与贴图。
> 系列基线问题清单见 `修改/美南烛/README.md`，此处只列本弹独有部分。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | **1.5 / 1.6** |
| 结构 | `Common/` + `1.6/`（**有正式版本目录**，比第 3 弹规范） |
| 规模 | 29 文件 / 3.03 MB |
| **硬依赖** | `OskarPotocki.VanillaFactionsExpanded.Core`（VEF 框架）——**已声明**，`loadAfter` 同 |
| 依赖状态 | ✅ **已装**（目录 `2023507013`，另有汉化包 `2024971883`） |
| 语言 | 无 `Languages/` |

```
Common/Sounds/SE/ABYSS_Spear.mp3                     ← 音效是 mp3（第 3 弹用 wav）
Common/Textures/AnimalProjectile/ABYSS_Spear.{png,dds.zstd}
Common/Textures/Things/Pawn/Animal/ABYSS_*           8 组双份
1.6/Defs/MVCF/SM_MVCF.ModDef.xml
1.6/Defs/Projectiles/Projectile_Animal.xml
1.6/Defs/Quest/IncidentDef.xml                        ← 新增
1.6/Defs/Quest/Script_AbyssCargo.xml                 ← 新增，2.5 KB
1.6/Defs/SoundDefs/SoundDef.xml
1.6/Defs/ThingDefs_Races/Races_Animal_ABYSS.xml
1.6/Defs/TrainableDefs/ABYSS_{Attack,Comfort}Trainable.xml
1.6/Patches/Additional_Storyteller.xml               ← 新增
```

描述定位：*"今後その仲間達を追加していきます"* —— 这是系列里的**续作起点**，
后续成员会以同一 mod 的形式继续追加。出现率低、范围广、全都能进商队。

---

## 它是什么

这是前四弹都没有的东西——**mod 主动改写叙事层，不只是加一只动物**。

三件套：

**① `IncidentDef`（不随机触发）**

```xml
<IncidentDef ParentName="GiveQuestBase">
  <defName>GiveQuest_ABYSS_Join</defName>
  <questScriptDef>ABYSS_Join</questScriptDef>
  <baseChance>0</baseChance>   <!-- given by a special storyteller comp -->
</IncidentDef>
```

`baseChance 0` = 从随机事件池里摘掉，只能由专属 comp 触发。

**② `Additional_Storyteller.xml`：给 `BaseStoryteller` 挂一个一次性 comp**

```xml
<Operation Class="PatchOperationAdd">
  <xpath>Defs/StorytellerDef[@Name="BaseStoryteller"]/comps</xpath>
  <value>
    <li Class="StorytellerCompProperties_SingleOnceFixed">
      <fireAfterDaysPassed>60</fireAfterDaysPassed>   <!-- 1 years -->
      <incident MayRequire="Ludeon.RimWorld.Royalty">GiveQuest_ABYSS_Join</incident>
      <skipIfOnExtremeBiome>false</skipIfOnExtremeBiome>
      <minColonistCount>3</minColonistCount>
      <allowedTargetTags><li>World</li></allowedTargetTags>
    </li>
  </value>
</Operation>
```

设计要点：

- 打在 **`BaseStoryteller`** 上 → **所有叙事者**（Cassandra / Randy / Adrian…）都会触发
- `SingleOnceFixed` + 第 60 天 → **1 个 RimWorld 年**（游戏内 1 年 = 60 天）触发一次，永不重复
- `minColonistCount 3` → 至少 3 个殖民者才触发（避免开局触发）
- `MayRequire="Ludeon.RimWorld.Royalty"` → 缺 Royalty 时整个 `<li>` 被丢弃

**核验**：`BaseStoryteller` ✅ 存在于 `Core\Defs\Storyteller\Storytellers.xml`
（用 `Name=` 声明的抽象父类）；`GiveQuestBase` ✅ 存在于
`Core\Defs\Storyteller\Incidents_World_Quests.xml`。**xpath 两端都接得上。**

---

## 三、MVCF 问题（与第 3 弹相同，且 defName 撞车）

`1.6/Defs/MVCF/SM_MVCF.ModDef.xml` 与第 3 弹**内容完全相同**，
`defName` 同为 **`MVSM`** —— 系列第 3、5、6 弹**三处重复定义同一个 Def**。

内容一致所以无害（后加载的覆盖先加载的，值一样），
但这是个隐患：将来任一弹要单独改 label 或特性列表就会互相覆盖。

**真正的问题没变：MVCF 框架本身没装。**

- `MVCF.ModDef` 类型不存在 → 该 XML 报错跳过
- `RangedAnimals` 不激活 → **远程攻击不工作**
- 本弹的跨版本适配层整体失效

与第 3 弹不同的是：**本弹正确声明了 VEF 依赖**，却漏了 MVCF 依赖。
说明作者知道要写依赖，只是漏了这一条。

---

## 怎么验的

指纹扫描：`wildBiomes=YES` · `trainableTags=YES` · `canArriveManhunter=YES` ·
`verbs=YES` · `nameOnTameChance=YES`

1. **`<wildBiomes>` 扁平写法静默失效**
2. **`<trainableTags><li>Attack</li>` 死配置**
3. **`<canArriveManhunter/>` 空标签**
4. **`.png` + `.dds.zstd` 双份** —— 8 组，约 **1.7 MB 冗余**
5. ~~**`PublishedFileId.txt` 0 字节**~~ —— **撤销**：实测为 `3460293910`（10 字节，正常）
6. **无 `Languages/`**
7. **TrainableDef 抄件 ×2**（Attack / Comfort）
8. **`nameOnTameChance` 被设成 1** —— 模板自带的 `2.race2.txt` 明确建议
   *"0～0.9 の範囲にとどめておくといいか"*，作者偏用 1.0
   （第 3 弹也犯了这个，第 1、2、4 弹没写这一项）

> 本弹的 `<verbs>` 字段与 `Verse.Verb_Shoot` 都合法，
> 但和第 3 弹一样受制于缺失的 MVCF。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| 高 | **装 MVCF**，或在 `About.xml` 补 MVCF 依赖 / 给 `SM_MVCF.ModDef.xml` 加 `MayRequire` |
| 高 | 重写 `<wildBiomes>` |
| 高 | `<canArriveManhunter/>` 显式写 `true` |
| 中 | `nameOnTameChance` 1 → ≤0.9（模板自己的建议） |
| 中 | 删 `<trainableTags>`；删两个 TrainableDef 抄件改用 `MayRequire` |
| 中 | 任务链的 `BaseStoryteller` 补丁建议加 `PatchOperationFindMod` 保护（避免与其他改叙事者的 mod 冲突） |
| 低 | 三个 `MVSM` 重复 Def：建议后续弹改成各自唯一 defName |
| 低 | ~~补 `PublishedFileId.txt`~~ —— **撤销**；删冗余 `.png`（约省 1.7 MB） |

任务链本身（§二）**结构正确、引用齐全，无需修改**。

---

## 可复用结论

1. **给叙事者打补丁要打在 `BaseStoryteller` 上** 才能覆盖全部叙事者，
   且用 `StorytellerCompProperties_SingleOnceFixed` + `fireAfterDaysPassed`
   就能实现"开局第 N 天触发一次"。`MayRequire` 是 DLC 依赖的标准做法。

2. **`baseChance 0` + 专属 comp** 是"只由特定条件触发的事件"的正确写法，
   避免它混进随机事件池。

3. **同一系列多个 mod 定义同名 Def 会互相覆盖。** 本系列第 3/5/6 弹都定义了
   `MVCF.ModDef` → `MVSM`。当前无害，但**一旦内容分叉就会出隐蔽的覆盖问题**。

4. **作者会为 VEF 写依赖、但会漏 MVCF** —— 同一个 mod 里两种依赖写法并存，
   所以不能假设"作者写了依赖就一定写全了"。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），任务链未在游戏内实机触发验证*
