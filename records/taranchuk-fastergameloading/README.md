# Faster Game Loading - Continued（`3652938473`）— 分析记录

| | |
|---|---|
| 本记录目录 | `修改/3652938473-FasterGameLoading/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\3652938473\` |
| mod 名 | Faster Game Loading - Continued |
| packageId | **`Taranchuk.FasterGameLoading`**（沿用原版 ID，见 §六） |
| 作者 | 綠菇（mushroomTW）—— **Taranchuk 原版的维护分支** |
| modVersion | 2026.06.20.1 |
| 支持版本 | **仅 1.6** |
| 源码 | https://github.com/mushroomTW/FasterGameLoading---Continued（原版 https://github.com/Taranchuk/FasterGameLoading） |

> 本 mod **无禁再分发声明**。
>
> **它对你的库特别相关**：本库有 **1021 个 mod**，
> 启动时间几乎肯定是最大的实际痛点，而这个 mod 正是专治此症。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | 10 文件 / 0.46 MB（核心是 1 个 96.5 KB 的 DLL） |
| 结构 | 扁平，无版本目录 |
| 语言 | 简中 / 繁中 / **英文** / 俄语（作者是繁体中文使用者，默认带英文原文） |
| `loadBefore` | `Ludeon.RimWorld` |
| `loadAfter` | `brrainz.harmony` + `garethp.modlistconfigurator` |
| 引用程序集 | `0Harmony 2.4.2.0`、`Assembly-CSharp 1.6.9655.19392`、`System.Xml`、`UnityEngine.ImageConversionModule`、`UnityEngine.CoreModule` |
| `PublishedFileId.txt` | `3652938473`（10 字节 ✅） |

```
About/About.xml + ModIcon.png + Preview.png + PublishedFileId.txt
Assemblies/FasterGameLoading.dll            96.5 KB
LanguageData/{ChineseSimplified, ChineseTraditional, English, Russian}/Keyed/…
LICENSE
```

---

## 它是什么

反射 `FasterGameLoading.dll` 得 58 个类型，其中 22 个带 `[HarmonyPatch]`。
**几乎没有一个碰游戏玩法**——全部是加载 / 资源 / 类型解析路径。

### 加载流程本身

| 补丁 | 目标 | 手段 |
|---|---|---|
| `ModContentPack_LoadPatches_Patch` | `Verse.ModContentPack.LoadPatches` | Prefix / Postfix / **Finalizer** |
| `ModContentPack_ReloadContentInt_Patch` | `Verse.ModContentPack.ReloadContentInt` | Prefix / Postfix |
| `ModAssetBundlesHandler_ReloadAll_Patch` | `Verse.ModAssetBundlesHandler.ReloadAll` | Prefix / Postfix |
| `DirectXmlLoader_XmlAssetsInModFolder_Patch` | `Verse.DirectXmlLoader.XmlAssetsInModFolder` | Prefix |
| `GenTypes_AllLeafSubclasses_Patch` | `Verse.GenTypes.AllLeafSubclasses` | Prefix |
| `GenTypes_GetTypeInAnyAssemblyInt_Patch` | `Verse.GenTypes.GetTypeInAnyAssemblyInt` | Prefix / Postfix |
| `Startup` | `Verse.StaticConstructorOnStartupUtility.CallAll` | Postfix |
| `World_FinalizeInit_Patch` | `RimWorld.Planet.World.FinalizeInit` | Postfix |
| `LanguageDatabase_SelectLanguage_Patch` | `Verse.LanguageDatabase.SelectLanguage` | Prefix |

> `LoadPatches` 那处带 **Finalizer**——作者认真处理了异常路径，
> 补丁自身失败不会把整个加载流程搞挂。这是成熟 patch 的标志。

### Def 与图形

| 补丁 | 目标 | 手段 |
|---|---|---|
| `ThingDef_PostLoad_Patch` | `Verse.ThingDef.PostLoad` | Prepare / **Transpiler** |
| `BuildableDef_PostLoad_Patch` | `Verse.BuildableDef.PostLoad` | Prepare / **Transpiler** |
| `GraphicData_Init_Patch` | `Verse.GraphicData.Init` | Prefix / Postfix |
| `GlobalTextureAtlasManager_BakeStaticAtlases_Patch` | `Verse.GlobalTextureAtlasManager.BakeStaticAtlases` | Prefix |
| `ModContentLoaderTexture2D_LoadTexture_Patch` | `Verse.ModContentLoader<Texture2D>.LoadTexture` | Prefix / Postfix |

> **两处用了 `Transpiler`**——这是 Harmony 里的 **IL 级重写**，
> 直接改方法体而不是前后插钩子。风险和性能收益都最高的一档。
> 这也是它对游戏版本敏感的原因（1.6 专用）。

### ⭐ 连 Harmony 自己都被打补丁

| 补丁 | 目标 |
|---|---|
| `AccessTools_AllTypes_Patch` | `HarmonyLib.AccessTools.AllTypes` |
| `AccessTools_TypeByName_Patch` | `HarmonyLib.TypeByName` |

`AccessTools.AllTypes()` 是 mod 启动时最慢的反射调用之一（会遍历所有程序集所有类型）。
FGL 把它缓存成静态列表 `allTypesCached` + `typesLock`，并提供 `Preload()` /
`BuildTypeList()` / `WarmupTypeCache()` 在空闲时段预热。

### XPath 缓存

| 补丁 | 目标 |
|---|---|
| `XmlNode_SelectSingleNode_Patch` | `System.Xml.XmlNode.SelectSingleNode(string)` |

加载期大量 XPath 查询结果缓存；进主菜单时由 `CacheResetter.ResetAll()` 彻底释放
（对应描述里的"进入主画面后彻底释放记忆体，防止执行期相容性冲突"）。

### 未标注目标的补丁

`FGLProgressReporter`、`RedirectHugslibToMainThread`、`SoundStarter_Patch`、
`SubSoundDef_ResolvePatch` 的 `[HarmonyPatch]` 参数为空，目标在运行时解析
（多半是为了容忍不同游戏版本的方法签名差异）。

---

## 怎么验的

没有源码可读（只发布 `.dll`），所以核验靠**反射 + 特性解析**，共四步：

**① 反射类型表** —— `FasterGameLoading.dll` 共 58 个非编译器生成类型。

**② 从 `[HarmonyPatch]` 特性直接读出补丁目标** —— 这是最关键的一步：

```csharp
$ty.GetCustomAttributesData()   // 读构造函数参数
```

`HarmonyPatch` 的构造参数就是补丁的类名与方法名，
`Verse.ThingDef.PostLoad`、`HarmonyLib.AccessTools.AllTypes`、`System.Xml.XmlNode.SelectSingleNode`…
**22 处补丁目标全部这样拿到**，比猜方法名再扫 IL 可靠得多
（对比 `records/717575199-MiscTraining/` 那次是靠猜 + 扫 IL 才定位到
`GenTypes.AllLeafSubclasses`）。

**③ 排序属性与设置项** —— 从特性参数里读出 `[HarmonyAfter("ChezhouLib.lib")]`、
`[HarmonyBefore("com.telefonmast.graphicssettings.rimworld.mod")]`；
再从 `FasterGameLoadingSettings : ModSettings` 的静态字段列出 7 个开关。

**④ 配套 mod 与版本号查证** —— 用 XML 精确匹配 `packageId` 确认
`garethp.modlistconfigurator` / `com.telefonmast.graphicssettings.rimworld.mod` / `ChezhouLib.lib`
三者均未安装；对比 FGL 引用的 `0Harmony 2.4.2.0` 与官方 Harmony `Current/` 里
实际的 `0Harmony 2.4.1.0`。

> **本轮的一次自查纠错**：首次反射时**没有预加载 `0Harmony` 和 `Assembly-CSharp`**，
> `GetCustomAttributesData()` 与 `GetParameters()` 大量抛
> *"未能加载文件或程序集 0Harmony, Version=2.4.2.0"*，
> 属性表全空。补上按依赖顺序预加载后重跑才拿到完整补丁清单。
> **教训：反射 mod 的 DLL 前必须先加载它的全部引用程序集**，
> 否则拿到的"零命中"是工具故障，不是数据事实。

---

## 三、⭐ 最能体现作者水平的两处：补丁排序属性

```
ModAssetBundlesHandler_ReloadAll_Patch     [HarmonyAfter("ChezhouLib.lib")]
ModContentLoaderTexture2D_LoadTexture_Patch [HarmonyBefore("com.telefonmast.graphicssettings.rimworld.mod")]
```

配合内部类 `DDSCompat`（含 `isImageOptActive` / `isGraphicsSetterActive` 两个探测字段）：

> **检测到 Image Opt / Graphics Settings+ 就自动让路**，自己的贴图降分辨率功能自动退避。

描述里也明说了这条：
*"ChezhouLib 的 AssetBundle reload patch 会早于 FGL 的重复 reload 防护执行，
因此 ChezhouLib 管理的 bundle 在开发用 reload 流程中仍可正确刷新。"*

**这是"性能 mod 该有的样子**：不靠抢占，而是靠精确排序和主动退让来共存。
本库里另有两个功能重叠的性能 mod（Missile Girl - Performance / DefLoadCache），
FGL 在描述里也明确写了"**二选一**"。

### 另一个懂行的细节：跳过外星种族 mod 的贴图

`AdaptiveBakingSkipList` 里有 `IsAlienRaceMod` 方法，
以及 `dependencyListMemberNames` / `dependencyPackageIdMemberNames` /
`targetMods` / `targetModRoots` / `ShouldSkipBaking` / `IsProtectedModTexturePath`。

→ **图集烘焙时主动跳过外星种族 mod 的贴图**。
   理由很清楚：大型种族 mod 的多层 alpha 贴图正是图集烘焙最容易出问题的地方。
   本库有 HAR（`839005762`）外加大量种族 mod，这条保护很实际。

---

## 四、七个设置项与针对本库规模的建议

反射 `FasterGameLoadingSettings : ModSettings` 得到的字段：

| 设置 | 默认 | 作用 |
|---|---|---|
| `earlyModContentLoading` | **开** | 在游戏空闲时段提前加载 mod 内容（现在包含官方 Core/DLC） |
| `XPathCaching` | **开** | 加载期缓存 XPath，主菜单时释放 |
| `DelayGraphicLoading` | 关 | 延后加载非必要贴图（背景装饰等） |
| `StaticAtlasesBaking` | 关 | 自适应图集烘焙，按 GPU 速度调批大小，保留 1.6 原版 atlas 预插入 |
| `EnableMultiThreading` | 关 | 多线程并行 XML 加载与类型解析 |
| `VerboseLogging` | 关 | 输出调试信息到控制台 |
| （另）贴图降分辨率 | 关 | 独立功能，缩图副本存在独立目录，可随时删掉还原 |

### 针对本库（1021 mod）的建议起点

> ⚠️ **以下是基于功能描述的推理，不是在你机器上实测过的数据。**
> 真正的判断需要对比开关前后的实际加载耗时。

| 设置 | 建议 | 理由 |
|---|---|---|
| `earlyModContentLoading` | **保持开** | 官方默认，利用空闲时间，风险最低 |
| `XPathCaching` | **保持开** | 官方默认，主菜单释放，不影响运行期 |
| `EnableMultiThreading` | **值得试，但要验证** | 对 1021 mod 规模收益应该最大，但多线程加载对**非线程安全的 mod** 有风险。开启后必须实测存档能否正常读入 |
| `StaticAtlasesBaking` | 可试 | 有 `AtlasBakeDiagnostics.LogPotentialMaskIssues` 会报告问题 mask，开了详细日志能观察 |
| `DelayGraphicLoading` | **建议先关着** | 作者自己写了："启用时静态图集会被再次烘焙，大型种族或高贴图量 mod 会产生**重复 atlas 显存占用**"——**本库正好是种族 mod 重灾区**（HAR + 一大堆） |
| `VerboseLogging` | 排查时开，平时关 | |
| 贴图降分辨率 | **先别用** | 你库里没装 Image Opt / Graphics Settings+，理论上它会自己启用；但外置转 DDS 工具质量更高更省空间 |

**配合环境变量** `HARMONY_NO_LOG`（详见 `修改/2009463077-Harmony/README.md`）
可以在性能测试期间避免 `harmony.log.txt` 堆积。

---

## 五、⚠️ 一处版本不匹配（观察项，非故障）

| | 版本 |
|---|---|
| FGL 编译时引用 | **`0Harmony 2.4.2.0`** |
| 官方 Harmony `Current/` 里的实际程序集 | **`0Harmony 2.4.1.0`**（其 modVersion 才是 2.4.2.0） |

即 FGL 比实际安装的 Harmony **新了一个补丁号**。

- 实践中非强命名程序集的绑定通常宽松，所以大概率能正常跑
- 但如果哪天遇到 **FGL 相关的 `MissingMethodException`**，这是第一个该怀疑的地方

> 相关背景：Harmony 官方 mod 的 `modVersion`（2.4.2.0）与内含 `0Harmony.dll`
> 的程序集版本（2.4.1.0）本来就不一致——这是正常的（外层包装与内层库独立版本化）。
> FGL 引用的是外层的号，所以看起来"对不上"。

---

## 六、它沿用了原版的 packageId

`packageId = Taranchuk.FasterGameLoading`，但作者是綠菇。

- **好处**：老配置无缝衔接，用户的 `modDependencies` 不会断
- **副作用**：Steam / 更新工具会把更新算到原版头上

这是分支维护的常规做法，不是错误。源码同时给了两个 GitHub 地址（原版 + 分支），
作者态度是透明的。

---

## 七、描述里推荐的配套 mod，本库均未安装

| packageId | 名称 | 状态 |
|---|---|---|
| `garethp.modlistconfigurator` | Mod List Configurator | 未装（在它的 `loadAfter` 里，不装不影响） |
| `com.telefonmast.graphicssettings.rimworld.mod` | Graphics Settings+ | 未装 |
| `ChezhouLib.lib` | ChezhouLib | 未装 |
| Loading Progress | 加载进度条 | 未见 |
| Missile Girl - Performance Mod / DefLoadCache | 性能 mod（**二选一**） | 未见 |

> 好处是**没有功能重叠的性能 mod 在跟你抢**。
> 坏处是 FGL 的两处 `HarmonyAfter` / `HarmonyBefore` 排序属性目前都用不上。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| — | **无需修改**。这是基础设施级 mod，改它等于改全库的加载行为 |
| 建议 | 先按 §四 的"建议起点"配好，然后**实测开关前后的加载耗时**再决定是否调整 |
| 建议 | 若开 `StaticAtlasesBaking`，配 `VerboseLogging` 观察 `AtlasBakeDiagnostics` 的 mask 报告 |
| 低 | 可安装 Graphics Settings+ 或 Image Opt，让 FGL 的贴图相关功能自动退避（更省心） |

---

## 可复用结论

1. **性能 mod 的正解是"排序 + 退让"，不是"抢占"。**
   FGL 用 `[HarmonyAfter]` / `[HarmonyBefore]` 精确排序，
   探测到同类工具就自动关闭自己的对应功能。
   **这是本库所有 mod 里最值得学的冲突处理范式。**

2. **给 Harmony 自己打补丁能省下大量启动时间。**
   `AccessTools.AllTypes()` / `TypeByName()` 是所有 C# mod 启动时的公共开销，
   在空闲时段预热并缓存，对 mod 数量敏感的库收益显著。

3. **`[HarmonyPatch]` 的参数能直接读出补丁目标。**
   反射 `GetCustomAttributesData()` 拿到构造函数参数，
   就是补丁打的类名 + 方法名——**比猜方法名可靠得多**。
   （本记录 22 个补丁目标全部是这样得到的。）

4. **补丁带 `Finalizer` 说明作者处理了异常路径**，
   带 `Prepare` 说明处理了目标方法不存在的兼容情况。
   看一个 patch mod 的成熟度，看这两者比看代码量准。

5. **`Transpiler` 是 IL 级重写，版本敏感度最高。**
   FGL 只支持 1.6、且两处用了 Transpiler——**这是"深度优化"的代价**。
   自己写 patch 时优先用 Prefix/Postfix，除非确实需要改方法体。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），FGL 2026.06.20.1*
*核验方式：反射 58 个类型 + 解析 22 处 `[HarmonyPatch]` 目标与排序属性 + 设置项字段导出*
*未实测：本机开关前后的实际加载耗时对比*
