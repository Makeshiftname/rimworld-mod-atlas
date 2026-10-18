# AKT_Ideology — 扶她文化（`RJW-文化-扶她文化`）— 分析记录

| | |
|---|---|
| 本记录目录 | `收录/RJW-文化-扶她文化（AKawaiiTent's Futa Ideology）/`（收录目录名直接用源目录名——**用户自命名的中文目录**） |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\RJW-文化-扶她文化（AKawaiiTent's Futa Ideology）\` |
| mod 名 | `AKT_Ideology` |
| packageId | **`AKT.Ideology`** |
| 作者 | AKawaiiTent |
| **分发渠道** | **非工坊**——`About/` 下**没有 `PublishedFileId.txt`**；`modDependencies` 里给的是 **LoversLab** 链接 |
| 版本 | 描述里写 "Version: 1.6"（未标明是 mod 版本还是 Ideology 版本） |
| 许可 | **未声明**——无 LICENSE 文件；`Textures/credits.txt` 写明素材来自他人 |
| 支持版本 | 1.5 / 1.6 |
| 语言 | **仅 ChineseSimplified**（6 个 DefInjected 文件），**无英文** |
| 分析日期 | 2026-10-17 |

> 本 mod 属 **成人向**（18+）内容，且**素材是他人作品的二次编辑**。
> 本记录只做技术分析与授权事实陈述。

**它在你库里的位置**：**纯 XML 的 RJW 附属内容包**——61 文件、**零 DLL、零 C# 源码**。
功能全靠**复用 RJW 自带的 6 个 `ThoughtWorker_*` 类**实现。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **61 文件 / 2,789,610 字节（2.66 MB）** |
| 结构 | `About/` + `Defs/`（6 文件）+ `Patches/`（1 文件）+ `Languages/ChineseSimplified/`（6 文件）+ `Textures/`（47 文件） |
| 类型 | **Ideology 内容包**（Meme / Precept / Issue / StyleCategory / ThingStyle / Thought） |
| Assemblies | **无**（无 C#，靠 XML 声明） |
| Source | **无** |
| Def 规模 | **16 个 Def**：1 MemeDef + 4 PreceptDef + 4 IssueDef + 1 StyleCategoryDef + 5 ThingStyleDef + 6 ThoughtDef（另含 1 个 patch 改 2 个既有 ThoughtDef） |
| Harmony 补丁 | **0**（不需要） |
| `modDependencies` | `rim.job.world` ✅ 已装（目录 `RJW_核心_本体`） |
| 谁依赖它 | **0 个**（全库扫描仅命中自身） |
| 素材来源 | **`credits.txt`：*"all art is edited and originally from either VincentCC or Vitalis"*** |

### 体积构成（关键）

| 类型 | 字节 | 占全 mod | 用途 |
|---|---|---|---|
| **`.clip`（Clip Studio 画稿）** | **1,099,879** | **39.4%** | **作者的绘画源文件，不参与游戏** |
| `.dds` | 952,688 | 34.2% | RimWorld **1.5** 加载 |
| `.dds.zstd` | 342,643 | 12.3% | RimWorld **1.6** 加载 |
| `.png` | 365,781 | 13.1% | 策划/编辑用（不含 `Preview.png`） |
| `Defs/` + `Patches/` | 14,673 | 0.5% | 全部逻辑 |

> 14 个游戏贴图**每张都同时提供三种格式**（`.dds` / `.dds.zstd` / `.png`），
> 数量一一对应（`.png` 多一个 `Preview.png`，属正常）。
> **真正被游戏加载的只有 `.dds`（1.5）与 `.dds.zstd`（1.6）**；
> `.png` 给策划看，`.clip` 是画稿——**后者占掉 39.4% 的体积，对玩家毫无作用**。

---

## 它是什么

一句话：**给 RimWorld 的 Ideology DLC 加一套"扶她至上"信仰**，并把原版的雕像与圣物图腾换成扶她主题。

`About.xml` 的自述很直白：*"Adds futanari supremeacy ideology. **Mostly just adds statues and idols.**"*

### 一、MemeDef：完整的一套 Ideology 信仰

`Defs/MemeDefs/FutanariSupremacy_Meme.xml` 定义 1 个 `MemeDef`：

| 字段 | 值 |
|---|---|
| `defName` | `FutaSupremacy` |
| `impact` | 1 |
| `iconPath` | **`UI/Memes/SupremacyFemale`** ← **原版 Ideology 贴图**（核实见下） |
| `generalRules/rulesStrings` | 5 条：`memeAdjective→futa`、`memeGod→Mother`、`memeLeaderNoun→queen`、`memeLeaderAdjective→alpha`、`memeMoralist→futa believer` |
| `symbolPacks` | `ideoName=Futa`、`theme=futanari`、`adjective=member=fertilist` |
| `thingStyleCategories` | 挂 `Futa` 样式分类（优先级 1） |
| `descriptionMaker/rules` | **16 条规则字符串**，覆盖 theist / ideological / archist / animist 四条创世神话线 |

> **借原版图标**：核实 `UI/Memes/SupremacyFemale` 出自
> `Data/Ideology/Memes_GenderSupremacy.xml`（原版"女性至上"meme 的图标）。
> 新 meme 直接复用它——省一张贴图，观感也贴切。

### 二、Issue + Precept：两套"想要 / 厌恶"

| Def | 说明 |
|---|---|
| `IssueDef FutaDesiredFemale` / `FutaDesiredMale` | "想变成扶她"的议题，`allowMultiplePrecepts=false` |
| `IssueDef FutaFemale` / `FutaMale` | 名为 "Trait Enforcer Female/Male" 的议题（**Defs 里有、Patches 与 Precepts 都没用到**） |
| `PreceptDef Futa_Desire_PreceptF` / `M` | "Futa Loved"，`requiredMemes=[FutaSupremacy]` |
| `PreceptDef Futa_Shunned_PreceptF` / `M` | "Futa Shunned"，**无 `requiredMemes`**，`defaultSelectionWeight=1` |

四个 IssueDef 的 `iconPath` 全部指向原版的 `UI/Issues/IdeoDiversity`。

> 注意：`Futa_Shunned_*` **没有 `requiredMemes`**，意味着它们不依赖这套 meme 也会出现在
> 原版 IDEO 的议题列表里——这可能是有意的（通用禁忌），也可能是漏写。

### 三、ThoughtDef：复用 RJW 的 6 个 worker，**自己零代码**

`Defs/ThoughtDefs/FutaChanges.xml` 定义 6 个 `ThoughtDef`，
全部只写 `workerClass` 指向 **RJW 自己的类**：

| defName | workerClass | 两档心情 |
|---|---|---|
| `male2futa2` | `rjw.ThoughtWorker_MtH` | +5 / +20 |
| `female2futa2` | `rjw.ThoughtWorker_FtH` | +5 / +20 |
| `futa2trap2` | `rjw.ThoughtWorker_HtT` | −5 / −20 |
| `futa2male2` | `rjw.ThoughtWorker_HtM` | −5 / −20 |
| `futa2female2` | `rjw.ThoughtWorker_HtF` | −5 / −20 |
| `trap2futa2` | `rjw.ThoughtWorker_TtH` | +5 / +20 |

每个都带 `nullifyingPrecepts` 指向对应的 `Futa_Shunned_*`——
**即"被这套教义厌恶"时，这些念头被抵消**。

**核实**（反射 `RJW_核心_本体/1.6/Assemblies/RJW.dll`，920 个类型）：

```
ThoughtWorker_MtH  存在，基类 = ThoughtWorker_SexChange
ThoughtWorker_FtH  存在，基类 = ThoughtWorker_SexChange
ThoughtWorker_HtT  存在，基类 = ThoughtWorker_SexChange
ThoughtWorker_HtM  存在，基类 = ThoughtWorker_SexChange
ThoughtWorker_HtF  存在，基类 = ThoughtWorker_SexChange
ThoughtWorker_TtH  存在，基类 = ThoughtWorker_SexChange
```

即：**RJW 早就备好了性别转换的 ThoughtWorker 家族**，本 mod 只要声明 Def 指向它们即可。
这就是它**不需要任何 DLL** 的原因——把"写 C# 补丁"降级成"填 XML"。

> 六个 `ThoughtDef` 里都留着一行被注释的
> `<!--<workerClass>rjw.ThoughtWorker_SexChange</workerClass>-->`——
> 作者曾考虑过直接用基类。

### 四、StyleCategory：把原版雕像/圣物图腾换皮

`Defs/StyleCatagoryDefs/StyleCategoryDefs.xml` 定义 `StyleCategoryDef Futa`
（`iconPath = UI/StyleCategories/Futa`，**这张是自带的**），
把 5 个 `ThingStyleDef` 绑到**原版 Ideology 的建筑**上：

| 原版 ThingDef | 样式 Def | graphicClass | drawSize | 贴图目录 |
|---|---|---|---|---|
| `SculptureLarge` | `Futa_SculptureLarge` | `Graphic_Random` | (3,3) | `Sculptures/Large/`（A–D 四张随机） |
| `SculptureGrand` | `Futa_SculptureGrand` | `Graphic_Random` | (4,4) | `Sculptures/Grand/`（A–D 四张随机） |
| `Ideogram` | `Futa_IdeogramA` | `Graphic_Single` | (4,4) | `IconFutaA` |
| `Ideogram` | `Futa_IdeogramB` | `Graphic_Single` | (6,3) | `IconFutaB` |
| `Ideogram` | `Futa_IdeogramC` | `Graphic_Single` | (6,3) | `IconFutaC` |

这就是描述里说的"Mostly just adds statues and idols"——**不新增建筑，只换皮原版雕像与圣物图腾**。
用 `Graphic_Random` 随机取 4 张之一，等于同一建筑有 4 种外观。

### 五、唯一的 Patch：一份写得很好的幂等追加

`Patches/Thoughts_SexChange.xml` 改的是 **RJW 自己的** `male2futa` / `female2futa`
两个 `ThoughtDef`（核实：两者确实在 RJW 的 `1.6/Defs/…/Thoughts_SexChange.xml` 里），
给它们的 `nullifyingPrecepts` **追加**一条 `Futa_Desire_*`。

写法用的是 **`PatchOperationConditional` 处理"元素在/不在"两种情况**：

```xml
<Operation Class="PatchOperationConditional">
  <xpath>Defs/ThoughtDef[defName="male2futa"]/nullifyingPrecepts</xpath>
  <nomatch Class="PatchOperationAdd">      <!-- 节点不存在 → 补一整个带 <li> 的节点 -->
    <xpath>Defs/ThoughtDef[defName="male2futa"]</xpath>
    <value><nullifyingPrecepts><li>Futa_Desire_PreceptM</li></nullifyingPrecepts></value>
  </nomatch>
  <match Class="PatchOperationAdd">        <!-- 节点已存在 → 只追加 <li> -->
    <xpath>Defs/ThoughtDef[defName="male2futa"]/nullifyingPrecepts</xpath>
    <value><li>Futa_Desire_PreceptM</li></value>
  </match>
</Operation>
```

> **这是本 mod 技术含量最高的一段**，也是最值得抄的写法：
> 向别的 mod 的列表字段追加元素时，用 `PatchOperationConditional` 分两支，
> 既不会因"节点已存在"报错，也不会覆盖别人已有的内容。**幂等且非破坏性。**

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 文件清单 / 字节 | `Get-ChildItem -LiteralPath -Recurse`（目录名含全角括号，必须用 `-LiteralPath`）+ `ReadAllBytes().Length` |
| 功能 | **7 个 XML 全部读完**（6 Def + 1 Patch）——本记录无推断成分 |
| `.clip` 是什么 | 读前 4 字节魔数 + 前 32 字节 ASCII |
| `.dds.zstd` 是否游戏支持 | 先扫 Assembly-CSharp 的 **ASCII 元数据堆**（0 命中）→ 改扫 **UTF-16 #US 堆**（仍 0 命中）→ 再用 **ripgrep 全库扫 `*.dds.zstd`** 确认是全库通行做法 |
| 依赖是否真实 | 反射 RJW.dll 逐个查 6 个 `ThoughtWorker_*` 类 + 读其 `BaseType` |
| 补丁目标是否真实 | 在 RJW 的 `Defs/` 里按 `<defName>male2futa</defName>` 精确匹配 |
| Meme 图标归属 | 在 `Data/{六个 DLC}/Defs` 里检索 `UI/Memes/SupremacyFemale` |
| DLC 是否齐备 | 反射 `Assembly-CSharp` 查 `RimWorld.MemeDef` / `PreceptDef` / `IssueDef` / `Verse.StyleCategoryDef` / `Verse.ThingStyleDef` / `Verse.ThingDefStyle` |
| 依赖图 | `[xml]` 解析全库 `About/About.xml`，取直接子元素 `<packageId>` |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| UTF-16 堆提取 | 必须能命中 `ModDdsLoader only supports FilesystemFile types.` | ✅ **命中，连同 17 条 dds 相关字面量** |
| ASCII 堆提取 | 必须能命中 `packageId` | ✅ |
| Meme 图标归属 | 原版 MemeDef 的 23 个 `UI/Memes/*` iconPath 里必须含 `SupremacyFemale` | ✅ 命中 |
| RJW worker 类 | `ThoughtWorker_MtH` 必须存在 | ✅ 6/6 全中 |
| 补丁目标 | `male2futa` 必须在 RJW 的 Defs 里 | ✅ |
| DLC | `RimWorld.MemeDef` 必须存在 | ✅ |
| 依赖扫描 | `brrainz.harmony` 必须命中 | ✅ |

### ③ 自查纠错（本轮我的工具错了 2 次）

**1. 先用 ASCII 元数据堆查 `zstd`，0 命中，差点写成"这个格式游戏不支持"。**
`Assembly-CSharp` 的 #Strings 堆里没有任何 `zstd`。
**但这不能下结论**——字符串**字面量**在 **#US 堆（UTF-16）**，ASCII 提取器看不见
（这正是本会话早先在 Cherry Picker 上踩过的坑，我又踩了一次）。
改用 UTF-16 提取后：命中 17 条 `dds` 相关字面量（含
`"Invalid DDS magic number"`、`"Unsupported compressed DDS texture format: {0:X8}"`），
证明工具本身有效，且托管层确实没有 `zstd` 字符串——
**说明 `.dds.zstd` 的解压在原生引擎侧**。最终用 ripgrep 全库扫 `*.dds.zstd` 定案：
ASEBI、黑山羊机械体、自我受孕针、羁绊的爱情等**大量 mod 都在用**，是 1.6 的通行格式。

**2. 阳性对照本身又写错了（第二次）。**
第一次我拿 `loadAfter` 当 UTF-16 堆的对照，它返回 FAIL——
但那是因为 `loadBefore`/`loadAfter` 是**元数据成员名**（在 #Strings 堆）、
不是字符串**字面量**。换成上表里那条 `ModDdsLoader…` 后才真正验证了提取器。

**教训（第二次同款）**：对照项选错时，失败的是对照而不是被测对象。
本会话已在 `2898044088` 收录时犯过一次，此处重犯。

### ④ 未核实

- **`.clip` 画稿是否该发布**：判断为"发布方漏加 `.gitignore`"，但**未验证**是否有意为之
  （Clip Studio 文件有时会被当作素材存档一起发布）。
- **素材授权**：`credits.txt` 只说"编辑自 VincentCC 或 Vitalis"，
  **没说原素材的许可**，也**没有 LICENSE**。原素材的实际授权条款**未核实**。
- **`Futa_Shunned_*` 没有 `requiredMemes` 是否有意**：未实机验证其在非扶她至上的原版
  意识形态里是否也会出现。
- **`IssueDef FutaFemale` / `FutaMale`（Trait Enforcer）未被任何 Precept 引用**：
  疑似未完成的设计，**未实机验证**是否会在游戏里报错或造成孤立议题。

---

## 上下游与冲突面

### 依赖方向：单向，且没有反向

```
RJW_核心_本体 (rim.job.world)
        ▲
        └── RJW-文化-扶她文化 (AKT.Ideology)      ← 纯 XML 附属
```

- `AKT.Ideology` 依赖 `rim.job.world` ✅ 已装
- **没有任何 mod 依赖 `AKT.Ideology`**（全库扫描仅命中自身 `packageId`）
- `About.xml` **没有 `loadAfter`** —— 靠包管理器按 `modDependencies` 排序即可

### 资产来源的追溯

`Textures/credits.txt` 全文：

> all art is edited and originally from either VincentCC or Vitalis

即**所有美术都是对 VincentCC / Vitalis 作品的二次编辑**。
作者做了署名（这点值得肯定），但：

- **没有 LICENSE 文件**，`About.xml` 也无 `<license>` 字段
- **没有说明原素材的许可条款**

在"素材是二次编辑"的前提下，这是本记录里**授权风险最明确**的一条。

### 分发渠道：LoversLab，不是工坊

`About/` 下**没有 `PublishedFileId.txt`**，且 `modDependencies` 里给的
`steamWorkshopUrl` 实际填的是 `https://www.loverslab.com/topic/110270-mod-rimjobworld`
（字段名与内容不符，但指向正确）。这是因为 RJW 本身不在工坊上架。

→ 本目录是**用户手工放置**的（源目录名也是中文自定义），**没有自动更新通道**。

### 1.6 兼容策略：三种贴图格式并行

| 格式 | 服务对象 | 是否被游戏加载 |
|---|---|---|
| `.dds` | RimWorld **1.5** | ✅ |
| `.dds.zstd` | RimWorld **1.6** | ✅ |
| `.png` | 策划 / 手工编辑 | ❌ |
| `.clip` | Clip Studio 画稿 | ❌ |

`.dds.zstd` 经全库核对是 **1.6 通行格式**（多个已收录 mod 都在用），
在托管层完全找不到字符串，说明**解压由原生引擎处理**。
**同时提供 `.dds` + `.dds.zstd` 是让同一个 mod 同时支持 1.5 与 1.6 的标准做法**。

---

## 可复用结论

1. **"零代码附属包"是可行的——前提是上游已经备好了扩展点。**
   本 mod 61 个文件、0 个 DLL，全靠 `workerClass` 指向 RJW 现成的
   `ThoughtWorker_SexChange` 家族。
   **上游框架把可复用的 worker 类公开出来，下游就能只写 XML**——
   这是"框架"与"内容包"分层最干净的形态。

2. **向别人的列表字段追加元素，用 `PatchOperationConditional` 分两支。**
   目标节点不存在 → 补一整个带子元素的节点；已存在 → 只追加子元素。
   本 mod 对 `male2futa`/`female2futa` 的 `nullifyingPrecepts` 就是这么做的：
   **幂等、不覆盖别人已有内容、不依赖上游的具体写法**。这是本 mod 最值得抄的一段。

3. **不新增建筑、只给原版建筑加 `StyleCategoryDef`，是"换皮"成本最低的做法。**
   本 mod 把扶他主题绑到原版 Ideology 的 `SculptureLarge` / `SculptureGrand` / `Ideogram` 上，
   配 `Graphic_Random` 从 4 张里随机——玩家获得"多种外观的雕像"，
   而 mod 只需 5 个 `ThingStyleDef` + 13 张贴图，**零新增建筑、零平衡改动**。

4. **meme 的 `iconPath` 可以借原版的。**
   `FutaSupremacy` 直接用原版"女性至上"meme 的 `UI/Memes/SupremacyFemale`。
   核实方法：去 `Data/<DLC>/Defs` 里检索该路径。
   **省一张贴图，而且视觉上恰好传达"同为至上型意识形态"**。

5. **贴图同时发 `.dds` 与 `.dds.zstd`，是跨 1.5/1.6 的标准做法。**
   `.dds.zstd` 是 1.6 的原生引擎侧格式（托管层无任何 `zstd` 字符串），
   实测体积约为对应 `.dds` 的 **1/3 到 1/2**。
   本 mod 14 张贴图三格式齐备，是可参照的模板。

6. **`.png` 与 `.dds`/`.dds.zstd` 并存是给策划留的编辑入口；但 `.clip` 是画稿。**
   本 mod 39.4% 的体积是两个 Clip Studio 文件（魔数 `CSFC` + `CHNK` 确认）。
   **发布包带上画稿，对玩家毫无作用**，只增加下载量——
   除非有意作为"素材存档"（社区常这么做）。加一条 `.gitignore` 即可避免。

7. **纯 XML 内容包的发布门槛比带代码的低得多，但仍需三样东西**：
   `About.xml`（含 `packageId` 与 `modDependencies`）、贴图（含目标游戏版本所需格式）、
   `Languages/<源语言>/`。
   本 mod 三样都齐——**且源语言就是它唯一提供的语言（简中）**，
   这是中文作者的 mod 常见做法：`label` 直接写英文、翻译只出中文，
   英文玩家会看到英文 label（`label` 写在 Defs 里，是原文）。

8. **记录一个 mod 要先看它是不是工坊 mod。**
   本 mod **没有 `PublishedFileId.txt`** ——它来自 LoversLab、由用户手工放置。
   收录目录名也是用户自命名的中文。这一类 mod **没有自动更新通道**，
   升级时需要手工替换，评估维护成本时要算进去。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **授权不明确** | 无 LICENSE、`About.xml` 无 `<license>`，且 `credits.txt` 明示素材是**对 VincentCC / Vitalis 作品的二次编辑**却未说明原许可。二次分发前需确认原素材条款 |
| 高 | **1.1 MB `.clip` 画稿**（占 39.4%） | 玩家用不到。若非有意作为素材存档，可移除（**需用户授权**） |
| 中 | **无英文语言文件** | 只有简中。英文玩家会看到 `Defs/` 里的英文原文 `label`。若要面向国际社区需补 English |
| 中 | `Futa_Shunned_*` 缺 `requiredMemes` | 未限定 meme，可能在原版意识形态里也出现。需实机确认是否有意 |
| 中 | `IssueDef FutaFemale` / `FutaMale` 孤立 | 定义了但没有任何 `PreceptDef` 引用，疑似未完成设计 |
| 低 | `steamWorkshopUrl` 字段填的是 LoversLab 链接 | 字段名与内容不符（虽然指向正确），属不规范写法 |
| 低 | `Description` 里 "Version: 1.6" 含义不明 | 未说明是 mod 版本还是 Ideology 版本 |

---

*2026-10-17 收录。①/② 档（纯 XML，7 个文件全部读完，无推断成分）。
交叉核实：RJW 的 6 个 ThoughtWorker 类与 2 个补丁目标真实存在；
Meme 图标确认借用原版；`.dds.zstd` 经全库 ripgrep 对照确认为 1.6 通行格式；
`.clip` 经魔数确认为 Clip Studio 画稿。
本轮工具自查纠错 2 次（先用 ASCII 堆查 zstd 致假阴性、阳性对照项两次选错），均已留档。*
