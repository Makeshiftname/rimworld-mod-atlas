# Privacy, Please!（RJW 隐私意识） — 分析记录

> 收录目录 `RJW_文化玩法_隐私意识`，源目录 `F:\Games\GBL\rimworld\Mods\RJW_文化玩法_隐私意识`。
> 分档 **③ 档**（101 文件 / 83 Def / 双程序集）+ 跨 mod 上下游接口审计。
> 本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里的任何文件。

---

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `Privacy, Please!`（README 里自称 **Privacy Please Forked**） |
| packageId | `abscon.privacy.please` |
| 作者 | `AbstractConcept`（原作者）；fork 贡献者 `AblativeAbsolute`（Quirks 子项目 + quirk 图标，changelog 署名） |
| 上游 | <https://gitgud.io/AbstractConcept/privacy-please>（写在 `About/Manifest.xml` 的 `downloadUri`；`About.xml` **没有 `<url>` 元素**） |
| 授权 | **未声明**。无 LICENSE / LICENCE 文件。README 明确写 "I claim no ownership… This version may be taken down by request from the original author" |
| 规模 | **101 文件 / 1,546,527 B（1.47 MB）** |
| 体积分布 | `About/` 1,025,046 B = **66.3%**（`Preview.png` 与 `ModIcon.png` 各 510,489 B，**两文件字节完全相同**）；`1.6/Textures/` 309,241 B = 20.0%；`Defs` 62,249 B；C# 源码 49,309 B；DLL 47,616 B |
| 类型 | RJW 下游玩法扩展：Ideology 教条驱动的心情反应 + 多人互动扩展 |
| 程序集 | 2 个：`Privacy-Please.dll`（41 类型 / 15 嵌套 / **2 处 Harmony 属性**）、`Privacy-Please-Quirks.dll`（5 类型 / **1 处 Harmony 属性**，`IfModActive` 条件加载） |
| 声明版本 | `About.xml` 写 **1.4 / 1.5 / 1.6** |
| 实际版本 | **只发 `1.6/`**。`LoadFolders.xml` 的 `<v1.4>`/`<v1.5>` 各自列出 `1.4`/`1.5` + `/`，而这两个目录不存在 → 实际只加载 `/`，而 `/` 里只有 `About/`、`Languages/`、`LoadFolders.xml`、`README.md`、`changelog.txt`、`.git*`，**没有任何 Defs / Assemblies / Textures** |
| 编译基线 | `AssemblyInformationalVersion = 1.0.0+4d60a284df1fbaf4167a8b88321ca1ab732956cc`（两个 DLL 同一 SHA，说明随包源码与产物同源）；引用 `Assembly-CSharp 1.6.9438.37837`、`RJW 1.6.9402.9962`（本机实装 `1.6.9655.19392` / `RJW 1.6.9576.22392`） |

### 依赖与装况（同时扫 `Mods\` 与 `Data\`）

| 关系 | packageId | 本机状态 |
|---|---|---|
| `modDependencies`（硬） | `brrainz.harmony` | ✅ `Mods\2009463077`（0Harmony v2.4.1.0） |
| `modDependencies`（硬） | `rim.job.world` | ✅ `Mods\RJW_核心_本体` |
| `loadAfter` | `UnlimitedHugs.HugsLib` | ✅ `Mods\818773962` |
| `loadAfter` + `LoadFolders IfModActive` | `rjw.quirks` | ❌ **未安装** → Quirks 子目录整体不加载 |
| `MayRequire` | `Ludeon.RimWorld.Ideology` | ✅ `Data\Ideology` |
| `MayRequire` | `erdelf.HumanoidAlienRaces` | ✅ `Mods\839005762` |
| `MayRequire` | `calamabanana.rjw.brothelcolony` | ✅ `Mods\RJW_文化玩法_妓院殖民地-1.6-test` |
| `MayRequire` | `RJW.SexCultEssentials` | ❌ 未安装（相关 `<li>` 被正确剥离） |
| issueDefName 隐式依赖 | `rjw.sexperience.ideology` | ✅ `Mods\RJW-文化-淫秽文化`（提供 `Necrophilia` / `Bestiality` / `Rape` / `Incestuos` / `Masturbation`） |
| csproj 编译期下载 | `RJW.dll` / `RJWQuirks.dll` / `AlienRace.dll` | 仅编译用；**`AlienRace` 不在产物引用列表里**（见下） |

> `SourceCode.csproj` 有个 `Downloads` target，Release 构建时从 gitgud / GitHub 拉三份 DLL 到 `obj\`，
> 全部 `<Private>False</Private>`。这是"编译期软依赖"的标准写法，本机**不需要**该目录存在。

---

## 它是什么

### 功能

当 pawn 撞见别人（正在性交或自慰）时，按 **行为类型 × 目击者特质 × Ideology 教条** 产生心情记忆，
极端情况还会触发逃跑、呕吐、打断性行为。除旁观反应外，还扩展了两条多人路线：
路过的人被邀请加入，以及被邀请旁观。

行为类型共 10 种，`SexActReactionDefs.xml` 顶部注释写明 **"Defs need to be listed in order of priority"** ——
`GetReactionsToSexAct` 遍历 `DefDatabase<SexActReactionDef>.AllDefs`，用 `AccessTools.Method` 按 `sexActCheck`
字符串反射调用同名静态方法，**首个命中即 `break`**。实际优先级：

```
Necrophilia → BestialityWithOrdinaryAnimal → BestialityWithSpecialAnimal → Bestiality
→ Rape → Infidelity → Incestuos → Xenophilia(HAR_AlienDating) → Exhibitionism → Whoring
```

### 表驱动结构

`SexActReactionDef` 是本 mod 的核心自定义 Def，字段（源码 `Defs/SexActReactionDef.cs`）：

| 字段 | 作用 |
|---|---|
| `issueDefName` | 指向 `IssueDef`，用于反查该 pawn 对此议题的 `Precept`（`GetNamedSilentFail`，取不到就静默 null） |
| `sexActCheck` | `SexInteractionUtility` 上的静态方法名，反射调用 |
| `pawnReaction` / `witnessReaction` | 各含 `defaultThoughtDef` + `preceptThoughtDefs` + `replacementThoughts` |

`replacementThoughts` 的条目支持四种触发条件：`requiredTraits` / `requiredQuirk` / `requiredPreceptDef`
（可再叠 `requiredProperty`，取值 `Female` / `Male` / `Slave`）。

**三级判定优先级**（`SexActReactionDef.GetThoughtDefForReactor`）：

1. `replacementThoughts` —— 特质 / quirk / 教条（含 gender 过滤）优先
2. `preceptThoughtDefs` —— 拿 `precept.def.defName` 去和 thoughtDef 名做 `Contains` 子串匹配
3. `defaultThoughtDef` —— 兜底

每级判定返回一个 `ReactionToSexAct` 枚举值（`Approval=1 / Uncaring=0 / Ignored=0 / Acceptance=-1 /
Discomfort=-2 / Panic=-3 / Nausea=-4`）。调用方统一用 `>= (int)Acceptance` 判"能否接受"。

### 数值

- 目击检查：`JobDriver_Sex.SexTick` 的 postfix 里 `IsHashIntervalTick(90)`，半径 **8 格**
- 邀请冷却：每人 **600 tick**（`invitationCoolDown`）
- 惊叹图标冷却：**90 tick**
- 三人加入概率：滑条 `chanceForOtherToJoinInSex`，默认 **0.25**，范围 0–1（存档键名是 `chanceForSexExtra`）
- 呕吐概率：命中 `Nausea` 后 **25%**；逃跑格数 24
- 被打断时把参与的 `JobDriver_Sex.ticks_left` 压到 **60**
- 旁观 Job 每 **120** tick 抛一次 `EyeHeart` fleck，同时 `Need_Sex.CurLevel += 0.5/2500`
- 伴侣邀请半径：**4 格**（`HarmonyPatch_JobDriver_Sex_setup_ticks` 里独立硬编码，与 8 格目击半径不同）

### 工程手法（值得学的部分）

- **补丁桩 + 条件子程序集**：`QuirkUtility.HasQuirk(Pawn, Quirks)` 方法体是
  `var _1 = pawn; var _2 = quirk; return false;`，带 `[MethodImpl(MethodImplOptions.NoInlining)]`。
  真实现放在 `ModCompatibility/Quirks` 的独立程序集里，用 `[HarmonyPatch(typeof(QuirkUtility), nameof(HasQuirk), ...)]`
  postfix 改写 `__result`。主程序集因此**完全不引用 `RJWQuirks`**。
- **条件加载**：`<li IfModActive="rjw.quirks">1.6/ModCompatibility/Quirks</li>`，
  第三方 quirk 支持与其 Def / 图标 / DLL 全部收在这一个子目录里，主程序集零污染。
- **把 Interaction 降级成纯日志**：`InteractionWorker_NullWorker.RandomSelectionWeight` 返回 `0f`，
  `Interacted` 把 `letterText`/`letterLabel`/`letterDef` 全置 null —— 让原版 AI 完全不会随机触发这些互动，
  只留下社交日志条目。
- **`MayRequire` 用得完整**：SCE / HAR / BrothelColony / Ideology 四类外部内容全部加了 `MayRequire`。
- **`using AlienRace;` 是编译期摆设**：`CompPawnThoughtData.cs` 和 `ModDefOf.cs` 顶部都有 `using AlienRace;`，
  但产物 `Privacy-Please.dll` 的 `GetReferencedAssemblies()` **不含 `AlienRace`** —— 编译器把未使用的 using 省略了。
  所以 HAR **不是运行时硬依赖**，`ModDefOf.cs` 里那三个字段的类型是原版 `RimWorld.BodyPartGroupDef`。

### 翻译

| Def 类型 | 有 Def | 已译 | 说明 |
|---|---|---|---|
| `Privacy_Please.SexActThoughtDef` | 52 | **52** | 全覆盖，`label` + `description` 都译（按 defName 求交，未译 0、孤儿 0） |
| `PreceptDef` | 6 | **6** | `label` + `description` 全覆盖 |
| `InteractionDef` | 4 | **4** | 含 `logRulesInitiator.rulesStrings` 每条 3–4 句 |
| `IssueDef` | 2 | **2** | `label` |
| `JobDef` | 2 | **2** | `reportString` |
| `RJWQuirks.QuirkDef` | 2 | **0** | `Cuckold` / `Voyeur` 的 `label` + `description` 未译 |
| **合计** | **79**（含 10 个无译文字段的 `SexActReactionDef`） | **66 / 68 有字面量的 Def** | **97%** |

Keyed：源码 39 个 `.Translate()` 字面量，**37 个有译文**。缺口 2 个都是同一个开关：
`worry_about_whoring` / `worry_about_whoring_desc` → 中文环境下这个勾选框会显示英文键名。
另有 4 个 Keyed 条目源码从不引用：`CuckoldQuirk`、`CuckolderQuirk`、`VoyeurQuirk`、`ignore_slave_rape`。

---

## 怎么验的

### ① 核验方法（可复现）

| 环节 | 做法 |
|---|---|
| 清点 | `Get-ChildItem -LiteralPath <mod> -Recurse -File` + `[System.IO.File]::ReadAllBytes().Length`（不看 KB 化列表） |
| 源码 | 16 个 `.cs` **全文通读**（随包完整 C#，无需反编译），主程序集 14 个 + Quirks 子项目 2 个 |
| Def | Python `ElementTree` 批扫 `1.6\**\*.xml`，收 `defName` / `ParentName=` / `MayRequire=` / `texPath` / `iconPath` / `symbol` |
| 交叉引用 | 48 个 `thoughtDef` 引用、10 个 `sexActCheck`、22 个 `requiredPreceptDef`、3 个 `requiredTraits`、8 个 `issueDefName`、4 个 `requiredQuirk` 逐一回查 |
| 反射 | 独立 PowerShell 进程，预载 = 游戏 `RimWorldWin64_Data\Managed` 全部 106 个 DLL + `0Harmony.dll` + RJW **1.6** + AlienRace **1.6**，用 `AttributeType.FullName` 数 Harmony 属性 |
| 跨 mod | 字节级 `bytes.find(b"<defName>X</defName>")` 扫 85,853 个 XML（不用 XML 解析，快一个量级） |

### ② 阳性对照

| 结论 | 对照样例 | 期望 | 实测 |
|---|---|---|---|
| Harmony 属性扫描可信 | `3521312241\1.6\Assemblies\CherryPicker.dll` | 7 处 | ✅ **7** |
| 预载清单完整 | `HarmonyLib.HarmonyPatch` 可解析 + 类型数 > 0 | True / >0 | ✅ True / 41 |
| DefInjected 取段函数正确 | `Exhibitionism_Acceptable.label` → `Exhibitionism_Acceptable`；`EyeHeart` → `EyeHeart` | 全 True | ✅ 4/4（脚本内 `assert`） |
| `Contains` 方向正确 | `"SawBestiality_Horrible".Contains("Bestiality_Horrible")` = True，反向 = False | 符合 | ✅ 4/4（脚本内 `assert`） |
| IssueDef 存在性扫描可信 | `Necrophilia` / `Bestiality` / `Incestuos` / `Rape` / `Masturbation` / `Exhibitionism` 各应命中 1 个 mod | 6/6 | ✅ **6/6** |
| BodyPartGroupDef 扫描可信 | 原版 Core 应报出一整串 | ≫3 | ✅ **30** 个 |

> **`Whoring` 的零命中结论就是靠最后两行撑住的**：同一次扫描里 6 个阳性对照全部命中、
> 85,853 个 XML 全文扫完，才敢说"`Whoring` 这个 `IssueDef` 本机全库不存在"。

### ③ 自查纠错（本轮我自己的工具错了 4 次）

1. **`Contains` 匹配方向测反了两次**。
   源码是 `associatedThoughtDef.defName.Contains(preceptDefName)`，即 **thought 含 precept**。
   我第一次写成 Python `precept in thought`、第二次写成 `thought in precept`，
   两次都得出 **27/27 条 `preceptThoughtDefs` 全部失配** —— 一个几乎要写成"整套教条联动是坏的"的假缺陷。
   第三次加了一组 `assert` 自检样本（4 条，正反各 2）才锁死方向。重测结果是 **27/27 全部命中**。
   → 教训：**子串包含类断言必须配一个"已知答案"的正反样本**，不能靠读代码确认方向后再手写。

2. **整库 `grep` 的"零命中"是超时，不是结论**。
   用 grep 工具扫 `Mods\` 整库查 `<defName>Whoring</defName>`，返回 `No matches found`；
   换成另一个模式立刻 `grep timed out`。**同一个工具、同一个路径，一个报"没找到"、一个报"超时"，
   说明前者的"没找到"不可信。** 改用 Python 字节级 `bytes.find` 一次扫完 85,853 个文件才拿到结论。

3. **`literal: true` 配了含 `|` 的模式** → 把整串含竖线当字面量搜，必然 0 命中。
   我据此差点判"这 4 个类/字段全是死代码"。改成正则后拿到真实的 15 处引用位置。

4. **DefInjected 叶路径格式切错段**。
   DefInjected 用的是 `<defName.字段>` 格式（**没有 DefKind 前缀**），
   我按 `tag.split(".",1)[1]` 取"DefKind"拿到的是字段名 `label`，于是 52 条 ThoughtDef 译文全被判成孤儿、
   覆盖率报成 18%。读了一个真实文件才发现格式是 `<Exhibitionism_Acceptable.label>`。修正后 **52/52、孤儿 0**。

5. **阳性对照探针本身写错**（差点反过来说"预载失败"）。
   `[Type]::GetType('HarmonyLib.HarmonyPatch, 0Harmony')` 返回 False，
   但同一脚本的 Harmony 属性扫描正常报出 7 处 —— 说明是探针坏了不是预载坏了。
   根因：`AssemblyName` 上没有 `GetCustomAttributes` 方法。
   改用 `[System.Reflection.Assembly]::LoadFrom(...).GetType(...)` 后探针返回 True。

6. **`Incestuos` 我一开始判成拼写错误，被证伪。**
   `SexActReactionDefs.xml` 里 `<issueDefName>Incestuos</issueDefName>` 少一个 `u`，
   我认定是作者拼错、会导致 `GetNamedSilentFail` 拿不到 IssueDef、整个乱伦联动失效。
   全库字节扫描显示 **`rjw.sexperience.ideology` 自己就把 `IssueDef` 命名成 `Incestuos`** ——
   上游本来就这么拼，本 mod 是精确对齐。**同一个词的"看起来像 typo"在这个生态里可能是上游约定。**

7. **`Genitals` / `Chest` / `Anus` 判成"不存在"，其实判错了类型**。
   原版 30 个 `BodyPartGroupDef` 里没有这三个，HAR 和 6 个官方 DLC 也没有。
   再查 RJW 才发现：这三个名字在 `RJW_核心_本体\1.6\Defs\BodyPartDefs\BodyParts_Flesh.xml` 里是 **`<BodyPartDef>`**，
   不是 `BodyPartGroupDef`。所以 `ModBodyPartGroupDefOf` 的三个字段是**类型选错**，而不是"依赖缺失"。

---

## 上下游接口审计

### 与 RJW 的耦合面

| 触点 | 用法 | 备注 |
|---|---|---|
| `JobDriver_Sex.setup_ticks` / `.SexTick` | Harmony postfix | 私有方法；补丁声明写成 `ref JobDriver_Sex __instance`（Harmony 支持但 `ref` 多余） |
| `JobDriver_SexBaseInitiator` / `_BaseReciever` | 两个自定义 JobDriver 的基类 | `JobDriver_JoinInSex` / `JobDriver_WatchSex` |
| `JobDriver_Rape` / `_RapeEnemy` / `_SexBaseRecieverRaped` / `_RapeComfortPawn` / `_RandomRape` | `GetVictim` 里逐个 `is` 判定 | 逐类型硬编码，见下方"死代码" |
| `xxx.can_do_loving` / `xxx.is_satisfied` / `xxx.quick_sex` / `xxx.casual_sex` / `xxx.gettin_raped` / `xxx.IsTargetPawnOkay` | 直接引用 | **`xxx` 是 RJW 的全小写内部类**，非常规 API 面 |
| `rjw.SexFluidDef` 之类 | **未引用** | 与 Cumpilation 那套体液系统无交互 |
| `CasualSex_Helper.CanHaveSex` / `.quickieAllowedJobs` | 招募判定 | |
| `AttractionUtility.Evaluate` | 候选加权（`RandomElementByWeight`）、双向 >0.1 门槛 | |
| `CondomUtility.TryUseCondom` / `SexUtility.ProcessSex` / `reduce_rest` / `ReadyForHookup` | 委托给 RJW 原有流程 | 没重写性行为本体，只重写「怎么凑到一起」 |
| `RJWHookupSettings.QuickHookupsEnabled` | 开关 | 只控制"上床时顺带邀人"，不控制旁观邀请 |

**耦合面评价**：不重写性行为本体，只在 Job 启动/目击判定上加分支，是 RJW 下游 mod 的正确姿势。
主要风险是大量私有方法名与 `xxx.*` 内部类引用 —— RJW 改版即失效。

### 硬伤清单（按严重度）

| # | 问题 | 位置 | 后果 |
|---|---|---|---|
| 1 | **`HasQuirk` 是永远 `return false` 的补丁桩**，靠 Quirks 子程序集的 postfix 填 | `Utilities/QuirkUtility.cs:17-23` | 本机 `rjw.quirks` **未装** → `IfModActive` 不成立 → 子目录不加载 → **3 个 quirk 全部静默失效**，游戏无任何提示 |
| 2 | 即使装了 `rjw.quirks`，`QuirkDefs.Exhibitionist` 也解析不了 | `ModCompatibility/Quirks/Source/QuirksCompatibility.cs:12` | 随包只带 `QuirkDef_Cuckold.xml` / `QuirkDef_Voyeur.xml`，**没有 `Exhibitionist`**。而 `Exhibitionist` 是全库引用最多的 quirk（7 处 `requiredQuirk`） |
| 3 | **`requiredQuirk` 写了枚举外的值 `Cuckolder`** | `SexActReactionDefs.xml:244` | `Enum.TryParse<Quirks>("Cuckolder")` 失败 → 永远 false。`About.xml` 宣称的"三个 quirk"里的第三个**不存在**（Keyed 里还留着 `CuckolderQuirk` 残留键） |
| 4 | **`ExposeData` 第二行 ref 写错字段** | `Settings/BasicSettings.cs:39` | `Scribe_Values.Look(ref worryAboutExhibitionism, "worryAboutWhoring", true)` → `worryAboutWhoring` **从不读配置**（每次启动回默认 `true`），且玩家对 `worryAboutExhibitionism` 的设置**被 `worryAboutWhoring` 的值覆盖** |
| 5 | **`worryAboutMasturbation` 是死开关** | 声明 + 存档键 + UI 勾选框齐备，**逻辑层 0 处引用** | 勾了没反应 |
| 6 | **`SexActIsExhibitionism` 的 `&&`/`||` 优先级写错** | `SexInteractionUtility.cs:311` | `A && B \|\| C` 解析为 `(A&&B)\|\|C` → 关掉"担心 exhibitionism"后，**正常性交照样触发反应**，只关掉了自慰 |
| 7 | **`SexActIsIncest` 守卫写成 `\|\|`** | `SexInteractionUtility.cs:297` | 意图应为 `&&`。且它是**唯一一个不受设置开关控制**的反应 —— 其余 9 种都能关 |
| 8 | **`Whoring` 这个 IssueDef 本机全库不存在** | `SexActReactionDefs.xml:394` | `issueDef` 为 null → `GetPreceptForIssue` 返回 null → whoring 的 `preceptThoughtDefs` 整段跳过，`PartookInWhoring_Sacred` / `SawWhoring_Sacred` **永不可达**（能提供它的 SexCultEssentials 本机未装）。`replacementThoughts` 里的 BrothelColony `CB_Prostitution_*` 分支仍生效 |
| 9 | **`ModBodyPartGroupDefOf` 三个字段类型选错** | `Utilities/ModDefOf.cs:8-13` | 字段声明为 `BodyPartGroupDef`，但 `Genitals`/`Chest`/`Anus` 在 RJW 里是 `BodyPartDef` → 3 个字段永远解析失败并报错；**且整个类从未被引用** |
| 10 | `ModSexActReactionDefOf.reactionToExhibitionism`、`PawnExtension.IsExhibitionist` 也是死代码 | `ModDefOf.cs:44-47`、`PawnExtension.cs:170` | grep 确认只有定义处、无调用处 |
| 11 | **`FilthDefs.xml` 前两个 op 加空 `<comps/>` 却从不往里加 comp** | `Patches/FilthDefs.xml:7-21` | `FilthCum` / `FilthGirlCum` 白白多一个空节点；后两个 op 改的却是 `ThoughtDef`，文件内容与文件名不符 |
| 12 | `CompPawnThoughtData.xml` 的 op1 可能冲掉继承来的 comp | `Patches/CompPawnThoughtData.xml:7-13` | `Defs/ThingDef[race][not(comps)]` 给"自己没写 `<comps>` 的种族 Def"补空 `<comps/>`。原版 `BasePawn` 自己**有** `<comps>`（含 `CompAttachBase`），但 `Human` / `AnimalThingBase` 都没有自己的 `<comps>`。若字段继承是"整字段替换"，`CompAttachBase` 会被清空 → 动物不能被牵领。**需实机验证** |
| 13 | `JobDriver_JoinInSex.TryMakePreToilReservations` 恒返回 `true` | `JobDrivers/JobDriver_JoinInSex.cs:13-16` | 第三方参与者**不做任何预约**，两人以上可能被派给同一张床/同一个伴侣 |
| 14 | `HarmonyPatch_JobDriver_Sex_setup_ticks` 里 `pawn.GetSexInitiator().IsInBed(...)` 无 null 检查 | `Patches/HarmonyPatch_RJW.cs:52` | 外层只保证参与者恰好 2 人；`GetSexInitiator()` 返回 null 就 NRE |
| 15 | `GetVictim` 里 `JobDriver_RandomRape` 分支完全重复 | `SexInteractionUtility.cs:272-289` | 4 段里有 2 段逐字重复的死代码 |
| 16 | 每次反应判定都做 10 次 `AccessTools.Method` 反射查找 | `SexInteractionUtility.cs:99` | 由 90 tick 一次、半径 8 格、逐个目击者调用；方法解析无缓存 |
| 17 | `CompTickRare` 对每摊污物做一次 `AccessTools.Field` | `Comps/CompPawnThoughtData.cs:42` | 反射字段查找未缓存，走 GC 压力路径 |
| 18 | 关设置窗口时遍历全图 pawn 重画 | `Settings/BasicSettings.cs:76-90` | `PortraitsCache.SetDirty` + `GlobalTextureAtlasManager.TryMarkPawnFrameSetDirty` 对每个 map pawn 各调一次 |
| 19 | `JobDef` 用裸 defName `JoinInSex` / `WatchSex` | `Defs/JobDefs.xml` | 无 mod 前缀，与其它 mod 撞名风险；且源码用 `GetNamed("JoinInSex", false)`（不报错） |
| 20 | `MasturbationPercept.xml` 的 op **没有 `MayRequire`** | `Patches/MasturbationPercept.xml:7-12` | xpath 指向 `IssueDef[defName="Masturbation"]`，该 Def 由 `rjw.sexperience.ideology` 提供；上游不在就会报错 |
| 21 | Keyed 缺 `worry_about_whoring` / `_desc` | `Languages/.../Keyed/SettingsKeys.xml` | 中文环境下该开关显示英文键名 |
| 22 | 两个 QuirkDef 的 `label` + `description` 未译 | `ModCompatibility/Quirks/Defs/...` | 4 个字段（且这两个 Def 在本机根本不加载） |
| 23 | 贴图 `UI/Flecks/Eye`、`UI/Flecks/Heart` 无任何引用 | `1.6/Textures/UI/Flecks/` | 只定义了 `EyeHeart` 一个 FleckDef，代码也只用 `EyeHeart` |
| 24 | 主树 9 个贴图 stem 的 `.dds` 是死重量 | `1.6/Textures/` | 都有 `.dds.zstd`，1.5+ 优先读 zstd。**Quirks 那 2 个相反**：无 zstd，其 `.dds` 是实际读取格式，不是冗余 |
| 25 | `About/Manifest.xml` 版本号还写 `1.0.0` | changelog 已到 **V1.4** | |
| 26 | 43 处 Def stage 名拼写错 | `Defs/ThoughtDefs/*.xml` | `Proud_of_seing_whoring`、`enjoing_incestours_act`、`cukolded_by_partner`、`exhilerated_*`、`caught_having_incestous_act` vs `caught_an_incestous_act` 等。不影响显示，但会污染翻译键、让译者困惑 |
| 27 | `Preview.png` 与 `ModIcon.png` 字节完全相同 | `About/` | 1,020,978 B 白重复（占全 mod 66%） |

### 顺带确认的设计是**正确**的

- 48 个 `thoughtDef` 引用 **100% 在本 mod 内解析，0 缺失**
- 10 个 `sexActCheck` 方法 **全部存在**（正则回查源码）
- `preceptThoughtDefs` 的 `Contains` 子串匹配 **27/27 全部命中**本机教条
  （前提是 `Whoring` 那个 issue 存在；见 #8）
  - 它确实脆弱：`Incestuos_Disapproved` 是 `Incestuos_Disapproved_CloseOnly` 的子串，
    靠 `preceptThoughtDefs` **列表顺序**保证先匹配长的那个。当前顺序恰好是对的，但改顺序就会静默串档。
  - 不过一个议题同时只能持有一个 precept，所以实际不会同时命中两个。
- `reactionToWhoring` 里 `Exhibitionism_*` 被当成 `requiredPreceptDef` 用（而非 issue 匹配）——
  这是有意的跨议题桥接，逻辑自洽。

---

## 可复用结论

1. **"永远 `return false` 的方法 + `[MethodImpl(NoInlining)]` + 条件加载子程序集"是可选功能的干净实现**：
   主程序集零第三方依赖，能力靠 `LoadFolders` 的 `IfModActive` + 子程序集 postfix 注入。
   **代价是：可选功能缺失时游戏完全静默**。用户看到的是"勾了没用"，没有任何日志线索。
   → 审 mod 时看到 `return false;` 的可疑桩方法，第一件事是找它的补丁方，并确认那个补丁方**在本机装没装**。

2. **`Enum.TryParse` 做数据驱动的枚举查表，失败是静默的**。
   XML 里写错一个 quirk 名 / trait 名，运行时表现为"这条规则永远不生效"，不报错。
   → 静态审计手法：把 XML 里所有"字符串查枚举/查 Def 名"的字段收齐，和枚举定义求差集，
   差集非空就是硬伤。本例 4 个 `requiredQuirk` 里 1 个在枚举外。

3. **`Scribe_Values.Look(ref X, "key", def)` 的 ref 与 key 不一致，是最难发现的一类 bug**：
   编译通过、运行不报错、UI 正常显示、存档文件正常写出，只是**值悄悄错了**。
   静态检测极便宜 —— 把每行的 `ref` 字段和 key 字符串列出来对齐，不一致一眼可见。
   → 同类要一起查：**声明了但 `ExposeData` 里从未出现的字段**（本例有 1 个）+ **Keyed 里有但源码从不引用的键**（本例 4 个）。

4. **子串包含匹配做 Def 名映射脆弱但当前可用**：
   `thoughtDefName.Contains(preceptDefName)` 让本 mod 不用在 Def 里重复声明 precept 名，
   27 条映射全靠它。风险是"一个名字是另一个名字的子串"。
   → 用它可以，但**列表顺序必须按"长名在前"排**，并在自己的脚本里对每个映射做一次正反断言。

5. **判断"某个 Def 全库不存在"前，先跑 6 个已知存在的同类 Def 当阳性对照**，
   并**用字节级 `bytes.find` 而不是 XML 解析或 grep**：
   - grep 工具在整库路径上会超时，而超时和"没找到"在某些调用路径下返回同一个结果
   - XML 解析慢两个数量级（1021 个 mod 全解析跑不完）
   → 三层判定：**对照命中 → 才看目标 → 目标零命中才是结论**。

6. **`About.xml` 的 `<author>` 与 README 的 fork 声明要分开看**。
   这里 `About.xml` 只写原作者 `AbstractConcept`，但 mod 目录名是中文二次整理名、
   README 标题是 "Privacy Please Forked"、changelog 里有第三方署名、两个 DLL 的 SHA 相同但
   `Manifest.xml` 的 `downloadUri` 仍指向上游 —— **四种信号共同表明这是未改 `About` 归属的 fork**。
   收录时按 fork 处理，并记录上游地址以便追溯。

7. **`LoadFolders.xml` 里"列了但不存在的目录"会让该游戏版本静默降级到 `/`**。
   本例声明支持 1.4/1.5/1.6，实际只发 `1.6/`；在 1.4/1.5 上 `/` 里只有 About 和 Languages，
   等于**没有任何 Def 与代码**。审多版本 mod 时，把 `LoadFolders` 里每个版本段的每个目录
   拿去 `Test-Path` 走一遍，比读 `<supportedVersions>` 可靠。

8. **`.dds` 死重量要看"有没有同 stem 的 `.dds.zstd`"，不能只看"游戏读不读 dds"**。
   本例主树 9 个 stem 全有 zstd → `.dds` 全是死重量；
   Quirks 子目录 2 个 stem 没有 zstd → 它们的 `.dds` 是**实际读取格式**。
   同一份 mod 里两种相反结论并存，说明这条规则必须**逐 stem 判**。

9. **反射审 .NET DLL 的预载清单**：游戏 `RimWorldWin64_Data\Managed` 全部 + `0Harmony.dll`
   （在 `Mods\2009463077\Current\Assemblies\`，不在游戏目录）
   + 目标 `GetReferencedAssemblies()` 里每个第三方程序集**且要选对版本**。
   本机 RJW 有 1.1–1.6 六份、版本号各不相同。探针用
   `[Assembly]::LoadFrom(0Harmony).GetType('HarmonyLib.HarmonyPatch')`，
   **不要**用 `[Type]::GetType(...)`（在 PS 里对已 LoadFrom 的程序集不稳定）。

10. **"看起来像 typo 的上游专名不要当 bug"**。
    `Incestuos` 少一个 `u`，我判成拼写错误；实际是 `rjw.sexperience.ideology` 的原始命名，
    本 mod 精确对齐。→ 拿可疑 defName 去**全库搜同名**，若有人用同样的拼法，就是生态约定。

---

## 修改建议

> **均未执行。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。**
> 且本 mod 是他人作品、按仓库约定不宜改动 mod 本体；以下仅为分析结论，若要修应由作者在其仓库进行。

### P0 — 会导致功能完全静默失效

1. `SexInteractionUtility.cs:311` 的括号：`return (BasicSettings.worryAboutExhibitionism && jobDriver.pawn.IsMasturbating()) || (...)`，
   让 exhibitionism 开关真正管住两条分支。
2. `BasicSettings.cs:39` 改回 `Scribe_Values.Look(ref worryAboutWhoring, "worryAboutWhoring", true);`。
3. 给 `worryAboutMasturbation` 补上逻辑读取点（目前 `SexActIsExhibitionism` 里自慰分支应受它控制），
   或从 UI 与存档键里删掉这个死开关。
4. `Quirks/Source/QuirksCompatibility.cs` 的 `QuirkDefs` 补 `Exhibitionist` 对应的 `QuirkDef`
   （或确认由 `rjw.quirks` 提供并在 `About` 里写明），并把 `SexActReactionDefs.xml:244` 的
   `Cuckolder` 与 `QuirkUtility.Quirks` 对齐（补枚举值或删该规则）。
5. `whoring` 的 `issueDefName` 改为对 `SexCultEssentials` 存在与否的容错写法，
   或给 `PartookInWhoring_Sacred` / `SawWhoring_Sacred` 加 `MayRequire` 说明。

### P1 — 报错 / 空转 / 稳定性

6. 删掉 `ModBodyPartGroupDefOf`、`ModSexActReactionDefOf`、`PawnExtension.IsExhibitionist`
   三个零引用类（连带消掉 4 条启动期 DefOf 报错）。
7. `SexInteractionUtility.cs:297` 的 `||` 改 `&&`；顺便给 `SexActIsIncest` 加一个
   `BasicSettings.worryAboutIncest` 开关，与其余 9 种对齐。
8. `SexInteractionUtility.cs:272-289` 删掉两段重复的 `JobDriver_RandomRape`。
9. `Patches/FilthDefs.xml` 删掉两个加空 `<comps/>` 的 op（或者补上要加的 comp），
   并把两个改 `ThoughtDef` 的 op 挪到名实相符的文件里。
10. `Patches/MasturbationPercept.xml` 的 op 加 `MayRequire="rjw.sexperience.ideology"`。
11. `HarmonyPatch_RJW.cs:52` 给 `GetSexInitiator()` 结果加 null 检查。
12. `LoadFolders.xml` 要么补 `1.4/`、`1.5/` 目录，要么把 `About.xml` 的 `<supportedVersions>`
    收敛到只声明 1.6 —— 现状是"声明支持但内容为空"。

### P2 — 性能与体积

13. `GetReactionsToSexAct` 把 `AccessTools.Method(...)` 结果按 `sexActCheck` 缓存起来
    （10 个 Def 的字符串→`MethodInfo` 映射，构造时建一次）。
14. `CompPawnThoughtData.CompTickRare` 把 `AccessTools.Field(typeof(Filth), "growTick")`
    提成 `static readonly FieldInfo`。
15. `ApplySettings` 加上 `pawn.RaceProps.IsMechanoid == false` 之类的过滤，
    或只在设置真正变化时才重画全图。
16. `About/Manifest.xml` 版本号 `1.0.0` → 与 changelog 对齐（当前应为 1.4）。
17. 删 `1.6/Textures/UI/Flecks/Eye.*` 与 `Heart.*`（无引用），
    以及主树 9 个 stem 的 `.dds`（有 `.dds.zstd` 时不被读取）。
    Quirks 那 2 个 `.dds` **要保留** —— 无 zstd，是实际读取格式。

### P3 — 一致性与文案

18. `Keyed/SettingsKeys.xml` 补 `worry_about_whoring` / `worry_about_whoring_desc`；
    清理 4 个源码不引用的残留键（`CuckoldQuirk` / `CuckolderQuirk` / `VoyeurQuirk` / `ignore_slave_rape`）。
19. 补两个 QuirkDef 的中文 `label` / `description`。
20. `JobDefs.xml` 的 defName 加上 mod 前缀（如 `Privacy_JoinInSex`），同步改两处 `GetNamed`。
21. 修 `Defs/ThoughtDefs/*.xml` 里 43 处 stage 名拼写（会同步影响翻译键）。
22. `About/ModIcon.png` 与 `About/Preview.png` 二选一，或换成不同尺寸的图标。
23. `InteractionDefs.xml` 里 `Exclaimation` → `Exclamation`（贴图文件名同步改）。
    注意这条会牵动已有翻译的 `<!-- EN: -->` 注释，属可选项。

### 未核实项（如实标注）

- **`CompPawnThoughtData.xml` 的 `<comps>` 会不会冲掉继承来的 `CompAttachBase`** ——
  取决于 RimWorld 字段继承是"整字段替换"还是"父子合并"（`InheritanceResolver` 等类型名在 106 个游戏程序集里 0 命中，未反编译 IL）。
  **实机验证方法**：装上本 mod，选一只可被牵领的动物，看能否正常套上牵引绳。
- **`LoadFolders` 里不存在的目录是静默跳过还是报错** —— 未反编译 `Verse.ModContentPack.InitLoadFolders()`。
  实机验证：在 1.5 存档里开本 mod，看 Player.log 有无相关报错。
- **`1.4` / `1.5` 兼容性** —— 本机无对应版本内容可验；按现状这两个版本实际上没有代码与 Def。
- **`JobDriver_Sex.setup_ticks` / `SexTick` 这两个私有方法名在 RJW 1.1–1.4 是否同名** ——
  本 mod 的 `1.4`/`1.5` 目录不存在，无法比对。若上游同 SHA 的 1.4 构建存在，需另行反射核对。
- **`xxx.*`（RJW 全小写内部类）在 RJW 各版本是否稳定** —— 只核了本机 1.6 那份 `RJW.dll`。
- **本 mod 未在 1.6 实机加载过** —— 以上全部结论来自源码通读 + XML/DLL 静态核验。
  尤其实机最值得先看的是：`ModBodyPartGroupDefOf` 的 3 条 DefOf 报错是否真的出现在 Player.log。
- **`RJW.SexCultEssentials` 装上后的表现** —— 本机未装，`MayRequire` 分支的正确性只做了静态确认。
- **fork 的授权链** —— `About.xml` 无 `<url>`、`Manifest.xml` 的 `downloadUri` 指向上游、
  README 声明"原作者可要求下架"、无 LICENSE。**原作者的许可条款未查**，转载前需确认。
