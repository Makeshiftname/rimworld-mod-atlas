# BORUM / 雪绒兽 — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/2 雪绒兽/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\2 雪绒兽\` |
| mod 名 / packageId | BORUM / `yukiyuki.BORUM` |
| 作者 | yukiyuki |

> **⚠️ 授权限制：禁止再分发。**
> `About.xml` 明文写有 *"Redistribution of this MOD data is prohibited."* / *"当MODの再配布を禁じます"*。
> 与 `修改/美南烛/` 同源同限制，本目录**只存结论，不收录其 Def 原文与贴图**。

> **本 mod 与 `修改/美南烛/`（ASEBI）同门同源**：同一作者、同一"动物 mod 制作模板"底子、
> 同样的 `AttackTrainable` / `ComfortTrainable` 抄件、同样的 `.png` + `.dds.zstd` 双份贴图。
> ASEBI 那次做完 1.6 兼容性核验的方法，**在本次可直接复用**——
> 所以本记录不重复核验过程，只在 §四 补做本 mod 独有的那几项。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | 1.0 – 1.6（实际只适配到 ~1.4，同 ASEBI） |
| 结构 | **无版本目录**，扁平 `Defs/` + `Textures/`（同 ASEBI） |
| 规模 | 3 个 XML + 14 个贴图 |
| 依赖 | 无（除游戏本体与 DLC 外无外部 mod 依赖） |
| 语言 | **无 `Languages/`** → 简中环境下描述是日文（同 ASEBI） |

### 文件构成

```
About/About.xml                          1.0 KB
About/preview.png                        336.1 KB
About/PublishedFileId.txt                2958418658（10 字节，正常）
Defs/ThingDefs_Races/Races_Animal_BORUM.xml      12.3 KB
Defs/TrainableDefs/BORUM_AttackTrainable.xml      0.5 KB
Defs/TrainableDefs/BORUM_ComfortTrainable.xml     0.4 KB
Textures/Things/Pawn/Animal/BORUM_{south,north,east}.{png,dds.zstd}
Textures/Things/Pawn/Animal/BORUM_Bones.{png,dds.zstd}
Textures/Things/Pawn/Animal/BORUMPack_{south,north,east}.{png,dds.zstd}   ← 驮兽叠层
```

> `PublishedFileId.txt` 内容为 `2958418658`（10 字节，正常）。
> （本节初稿曾误记为"0 字节空文件"，是目录列表里 KB 四舍五入显示 0 导致的误读，已更正。）

---

## 它是什么

作者给的人设与 ASEBI 同源：*"寒冷地に生息する生物で異界から来た"何か"と既存の生物との
交配実験によって作られた生物"*——来自异界的"某物"与现有生物杂交实验的产物。

描述里那句是它的角色注解：

> *"所詮は混ざりものなので角は取れません。質が悪いのでしょう。"*
> （反正是混血，角是去不掉的。品质大概也不好吧。）

这句话直接解释了它为什么用 `Leather_Thrumbo`——原版大虫（Thrumbo）的皮革在游戏里
本来就是"品质不佳"的设定材料。作者把这个吐槽落到了实际配置上，是个小巧的呼应。

攻击工具名也印证了"混血"人设：ASEBI 是**左/右触腕**（软体、壳兽），
BORUM 是**左/右大爪**（爪类、兽形）。

---

## 三、与 ASEBI 的数值对照

同作者同模板，同一套骨架，只改了数值。下表左 ASEBI / 右 BORUM：

| 项 | ASEBI | BORUM | 差异意图 |
|---|---|---|---|
| **温度区间** | −15 ~ 65 | **−70 ~ 45** | 严寒种，针叶树林/雪原 |
| MoveSpeed | 4.5 | **6** | 快于人（4） |
| 钝器抗性 | 0.15 | **0.35** | 更耐打 |
| 灼热抗性 | 0.10 | **0.20** | — |
| 尖锐抗性 | 1.0 | 1.0 | 同样"横推一切" |
| 可燃性 | 0.50 | **0.20** | 更难点燃 |
| MeatAmount | 80 | 50 | — |
| LeatherAmount | 80 | 50 | — |
| leatherDef | `Leather_Heavy` | **`Leather_Thrumbo`** | 见 §二 |
| baseHealthScale | 7.0 | 6.0 | — |
| Mass | 120 | 110 | — |
| 攻击 power | 10 | 7 | — |
| 攻击冷却 | 1.25 s | **1.0 s** | 输出更密 |
| 击晕（surpriseAttack） | 30 | 30 | 同 |
| baseBodySize / petness / wildness / hunger | 1.7 / 0.4 / 0.30 / 0.2 | 1.7 / 0.4 / 0.30 / 0.2 | 完全一致 |
| 产奶 | 每 2 天 40 | **每 5 天 80** | 总量翻倍、频率减半 |
| 怀孕天数 | 15 | 20 | — |
| 寿命 | 50 | 50 | — |
| 群组大小 | 1–3 | 1–2 | — |
| maxGenerationAge | 98 | **10** | 差异最大的一项 |
| **manhunterOnDamageChance** | *（未设）* | **0.5** | **BORUM 独有的修正** |
| tradeTags | AnimalExotic + AnimalInsect | **AnimalExotic** | 少了虫类标签 |
| 音效 | SmallScratch | SmallScratch | 同 |
| drawSize | 1.5 | 1.5 | — |

**唯一一处相对 ASEBI 的实质改进**：BORUM 显式设置了
`<manhunterOnDamageChance>0.5</manhunterOnDamageChance>`，ASEBI 没有这一项。
（原版大型食肉兽/巨蛛常用 0.1–0.35，0.5 相当高——被打就还手的概率过半。）

其余全部是同一模板的换皮。

---

## 怎么验的

### ✅ 本 mod 独有的待验项，已通过

| 项 | 结果 |
|---|---|
| `leatherDef = Leather_Thrumbo` | **存在**（`Core\Defs\ThingDefs_Items\Items_Resource_Stuff_Leather.xml`）。ASEBI 用的是 `Leather_Heavy`，本项是唯一需要单独查的新引用 |
| `Release`（抄件里的 prerequisite） | 存在（`Core\Defs\TrainableDefs\Trainables.xml`） |

### ⚠️ 继承自模板、与 ASEBI 完全相同的问题

复用 ASEBI 那次已完成的 IL 核验结论，此处不再重跑：

1. **`<wildBiomes>` 扁平写法失效** —— 1.6 中 `Verse.RaceProperties.wildBiomes`
   类型是 `List<RimWorld.AnimalBiomeRecord>`，记录为 `{BiomeDef biome; float commonality;}`；
   自定义加载器 `LoadDataFromXmlCustom` 只有 38 字节、只引用 `"biome"` 字面量，
   期望的是 `<biome>` 子元素。BORUM 那 12 行扁平写法同样拿不到 biome 值，
   **且因为有自定义加载器，连格式错误都不会报——静默失效**。
   → 本 mod 描述里"寒冷regions 活动"的设定同样不生效。

   修正写法：

   ```xml
   <wildBiomes>
     <li><biome>SeaIce</biome><commonality>0.02</commonality></li>
     <li><biome>BorealForest</biome><commonality>0.08</commonality></li>
     <li><biome>ColdBog</biome><commonality>0.08</commonality></li>
     ...
   </wildBiomes>
   ```

2. **`<trainableTags><li>Attack</li></trainableTags>` 是死配置** ——
   `trainableTags` / `untrainableTags` / `TrainableDef.tags` 三字段在 1.6 程序集里
   **零读取点**；合法标签只有 `Basic` / `Combat` / `Help` / `Work`，
   `Attack` 也不是标签名（攻击训练的 defName 是 `Release`，标签 `Combat`）。
   → 无副作用，可删。

3. **`<canArriveManhunter/>` 空标签** —— 本 mod 用的是**自闭合**写法
   （ASEBI 是 `<canArriveManhunter></canArriveManhunter>`），性质相同：
   该字段是普通 `bool`，唯一消费点 `RimWorld.AggressiveAnimalIncidentUtility::CanArriveManhunter`。
   模板注释说"不写=true，会出现在人潮里"，但空标签既不是"不写"也没给出明确值。
   Verse 在 `DirectXmlToObject` 里既不调 `Convert.ToBoolean` 也不调 `XmlConvert.ToBoolean`，
   回退行为未确认。**建议显式写 `<canArriveManhunter>true</canArriveManhunter>`**。

4. **`AttackTarget` / `Comfort` 是照抄 Odyssey 原版** ——
   实测 BORUM 的两个文件与 ASEBI 的**逐行完全相同**，
   且与 `Data\Odyssey\Defs\Misc\Trainables.xml` 仅 `AttackTarget` 的 description
   差半句（多了 "that its master can see"）。
   原版正确做法是 `<li MayRequire="Ludeon.RimWorld.Odyssey">AttackTarget</li>`
   （全库 570 处这种写法），本 mod 自带副本属冗余，无害。

5. **`.png` 与 `.dds.zstd` 双份并存** —— 14 个贴图文件里 7 组双份，
   合计约 **1.6 MB 冗余**。引擎优先读 `.dds.zstd`，`.png` 用不上。
   （与 `717575199-MiscTraining` 不同——那份的 png 是有意的源图保留，这份不是，
   因为这里的 png 达 180–250 KB 级，和 dds 内容重复。）

6. **无 `Languages/`** —— 简中界面下走英文 `label` + 日文 `description`。

### ✅ 无其他风险

- `AnimalThingBase` / `AnimalKindBase`：存在（`Core\Defs\ThingDefs_Races\Races_Animal_Base.xml`，
  用 `Name=` 而非 `defName=` 声明抽象父类）
- `Milk` / `AnimalBaby`·`Juvenile`·`Adult` / `Blunt` / `Stun` /
  `Pawn_Melee_SmallScratch_*`：全部存在
- `foodType: OmnivoreAnimal`、`trainability: Advanced`、`specialTrainables`：有效
- `wildGroupSize` 的 `<min>/<max>`：字段仍是 `Verse.IntRange`，旧写法属标准字段映射

---

## 修改建议

与 ASEBI 同款，按优先级：

| 优先级 | 事项 |
|---|---|
| 高 | **重写 `<wildBiomes>`** 为 `<li><biome>…</biome><commonality>…</commonality></li>`——唯一的真功能缺失，"寒冷地区生物"的设定现在没生效 |
| 高 | `<canArriveManhunter/>` 显式写 `true` |
| 中 | 删除 `<trainableTags>` 整块 |
| 中 | 删除两个 TrainableDef 文件，改用 `<li MayRequire="Ludeon.RimWorld.Odyssey">` |
| 低 | ~~补 `PublishedFileId.txt`~~ —— **撤销**：实测内容为 `2958418658`，本来就有 |
| 低 | 删除冗余 `.png`（约省 1.6 MB） |

改动只涉及 `Defs/`，**不触及贴图**。因禁再分发，仅供本地自用。

---

## 可复用结论

1. **同作者同模板的一批 mod 可以共享一次核验。** ASEBI 那次做完 IL 级验证后，
   BORUM 只需补查它独有的引用（`Leather_Thrumbo`）即可——
   结构、字段、缺陷全部同源。**遇到同 packageId 前缀 / 同作者 / 同文件命名的 mod 优先考虑合并分析。**

2. **`<canArriveManhunter/>` 与 `<canArriveManhunter></canArriveManhunter>` 是同一类问题**，
   模板作者在自闭合和成对标签之间摇摆，但结果一样：都是空 bool，行为未定。

3. **禁再分发的 mod 适合放 `修改/` 做笔记，不适合进 `收集/` 归档。**
   两份同源 mod（ASEBI / BORUM）的记录可以互相交叉引用，避免重复。

4. **⚠️ 目录列表里的文件大小会被 KB 四舍五入，10 字节显示为 `0`。**
   本记录初稿据此误判 `PublishedFileId.txt` 是空文件，实际是正常的 10 字节工坊 ID。
   → **要判断文件是否为空，读字节数（`[System.IO.File]::ReadAllBytes($p).Length`），
   不要看 KB 化的列表输出。**

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机验证*
*核验方式：复用 `修改/美南烛/README.md` 已完成的 IL 级验证，仅补查本 mod 独有引用*
