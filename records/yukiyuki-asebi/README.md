# 美南烛 / ASEBI — 分析记录

> **⚠️ 授权限制：禁止再分发。**
> 本 mod 的 `About/About.xml` 明文写有 *"Redistribution of this MOD data is prohibited."* /
> *"当MODの再配布を禁じます"*。
> 因此本目录**只保存分析结论与修改建议**，**不收录其 Def 原文、贴图或其他 mod 数据**。
> 正文引用的是字段名与数值（用于说明机制），不是对原文件的搬运。
> 该 mod 不适合按仓库 `收集/` 的常规方式归档或发布，仅供本地自用与学习。

---

## 身份卡

| 项 | 值 |
|---|---|
| 目录名 | `1 美南烛` |
| packageId | `yukiyuki.ASEBI` |
| mod 名 / 作者 | ASEBI / yukiyuki |
| 工坊 ID | 2956633535（`About/PublishedFileId.txt`） |
| 声明支持版本 | 1.0 – 1.6 |
| 实际适配 | ≈1.4 时代（见第四节） |
| 本地游戏版本 | RimWorld 1.6.9655.19392（Core + Ideology + Anomaly + Biotech + Royalty + **Odyssey**） |
| 类型 | 纯 XML 单种族（standalone 类），无 C#、无 Harmony |
| 源码位置 | `F:\Games\GBL\rimworld\Mods\1 美南烛` |

### 文件构成

```
About/About.xml                     作者、版本声明、禁改声明
About/preview.png                   预览图（娘化插画，非游戏内截图）
About/PublishedFileId.txt
Defs/ThingDefs_Races/Races_Animal_ASEBI.xml   ★ 主体：ThingDef ASEBI + PawnKindDef ASEBI
Defs/ThingDefs_Races/1.race1.txt     ← 模板教学备忘（Shift-JIS）
Defs/ThingDefs_Races/2.race2.txt     ← 模板教学备忘（Shift-JIS）
Defs/ThingDefs_Races/3.Pawnkind.txt  ← 模板教学备忘（Shift-JIS）
Defs/TrainableDefs/ASEBI_AttackTrainable.xml  见 §4.2
Defs/TrainableDefs/ASEBI_ComfortTrainable.xml 见 §4.2
Textures/Things/Pawn/Animal/ASEBI_{south,north,east}.{png,dds.zstd}
Textures/Things/Pawn/Animal/ASEBI_Bones.{png,dds.zstd}       干尸（dessicated）
Textures/Things/Pawn/Animal/ASEBIPack_{south,north,east}.{png,dds.zstd}  驮兽叠层
Textures/.../グラの種類メモ.txt      ← 贴图规范备忘（Shift-JIS）
初心者の方向け説明書.txt              ← 模板原版说明书（Shift-JIS）
```

无 `Languages/` 目录。

---

## 它是什么

这是本 mod 最有价值的一点——**作者把「动物 mod 制作模板」直接改成了发布品**。

`初心者の方向け説明書.txt`（按 Shift-JIS 解码）通篇在教读者怎么把模板里的 `XXXX` 批量替换成 `MickeyMouse`，
连常见错误示例都是模板原文：`<race>MickeyMouse</race>` 与 `<defs>MickeyMous</defs>`（少个 e），
教程参考 `http://seesaawiki.jp/rimworld/`，求助指向推特 `@uniinu_steam`。

`Defs/ThingDefs_Races/` 下的 `1.race1.txt` / `2.race2.txt` / `3.Pawnkind.txt` 是同一套模板的字段教学备忘
（statBases / race / PawnKindDef 三块）。它们被改名成 `.txt` 而不是 `.xml`，**目的就是让游戏不去解析它们**。

作者实际的改动只有三处：把 MickeyMouse 换成 ASEBI、加一张娘化贴图、覆写了一套战斗/属性数值。
XML 注释密度极高（逐字段日文说明），是少见的"能完整读懂作者意图"的 mod。

> **易踩的坑**：这四个 `.txt` 是 **Shift-JIS** 编码。用 `read` 工具或 UTF-8 读会全是乱码，
> 必须 `[System.Text.Encoding]::GetEncoding(932)` 转码。

---

## 三、数值设计解读

作者在注释里直说了设计意图：
*"華奢なモンスター娘なのに体重120ｋｇとかいやだ！ってRPにこだわりたい人向け。僕は拘ります。"*
（为了坚持"娇小魔物娘却有 120kg 体重"的 RP）

核心是**外观萌、数值按巨兽配**：

| 维度 | 配置 | 参照（1.6 原版） |
|---|---|---|
| 体力 | `baseHealthScale 7.0` | 熊 1.3；犀牛/巨兽 8.0 |
| 体格 | `baseBodySize 1.7` | 远超救援门槛 0.65 → **可驮运、可抬伤员** |
| 体重 | `Mass 120` | 远超 `baseBodySize 1.7` 的常规配比 |
| 战斗力 | `combatPower 15` | 兔 33 / 鸡 45 / 熊 200（**偏低**） |
| 尖锐抗性 | `ArmorRating_Sharp 1.0` | 枪、剑、爪在 1.6 均算穿刺 → **等于对远程+近战近乎全免疫** |
| 钝器 / 灼热 | `0.15` / `0.10` | 基本不挡 |
| 移动 | `MoveSpeed 4.5` | 人 = 4 |
| 屠宰 | 肉 80 / 皮 80（`leatherDef = Leather_Heavy`） | 产能型宠物 |
| 产奶 | 每 2 天 40 单位，`milkFemaleOnly=false` | **公母都能挤** |
| 驯服风险 | `manhunterOnTameFailChance 0.5` | 一半概率驯服当场狂暴 |
| 猎物豁免 | `canBePredatorPrey=false` | 猛兽不把它当猎物 |
| 繁殖 | 怀孕 15 天 / 寿命 50 年 / 野生群组 1–3 | — |
| 训练 | `Advanced`，可学「指定攻击目标」「安慰」 | — |
| 贸易标签 | `AnimalExotic` + `AnimalInsect` | 异域商人只收购；带虫类标签则可能被虫商带来 |

`trainability = Advanced` + `specialTrainables` 在 1.6 下确认有效（见 §4 有效项）。

---

## 怎么验的

### 核验方法（可复现）

1. 把 mod 里每个 **Def 引用**和**字段名**，拿本机 `Data\` 下全量 1558 个 Def 文件做文本比对；
2. 反射 `RimWorldWin64_Data\Managed\Assembly-CSharp.dll`，读 `Verse.RaceProperties` /
   `Verse.PawnKindDef` / `RimWorld.TrainableDef` 的**真实字段表与类型**；
3. 扫描 IL：对关键字段做 `ldfld` 全程序集读取点定位，确认"这个字段现在还有没有人用"；
   同时解出 `DirectXmlToObject` 的报错字符串，确认列表节点的合法写法。

> 第 3 步的扫描器做过**阳性对照**：`wildBiomes` 命中 1 处、`petness` 7 处、
> `specialTrainables` 8 处、`canArriveManhunter` 1 处。阳性对照通过后，
> `trainableTags` 等字段的 **0 命中**结论才可信。

### ✅ 确认有效

| 项 | 1.6 现状 |
|---|---|
| `ParentName="AnimalThingBase"` / `"AnimalKindBase"` | 存在。位于 `Core\Defs\ThingDefs_Races\Races_Animal_Base.xml`，用 `Name=` 而非 `defName=` 声明抽象父类 → **按 defName 文本 grep 会漏掉**，别据此判断缺失 |
| `Leather_Heavy` / `Milk` | 存在 |
| `AnimalBaby` / `AnimalJuvenile` / `AnimalAdult` | 存在（`Core\Defs\Misc\LifeStageDefs\LifeStages.xml`） |
| `Blunt` / `Stun` / `Pawn_Melee_SmallScratch_*` | 全部存在 |
| `foodType: OmnivoreAnimal` | 有效，`FoodTypeFlags` 枚举成员仍在 |
| `trainability: Advanced` + `specialTrainables` | 有效。8 个消费点，含 `RimWorld.Pawn_TrainingTracker::CanAssignToTrain` |
| `tradeTags` | 是字符串列表，本就不需要对应 Def 存在 |
| `wildGroupSize` 的 `<min>/<max>` | 字段仍是 `Verse.IntRange`，旧写法属标准字段映射。原版 1.6 已改用紧凑串 `3~7`，但那只是风格变化 |

### ⚠️ 问题清单

#### 4.1 生态分布表失效（最需要改的一处）

**现象**：mod 用的是旧式扁平写法

```xml
<wildBiomes>
  <SeaIce>0</SeaIce>
  <TemperateForest>0.15</TemperateForest>
  <TropicalSwamp>0.05</TropicalSwamp>
</wildBiomes>
```

**证据链**：

1. 1.6 中 `Verse.RaceProperties.wildBiomes` 的类型是 `List<RimWorld.AnimalBiomeRecord>`，
   每条记录为 `{ BiomeDef biome; float commonality; }` —— 已从旧版 `Dictionary<BiomeDef,float>` 改成记录列表。
2. 该类型的自定义加载器 `LoadDataFromXmlCustom(XmlNode)` 只有 **38 字节**，
   全函数**只引用 `"biome"` 一个字符串字面量** → 它期望从子节点里读 `<biome>`。
   扁平写法没有 `<biome>` 子节点，biome 字段拿不到值。
3. `Verse.DirectXmlToObject::ValidateListNode` 的报错串明确写着
   *"List item found with name X that is not `<li>`, and which does not have a custom XML loader method"*。
   因为 `AnimalBiomeRecord` **有**自定义加载器，所以连格式错误都不会报 —— 静默失效。
4. 全程序集内 `wildBiomes` 只有**一个**消费点：`RimWorld.BiomeDef::CommonalityOfAnimal(PawnKindDef)`。
5. **整个 1.6 原版数据里没有任何一处 author 过 `<wildBiomes>`。**

**结论**：作者写的 12 行生态分布大概率既不报错也不生效，ASEBI 的出现地点不由这段控制。

**修正写法**：

```xml
<wildBiomes>
  <li><biome>TemperateForest</biome><commonality>0.15</commonality></li>
  <li><biome>TropicalRainforest</biome><commonality>0.15</commonality></li>
  <li><biome>BorealForest</biome><commonality>0.05</commonality></li>
  <li><biome>AridShrubland</biome><commonality>0.05</commonality></li>
  <li><biome>Desert</biome><commonality>0.05</commonality></li>
  <li><biome>TemperateSwamp</biome><commonality>0.05</commonality></li>
  <li><biome>ColdBog</biome><commonality>0.05</commonality></li>
  <li><biome>TropicalSwamp</biome><commonality>0.05</commonality></li>
</wildBiomes>
```

替代方案：**整块删掉**，让它走游戏默认分布。

> **未验证项**：空列表时 `CommonalityOfAnimal` 的回退值未从 IL 中解出。
> "整块删掉"是否等价于默认分布，属未在游戏内实测的推断。

> **分析过程中的判断修正**：本项先后得出过两个不同结论，均已修正 ——
> 先按"原版 0 处出现 `<wildBiomes>`"推断字段已被删除；再按"存在自定义加载器"推断扁平写法仍受支持。
> **最终结论**：字段未删，元素类型已变，扁平写法确实不生效。记录于此以免后人重走。

#### 4.2 `AttackTarget` / `Comfort` 是照抄 Odyssey 原版

`Defs/TrainableDefs/` 下两个文件与 `Data\Odyssey\Defs\Misc\Trainables.xml` **逐字相同**，
只有 `AttackTarget` 的 description 多了半句 "that its master can see"。

原版的正确做法是 `<li MayRequire="Ludeon.RimWorld.Odyssey">AttackTarget</li>`
（全库共 570 处这种写法），而这个 mod 自带了一份副本。

- 装了 Odyssey：mod 副本会覆盖原版那份（内容等价，无害），但属于重复 Def
- 没装 Odyssey：反而能正常工作
- **结论：冗余但无害**。可保留，也可删掉两个文件并改用 `MayRequire`

#### 4.3 `<trainableTags><li>Attack</li></trainableTags>` 是死配置

`RaceProperties.trainableTags`、`RaceProperties.untrainableTags`、`TrainableDef.tags`
这三个字段在 1.6 程序集里**零读取点**（`ldfld` 全程序集扫描，阳性对照已通过）。

而且合法标签只有 `Basic` / `Combat` / `Help` / `Work`（见 `Core\Defs\TrainableDefs\Trainables.xml`），
`Attack` 根本不是标签名 —— 攻击训练的 defName 是 `Release`，标签是 `Combat`。

**结论：无副作用，但也没意义，可直接删。**

> 附带：1.6 原版动物普遍不再写 `trainableTags`，而是写 `specialTrainables`。
> 唯一还在用 `trainableTags` 的是 Ideology 的德鲁伊（`Ideology\Races_Animal_Special.xml`）。

#### 4.4 `<canArriveManhunter></canArriveManhunter>` 是空标签

该字段是普通 `bool`，全程序集唯一消费点：
`RimWorld.AggressiveAnimalIncidentUtility::CanArriveManhunter`。

模板注释写的是"不写=true，会出现在人潮里"，但**空标签既不是"不写"，也没给出明确值**。

未能确认 Verse 对空 bool 的回退行为 —— `DirectXmlToObject` 既不调 `Convert.ToBoolean`
也不调 `XmlConvert.ToBoolean`（已用 IL 验证），走的是自定义分支。

**结论：按"行为未定"处理。建议显式写成 `<canArriveManhunter>true</canArriveManhunter>`。**

#### 4.5 贴图双份并存

每张贴图同时存在 `.png` 与 `.dds.zstd`，合计约 **2 MB 冗余**。
引擎优先读 dds，`.png` 基本用不上（当初多半是某个打包/转换工具加的）。
可删 `.png`。

#### 4.6 无 `Languages/`

简中界面下物品名走英文 `label`、描述走日文 `description`，游戏内会看到一段日文。

---

## 五、在本机 Mods 库中的上下游

扫描全部 1029 个 `About/About.xml`，有两个 mod 声明 `loadAfter yukiyuki.ASEBI`，都排在它之后：

| packageId | 目录名 | 作用 |
|---|---|---|
| `ChinesePack.yukiyuki.animalgirls` | `yuki的魔物娘汉化整合(YAEMU,BORUM,ASEBI,...)` | 补上 §4.6 缺失的汉化 |
| `sizedapparel.yuki.monster.girls` | `RJW-Sar0-YUKI魔物娘SA1.6` | SizedApparel 体型适配 |

即本 mod 在当前配置中是被包在两层下游的**基础件**。

---

## 修改建议

1. **重写 `<wildBiomes>`** 为 `<li><biome>…</biome><commonality>…</commonality></li>`，或整块删除 —— 唯一的真功能缺失
2. **`<canArriveManhunter>` 显式写 `true`**
3. 删除 `<trainableTags>` 整块
4. 删除两个 TrainableDef 文件，改用 `<li MayRequire="Ludeon.RimWorld.Odyssey">`
5. 删除冗余 `.png`（约省 2 MB）

改动只涉及 `Defs/ThingDefs_Races/Races_Animal_ASEBI.xml` 与两个 TrainableDef 文件，
**不触及贴图与教程文本**，风险面很小。

---

## 可复用结论

与具体 mod 无关、对 RimWorld 1.6 Def 调试普遍有效：

1. **抽象父类用 `Name=` 而非 `defName=` 声明**
   （`Races_Animal_Base.xml` 里 `<ThingDef Name="AnimalThingBase" Abstract="True">`）。
   按 `<defName>` 文本 grep 会误判为"不存在"。判断引用是否存在要看**类型反射**，不能只看文本。

2. **`AnimalBiomeRecord` 这类"记录列表"类型的旧式扁平 XML 已失效**
   判据：该类型有没有 `LoadDataFromXmlCustom(XmlNode)`，以及它引用了哪些字符串字面量。
   有自定义加载器 = 走的是兼容分支，**没报格式错误 ≠ 解析成功** —— 静默失效最危险。

3. **"字段还在" ≠ "字段还在被用"**
   `trainableTags` / `untrainableTags` / `TrainableDef.tags` 就是典型：字段还在（可序列化、兼容存档），
   但已无任何读取点，纯死配置。

4. **0 命中结论必须配阳性对照**
   同一套 IL 扫描器要先证明它能命中已知活跃字段，再去相信它的 0 命中。

5. **原版 0 处使用 ≠ 字段不存在**
   要么是原版改用了别的机制，要么是原版根本用默认值（`wildBiomes` 属后者）。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机验证*
