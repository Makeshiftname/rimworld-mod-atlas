# SANKA and SOSIN / 素心和葬歌 — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/3 素心和葬歌/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\3 素心和葬歌\` |
| mod 名 / packageId | SANKAandSOSIN / `yukiyuki.SANKAandSOSIN` |
| 作者 | yukiyuki |

> **⚠️ 授权限制：禁止再分发**（同 `修改/美南烛/`、`修改/2 雪绒兽/`）。
> 本目录只存结论，不收录其 Def 原文与贴图。

> **本记录是同作者六连包中的第三弹，也是第一个"有自己东西"的：**
> 前两个（ASEBI / BORUM）是纯换皮模板，本 mod 引入了
> **远程攻击（`<verbs>` + 自定义 Projectile）** 和 **MVCF 多版本兼容框架**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | **1.4 / 1.5 / 1.6**（比前两个的"1.0–1.6"窄，也更诚实） |
| 结构 | `Common/` + `Defs/`（根目录），**无版本目录**——版本差异交给 MVCF |
| 规模 | 42 文件 / 5.67 MB |
| `modDependencies` | **完全没写**（见 §三，这是本 mod 最严重的问题） |
| 语言 | 无 `Languages/` → 简中环境下描述是日文 |

### 文件构成

```
Common/Sounds/SE/spine.wav                            172.4 KB
Common/Textures/AnimalProjectile/spine.{png,dds.zstd}
Common/Textures/Things/Pawn/Animal/SANKA_{south,north,east}.{png,dds.zstd}
Common/Textures/Things/Pawn/Animal/SANKA_Bones.{png,dds.zstd}
Common/Textures/Things/Pawn/Animal/SANKAPack_{south,north,east}.{png,dds.zstd}
Common/Textures/Things/Pawn/Animal/SOSIN_*  （同上 4 组）
Defs/MVCF/SM_MVCF.ModDef.xml
Defs/Projectiles/Projectile_Animal.xml
Defs/SoundDefs/SoundDef.xml
Defs/ThingDefs_Races/Races_Animal_SANKA.xml
Defs/ThingDefs_Races/Races_Animal_SOSIN.xml
Defs/TrainableDefs/AttackTrainable.xml
Defs/TrainableDefs/ComfortTrainable.xml
Defs/TrainableDefs/ForageTrainable.xml          ← 新增
```

> `PublishedFileId.txt` 内容为 `2966265703`（10 字节，正常）。
> （初稿曾误记为"0 字节空文件"，是目录列表 KB 四舍五入显示 0 导致的误读，已更正。）

---

## 它是什么

人设延续同系列：异界"某物"与**实验体双子**交配实验的产物，
有情感与**同伴意识**，会"为自己的同伴行动"。

与前两弹的纯换皮不同，本 mod 给出了**双向差异化的一对**：

| 项 | SANKA | SOSIN | 定位 |
|---|---|---|---|
| 体力 `baseHealthScale` | 7.5 | **9.5** | SOSIN 更肉 |
| 饥饿 `baseHungerRate` | **2.5** | 0.5 | SANKA 饿 5 倍 |
| 射程 | **20** | 15 | SANKA 远程 |
| 移速 | 3.8 | 4.0 | — |
| 体温上限 | 45 | 55 | SOSIN 更耐热 |
| 肉量 | 95 | 105 | — |
| 尖锐抗性 | 0.80 | **0.90** | SOSIN 更硬 |
| 钝器抗性 | 0.35 | 0.25 | SANKA 更耐打 |
| 体重 | 120 | 130 | — |
| 近战冷却 | 3 / 2 s | 4 / 1 s | — |
| 击晕量 | 25 | 30 | — |

→ **SANKA = 高速、高耗、远程突击型；SOSIN = 高耗血、低耗、近战肉盾型。**
描述里"射 Tucked出棘を補うため多めのエサを必要とします。エサの消費には気を付けて下さい"
说的就是 SANKA 那个 `baseHungerRate 2.5`。

其余共有设定：`ArmorRating_Sharp 0.80`（终于不再是三个 1.0）、`ToxicResistance 0`（讽刺的是
它自己发射带毒的棘）、`PsychicSensitivity 0.1`（本系列第一个非零）、
`petness 0.7`（最干净）、`predator true`、`lifeExpectancy 60`、
产奶每 5 天 140（三弹里最高）。

---

## 三、最严重的问题：MVCF 没装，且完全没声明依赖

`Defs/MVCF/SM_MVCF.ModDef.xml`：

```xml
<MVCF.ModDef>
  <defName>MVSM</defName>
  <label>MagicalMenagerie</label>
  <ActivateFeatures>
    <li>RangedAnimals</li>
    <li>HediffVerbs</li>
    <li>IntegratedToggle</li>
  </ActivateFeatures>
</MVCF.ModDef>
```

**用 XML 解析逐个 mod 读自身 `packageId` 后确认：本库 1021 个 mod 里没有任何一个是 MVCF
（Multi-Version Compatibility Framework）。**

后果链：

1. `MVCF.ModDef` 这个 Def 类型不存在 → 该 XML 加载报错、被跳过
2. **`RangedAnimals` 特性不会激活**——而这正是让普通动物能使用
   `<verbs>` 的那个机制
3. 因此 SANKA / SOSIN 的**远程棘刺射击很可能完全不工作**（只剩下近战）

> **诚实标注**：`<verbs>` 字段本身与 `Verse.Verb_Shoot` 类型**都真实存在且合法**
> （见 §五核验），所以 Def 能正常解析、不会崩。
> 但"动物能用身体发射远程"是 MVCF `RangedAnimals` 提供的运行时补丁，不是原版自带。
> **最终判定需游戏内实测**，但按机制推断不工作的可能性很高。

`About.xml` 里 `modDependencies` 是空的——连 HAR、Odyssey 都没声明。

### 附带影响：MVCF 不在，跨版本兼容也没了

本 mod 没有版本目录，全靠 MVCF 做版本条件加载。MVCF 缺失 = 整个版本适配层失效。

---

## 四、继承自模板的老问题（与前两弹完全相同）

复用 `修改/美南烛/` 已完成的 IL 级核验：

1. **`<wildBiomes>` 扁平写法静默失效** —— 1.6 中该字段是
   `List<RimWorld.AnimalBiomeRecord>`（`{BiomeDef biome; float commonality;}`），
   自定义加载器 `LoadDataFromXmlCustom` 仅 38 字节、只引用 `"biome"` 字面量，
   期望 `<biome>` 子元素。SANKA 与 SOSIN 各 12 行扁平写法同样失效，
   **且因有自定义加载器连格式错误都不报**。
   → 描述里"熱帯雨林など温暖地に生息"的设定同样不生效。

2. **`<trainableTags><li>Attack</li></trainableTags>` 死配置** ——
   `trainableTags` / `untrainableTags` / `TrainableDef.tags` 在 1.6 零读取点；
   合法标签只有 `Basic` / `Combat` / `Help` / `Work`。

3. **`<canArriveManhunter/>` 空标签** —— 普通 `bool`，唯一消费点
   `AggressiveAnimalIncidentUtility::CanArriveManhunter`。回退行为未确认，
   **建议显式写 `true`**。

4. **TrainableDef 抄件 ×3** —— 本弹多了一个 `ForageTrainable.xml`。
   三个文件（`AttackTarget` / `Comfort` / `Forage`）均与
   `Data\Odyssey\Defs\Misc\Trainables.xml` 逐字相同，
   原版正确做法是 `<li MayRequire="Ludeon.RimWorld.Odyssey">…</li>`。

5. **`.png` + `.dds.zstd` 双份** —— 18 个贴图 = 9 组双份，约 **3.1 MB 冗余**。

6. **无 `Languages/`**。

---

## 怎么验的

| 项 | 结果 |
|---|---|
| `Verse.ThingDef.verbs : List<…>` | **PRESENT** —— `<verbs>` 是合法字段 |
| `Verse.Verb_Shoot` | **存在** |
| `BaseBullet`（Projectile 父类） | **存在**，`Core\Defs\ThingDefs_Misc\Weapons\BaseWeapons.xml`（原版 Core，**不需要** Anomaly） |
| `ScratchToxic`（额外伤害） | **存在**，`Core\Defs\DamageDefs\Damages_MeleeWeapon.xml` |
| `GunTail_Light`（尾音） | **存在**，`Core\Defs\SoundDefs\World_Oneshots_Tails.xml` |
| `Leather_Heavy` / `Milk` / `AnimalBaby·Juvenile·Adult` | 存在（前两弹已验证） |
| 贴图 `AnimalProjectile/spine`、`Things/Pawn/Animal/SANKA_*`、`SOSIN_*` | 均在 `Common/Textures/` 下找到 |

> **核验过程中的一次自我修正**：我第一次查 `BaseBullet` 时用了 `Select-String -List`，
> 只返回首个匹配文件，于是误报"只在 Anomaly 里找到"。
> 去掉 `-List` 重查后发现 Core 里就有——`ParentName="BaseBullet"` 在 Core 单独用了 13 次。
> **教训**：`-List` 只能回答"有没有"，回答不了"在哪里有"。

### 棘刺弹丸 `spine`（紫棘）

| 参数 | 值 |
|---|---|
| 伤害类型 | `Bullet` |
| 基础伤害 | 10 |
| 穿甲 | **0.75** |
| 停止力 | 4.0 |
| 弹速 | 60 |
| 额外伤害 | `ScratchToxic` 5（穿甲 1，**触发概率 1**） |

发射参数：射界 1s，射程 20（SANKA）/ 15（SOSIN），**3 连发**，
`requireLineOfSight=true`，`muzzleFlashScale 5`。

---

## 六、两处作者自相矛盾的地方

1. **`SoundDef` 名字叫 `SMFlamethrowerSE`**（喷火器？），
   实际内容是棘刺发射音效。明显是从别的 mod 复制来的残留命名，与 `spine` 对不上。

2. **`nameOnTameChance` 被设成了 1** —— 而**模板自带的说明书明确警告过这个值**。
   `Defs/ThingDefs_Races/2.race2.txt`（前两弹也在）里写着：

   > *"nameOnTameChance — テイムした時に名前が付く確率。現在（2018/9/15）EDBで1の動物の
   > 種族名が名前になる不具合があるので、特別な拘りがなければ **0～0.9 の範囲**にとどめて
   > おくといいかと思います。"*

   作者偏偏用了 1.0。前两弹（ASEBI / BORUM）都没写这一项，本弹是第一个写的。

---

## 七、本系列全家福

用 XML 解析统计本库的 `yukiyuki.*`：

| 目录 | packageId | 状态 |
|---|---|---|
| `1 美南烛` | `yukiyuki.ASEBI` | 已分析 → `修改/美南烛/` |
| `2 雪绒兽` | `yukiyuki.BORUM` | 已分析 → `修改/2 雪绒兽/` |
| `3 素心和葬歌` | `yukiyuki.SANKAandSOSIN` | **本记录** |
| `4 …` | `yukiyuki.YAEMU` | 未分析 |
| `5 …` | `yukiyuki.ABYSS` | 未分析 |
| `6 …` | `yukiyuki.FLESHIA` | 未分析 |
| `yuki的魔物娘汉化整合…` | `ChinesePack.yukiyuki.animalgirls` | 覆盖全部六个的汉化包 |

**用户目录里的 1–6 号正好就是这个作者的全六弹。**

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| 高 | **装 MVCF**，或在 `About.xml` 声明 MVCF 依赖 / 给 `SM_MVCF.ModDef.xml` 加 `MayRequire` |
| 高 | **重写两个 `<wildBiomes>`** 为 `<li><biome>…</biome><commonality>…</commonality></li>` |
| 高 | `<canArriveManhunter/>` 显式写 `true` |
| 中 | 删除 `<trainableTags>` 整块 |
| 中 | 删除三个 TrainableDef 抄件，改用 `<li MayRequire="Ludeon.RimWorld.Odyssey">` |
| 中 | `nameOnTameChance` 从 1 降到 ≤0.9（模板自己的建议） |
| 低 | `SoundDef` 改名 `SMSpineSE` 之类，对得上内容 |
| 低 | ~~补 `PublishedFileId.txt`~~ —— **撤销**：实测内容为 `2966265703`，本来就有 |
| 低 | 删除冗余 `.png`（约省 3.1 MB） |

改动只涉及 `Defs/`，**不触及 `Common/` 的音效与贴图**。因禁再分发，仅供本地自用。

---

## 可复用结论

1. **同系列 mod 应当批量分析。** 前两弹建立的"模板基线问题清单"
   （wildBiomes / trainableTags / canArriveManhunter / 抄件 TrainableDef / 贴图双份）
   可以直接复用到后续弹窗，只需补查新增机制——
   本次只多花了查 MVCF、`verbs` 字段、`BaseBullet` 三件事。

2. **`<MVCF.ModDef>` / 任何第三方框架的 Def 类型都是硬依赖**，
   而框架本身可能被玩家删掉。作者必须写 `MayRequire` 或 `modDependencies`。

3. **Def 字段"合法"不等于机制"能工作"。**
   `ThingDef.verbs` 和 `Verb_Shoot` 都真实存在，Def 解析不会报错，
   但让动物使用身体发射器的是 MVCF 的运行时补丁。
   **判断功能是否可用，要找补丁是谁做的，不能只看字段在不在。**

4. **`Select-String -List` 回答不了"在哪些文件"** —— 只给首个匹配。
   需要列全部匹配时去掉 `-List`。这个问题本轮让我误报了一次"BaseBullet 需要 Anomaly"。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机验证*
*核验方式：复用 `修改/美南烛/` 的 IL 级结论 + 补查本 mod 新增机制*
