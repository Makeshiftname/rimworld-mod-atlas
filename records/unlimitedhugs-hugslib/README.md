# HugsLib（`818773962`）— 分析记录

| | |
|---|---|
| 本记录目录 | `records/818773962-HugsLib/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\818773962\` |
| mod 名 | HugsLib |
| packageId | **`UnlimitedHugs.HugsLib`** |
| 作者 | UnlimitedHugs |
| 工坊 ID | `818773962`（`PublishedFileId.txt` **9 字节**——工坊 ID 恰好 9 位，与其它 10 字节的 mod 不同，不是缺内容） |
| 版本 | **12.0.0**（`About/Version.xml` 的 `overrideVersion`，不来自 `About.xml`） |
| 许可 | **未声明**——`About.xml` 无 `<license>`、目录内无 LICENSE |
| 支持版本 | **1.0 / 1.1 / 1.2 / 1.3 / 1.4 / 1.5 / 1.6**（收录记录里**跨度最大**，7 个版本） |
| 语言 | **13 个语种**（收录记录里最多） |
| 分析日期 | 2026-10-17 |

> 本 mod **无禁再分发声明**，但**同样无任何许可声明**。

**它在你库里的位置**：收录记录里**依赖面最广的基础设施**——本库实测 **27 个 mod 依赖它**，
其中包括整个 RJW（Rim Job Worlds）系列。它自己只产出 **6 个 Def**（5 个快捷键 + 1 个分类），
价值全在被别人调用。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **68 文件 / 2,470,894 字节（2.36 MB）** |
| 结构 | `About/` + **`Assemblies/`（含 1.0 版 + 自带 Harmony）** + `Defs/` + `Languages/` + `Textures/` + `LoadFolders.xml` + **`v1.1/`–`v1.6/`（带 `v` 前缀）** |
| 类型 | **基础设施**（给别的 mod 用的共享功能库 + 设置框架） |
| 主 DLL（v1.6） | 206,336 B，`AssemblyVersion` 恒为 **1.0.0.0**（真实版本走 `Version.xml`） |
| 随包 XML 文档 | 每版一份 `HugsLib.xml`（根元素 `<doc>`），v1.6 有 **233 条公开成员**、**80 个公开类型** |
| Def 规模 | **只有 6 个**（1 个 `KeyBindingCategoryDef` + 5 个 `KeyBindingDef`） |
| Harmony 补丁 | **15 个类**（`HugsLib.Patches.*`） |
| 语言 | 13 语种；英文 75 条 Keyed 为基准 |
| `modDependencies` | `brrainz.harmony` ✅ 已装（`2009463077`） |
| `loadAfter` | `Ludeon.RimWorld` + 4 个官方 DLC + `brrainz.harmony` |
| **自带 `0Harmony.dll`** | **是** ⚠️ 见「上下游与冲突面」 |
| 构建/更新工具链 | **VersionControl（`About/Version.xml`）+ ModSync（`About/ModSync.xml`）** |

---

## 它是什么

一句话：**给 mod 作者的一站式基础设施**——设置界面、日志窗口、更新公告、
快捷键、版本检查、游戏重启、外壳调用，外加一套让别的 mod 挂上来的基类。
`About.xml` 的自述只有一句："HugsLib is a library that provides shared functionality to other mods."

### 80 个公开类型按子系统

| 子系统 | 类型 | 作用 |
|---|---|---|
| **Core**（14） | `HugsLibMod`、`HugsTickProxy`、`StaticInitializer`、`EarlyInitAttribute`、`PersistentDataManager`、`LibraryVersionChecker`、`ManifestFile`、`VersionFile`、`VersionShort`、`HugsLibKeyBindings`、`KeyBindingHandler`、`HugsLibTextures`、`QuickRestarter`、`UnityProxyComponent`、`Dialog_LibraryUpdateRequired` | 生命周期、版本文件解析、持久数据、快捷键 |
| **Utils**（14 类型） | **`ModBase`（28 个公开成员）**、**`HugsLibUtility`（22 个）**、`ModLogger`、`HarmonyUtility`、`AssemblyVersionInfo`、`Dialog_Confirm`、`Dialog_Message`、`DistributedTickScheduler`、`DoLaterScheduler`、`TickDelayScheduler`、`Tracer`、`PlatformUtility`、`InjectedDefHasher`、`UtilityWorldObject(+Manager)` | **给下游用的基类与工具类**；三个调度器（分布式 tick / 稍后执行 / 延迟 tick） |
| **Settings**（19+） | `Dialog_ModSettings`、`ModSettingsManager`、`ModSettingsPack`、`ModSettingsWidgets`、`ModSettingsWindowState`、`SettingHandle(+Convertible/ConvertibleUtility)`、`CachedLabel`、`ContextMenuEntry`、`Validators` | **设置框架**：设置句柄、校验器、上下文菜单项 |
| **News**（6+1） | `UpdateFeatureDef`、`Dialog_UpdateFeatures`、`Dialog_UpdateFeaturesFiltered`、`UpdateFeatureManager`、`UpdateFeatureDefLoader`、`UpdateFeatureDefFilteringProvider`、`UpdateFeaturesDevMenu` | **更新公告系统**，`UpdateFeatureDef` 是一个自定义 Def |
| **Quickstart**（4） | `QuickstartController`、`QuickstartSettings`、`Dialog_QuickstartSettings`、`QuickstartStatusBox` | 主菜单上的"快速开始"引导 |
| **Logs**（3） | `Dialog_PublishLogs`、`LogPublisher`、`LogWindowExtensions`（+ `WidgetAlignMode` / `WidgetDrawer` 枚举） | 日志窗口 |
| **Spotter**（2，1.6 新增） | `ModSpottingManager` + `TrackingEntry` | **mod 侦测**——检测其它 mod 是否加载 |
| **Shell**（3） | `Shell`、`ShellOpenDirectory`、`ShellOpenLog` | 调系统默认程序打开目录/日志 |
| **Patches**（15） | 见下表 | |

### 15 个 Harmony 补丁

`HugsLib.Patches.*`：
`Game_FinalizeInit_Patch`、`Game_FillComponents_Patch`、`Game_DeinitAndRemoveMap_Patch`、
`Map_FinalizeInit_Patch`、`Map_ConstructComponents_Patch`、
`MapComponentUtility_MapGenerated_Patch`、`PlayDataLoader_Patch`、`LanguageDatabase_Patch`、
`ModsConfig_RestartFromChangedMods_Patch`、
`DebugWindowsOpener_Patch`、`EditWindow_Log_Patch`、`Root_Patch`、`UIRoot_OnGUI_Patch`、
`Root_OnGUI_Patch`、`MainMenuDrawer_Quickstart_Patch`。

> 补丁面集中在**游戏启动/地图生成/主界面绘制**三个阶段——
> 这与它的定位一致（基础设施要在最早的时刻把自己挂上去），
> 而不是去改玩法。

### 它的 6 个 Def：5 个快捷键

`Defs/KeyBindingCategoryDefs/KeyBindingCategories.xml` 定义 1 个分类 `HugsLibShortcuts`（label "HugsLib"），
`Defs/KeyBindingDefs/KeyBindings.xml` 定义 5 个键：

| defName | label | 默认键 |
|---|---|---|
| `PublishLogs` | Publish log file (hold Ctrl) | **F12** |
| `OpenLogFile` | Open log file | — |
| `RestartRimworld` | Restart Rimworld | — |
| `HLOpenModSettings` | Open Mod Setting window | — |
| `HLOpenUpdateNews` | Open Mod Update News window | — |

对应英文 Keyed 前缀 `HugsLib_settings_*`（75 条，含 `btn` / `windowTitle` / `resetValue` /
`resetAll` / `resetAll_prompt` / `noSettings` / `resetMod` / `resetMod_prompt` …）——
即那套设置窗口的界面文案。

### 版本管理：两套工具链

`About/Version.xml`（**VersionControl / BrightConstruct** 格式）：

```xml
<VersionData>
  <overrideVersion>12.0.0</overrideVersion>
  <gitHubRepository>UnlimitedHugs/RimworldHugsLib</gitHubRepository>
</VersionData>
```

`About/ModSync.xml`（**ModSync** 格式）指向 GitHub `UnlimitedHugs/RimworldHugsLib` 的
`master` 分支、`DownloadFrom=ModSyncReleases`、`SaveBreaking=False`。

两套并存于同一个 `About/`——**前者管版本号与仓库，后者管自动更新**。
这也解释了为什么 `AssemblyVersion` 七个版本目录全是 `1.0.0.0`：
真实版本号由外部元数据携带，不进程序集身份。

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse` + `ReadAllBytes().Length` |
| 依赖图 | `[xml]` 解析全库 `About/About.xml`，取 `ModMetaData` **直接子元素** `<packageId>`，检索正文含 `UnlimitedHugs.HugsLib` 的节点 |
| API 表面 | **直接读随包 `HugsLib.xml`**（.NET XML 文档，`<doc>` 根），按 `<member name="T:…">` 提取类型表 |
| 跨版本引用 | 逐版本 `ReflectionOnlyLoadFrom` 读 `GetReferencedAssemblies()` |
| 版本号 | 读 `About/Version.xml` 与 `About/ModSync.xml`，**不信 `AssemblyVersion`** |
| 二进制同一性 | 逐 DLL `Get-FileHash` SHA256 横向比对 |
| 翻译 | `[xml]` 读 `LanguageData`，元素名即 key；按语种分别计数 |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| packageId 依赖扫描 | `brrainz.harmony` 必须命中 | ✅ |
| 依赖扫描的匹配能力 | 必须扫出 **27 个** mod 而非 0/1 | ✅ |
| XML 文档解析 | 根元素必须是 `<doc>` 且成员数 > 0 | ✅ 233 条 |
| `#Strings` 提取（辅助） | `packageId` 必须能在 Assembly-CSharp 元数据里命中 | ✅ |
| 翻译词条 | 英文应含 `HugsLib_settings_*` 前缀 | ✅ 75 条 |
| `PublishedFileId.txt` | 应为纯 ID、无 BOM 无换行 | ✅ 9 字节 `818773962` |

### ③ 自查纠错（本轮我的工具错了 3 次）

**1. 怀疑韩语 DefInjected 的文件夹名用了复数（`KeyBindingCategoryDefs`）会导致不生效——不成立。**
我看到韩语目录是 `KeyBindingCategoryDefs/`（复数）而其它语种是 `KeyBindingCategoryDef/`（单数），
差一步就记成"韩语翻译失效"。
**读内容才发现 Def 类型取自元素名而非文件夹名**：韩语与日语文件里的元素名都是
`<HugsLibShortcuts.label>` / `<HugsLibShortcuts.description>`，完全一致。
→ DefInjected 的**文件夹名是装饰性的**，判断能否生效要看元素名。

**2. 同一 AppDomain 里连着 `ReflectionOnlyLoadFrom` 多个同名程序集直接抛异常。**
七个版本的 DLL 全叫 `HugsLib`，第二个就报
"程序集已从其他位置加载。无法从同一个 Appdomain 中的另一新位置加载"。
最初以为能靠 `-Depth` 绕过——不能，身份冲突是硬限制。
改法：**每个版本开一个独立 `powershell -NoProfile -Command` 进程**。
（中途又踩了一次：`& powershell -Command $script $path` 里 `param($p)` 不生效，
路径被当成第二条命令，$p 为空 → "String cannot have zero length"。
**正确写法是把路径直接插进命令字符串**。）

**3. 差点断言"根目录 `Assemblies/` 的 Harmony 1.2 会被一起加载、污染全库"——证据不足。**
见下面的「未核实」。

### ④ 未核实（本记录最重要的一条）

**根目录 `Assemblies/` 在 1.6 下是否与 `v1.6/Assemblies/` 同时被加载，无法从静态分析确定。**

已确认的事实：

| 项 | 值 |
|---|---|
| 根 `Assemblies/0Harmony.dll` | 113,152 B，**v1.2.0.1**（Harmony **1.x**） |
| 本库官方 Harmony（`2009463077`） | 2,456,064 B，**v2.4.1.0**，Manifest 声明 **2.4.2.0** |
| 两者是否同一文件 | **否** |
| `LoadFolders.xml` | `v1.1`–`v1.6` 各写 `/` + 该版本目录；**没有 `<v1.0>`** |
| `supportedVersions` | 却列了 `1.0` |

倾向性推断（**未证实**）：`Verse.ModContentPack` 有 `foldersToLoadDescendingOrder` 字段
和 `CommonFolderName` 常量，看起来是把根目录 `/` 当作"各版本共享的内容目录"、
与"版本专有的 Assemblies 目录"分开处理。若如此，
**根目录那份 Harmony 1.2 在 1.6 下不会加载**，只是一份 1.0 时代的遗留。

我尝试过证伪/证实但未成功：`Assembl` 字面量在 `ModMetaData` / `ModContentPack` /
`LoadedModManager` 的 IL 里都扫不到（`AssembliesFolder` 只是字段名）。
**没有实机运行，因此不下结论。**

> 这条为什么重要：它决定 **HugsLib 到底算不算那 85 个"自带重复 `0Harmony.dll`"案例之一**。
> 上一轮收录 `3498575851` 时已把这类问题定性为全库级隐患。

---

## 上下游与冲突面

### 谁依赖它：本库实测 27 个

| packageId | 声明方式 |
|---|---|
| `UnlimitedHugs.AllowTool`、`UnlimitedHugs.DefensivePositions` | 同作者配套 mod |
| **`RWZH.ChinesePack.HugsLib`** | **社区汉化包**（已在库） |
| `RJW.Sexpanded.Core` / `.Corruption` / `.ReProduction`、`rjw.FB` / `rjw.FC` / `rjw.FH` / `rjw.std`、`LustLicentiaSerums.RJWLabs` | **RJW 系列全家桶** |
| `com.yayo.yayoAni.continued`、`c0ffee.rjw.IdeologyAddons` | 成人向扩展 |
| `V1024.EBFramework`、`void.charactereditor`、`VouLT.BetterPawnControl`、`vr.missilegirl`、`Doug.NoJobAuthors`、`rim.job.world` | 框架 / 角色编辑 / 职业向 |
| `Superniquito.ModOptionsSort`、`m00nl1ght.MapPreview`、`nugerumon.RomanceTweaksMoreOptions` | 工具类 |
| `abscon.privacy.please`、`hehehew.Sexystatue2`、`Bichang.Kyulen`、`cof.moretorture` | 杂项 |

声明方式分布：`loadAfter` 22、`modDependencies` 9、**`modDependenciesByVersion` 4**、
**`loadAfterByVersion` 1**。
后两种是 **VersionControl 工具链**的变体元素——**依赖方里也有用同一套工具链的 mod**，
说明 HugsLib 的更新管理方式在生态内有传播。

### ⚠️ 自带 Harmony：跨大版本共存

HugsLib 根 `Assemblies/` 里的 `0Harmony.dll` 是 **Harmony 1.2.0.1**，
而本库官方 Harmony 是 **2.4.x**。这是**跨大版本**（1.x vs 2.x）的共存，
比同版本号不同构建的那 81 份 `0MultiplayerAPI.dll` 性质更重。
是否实际生效见「未核实」。

> 另注：`About.xml` 既声明 `<modDependencies>brrainz.harmony</modDependencies>`（硬依赖）
> **又自带一个 `0Harmony.dll`**。两者并存，说明作者考虑过"有人不装 Harmony mod"的场景。

### 语言覆盖：13 语种，简中只到 59%

| 语种 | Keyed 词条 | DefInjected 文件 |
|---|---|---|
| English | **75**（基准） | 0（英文是源语言，正确） |
| Japanese | **75** | 2 |
| German / PortugueseBrazilian / Russian / Turkish | 73 | 2 |
| **ChineseTraditional** | 58 | 2 |
| **ChineseSimplified** | **44** | 2 |
| French / Korean / Spanish / SpanishLatin | 44 | 2 |
| **Polish** | **34** | **0** |

- **简中只有英文的 59%**，繁中 77%。
- **波兰语只有 Keyed、没有 DefInjected** → 5 个快捷键的 label/description 在波兰语下不翻译。
- 英文没有 DefInjected 是**正确的**（label 直接来自 `Defs/*.xml`）。
- 本库已装 **`RWZH.ChinesePack.HugsLib`** 汉化包，可补简中缺口。

---

## 可复用结论

1. **把根目录当"各版本共享内容"，版本目录只放"版本专有内容"，是最省力的跨版本布局。**
   本 mod 根目录放 `Defs/` `Languages/` `Textures/`（全版本共享），
   `v1.1`–`v1.6` 各只放 `Assemblies/`（版本专有）。
   `LoadFolders.xml` 每段只写两条：`/` + 版本目录，**完全收敛**。
   对照 `AGENTS.md` 那条"避免用 LoadFolders.xml"——这个用法说明
   **LoadFolders 的问题从来不是"用了"，而是"用它做版本分发"**。

2. **`supportedVersions` 与 `LoadFolders` 不一致时，缺的那一版由根目录兜底。**
   本 mod 声明支持 1.0，但 `LoadFolders` 只写了 `v1.1`–`v1.6`——
   根 `Assemblies/` 里那份引用 `Assembly-CSharp 1.0.7036` 与单体 `UnityEngine.dll` 的
   **就是 1.0 专用构建**。逐版本读 `GetReferencedAssemblies()` 就能验证这一点。

3. **"真实版本号"不该放进程序集身份。**
   七个版本目录的 `AssemblyVersion` 全是 `1.0.0.0`，
   真实版本 12.0.0 放在 `About/Version.xml`（VersionControl）与 `About/ModSync.xml`（ModSync）。
   好处：升级不改变程序集绑定关系；代价：只看 DLL 无法判断版本。

4. **DefInjected 的文件夹名是装饰性的，Def 类型取自元素名。**
   韩语用 `KeyBindingCategoryDefs/`（复数）而其它语种用 `KeyBindingCategoryDef/`，
   两边元素名都是 `<HugsLibShortcuts.label>`，**都生效**。
   核对翻译是否可用要看**元素名**，不要看文件夹名。

5. **同一 AppDomain 里反射多个同名程序集必然失败，改用独立进程。**
   分析多版本 mod 时，七个版本的 DLL 全叫 `HugsLib`，
 第二个 `ReflectionOnlyLoadFrom` 就抛"已从其他位置加载"。
 唯一可靠解法是**每版开一个进程**。
 顺带：`& powershell -Command $script $path` 里的 `param()` 不生效，
 **要把路径直接插进命令字符串**。

6. **"基础设施 mod 的补丁面"能反映它的定位。**
   HugsLib 的 15 个补丁全在**游戏启动 / 地图生成 / 主界面绘制**，
 一个都不碰玩法。反过来，看补丁打在哪一层，就知道这个库想当谁的"地基"。

7. **给 mod 用的一站式服务，典型清单是：设置 UI + 日志 + 更新公告 + 快捷键 + 重启 + 外壳调用。**
   HugsLib 的 80 个公开类型几乎全部围绕这六件事，外加 `ModBase`（28 个公开成员）这个
   "让下游挂上来"的基类。评估一个新框架值不值得用，看它有没有把这六件事做全。

8. **翻译覆盖率要分 Keyed 和 DefInjected 两项分别数。**
   本 mod 简中 Keyed 44/75（59%），但 DefInjected 是齐的（2 文件）；
   波兰语反过来——Keyed 34 条却**完全没有 DefInjected**，
 导致 5 个快捷键不翻译。只看一个总数会同时掩盖这两种缺口。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **核实根目录 `0Harmony.dll` 是否加载** | 决定它算不算 85 个重复 Harmony 案例之一。静态分析已到极限，**需实机验证**（检查游戏加载后的程序集列表）。用户未授权，暂不动 |
| 高 | **补许可声明** | 无 `<license>`、无 LICENSE。27 个 mod 依赖它，授权不明确影响面最大 |
| 中 | 简中缺口 | 简中 44/75。本库已装 `RWZH.ChinesePack.HugsLib`，先核对汉化是否已补齐再决定是否需要动手 |
| 中 | 波兰语缺 DefInjected | 5 个快捷键 label 不翻译，属遗漏 |
| 低 | `LoadFolders` 与 `supportedVersions` 不一致 | 声明支持 1.0 但无 `<v1.0>` 段；虽能靠根目录兜底，但建议加注释或补段说明 |
| 低 | 七版本目录二进制冗余 | v1.3/v1.4 文档完全相同、v1.5/v1.6 文档完全相同而 DLL 不同；根目录另存一份 1.0 构建。属正常跨版本成本，无需清理 |

---

*2026-10-17 收录。④ 档：已查依赖图（27 个依赖方 + 1 个汉化包）、
七版本程序集引用逐一核对、自带 Harmony 与官方 Harmony 的版本冲突、13 语种覆盖分项统计。
本轮工具自查纠错 3 次（误判 DefInjected 文件夹名、同名程序集同进程加载失败、
`& powershell -Command` 的 param 不生效），均已留档；
「根目录 Assemblies 是否加载」如实标记为未核实，未下结论。*
