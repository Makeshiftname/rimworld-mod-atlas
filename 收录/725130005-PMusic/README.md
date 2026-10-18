# P-Music（`725130005`）— 分析记录

| | |
|---|---|
| 本记录目录 | `修改/725130005-PMusic/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\725130005\` |
| mod 名 / packageId | P-Music / `Peppsen.PMusic` |
| 作者 | Peppsen（另有 ZumZum、SpacekatTommy 参与曲目） |
| 工坊 | https://steamcommunity.com/sharedfiles/filedetails/?id=725130005 |

> 本 mod **无授权限制**（无禁再分发声明）。
>
> **与前八份记录最大的不同**：这是纯粹的**内容型 mod**——
> 56 首自制歌曲 + 一份 SongDef，**无 C#、无 patch、无外部依赖、无贴图**。
> 整份 mod 只有 2 个 XML，其中一个是 About.xml。
> 因此本记录的重点不在"有没有坑"，而在**音频规格**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | 1.0 – 1.6（跨七个大版本，结构从未变过） |
| 结构 | `About/` + `Defs/SongDefs/` + `Sounds/`，**无版本目录** |
| 规模 | 60 文件 / **276.43 MB** |
| 依赖 | 无 |
| 语言 | 无 `Languages/`（见 §四，说明这不是问题） |
| `PublishedFileId.txt` | `725130005`（9 字节，正常 ✅） |

```
About/About.xml                       0.5 KB
About/preview.png
About/PublishedFileId.txt             9 字节
Defs/SongDefs/Songs_Gameplay.xml      5.4 KB   ← 全部逻辑就这一个文件
Sounds/*.ogg                          56 个，共 276.43 MB
```

**注意**：ogg 直接放在 mod 根的 `Sounds/` 下，没有子目录。
所以 `clipPath` 写的是裸名（如 `Lovely_Day`），对应 `Sounds/Lovely_Day.ogg`。
原版则用 `Songs/Relax/...` 这类带层级的路径。两种写法都合法。

---

## 它是什么

**纯内容型 mod**：56 首自制曲目 + 一份 SongDef 定义，**没有一行代码**。

- 作者 Peppsen（另有 ZumZum、SpacekatTommy 参与曲目）
- 全 mod 只有 2 个 XML（其中一个是 `About.xml`），无 C#、无 patch、无外部依赖、无贴图
- 体积 276.43 MB 全部来自 56 个 `.ogg`，每个约 4.94 MB
- 声明支持 1.0 – 1.6，**七个大版本结构从未变过**
- ogg 直接放在根目录 `Sounds/` 下（无子目录），所以 `clipPath` 写的是裸名如 `Lovely_Day`；
  原版则用 `Songs/Relax/...` 这类带层级的路径

曲目覆盖的作息与氛围：白天小调、夜晚曲、战斗曲（`tense`）、
一首限定冬季的 `Rimmas`（`commonality 2.0`，全库唯一显式权重）。

---

## 怎么验的

先查了原版 `Core\Defs\Misc\SongDefs\Songs_Gameplay.xml`（35 首）的写法：
**`defName` 出现 0 次、`label` 0 次、`genre` 0 次**。
也就是说原版 gameplay 歌曲同样是裸 `clipPath + volume`。

本 mod 的 56 条 SongDef 用到的字段，逐个对照 `Verse.SongDef` 的真实字段表：

| 字段 | SongDef 声明类型 | 本 mod 是否使用 | 合法 |
|---|---|---|---|
| `clipPath` | `String` | ✅ 56 条全部 | ✅ |
| `volume` | `Single` | ✅ 56 条全部 | ✅ |
| `tense` | `Boolean` | ✅ 约 13 条 | ✅ |
| `allowedTimeOfDay` | `TimeOfDay` | ✅ Day×5 / Night×3 | ✅ |
| `allowedSeasons` | `List<SeasonDef>` | ✅ 仅 1 条（Winter） | ✅ |
| `commonality` | `Single` | ✅ 仅 1 条（2.0） | ✅ |
| `playOnMap` | `Boolean` | ❌ 未用 | — |
| `minRoyalTitle` | `RoyalTitleDef` | ❌ 未用 | — |
| `clip` | `AudioClip` | ❌ 未用 | — |

**零非法字段，零缺失引用。** 这是本系列记录里最干净的一个 mod。

### 数值分布

| 项 | 分布 |
|---|---|
| `volume` | 0.6（6 首）/ 0.7（44 首）/ 0.8（2 首）/ 0.9（3 首） |
| `tense` | 约 13 首标记为紧张曲（战斗/袭击用） |
| `allowedTimeOfDay` | Day 5 首、Night 3 首，其余全天 |
| `allowedSeasons` | 仅 `Rimmas` 限定冬季，且 `commonality 2.0`（唯一显式权重） |

设计意图清楚：**大部分是无时段限制的通用曲，少数按时段/季节点题**，
并用 `tense` 区分战斗曲——都是原版 SongDef 的标准用法。

---

## 三、⚠️ 唯一值得关注的地方：276 MB 的音频规格

解析全部 56 个 ogg 的 Vorbis 识别头：

| 指标 | 结果 |
|---|---|
| 文件数 | 56 |
| 声道 | **全部 2ch（立体声）** |
| **采样率** | **48000 Hz × 34，44100 Hz × 22** ← 不一致 |
| 标称码率 | 192kbps 与 128kbps **混用** |
| 总体积 | **276.43 MB** |
| 平均每首 | **4.94 MB** |

### 两个可以指出的点

**① 采样率不统一**（48k 34 首 / 44.1k 22 首）。
说明这批曲子不是一次性用同一套导出参数做的。对游戏播放**没有功能影响**
（RimWorld 走 Unity 音频系统，会重采样对齐），但会让音频中间件做无谓的转换。

**② 192kbps 立体声对游戏背景音乐来说明显过重。**
RimWorld 的音乐是循环背景音，128kbps 立体声（甚至 96k）听感差别极小，
体积可以压到三分之一。276 MB 里大约有 **1/3 到 1/2 是可以省下来的冗余码率**。

> **未验证项**：本机游戏目录下**没有任何原版 ogg**
> （`Data\Core\Sounds` 为空，原版音乐在未下载的 Steam 独立内容包里），
> 所以**无法给出与原版每首体积的直接比值**。上面的判断基于通用音频常识，
> 不是与原版的实测对比。

### 修法（如需瘦身）

用 ffmpeg 统一转一遍即可，例如：

```bash
ffmpeg -i in.ogg -ac 2 -ar 44100 -c:a libvorbis -q:a 4 -map_metadata -1 out.ogg
```

`-q:a 4` 大约落在 128kbps 上下，`-map_metadata -1` 去掉来源标签。
转完记得同步改 `Songs_Gameplay.xml` 里的 `clipPath`（或保持同名覆盖）。

⚠️ **仅在你确实需要省空间时才做**——转换会重新编码、有音质损失，
且这属于对他人 mod 的改动。276 MB 在现代硬盘上并不构成问题。

---

## 四、为什么没有 `Languages/` 不是问题

音乐 mod 不需要翻译，因为**歌曲本来就没有 `label`**——
原版 gameplay 歌曲也没有（见 §二）。游戏里不会显示曲名列表，
只有"正在播放"的进度条。用户看到的是画面不是文字。

---

## 五、与你库里的另一个音乐 mod 不冲突

`F:\Games\GBL\rimworld\Mods\music` 目录：

| 项 | 值 |
|---|---|
| packageId | **`s.g`** |
| author / description | **`none`** / `none` |
| 规模 | 78 文件 / 247.66 MB |
| 曲目 | 75 首 |

**逐条比对 `clipPath` 后确认：与 P-Music 的 56 首零重叠。**
两个 mod 可以同时加载，共 131 首歌曲。

> 顺带一提：`music` 那个目录的 packageId 是 `s.g`、作者和描述都写着 `none`，
> 不像工坊原样下载的 mod（正常应该有真实 packageId 和作者名），
> 更像是解包后重新打包、或本地自制的音乐包。不影响加载。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| 低 | 如需瘦身：统一转 44100 Hz / 128kbps，预计可从 276 MB 降到 100 MB 上下 |
| 无 | **无需任何功能性修改** —— 字段合法、引用齐全、与原版写法一致 |

---

## 可复用结论

1. **纯内容型 mod 的核验重点完全不同。** 前八份记录的对象都有种族 Def、
   补丁或代码，需要核字段与引用；音乐/贴图类 mod 只有一份 `SongDef`，
   真正该查的是**音频规格**（采样率一致性、码率、声道）
   和**能否与同库其他同类 mod 冲突**。

2. **`clipPath` 重复会导致 SongDef 冲突。** 两个音乐 mod 若含同名 `clipPath`，
   后加载的会覆盖先加载的。本机两个音乐 mod 恰好零重叠，
   **这是需要实测比对而不是假设的事情**——不能用"应该不重名"代替逐条 diff。

3. **"原版也这么写"是最强的合法性依据。**
   本 mod 不写 `defName` 看着可疑，但原版 gameplay 歌曲同样不写——
   先查原版同类 Def，能省掉一次误判。

4. **⚠️ 目录列表里的文件大小会被 KB 四舍五入。**
   本轮分析 `725130005` 时顺手核对了前七个 mod 的 `PublishedFileId.txt`，
   发现自己在四份已写记录里误判成"0 字节空文件"并给出了错误的修改建议——
   实际全是正常的 9~10 字节工坊 ID。**根因是列表输出用了
   `[math]::Round($_.Length/1KB,1)`，10 字节被显示成 `0`。
   判断文件是否为空要读字节数，不要看 KB 化的列表。**
   已更正 `修改/2 雪绒兽/`、`3 素心和葬歌/`、`4 八重律/`、`5 阿比斯/`、
   `6弗莱西雅/` 五份记录并撤销相关建议。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机试听*
*核验方式：`Verse.SongDef` 字段反射 + 原版 SongDef 对照 + ogg Vorbis 头解析 + 与 `Mods\music` 逐条 clipPath 比对*
