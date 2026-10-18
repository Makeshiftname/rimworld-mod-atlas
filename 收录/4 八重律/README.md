# YAEMU / 八重律 — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/4 八重律/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\4 八重律\` |
| mod 名 / packageId | YAEMU / `yukiyuki.YAEMU` |
| 作者 | yukiyuki |

> **⚠️ 禁再分发**（同系列六弹一致）。本目录只存结论，不收录 Def 原文与贴图。
> 系列基线问题清单见 `修改/美南烛/README.md`，此处只列本弹独有部分。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | 1.4 / 1.5 / 1.6 |
| 结构 | 扁平 `Defs/` + `Textures/`，**无 `Common/`、无版本目录**（同第 1、2 弹） |
| 规模 | 24 文件 / 3.47 MB |
| 外部依赖 | 无 |
| 语言 | 无 `Languages/` |

```
About/About.xml / preview.png / PublishedFileId.txt（`2962748302`，正常）
Defs/ThingDefs_Races/Defs.txt              ← 见 §二，是垃圾
Defs/ThingDefs_Races/Races_Animal_YAEMU.xml
Defs/TrainableDefs/YAEMU_AttackTrainable.xml
Defs/TrainableDefs/YAEMU_ComfortTrainable.xml
Defs/TrainableDefs/YAEMU_DigTrainable.xml   ← 新增
Textures/Things/Pawn/Animal/YAEMU_*        8 组双份（png + dds.zstd）
```

人设：*"凶悪な捕食器官を持つ生物"YAEMU"*——热带雨林与沙漠活动的**捕食者**，
*"よく食べる子です"* 对应高 `baseHungerRate`。**无远程攻击**（本弹仍是纯近战模板）。

---

## 它是什么

yukiyuki 同系列模板的**第四弹**，一只纯近战的捕食者。与前三弹同构：
单只兽、单个 `ThingDef` + `PawnKindDef`、共用同一套模板注释。

作者给的设定是 *"凶悪な捕食器官を持つ生物"*（拥有凶恶捕食器官的生物）——
活动范围写的是热带雨林与沙漠，*"よく食べる子です"* 对应高 `baseHungerRate`。

**本弹相对前三弹的增量只有一处**：多了一个 `Dig`（挖掘）训练项。
`Attack` / `Comfort` / `Dig` 三个 TrainableDef 全部是 Odyssey
`Data\Defs\Misc\Trainables.xml` 的逐字抄件。

其余全是换皮：无远程攻击、无 MVCF、无 C#、无任务链。

---

## 两处纯粹的垃圾（不影响运行，但白占空间）

### `Defs.txt` 是陈旧副本

227 行的 `.txt`，是 `Races_Animal_YAEMU.xml`（229 行）的**早期版本**——
142 行有差异。因为扩展名是 `.txt`，**RimWorld 根本不会加载它**（只解析 `.xml`）。

属于作者编辑过程中留下的中间稿，删掉即可。

### `YAEMUzPack_north` 是拼错的重复文件

实测 md5：

| 文件 | 大小 | md5(前12) |
|---|---|---|
| `YAEMUPack_north.dds.zstd` | 199.0 KB | `04aa2998040e` |
| `YAEMUzPack_north.dds.zstd` | 199.0 KB | **`04aa2998040e`** ← 完全相同 |
| `YAEMUPack_north.png` | 241.9 KB | `060cf59cbf38` |
| `YAEMUzPack_north.png` | 241.9 KB | **`060cf59cbf38`** ← 完全相同 |

多出来的 `z` 应是敲键盘手滑。Def 引用的是 `Things/Pawn/Animal/YAEMUPack`，
所以这两个文件**永远不会被读取**——纯浪费 **441 KB**。

---

## 怎么验的

指纹扫描结果：`wildBiomes=YES` · `trainableTags=YES` · `canArriveManhunter=YES` ·
`verbs=no` · `nameOnTameChance=no`

即三条老问题全中：

1. **`<wildBiomes>` 扁平写法静默失效** —— "熱帯雨林や砂漠など温暖地域"的设定不生效
2. **`<trainableTags><li>Attack</li>` 死配置** —— 该字段在 1.6 零读取点
3. **`<canArriveManhunter/>` 空标签** —— 建议显式写 `true`

外加：

4. **TrainableDef 抄件 ×3** —— 本弹新增 `Dig`（对应 Odyssey 的挖掘训练）。
   三个文件均与 `Data\Odyssey\Defs\Misc\Trainables.xml` 逐字相同。
5. **`.png` + `.dds.zstd` 双份** —— 8 组，约 **2.0 MB 冗余**（外加 §2.2 的 441 KB 死文件）
6. ~~**`PublishedFileId.txt` 0 字节**~~ —— **撤销**：实测为 `2962748302`（10 字节，正常）。
   原判据是目录列表的 KB 四舍五入显示 0，属误读。
7. **无 `Languages/`**

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| 高 | 删 `Defs/ThingDefs_Races/Defs.txt`（不会被加载的 227 行陈稿） |
| 高 | 删 `YAEMUzPack_north.{png,dds.zstd}`（拼错的重名文件） |
| 中 | 重写 `<wildBiomes>` 为 `<li><biome>…</biome><commonality>…</commonality></li>` |
| 中 | `<canArriveManhunter/>` 显式写 `true` |
| 中 | 删 `<trainableTags>` 整块 |
| 中 | 删三个 TrainableDef 抄件，改用 `<li MayRequire="Ludeon.RimWorld.Odyssey">` |
| 低 | ~~补 `PublishedFileId.txt`~~ —— **撤销**（本来就有 `2962748302`） |
| 低 | 删冗余 `.png`（约省 2.0 MB） |

改动只涉及 `Defs/` 与 `Textures/`，仅本地自用。

---

## 可复用结论

1. **同系列弹数之间的"作者习惯"会随时间改进。**
   本弹仍全中三条老问题，但第 6 弹已经把 `trainableTags` 删掉了——
   **批量分析必须逐弹扫描指纹，不能凭前几弹推断后面。**

2. **拼错的重复贴图要用 md5 找，不要靠肉眼看文件名。**
   本弹 `YAEMUzPack_north` 与 `YAEMUPack_north` 只差一个字符，md5 完全一致。

3. **`.txt` 文件在 Defs 目录里是"看不见的垃圾"。**
   RimWorld 只解析 `.xml`，所以放在 `Defs/` 下的 `.txt` 不会被加载也不会报错——
   很容易误以为它是有效文件。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机验证*
