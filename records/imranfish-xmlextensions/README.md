# XML Extensions（`2574315206`）— 分析记录

| | |
|---|---|
| 本记录目录 | `records/2574315206-XMLExtensions/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\2574315206\` |
| mod 名 | XML Extensions |
| packageId | **`imranfish.xmlextensions`** |
| 作者 | Imranfish |
| 工坊 ID | `2574315206`（`PublishedFileId.txt` 恰 10 字节 ✅） |
| 许可 | **未声明**——`About.xml` 无 `<license>`、目录内无 LICENSE |
| 支持版本 | **1.2 / 1.3 / 1.4 / 1.5 / 1.6**（收录记录里版本跨度最宽的一个，5 个版本） |
| 语言 | 英文（**无中文，但本库已装社区汉化**，见「上下游」） |
| 分析日期 | 2026-10-17 |

> 本 mod **无禁再分发声明**，但**同样无任何许可声明**。

**它在你库里的位置**：这是收录记录里**唯一一个"给 XML 补丁系统本身加语言特性"的 mod**。
它不产出内容、不改玩法——它把 DefInjected 的 XML 从**声明式**变成了**带循环、条件、变量、函数、try-catch 的命令式语言**。
本库实测 **17 个 mod 依赖它**。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **26 文件 / 998,957 字节（975.5 KB）** |
| 结构 | `About/` + `LoadFolders.xml` + `Textures/` + **`1.2/`–`1.6/`**（**用了 LoadFolders.xml**） |
| 类型 | **基础设施**（XML 补丁 DSL + mod 设置 UI 框架） |
| 主 DLL（1.6） | 165,376 B / **257 个类型**，其中 `XmlExtensions` 命名空间业务类型 **149 个** |
| Def 规模 | **只有 1 个 Def**（`XmlExtensions_MainButton_ModSettings`），但**注册了 3 个自定义 Def 类型** |
| Harmony 补丁 | **11 个类**（见下） |
| 随包 XML 文档 | `Assemblies/XmlExtensions.xml`，26,747 B / 86 条公开成员说明（1.3 起才有） |
| 语言 | English 1.6 = **26 条**（1.2–1.4 为 45 条，1.5 起砍到 22/26） |
| `modDependencies` | `brrainz.harmony` ✅ 已装（`2009463077`） |
| `loadAfter` | `ludeon.rimworld`（全小写，见「怎么验的 → 大小写」） |
| 是否自带 `0Harmony.dll` | **否** ✅ |
| 贴图 | **4 张**（1 个主按钮 + 1 个图标），`.dds`/`.png` 双格式 |

### 目录分布

| 目录 | 文件数 | 字节 |
|---|---|---|
| `1.5/` | 4 | 209,367 |
| `1.3/` | 4 | 200,254 |
| `1.6/` | 4 | 194,992 |
| `1.4/` | 4 | 193,086 |
| `1.2/` | **2** | **33,212** |
| `About/` | 3 | 126,925 |
| `Textures/` | 4 | 40,841 |
| `LoadFolders.xml` | 1 | 280 |

> `1.2/` 只有 **2 个文件**（DLL 29,184 B + 英文 Keyed），**没有 XML 文档、没有 Defs、没有主按钮**——
> 1.2 是明显的精简版。1.3 的 DLL 直接涨到 171,008 B（**5.9 倍**）。

---

## 它是什么

`About.xml` 自己的描述只有两句，但信息密度很高：

> Extends the functionality of XML patch operations, and allows for the easy creation of mod settings.
> **While this mod is loaded, XML errors will generate a stack trace.**

### 一、给 XML 补丁加一门命令式语言

1.6 的 149 个业务类型里，**绝大多数是新的 `PatchOperation` 子类**，构成一棵三层继承树：

```
Verse.PatchOperation
└─ XmlExtensions.PatchOperationExtended              ← 根，提供 Error() 与变量替换
   ├─ PatchOperationExtendedPathed                  ← 带 xpath 定位
   │  ├─ PatchOperationExtendedAttribute
   │  │  ├─ PatchOperationAttributeAdd
   │  │  ├─ PatchOperationAttributeRemove
   │  │  └─ PatchOperationAttributeSet
   │  ├─ PatchOperationSafe                          ← "安全"系列（下面单说）
   │  │  ├─ PatchOperationSafeAdd
   │  │  ├─ PatchOperationSafeAddOrReplace
   │  │  ├─ PatchOperationSafeCopy
   │  │  ├─ PatchOperationSafeRemove
   │  │  ├─ PatchOperationSafeReplace
   │  │  ├─ PatchOperationAddOrReplace
   │  │  └─ HybridPatch
   │  └─ PatchOperation{Add,Insert,Remove,Replace,Copy,Math,SortList,SetName,
   │                    EditString,RemoveDuplicateNodes,AddModExtension,
   │                    CreateDocument} / SetScope
   ├─ PatchOperationValue                            ← 能求值
   │  ├─ PatchOperationValuePathed
   │  │  ├─ GetAttribute
   │  │  └─ GetName
   │  ├─ DefDatabaseOperation                        ← 直接操作 DefDatabase
   │  │  ├─ DefDatabaseForEach
   │  │  ├─ DefDatabaseCreateVariable
   │  │  ├─ DefDatabaseConditional
   │  │  ├─ DefDatabaseOperationAdd
   │  │  ├─ DefDatabaseOperationAddDef
   │  │  ├─ DefDatabaseOperationInsert
   │  │  ├─ DefDatabaseOperationRemove
   │  │  ├─ DefDatabaseOperationReplace
   │  │  ├─ DefDatabaseOperationSortList
   │  │  └─ DefDatabaseLog
   │  └─ EvaluateBoolean / FindNodeInherited / Translate / ApplyAction /
   │      CreateVariable / CumulativeMath / ApplyValueOperation /
   │      UseSetting / UseSettings / UseSettingExternal / UseSettingsExternal
   └─ 控制流
      ├─ Conditional / ConditionalInherited
      ├─ ForEach / ForEachDescendant / ForLoop / WhileLoop
      ├─ IfStatement / Sequence / TryCatch / Case / PatchByCase
      ├─ OptionalPatch / OptionalPatchExternal
      ├─ AggregateValues / ApplyPatch / ApplyInDocument / MergeDocument / CreateDocument
      ├─ FindMod / Log / Nop
      └─ StopwatchStart / StopwatchStop / StopwatchPause / StopwatchResume   ← 性能计时
```

配套的求值/工具 API（作者在 XML 文档里逐条写了说明）：

| 方法 | 作者原文要点 |
|---|---|
| `Helpers.SubstituteVariableXmlContainer` | "Substitutes a variable with its value in a given XmlContainer" |
| `Helpers.RelationOnString` | "Computes a binary relation between two strings"，参数 `nonNumeric=true` 时"按字符串解释并用字典序比较" |
| `Helpers.OperationOnString` | "Performs a mathematical on two strings" |
| `Helpers.GetPatchFromString` | "Creates a PatchOperation from its OuterXml"——**把 XML 片段变成操作对象** |
| `PatchOperationSafe.ContainsNode` | "Checks if a node contains another node… XmlDocument doesn't matter" |
| `XmlNodeExtensions.ReplaceWith` | "Replace all attributes and children of the current node with those of the given node" |

枚举：`Mode` / `Compare` / `Operation` / `Order`（出现 4 次，分属不同上下文）/ `RangeEnd` / `SearchType` / `Logic`。

内部支撑类：`PatchCoordinator`、`PatchFilter`、**`PatchProfiler`**、`PatchManager`、
`XmlDocumentManager`、`ModTypeEmitter`、`DefDatabaseSearcher`、
`ErrorManager` / `ErrorContext` / `ErrorHandler`（后三者组成错误栈机制）。

### 二、`PatchOperationSafe`：让 XML 出错不再是"静默失败"

这是本 mod 最实用的一族。`ErrorManager.PrintErrors` 的说明是
"**Prints the stack of errors, then clears them**"，
且签名带 `ModContentPack mod`——**错误按 mod 归属**。

`PatchOperationSafe` 系列的命名本身就说明了意图：
`SafeAdd` / `SafeReplace` / `SafeCopy` / `SafeRemove` / `SafeAddOrReplace` /
`PatchOperationAddOrReplace` / `HybridPatch`。
配合 `About.xml` 那句"XML errors will generate a stack trace"，
它把 RimWorld 原版 XML 补丁最著名的痛点（**xpath 没命中时一声不吭**）补上了。

### 三、mod 设置界面（"easy creation of mod settings"）

3 个自定义 Def 类型 + 一整套设置容器：

| 类型 | 说明（作者原文） |
|---|---|
| `SettingsMenuDef` | "A Def that defines a settings menu"，字段 `tKey` / `defaultSpacing` / `settings` / `keyedActions` / `preOpenActions` / `onFrameActions` / `postCloseActions` / `modId` / `submenu` / `tagMap` / `ticksOpen` |
| `PatchDef` | "A Def that contains a patch"，字段 `parameters` / `apply` / `brackets` / `valueOperation` |
| `SlateDef` | "**A Def that does not anything, exists only as a way to store information**" |

设置侧：`Setting.SettingContainer`（抽象，"Inherit from this class in order to create a new setting"，
字段含 `key` / `padAbove|Below|Left|Right` / `showDimensions` / `addDefaultSpacing`）、
`Setting.KeyedSettingContainer`（多一个 `defaultValue`）、
`SettingsManager`（按 `modId` + `key` 二级索引，9 个方法，
`SetSetting` 的说明写明 "**The settings will be saved via Scribe as soon as the user closes the 'More Mod Settings' menu**"）、
`Container`（`tag` 供 xpath 引用、`SearchType` 枚举决定与搜索框的交互、
`PreOpen` / `PostClose` / `Init` 三个生命周期钩子）。

`ModTypeEmitter` 的说明是 "**Class for emitting a Mod Subtype with given SettingsMenuDef**"
——即**运行时用反射生成设置控件子类**，让 mod 作者能纯 XML 声明一个新设置类型。

嵌入 C# 的两条路：
- `Action.ActionContainer`（"Inherit from this class in order to embed C# code into XML"，
  实现 `ApplyAction()`，返回值写进 `output` 字段）
- `Action.KeyedAction`（绑一个 key，"called everytime a specified key is changed"，
  实现 `ApplyKeyedAction(oldValue, newValue)`）

### 四、API 生命周期管理（少见的贴心设计）

- `XmlMod.WarnUsingObselete(string, object, Type[])` —— "Throws a warning and offers alternatives.
  **Appends the modId before the warning.**"
  （方法名里 `Obselete` 是作者的拼写错误，保留在公开 API 上）
- `UnusedSettings_Window` + 一整套 Keyed 词条：
  `XmlExtensions_ViewUnusedSettings` / `XmlExtensions_InactiveMods` /
  `XmlExtensions_SelectedModUnusedKeys` / `XmlExtensions_DeleteKeys` /
  `XmlExtensions_DeleteAllUnusedKeys` / `XmlExtensions_ConfirmResetAll`

即：**能查出"哪些 mod 定义了设置却没被用"并一键清理**。
一个设置系统跑了多个大版本后必然积累垃圾键，作者为此做了 UI。

### 五、11 个 Harmony 补丁：温和式接管

| 补丁类 | 目标 | 作用 |
|---|---|---|
| `ApplyPatches_Patch` | `LoadedModManager.ApplyPatches` | 接管**补丁总入口** |
| `PatchOperation_Patch` | `PatchOperation.Apply` | 接管所有补丁操作的总入口 |
| `PatchOperationConditional_Patch` | `PatchOperationConditional.ApplyWorker` | 让原版条件操作兼容扩展体系 |
| `PatchOperationSequence_Patch` | `PatchOperationSequence.ApplyWorker` | 同上（序列） |
| `PatchOperationAttribute{Add,Remove,Set}_Patch` | 各自 `ApplyWorker` | 同上（属性操作） |
| `PatchOperationFindMod_Patch` | `PatchOperationFindMod.ApplyWorker` | 同上 |
| `PatchOperationSetName_Patch` | `PatchOperationSetName.ApplyWorker` | 同上 |
| `TrySortMods_Patch` | `ModsConfig.TrySortMods` | **介入 mod 加载顺序排序** |
| `Dialog_Options_Patch` | `Dialog_Options.DoCategoryRow` | 在原版"选项"菜单里**加一行** |

> 关键设计取向：**它不替换原版的操作类，而是给原版操作打补丁让它们与扩展体系共存**。
> 加上 `Dialog_Options_Patch` 与可选的 `MainButtonDef`，
> 用户既能在原版"选项"菜单里找到，也能用独立主按钮打开——**入口可选择，不强加**。

界面开关（`XmlExtensions_ShowSettingsButton` / `XmlExtensions_AddMainButton` 两个词条）
说明主按钮与选项菜单行都是**可开关的**，且带确认对话框。

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse` + `ReadAllBytes().Length` |
| 依赖图 | `[xml]` 解析全库 `About/About.xml`，取 `ModMetaData` **直接子元素** `<packageId>`，检索正文含 `imranfish.xmlextensions` 的节点 |
| API 表面 | **直接读随包 `Assemblies/XmlExtensions.xml`**（.NET XML 文档），按 `<member name="…">` 提取公开成员，**带作者的 `<summary>`** |
| 类型全貌 / 继承树 | `GetTypes()` + 读 `BaseType.FullName`，按命名空间过滤 |
| 跨版本演进 | 逐版本读 `XmlExtensions.xml` 的成员表做**集合差**（新增 / 移除分开列） |
| Def / 字段 | `BaseType.FullName -match 'Verse\.Def$'` 找自定义 Def；字段以**文档文件**为准（见纠错 1） |
| 翻译 | `[xml]` 读 `LanguageData` 的元素名即 key |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| packageId 依赖扫描 | `brrainz.harmony` 必须命中 | ✅ |
| 依赖扫描的匹配能力 | 必须扫得出**17 个**引用方而非 0/1 | ✅ |
| XML 文档解析 | 必须含 `<member name=` 且命名空间为 `XmlExtensions` | ✅ 86 条 |
| `GetTypes()` | 必须能列出 `PatchDef` / `SettingsMenuDef` / `SlateDef` | ✅（补齐预载后） |
| 翻译词条提取 | 英文应含 `XmlExtensions_Label` | ✅ 26 条 |
| 跨版本集合差 | 必须报出非空的新增/移除集合 | ✅ 新增 35 / 移除 19 |

### ③ 自查纠错（本轮我的工具错了 3 次）

**1. 以为 `Assemblies/*.xml` 是 RimWorld 的 ModExtension API 定义。**
我看到 `1.6/Assemblies/XmlExtensions.xml` 有 26 KB，就推断这是"它自己声明的 API"。
按这个假设去统计 `Class=` 属性，结果**一个都没匹配到**——正控失败。
改看文件头才发现根元素是 `<doc>` / `<assembly><name>XmlExtensions</name>`：
这是 **.NET XML 文档注释文件**（IntelliSense 用），RimWorld 根本不读。
**修正后的做法反而更好**：它逐条列出了全部公开成员**和作者的说明文字**，
比反射出来的裸签名信息量大得多。
→ 判断 `Assemblies/` 里的 XML 是数据还是文档，看**根元素**（`<doc>` = 文档）。

**2. 用反射取自定义 Def 的字段，结果全是 0 个。**
我写了 `Where-Object { $_.DeclaringType -eq $_ }` 这种自指过滤（写错了），
于是 `PatchDef` / `SettingsMenuDef` / `SlateDef` 三个类都显示"0 个自有字段"。
**是靠和文档文件对照发现的**：文档里白纸黑字写着 `PatchDef.parameters` 等 4 个字段。
→ Def 类的字段清单以 **XML 文档文件**为准，比反射更可靠（还带注释）。

**3. PowerShell 字符串插值里 `"$v: 无"` 解析失败。**
`$v:` 被当成盘符限定变量，整段脚本 ParseError。改成 `"${v}: 无"` 即可。
（和收录区标准里记的"先读字节数再看 KB 列表"同源——**工具报的"错"经常是错在工具自己**。）

**4. `loadAfter` 写成全小写 `ludeon.rimworld`——查证后确认无害。**
先例：全库 About.xml 里出现次数最多的写法就是各种大小写混写（`Ludeon.RimWorld` /
`ludeon.rimworld` / `Ludeon.Rimworld` 都见过）。
上一轮收录 `3033901359` 时已确认 `Verse.ModMetaData` 有 `packageIdLowerCase` 与
`SamePackageId`——**packageId 匹配大小写不敏感**，本 mod 的写法不构成 bug。

### ④ 未核实

- **随包无源码、无 LICENSE**，因此 `PatchOperationSafe` 的"safe"具体判定逻辑、
  `PatchProfiler` 的输出形态等只能从命名与类型层次推断，**未读实现**。
- **`1.2` 版本只有 29 KB 的 DLL**，与 1.3 差 5.9 倍，功能差异**未逐一比对**
  （1.2 无 XML 文档文件，拿不到它的公开 API 清单）。
- **本库装的 `asavikle.XML.Extensions.cn` 汉化未逐词条核对**，只确认了它存在且覆盖简繁双语。

---

## 上下游与冲突面

### 谁依赖它：本库实测 17 个

| packageId | 工坊目录 | 声明方式 |
|---|---|---|
| `aki.ADogSaidAnimalProsthetics2` | 3248192274 | `loadAfter` |
| `Aoba.Fortress.Industrial` | 2561619583 | `loadAfter`（与上一轮收录的 AOBA 生态重叠） |
| **`asavikle.XML.Extensions.cn`** | 2719998589 | `loadAfter`（**汉化包**） |
| `buyue.SimpleTextureTweaks` | 3245917504 | `modDependencies` + `loadAfter` |
| `carnap2.TMaterials.Glass` | 2845463213 | `loadAfter` |
| `carnap2.TMaterials.Unique` | 2845480835 | `loadAfter` |
| `Chougou.KiiroMedievalExpansion` | 3552593338 | `loadAfter` |
| `erdelf.HumanoidAlienRaces` | 839005762 | `loadAfter` |
| `Meow.Wallsaresolid` | 3550768004 | `loadAfter` |
| `Neko.Thunderstorm` | 3278460897 | `modDependencies` + `loadAfter` |
| `PikaJo.KiiroCatmintFoodExpend` | 3669848797 | `loadAfter` |
| `quartz.floorstoragetanks` | 3625783623 | `modDependencies` + `loadAfter` |
| `SamBucher.ADogSaidAnimalProsthetics2` | 3238353862 | `loadAfter` |
| `vat.epoeforked` | 1949064302 | `loadAfter` |
| `Victor.WallsAreSolid` | 2896548513 | `modDependencies` + `loadAfter` |

依赖方里 **6 个是"墙面/材质/贴图/天气/储罐"类**——
说明它的典型用法正是"用 XML 循环批量改别人的 Def"，这类活没有循环很难写。

### 中文：本体没有，但库里已经装了汉化

**本体 5 个版本目录都只有 `Languages/English/`**，无任何中文。
但本库装着 **`asavikle.XML.Extensions.cn`（`2719998589`，作者 asavikle）**：

```
About/About.xml + Preview.png + PublishedFileId.txt
Languages/ChineseSimplified/Keyed/XMLExtensions_Keyed_EN.xml      (4010 B)
Languages/ChineseSimplified/DefInjected/MainButtonDef/…xml         ( 305 B)
Languages/ChineseTraditional/Keyed/XMLExtensions_Keyed_EN (1).xml  (4012 B)
Languages/ChineseTraditional/DefInjected/MainButtonDef/…xml         ( 303 B)
```

翻译文件名沿用英文源文件名（`XMLExtensions_Keyed_EN.xml`）——
这是 RimWorld 的**要求**，游戏靠文件名匹配源文件，不是命名错误。
汉化文件 4,010 B 比本体 1.6 的英文 2,373 B 还大，说明它覆盖了**更全的词条集**
（可能连带补齐了 1.3/1.4 时代那 19 条已被砍掉的键）。

### 与本库其他收录记录的关系

- `Aoba.Fortress.Industrial`（上一轮 `3033901359` 记录的 AOBA 生态成员）也依赖它。
- 本库已知的 `erdelf.HumanoidAlienRaces`、`Chougou.KiiroMedievalExpansion`、
  `PikaJo.KiiroCatmintFoodExpend` 说明它已被**较老的种族/中世纪向 mod** 采用——
  对"基础设施型 mod 生命周期"的判断有参考价值。

### 结构风险：本轮未发现

- 不自带 `0Harmony.dll` ✅
- 不带 `0MultiplayerAPI.dll` ✅（与上一轮 `3498575851` / `3033901359` 不同）
- 只有一个 Mod 与它绑定了别的 Multiplayer 桩？**不适用**——它根本不引用 Multiplayer。

---

## 可复用结论

1. **XML 补丁的"静默失败"是可以被治好的，而且治法很朴素。**
   RimWorld 原版 xpath 没命中不报错，mod 作者往往到游戏里才发现没生效。
   `PatchOperationSafe` 系列的命名 + `ErrorManager.PrintErrors(源文件, ModContentPack)`
   把**错误按 mod 归属**打出来，就是最直接的解法。
   凡是做数据管线的 mod，"出错要能定位到谁"比"功能更强"更重要。

2. **给别人的系统加特性，"打补丁共存"优于"替换"。**
   本 mod 不重写 `PatchOperationConditional` / `PatchOperationSequence` 等原版操作，
   而是对它们的 `ApplyWorker` 打补丁（7 处），让它们与扩展体系共存。
   再加 `Dialog_Options_Patch` 把入口塞进原版"选项"菜单——
   **入口可选择、不强加**，是对既有生态侵入最小的做法。

3. **基础设施 mod 必须处理"API 自己的生命周期"。**
   `XmlMod.WarnUsingObselete(msg, obj, Type[])` 让作者能标记弃用并**打印出还在用它的 modId**，
   再配上"未使用设置"的查看/清理窗口。
   一个跨多个游戏大版本的框架 API，必然要淘汰旧成员；
   **能报出"谁还在用"比"直接删掉"有价值得多**。

4. **把 XML 文档注释文件随包发布，是被严重低估的做法。**
   本 mod 每版都带一份 `Assemblies/XmlExtensions.dll.xml`（26 KB / 86 条成员说明），
   每条都带作者的 `<summary>` 和 `<param>`。
   对使用者来说这就是 API 手册；对分析者来说，它比任何反射结果都准确——
   **反射给签名，文档给意图**。

5. **多版本支持的最省力形态：LoadFolders + 每版一个目录，内容按需增减。**
   本 mod 的 `LoadFolders.xml` 五段各写 `/` + 对应版本目录，是完全收敛的写法；
   `1.2` 只有 2 个文件、1.3 起才逐步补上 XML 文档与主按钮 Def，
   说明**老版本目录不必强行对齐新版本的功能集**。

6. **判断一个 mod 是不是"基础设施"，看它的 `loadAfter` 被谁引用，而不是看它有没有内容。**
   本 mod 只有 **1 个 Def**、4 张贴图、26 个文件——单看规模完全不像基础设施；
   但它有 17 个依赖方，其中 6 个是"改别人 Def"类的 mod。

7. **`Order` 这类枚举出现多次，说明同名不同域——按名字 grep 会合并错。**
   1.6 的 `XmlExtensions` 命名空间里有 **4 个都叫 `Order` 的枚举**
   （分属不同上下文），另有 `Compare` 2 个。统计"枚举数量"时不能按名字去重。

8. **翻译文件与源文件同名是 RimWorld 的硬要求，不是命名疏忽。**
   本体英文叫 `XMLExtensions_Keyed_EN.xml`，汉化包也叫同一个名字（繁中还多了 `(1)` 后缀，
   同样是合法做法）——因为游戏按文件名找对应关系。
   看到"翻译文件名字里带 _EN"或带 `(1)`，**先确认是机制还是错误**。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **补许可声明** | `About.xml` 无 `<license>`、无 LICENSE 文件。基础设施类 mod 被 17 个 mod 依赖，授权不明确影响面更大 |
| 中 | 本体不带中文 | 本库**已装** `asavikle.XML.Extensions.cn` 覆盖简繁，实际影响有限；若上游愿意，可直接合入本体 |
| 中 | 核对汉化覆盖 | 汉化文件 4,010 B > 本体 1.6 英文 2,373 B，疑似覆盖了 1.3/1.4 时代的旧键；建议核对是否有多余词条 |
| 低 | `1.2` 版本定位不明 | 29 KB vs 1.3 的 171 KB，功能差异大但无文档说明，建议在 `About.xml` 或 readme 里注明 |
| 低 | `Obselete` 拼写 | 公开 API `WarnUsingObselete` 拼写错误；改名会破坏兼容，建议保留并在文档里说明 |
| 低 | 英文词条从 45 砍到 26 | 1.5 起的精简未见说明；若旧 mod 仍引用被砍的键，会有缺词条风险 |

---

*2026-10-17 收录。④ 档：已查依赖图（17 个依赖方，含 1 个汉化包）、
逐版本 API 集合差（新增 35 / 移除 19）、11 个 Harmony 补丁目标、随包 XML 文档 86 条成员说明。
本轮工具自查纠错 3 次（误判 Assemblies 里的 XML 为 ModExtension API、
Def 字段自指过滤写错、PS 字符串插值 `$v:` 解析失败），均已留档。*
