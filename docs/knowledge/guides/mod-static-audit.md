# mod 静态审计方法（不改 mod 本体的前提下核验它到底做了什么）

本篇不讲「怎么实现功能」，讲**收录/审阅一个他人 mod 时，如何在不改动它的前提下证明它的行为**：
依赖装况、程序集里到底有什么、补丁打在哪个方法上、翻译能否生效、多版本是否真能加载、贴图是否可达。

收录来的 mod 不宜改动本体，所有结论只能靠**只读静态核验**得出；而静态核验的最大风险是
**假阴性**（把「我的工具坏了」写成「mod 缺东西」）。所以第 0 节是全篇前提。

---

## 0. 总原则：零命中先证伪工具

任何「不存在 / 未引用 / 缺失 / 这个类没有这个字段」的结论，动笔前必须先排除工具侧原因。
本仓库历史踩过的工具侧原因至少 6 种：

| 症状 | 真实原因 | 自查方式 |
|---|---|---|
| 零命中 | 检索超时（与「没找到」返回同样结果） | 收窄路径重跑；换字节级扫描 |
| 零命中 | 路径分隔符不匹配（`A\B` vs `A/B`） | 比对前统一 `.replace("\\", "/")` |
| 零命中 | 文件名没剥扩展名（`x.png` vs `x.dds`） | 先 `splitext()` 取 stem |
| 零命中 | XML 里把**属性**当子元素找（`ParentName`/`Name`/`Abstract`） | `el.get("ParentName")` 而非 `findtext` |
| 零命中 | 正则里含 `|` 且按字面量匹配 | 改用真正的 alternation |
| 大量零命中 | 查表键大小写不敏感 / `$` 锚到整段末尾 | 换成按 token 逐个比对 |
| 加载链整体失效 | 反射预载清单漏程序集 | 见 §2.1 的自检正控 |

**三个高灵敏度的检测信号**（比「有没有差异」更早暴露问题）：

1. **差异行数 == 文件总数** → 说明两边根本没可比上（键选错了），不是「内容有问题」。
2. **正控也一起失败** → 说明是工具/环境坏了，不是被测对象的问题。
3. **类型表返回 0 个类型** → 预载失败，不是「这个 mod 没定义自定义类型」。

**阳性对照（positive control）纪律**：任何零命中的扫描，同一轮里必须扫 1–6 个**已知存在**的目标，
全命中才敢对目标的零命中下结论。对照选错时失败的是对照——此时第一反应是**换对照**，
而不是改结论。常见选错：拿元数据成员名（存在 `#Strings` 堆）当字符串字面量（存在 `#US` 堆）的对照。

**方向敏感断言**：读完代码方向后仍要写自检样本。Python 的 `a in b` 等于 C# 的 `b.Contains(a)`，
方向与书写顺序相反；这类断言连错两次就会产出「27/27 全部失配」的整片假缺陷。
用 `assert` 把正反样本写进脚本，比事后人工核对可靠。

---

## 1. 依赖与装况核验

**1.1 判「某 packageId 是否安装」必须解析 XML，不能 grep。**
子串 grep 会命中别的 mod 的 `<modDependencies>` / `<loadAfter>` 里列出的 packageId。
实例：`erdelf.HumanoidAlienRaces` 命中某个贴图修正包的依赖列表、`Haplo.Miscellaneous.Core`
命中 `2015093322`（其实是边缘汉化包）——两次都误判成「已安装」。
正确做法：遍历各 `About/About.xml`，只取 `ModMetaData` 的**直接子元素** `<packageId>`
（嵌套在 `<li>` 里的不算），用 `ET.parse` 读。

**1.2 不能用哈希表判存在性**（PowerShell 的 `@{}` 键大小写不敏感）。
查 `oskarpotocki.vanillafactionsexpanded.core` 与 `OskarPotocki.VanillaFactionsExpanded.Core`
会命中同一条，差一步就凭空造出一个「重复 packageId」。判存在性一律走 XML 直系子元素，
并把查到的**原始大小写**记进记录。

> 反向结论：**RimWorld 自己匹配 packageId 是大小写不敏感的**——`Verse.ModMetaData` 有
> `packageIdLowerCase` 字段与 `SamePackageId` 方法。所以 `About.xml` 的 `loadBefore`/`loadAfter`
> 写成全小写**不构成 bug**（Cherry Picker 的 `3521312241` 就这么写）。
> 判定「大小写写错导致加载顺序失效」之前先确认这一点。

**1.3 官方 DLC 的 packageId 在 `Data\<DLC>\About\About.xml`，不在 `Mods\`。**
只扫 `Mods\*\About\About.xml` 的依赖脚本会把 `Ludeon.RimWorld.Royalty` / `Ideology` / `Biotech` /
`Anomaly` / `Odyssey` / `Ludeon.RimWorld` **全部误报 MISSING**。
→ 依赖装况扫描必须**同时扫 `Mods/` 与 `Data/`**。

**1.4 判定「运行时是否真依赖某 mod」看产物引用表，不看 `using`。**
实例：某 mod 源码 3 处 `using AlienRace;`、csproj 也 `<Reference Include="AlienRace">`，
但产物 `GetReferencedAssemblies()` **不含 AlienRace**（编译器省略了未使用的 using）→ 不是硬依赖；
反之同 mod 的 Quirks 子程序集**确实**列出 `RJWQuirks 1.6.0.1` → 是硬依赖。

**1.5 「列了支持某版本」≠「那个版本可用」。**
把 `LoadFolders.xml` 每个版本段的每个目录拿去做存在性检查，比读 `<supportedVersions>` 可靠。
实例：某 mod 声明支持 1.4/1.5/1.6 但只发 `1.6/`；1.4/1.5 落到 `/`，而 `/` 里只有 About/Languages
→ **那两个字面上「支持」的版本没有任何 Def 与代码**。

---

## 2. 程序集与类型判定（反射）

### 2.1 判断某 DLL 是否*定义*了某类型 → 必须枚举类型表，二进制字符串扫描不够

在 DLL 字节里搜命名空间串，**定义方和引用方都会命中**，区分不了；
且「定义方」不会出现在自己的 `GetReferencedAssemblies()` 里。
实例：`SizedApparel.SkeletonDef` —— `GetReferencedAssemblies()` 没列 SizedApparel，
字符串扫描只找到 4 个 RJW 适配 dll，我据此判「SizedApparel 框架未安装」，
实际 `SizedApparelforRJW.dll` 自己定义了整个 `SizedApparel.*`（96 个类型）。

正确做法（顺序不能省）：

1. `LoadFrom` 预加载游戏 `Managed` 全部 DLL；
2. 再加目标 DLL 的**全部引用程序集**（先扫 `GetReferencedAssemblies()` 照着补，别凭记忆猜）；
3. **Harmony 必须单独加**——`0Harmony.dll` 不在游戏 `Managed` 目录（在某个 mod 的
   `Current/Assemblies/` 下）；不预载时 `HarmonyLib.*` 属性类型解析不了；
4. `GetTypes()`，吃 `ReflectionTypeLoadException.Types` 拿部分类型；
5. 类型表要含**嵌套类型**（`GetNestedTypes()`），否则 `<GetGizmos>d__26` 这类全漏。

**自检正控**：目标类型数必须 > 0 **且** `HarmonyLib.HarmonyPatch` 能解析。任一为 0 就是预载清单漏了东西。

**2.2 同名程序集不能在同一 AppDomain 里连着反射。**
七版本目录的 DLL 全叫 `HugsLib`，第二个 `ReflectionOnlyLoadFrom` 就抛
「程序集已从其他位置加载」——身份冲突是硬限制，换目录/改名都没用。
**唯一可靠解法：每个版本开一个独立进程**。
实例：某 mod 的 `RJW.dll` 在本机有 1.1/1.2/1.3/1.4/1.5/1.6 **六份且版本号各不相同**
（1.6 是 `1.6.9576.22392`，1.5 是 `1.5.9201.31093`，1.1–1.4 全是 `0.0.0.0`）
→ 预载错版本会得到不同结果。

**2.3 核心类型在 `RimWorld` 命名空间，不在 `Verse`。**
`RimWorld.BuildingProperties`、`RimWorld.XenotypeDef` 都是。
写 `Verse.XenotypeDef` 会让 `GetType` 返回 `$null`，而 `$null` 上调 `GetField` 一路抛异常——
外面若套了 `try/catch`，就变成**成片的可信度为零的假阴性**（曾据此差点把 5 个真实字段写成 absent）。
→ **判定类型不存在之前，先用已知存在的类型（如 `Verse.Building`）验证反射工具本身。**

**2.4 `Assemblies/*.xml` 有两种可能，先看根元素。**
`<doc><assembly><name>X</name>` = **.NET XML 文档注释文件**（IntelliSense 用，RimWorld 不读）；
`<XmlExtensionDef>` 之类才是 ModExtension 数据。
实例：`2574315206`（XML Extensions）每版都带一份 26 KB 的 `Assemblies/XmlExtensions.dll.xml`，
我误当成「它自己声明的 API」，按 `Class=` 统计全空才暴露。
→ **文档文件反而是金矿**：逐条列出公开成员**和作者的 `<summary>` / `<param>` 说明**，
比反射出的裸签名信息量大得多；定自定义 Def 类的字段清单也优先用它。

**2.5 反射自定义 Def 类的字段表 = 免费拿到这个 mod 的内容 schema。**
实例：`Cumpilation.Cumflation.StuffingDef`(8 字段) /
`Cumpilation.Gathering.FluidGatheringDef`(8) / `Cumpilation.Reactions.Fluid_Record_Mapping`(3)。
读完就知道整条内容管线是**表驱动**的（液体→Hediff→三档想法 / 液体↔可收集物换算 / 液体→两条 RecordDef），
比通读 192 个类型高效得多。
做法：从 XML 收集带命名空间的根元素名 → 逐个回查 DLL 类型表。

**2.6 按「基类等于 X」筛派生关系必须走完整继承链，不能只看直接基类。**
实例：`RJW_核心_本体` 的 Def XML 里有 **17 个** `rjw.*` 自定义根元素，
只用单层正则只得到 **10 个**——少的 7 个派生自中间层（`Verse.HediffDef`、`Verse.MentalStateDef`、
`Verse.MentalBreakDef`、`Verse.ThingDef`、`Verse.RecipeDef`，以及该 mod 自己的 `rjw.HediffDef_EnemyImplants`）。
→ 回答「某 mod 定义了几个自定义 Def 类型」时，**先把 XML 里用到的根元素名逐个回查程序集、
再沿 BaseType 一路往上走到 `Verse.Def`**。数量报小会直接误导工作量估计。

**2.7 判定「上游扩展点」时优先找插件点，而不是自己写补丁。**
RJW 的 `[StandardPreference]` + `rjw.Modules.Attraction.AttractionPreference` 是一套完整注册机制：
带特性的静态 `ApplyTo(ref AttractionRequest)` 里 `request.SetPreference(new X())`、
构造函数 `base(AttractionMode.X, nameof(Y), FactorOperation.Z)`、
覆写 `GetOperand` 返回 0/1/1.25 这类乘数。**这种扩展点比自己写补丁划算得多，审 mod 时值得专门找。**

---

## 3. 无源码时的二进制静态扫描

**3.1 两个堆都要扫，且必须后缀感知。**
- **#Strings 堆（ASCII，按 0x00 切分）**放类型名/成员名，但做**后缀共享**：
  短名字可能只作为长名字内部的后缀存在。实例：`TraitDef` 只藏在 `WeaponTraitDef` 里、
  `RulePackDef` 藏在 `processRulePackDef` 里——朴素提取会**假阴性**。
  → 存在性判断用 `regex Escape($n) + '$'` 后缀匹配。
- **#US 堆（UTF-16，同样按 0x00 切分）**放字符串字面量。
  `AccessTools.TypeByName("…")` 的参数、`GenGeneric` 的方法名**只**在这里，ASCII 提取器一个都看不见。

**3.2 先切成 token 数组再比对。**
`[regex]::Matches($bigString, Escape($n)+'$')` 不加 `RegexOptions.Multiline` 时
`$` 只锚到整段输入末尾，等于在找「最后一个 token 正好等于该名」，扫大 DLL 时全部报 0。

**3.3 扫 Harmony 补丁三步缺一不可。**
① 先 `LoadFrom` Harmony（见 §2.1，注意程序集名是 **`0Harmony`** 不是 `HarmonyLib`）；
② **用 `AttributeType.FullName` 判属性，不要用 `ToString()`**，并把属性读取异常**显式计数打出来**
（`try/catch` 吞掉异常会让「这个 mod 没用 Harmony」和「我的扫描器坏了」看起来一模一样）；
③ 阳性对照拿已知带补丁的 DLL（本机现成的是 Cherry Picker 的 `3521312241`，应报 7 处：
6 个 `Patch_*` 类型级 `HarmonyPatch` + `Patch_Wear` 的 `HarmonyPriority`）。

**3.4 CHANGELOG 声明的改动可用二进制独立证实。**
实例：`changelog.txt` 说 1.2.4 把某 XML 改动换成了 .dll 补丁，1.6 的 DLL 里确实多出
`Patch_AllowedStuffsFor_noCumRuins` 而 1.5 没有。正向可用（log 有→DLL 有），
反向也可用（log 有→DLL 无 = 改动没生效或被回滚）。

**3.5 `.NET SDK` 会把构建时的 git commit 写进 `AssemblyInformationalVersion`**（`<Version>+<commit>`）
——读它再按 SHA fetch 就能拿到产物对应的确切源码，即使该 commit 不在任何公开分支上。

---

## 4. Harmony 与 PatchOperation 审计

**4.1 源码里注释掉的补丁，可能在旧版本 DLL 里仍然活着。**
实例：某 mod 三个 Harmony 补丁当前源码全注释，但 1.3 的 DLL Harmony 属性 10 处、1.4+ 只有 7 处
→ 1.3 下仍在生效。**只看源码会以为各版本行为一致，必须反射每个版本的 DLL 并与源码对照。**
反向可用来确认依赖迁移：同 mod 的 `CRIALactation` 在 1.5 从 REF `Milk` 变成 `EqualMilking`，
正好对上 `LoadFolders` 条件依赖从 `rjw.milk.humanoid` 换成 `akaster.equalmilking`
——两条独立证据对上才敢下结论。

**4.2 打补丁前先读目标原版 Def，它可能已经有那个节点。**
原版 `ThingDef Name="BasePawn"` 自带 `<comps>`（`Core\Defs\ThingDefs_Races\Races_Animal_Base.xml`，
内容是 `CompAttachBase`）。所以「往 BasePawn 挂 comp」类补丁可以省掉造空 `<comps/>` 的步骤——
我曾推理「条件分支不跑会导致补丁失败」，读到原文件才发现目标节点本来就在，**差点写成假缺陷**。
（同时：那个 `PatchOperationConditional` 的 nomatch 分支才是死代码，Core 单独就有 398 处 `<comps>`。）

**4.3 抽象父类正则不能假设属性顺序。**
用 `Name="..."[^>]*Abstract="?true` 会漏掉
`<TerrainDef Abstract="True" ParentName="FloorBase" Name="TileMetalBase">` 这类 `Abstract` 在前的写法。
→ 改成两次独立匹配，或直接全文搜名字再人工确认。

**4.4 条件加载是「零提示」的静默失效源。**
`LoadFolders.xml` 支持 `IfModActive=`（软依赖）与 `IfModNotActive=`（互斥加载）。
两者都不产生任何游戏提示，功能静默消失。实例：`akaster.equalmilking` 只写在 `loadAfter`、
没进 `modDependencies` → 整个 `CRIALactation`（Def + DLL）不加载且零提示。
想给提示要么写进 `modDependencies`，要么恢复作者那个被注释掉的 `SoftDependencyChecker`
（`[StaticConstructorOnStartup]` + `Log.Warning`）。`IfModNotActive` 更隐蔽——它只在
**「依赖不存在」**时才生效。

**4.5 「永远 `return false` 的方法 + `[MethodImpl(NoInlining)]` + `LoadFolders IfModActive` 子程序集 postfix」
是可选功能的干净实现**（主程序集零第三方依赖），**代价是完全静默**。
→ 审 mod 看到可疑桩方法，第一件事是找补丁方，并确认**补丁方在本机装没装**。

---

## 5. Def 与 DefInjected 审计

**5.1 DefInjected 的标签是 `<defName.字段>` 叶路径格式，标签里没有 DefKind 前缀。**
实例 `<Exhibitionism_Acceptable.label>可接受</Exhibitionism_Acceptable.label>`。
按 `tag.split(".",1)[1]` 取「DefKind」拿到的是**字段名** `label`，于是 52 条 ThoughtDef 译文
全被判成孤儿、覆盖率报成 18%。**正确取法是取第一段 `tag.split(".",1)[0]`**。
字段可能是多段（`stages.<stageName>.label`），也要能处理。
→ 写这类脚本前先 `read` 一个真实 DefInjected 文件，别凭印象。

**5.2 DefInjected 的文件夹名是装饰性的，Def 类型取自元素名。**
`DefInjected/KeyBindingCategoryDefs/`（复数）与 `DefInjected/KeyBindingCategoryDef/`（单数）**都能生效**。
实例：HugsLib（`818773962`）的韩语用复数目录名，我差点记成「韩语翻译失效」。
→ 核对翻译能否生效**只看元素名**，别看文件夹名。

**5.3 翻译覆盖率必须按 defName 求交，且两边都要归一化。**
实例：译文归在 `DefInjected/ThoughtDef/`，而源码里的根元素是 `<Privacy_Please.SexActThoughtDef>`。
按文件夹配对会得出「全未翻译」的假结论。
→ 源侧收「根元素 tag → defName」；译侧收 `DefInjected/<文件夹名>/**` 的 defName（第一段），
再按**文件夹名**去和源侧的**根元素 tag** 对齐。子模块命名空间（`Privacy_Please.` / `RJWQuirks.`）
要从 tag 里剥掉再比对。

**5.4 「字节不同」≠「内容冲突」，翻译比对要分三层：字节 → 空白归一化 → 逐键→值。**
实例：38 个共享 DefInjected 里 4 个字节不同，但译文值**全部一致**，差异只在 `<!-- EN: -->`
注释（1.6 那份英文描述已更新，根目录那份停留在旧文案）与缩进。
**先做最贵的那层（逐键→值）再下结论**，否则会把「维护冗余」误报成「翻译打架」。
归一化器不能太宽松——用它验一遍「原本字节就相同的文件」，若它们归一化后不等，则该测试无意义。

**5.5 全库 Def 存在性检查用字节级扫描，不要用递归 grep。**
在 mod 集合根目录上做内容检索会超时，而**超时与「没找到」可能返回同一个结果**——
同一工具、同一路径，一个模式报 `No matches found`、另一个报 `grep timed out`，说明前者不可信。
→ 改用 Python 字节级 `data.find(b"<defName>X</defName>")`：比 XML 解析快两个数量级，且不会超时。
→ **必须配阳性对照**：同一轮扫 6 个已知存在的 defName，全命中才敢对目标的零命中下结论。

**5.6 `Enum.TryParse<T>` 做数据驱动查表，失败是静默的。**
XML 里写错一个 quirk 名 → 返回 false → 那条规则永远不生效，不报错。
→ 把 XML 里所有「字符串查枚举 / 查 Def 名」的字段收齐，与枚举定义求差集。
实例：4 个 `requiredQuirk` 里 1 个（`Cuckolder`）在枚举外，而 `About.xml` 还在宣传它。

**5.7 `Scribe_Values.Look(ref X, "key", def)` 的 ref 与 key 不一致是最难发现的 bug 类。**
编译通过、运行不报错、UI 正常、存档正常写，只是**值悄悄错了**。
静态检测三件套（都很便宜）：
① 逐行对齐 `ref` 字段与 key 字符串；
② **声明了但 `ExposeData` 里从未出现的字段**（实例：`worryAboutWhoring`）；
③ **Keyed 里有但源码 `.Translate()` 字面量里没有的键**（实例 4 个残留）。
注意 ③ 的反向也查：源码用了但 Keyed 缺的。

**5.8 「看起来像 typo 的上游专名」不要当 bug。**
实例：`<issueDefName>Incestuos</issueDefName>` 少一个 `u`，判成拼写错误会导致整个乱伦联动失效；
实际是 `rjw.sexperience.ideology` 自己就这么命名，本 mod 是精确对齐。**同名即生态约定。**

**5.9 找不到某个 Def 名不等于缺陷——先确认它的 Def 类型。**
实例：`ModBodyPartGroupDefOf` 把 `Genitals`/`Chest`/`Anus` 声明成 `BodyPartGroupDef`，
但原版 30 个 `BodyPartGroupDef` 里没有、6 个官方 DLC 和 HAR 也没有；
RJW 的 `1.6\Defs\BodyPartDefs\BodyParts_Flesh.xml` 里这三个是 **`<BodyPartDef>`**。
→ 判「某个 Def 名不存在」时同时确认 Def 类型：找不到可能是类型选错。

**5.10 缺陷数量与方法都会骗人，所以结论要交叉验证。**
实例：某 mod 里 `associatedThoughtDef.defName.Contains(preceptDefName)` 这条教条联动，
我连错两次，得到「27/27 条全部失配」的假缺陷；加 4 条 assert 样本后重测是 **27/27 全中**。

---

## 6. 多版本结构与工程约定

**6.1 多项目 mod 里每个项目的语言树要各自带 `Languages/` 层**：`<loadFolder>/Languages/<lang>/`。
少一层整棵翻译失效且**不报错**（实例 `CRIAOrgy/ChineseSimplified/` 少 `Languages/`，
而同 mod 的 `CRIALactation/1.x/Languages/English/Keyed/` 是对的）。核对翻译位置先看层级。

**6.2 `<Publicize Include="RJW" />` + `<Publicize Include="Assembly-CSharp" />`**
（NuGet `Krafs.Publicizer`，配套 `packages.config` + `EnsureNuGetPackageBuildImports` 目标）
＝**编译期**访问 internal/private，可直接 `AccessTools.DeclaredMethod(typeof(第三方内部类), ...)`。
引用第三方 mod DLL 必须 `<Private>False</Private>`，否则会复制进自己的输出造成类型身份分裂。

**6.3 用编译配置决定输出版本目录**：`Debug → 1.5\Assemblies\`、`Release → 1.6\Assemblies\`。
源码一份，切版本只改 OutputPath。`AssemblyName` 要带撇号就写 `%27`（产物还原成 `'`）。

**6.4 `[HarmonyReversePatch(HarmonyReversePatchType.Snapshot)]`**：打补丁瞬间快照原方法体，
使该方法能在补丁类里当普通方法调用 → postfix 里「复用原逻辑 + 追加」而非模拟。
实例 `CRIALactation.HarmonyPatch_FoodUtility.AddThoughtsFromIdeo_Patch`。

**6.5 Transpiler 替换 `call` 目标、替换后的方法内部再回调原方法**＝给第三方判定加附加条件的
最干净写法（AND 而非 OR）。实例 `HarmonyPatch_CasualSex_Helper`。

**6.6 `[StaticConstructorOnStartup]` 里遍历 `DefDatabase<ThingDef>.AllDefs` 的两个高频坑：**
- **嵌套循环**：外层（所有人形种族）套内层（全部 ThingDef），内层被重复执行 N 遍；
- **同一段里两个相邻操作一个有去重一个没有**：实例里给 comp 写了 `if (!comps.Any(...))` 去重（还带注释），
  紧接着的 tab 就直接 `Add` 无去重 → 重复注册。

另外 `inspectorTabsResolved` 是游戏自己解析出来的缓存，手动往里塞等于绕过解析流程。
实例里还发现内层用 `thingClass == typeof(Pawn)` 匹配所有物种、外层用 `race.Humanlike`，两者不一致。

**6.7 装备的 `equippedStatOffsets` 可以承载「解锁能力」的语义。**
把 `MaxPersonalLieges: 1.0` 挂在项圈上 → 「戴上项圈」这个动作本身授予能力，脱下即失效。
比全局 StatDef + 条件判断干净，且天然与物品的生产/获取链绑定。

**6.8 `AcceptanceReport` 有隐式 bool 转换**，所以 `Where(x => IsActivePawn(x))` 能编译。
实例还叠加了一个 `AddRange` 到自己过滤出的同一批元素 → `HashSet` 去重 → **彻底的 no-op**，
导致 `IsActivePawn` 从未生效。**`AddRange` 自己过滤出来的同一批元素是典型 no-op**；
若注释描述了明确意图（「过滤 X 再补 Y」）而第一行就没过滤，属注释与实现不符，比 bug 更隐蔽。

**6.9 接第三方 mod 的 Job 系统，能派生就别重写。**
实例 5 个 JobDriver/JobGiver 全部派生自 RJW 已有基类
（`JobDriver_SexQuick` / `JobDriver_Rape` / `JobGiver_DoQuickie` /
`JobGiver_ComfortPrisonerRape` / `JobDriver_SexBaseRecieverQuickie`）——继承即获得完整 toil 树、
预约与路径检查。**反之，看到一堆 `JobDriver_… : Verse.JobDriver` 要留心：那通常是把上游做好的事重写了。**

---

## 7. 贴图与资源审计

**7.1 `Graphic_Multi` 按 `<texPath>_<朝向>.png` 取图**，不是 `<texPath>.png`，也**不是** `<texPath>_Atlas.png`。
反射 `Verse.Graphic_Multi` 的属性就是答案：`MatNorth` / `MatSouth` / `MatEast` / `MatWest` / `MatSingle`。
字面量 `Atlas` 在 Assembly-CSharp 里有、`_Atlas` 在 ASCII 与 UTF-16 **两堆里都**查不到
（对照 `Graphic_Single` 命中 7281205）。
→ 审计贴图时 `texPath` 要当**前缀**解析，并单独统计每种朝向齐不齐
（不必一致，实例：四向 6 个 / 两向 10 个 / 三向 4 个）。只探 `<texPath>.png` 会误报大量「缺失」。

**7.2 可达性陷阱：同名但不同内容。**
实例 `CRIALaction/UI/x.png` 缺 `Textures/` 层 → 游戏读不到，且 sha 与根 `Textures/UI/x.png` 不同。
→ 「文件存在」不等于「可达」，必须按游戏实际的相对路径层数核对。

**7.3 `.dds` 是否死重量，取决于有没有 `.dds.zstd`。**
1.5+ 优先读 `.dds.zstd`；没有 zstd 时 `.dds` 就是实际读取格式，**不是冗余**。
实例：某 mod 116 个 `.dds` 占 88% 体积但没 zstd → 全都用得上；
同作者的另一 mod 同时带 `.png`+`.dds`+`.dds.zstd` → 那个 `.dds` 才真没人读。
→ 判贴图冗余先看**三种格式的齐备情况**，别只看「游戏读不读 dds」。

**7.4 「引用能否解析」与「磁盘文件是否都被引用」是两个独立方向。**
实例：前者 42/42 全绿，后者 37/116 无引用。审计贴图两个方向都要查。

**7.5 审 mod 体积先看 `About/`。**
实例 3.02 MB 里 2.56 MB（80.7%）是 `Preview.png`，代码 + Def + 贴图不到 240 KB。
→ 先确认体积大头，再决定值不值得逐文件分析。

**7.6 跨根目录比对资源路径必须分别归一化。**
mod 内是 `Textures/x`，游戏内是 `Core/Textures/x`，共用一个前缀规则会把原版路径全判成缺失。

**7.7 引用型清单比对的两条硬规则**（本仓库高发假阴性）：
① 路径分隔符统一 `.replace("\\", "/")`；
② 比文件名集合前先 `splitext()` 取 stem（`Compare-Object 'x.png' 'x.dds'` 会给 232 行全量差异）。
更省事：直接按 **basename 或 defName** 比，别拿整条相对路径当键。

---

## 8. 生态与合规约定

**8.1 fork 检测的信号要合看**：中文二次整理的目录名 / README 标题带 "Forked" /
`changelog.txt` 里有第三方署名 / `About/Manifest.xml` 的 `downloadUri` 仍指向上游 /
`About.xml` 没有 `<url>`。某实例五种全中 → 按 fork 处理并记录上游地址。
`About.xml` 有没有 `<url>` 决定能否追溯上游——没有就只能分析随包源码。

**8.2 `About/Manifest.xml` 的 `<version>` 可能严重过期**（实例写 1.0.0 而 changelog 已到 V1.4）。

**8.3 识别许可要读 `LICENCE` 正文首几行，不要信 README 徽章。**
实例：随包 661 行 `LICENCE` 是 **AGPL-3.0**，README 徽章却写 `GPL3`——AGPL 多第 13 条网络服务条款，
对外声称与随包文本不一致属需澄清的合规问题。

**8.4 `<authors>`（复数）是正确写法**，不是 `<author>` 笔误。反射 `Verse.ModMetaData`：
属性叫 `Authors`（`IEnumerable`）+ `AuthorsString`。
→ 看到「疑似笔误」先反射属性名，别急着记进缺陷表。
同理，`<building>` 里的 `maxItemsInCell` / `fixedStorageSettings` / `defaultStorageSettings` /
`preventDeteriorationOnTop` / `ignoreStoredThingsBeauty` 全是原版 `RimWorld.BuildingProperties`
的真实字段，不是下游框架注入的私有字段——怀疑「框架 mod 往原版节点写私有字段」要先反射证伪。

**8.5 同一作者的两个 mod 放进同一次收录做横向对照，性价比最高。**
姊妹 mod 已验证过框架的抽象父 / `BuildingProperties` 字段集 / 补丁 xpath / `Graphic_Multi` 约定，
第二份直接复用，只看差量。实测收获：同作者两份下游包容量文案正确率 `20/21` vs `14/27`
——**说明不能因「上个 mod 靠谱」就跳过**，批量生成的文案是高发错区。

---

## 9. 审一个 mod 的建议顺序

1. `About/About.xml` + `About/Manifest.xml`：packageId / 作者 / 上游 / 版本声明（声明只作线索）。
2. 目录清单 + 体积分布（先看 `About/`），定位大头。
3. `LoadFolders.xml` 每个版本段的目录做存在性检查 → 确认哪些版本真的有货。
4. `Assemblies/`：程序集清单 → `GetReferencedAssemblies()` 判真实依赖 → 预载后取类型表。
5. 依赖装况：同时扫 mod 目录与游戏数据目录的 `About.xml`（只取直系子元素 `<packageId>`）。
6. 定制 XML：DefInjected 覆盖率（按 defName 求交）、`Enum.TryParse` 差集、`Scribe_Values` ref/key 对齐。
7. 贴图：`texPath` 前缀 + 朝向齐备性、zstd 齐备性、可达路径层数、引用双向审计。
8. 代码/补丁：源码注释掉的补丁要对照旧版 DLL；XML 补丁的 xpath 要回原版 Def 核对。
9. 性能静态信号：`.xml` 里出现「方法名字符串」驱动反射（`AccessTools.Method`）、
   在 `CompTickRare` 循环体里逐个查字段（`AccessTools.Field`）——都无缓存，天然每帧级开销。
10. 缺陷定稿前逐条自问：这会不会是我的工具坏了？正控过了吗？

---

## 相关

- 怎么**实现**这些功能 → [harmony-patching.md](harmony-patching.md)、
  [xml-defs-and-patches.md](xml-defs-and-patches.md)、[cross-version-structure.md](cross-version-structure.md)
- 翻译结构 → [translations-localization.md](translations-localization.md)
- 游戏系统本身由什么构成 → [mechanics/README.md](../mechanics/README.md)
- 全库检索与验收门槛 → [CONTRIBUTING.md](../CONTRIBUTING.md)
