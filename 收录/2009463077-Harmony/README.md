# Harmony（`2009463077`）— 分析记录

| | |
|---|---|
| 本记录目录 | `修改/2009463077-Harmony/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\2009463077\` |
| mod 名 / packageId | Harmony / `brrainz.harmony` |
| 作者 | Andreas Pardeike（Brrainz） |
| 版本 | modVersion **2.4.2.0**（内含 `0Harmony.dll` 程序集版本 **2.4.1.0**） |
| 授权 | **MIT License**（`LICENSE`，Copyright (c) 2017 Andreas Pardeike） |
| 工坊 / 源码 | 2009463077 / https://github.com/pardeike/HarmonyRimWorld |

> **本 mod 是 MIT 授权**——与前六弹 yukiyuki 系列的"禁止再分发"完全相反，
> 可以自由修改、再分发，只需保留版权声明。
>
> 它是**全库的地基**：363 个 mod 把它声明为硬依赖。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | 14 文件 / 5.46 MB |
| 支持版本 | 1.2 / 1.3 / 1.4 / 1.5 / 1.6 |
| `loadBefore` | `Ludeon.RimWorld` —— **必须在游戏本体之前加载** |
| Def / 贴图 | 无（纯二进制） |
| `About/PublishedFileId.txt` | `2009463077` ✅ |

```
LICENSE                        1.1 KB   MIT
Readme.md                      2.0 KB   作者使用说明
LoadFolders.xml                0.3 KB   ★ 见 §二
About/About.xml + Manifest.xml + PublishedFileId.txt + preview
1.4/Assemblies/0Harmony.dll      910.0 KB   (md5 993f258153)
1.4/Assemblies/HarmonyMod.dll      5.0 KB
1.5/Assemblies/0Harmony.dll     2144.0 KB   (md5 4131a87e7c)
1.5/Assemblies/HarmonyMod.dll     12.0 KB
Current/Assemblies/0Harmony.dll 2398.5 KB   (md5 2afc09f2cd)  ← 1.6 用这个
Current/Assemblies/HarmonyMod.dll 17.5 KB
```

> `About/Manifest.xml` 是 RimWorld 新的 mod 清单格式
> （`identifier: net.pardeike.rimworld.mod.harmony`），
> 与老的 `About.xml` 并存，属于过渡期产物。

---

## 二、⭐ 全库最聪明的版本方案：`Current` 目录

```xml
<loadFolders>
  <v1.2><li>/</li><li>1.4</li></v1.2>
  <v1.3><li>/</li><li>1.4</li></v1.3>
  <v1.4><li>/</li><li>1.4</li></v1.4>
  <v1.5><li>/</li><li>1.5</li></v1.5>
  <v1.6><li>/</li><li>Current</li></v1.6>
</loadFolders>
```

**三个物理目录覆盖五个游戏版本**：1.2/1.3/1.4 共用 `1.4`，1.5 用 `1.5`，**1.6 用 `Current`**。

`Current` 的含义是"当前及以后所有版本"——
1.7 发布时只需加一行 `<v1.7><li>/</li><li>Current</li></v1.7>`，
**不需要重新编译任何 DLL**。

> 这正是本仓库 `AGENTS.md` 说"避免用 LoadFolders.xml"的原因：
> LoadFolders 容易写出**跨版本互相污染**的组合（见 §六）。
> 但 Harmony 靠"一个 Current 兜底未来"的克制用法，把这个机制用对了。
> **判断 LoadFolders 用得好不好，看它是不是在版本边界处收敛，而不是扩散。**

---

## 它是什么

### `0Harmony.dll`（库本体，2.4 MB）

- 引用程序集：**只有 `mscorlib` / `System` / `System.Core`**
  → **零 Unity、零 RimWorld 依赖**，是完全独立的纯 .NET 库
- 内嵌资源（解释了 2.4 MB 的体积来源）：
  - `exhelper_linux_x86_64.so` / `exhelper_linux_arm64.so`
  - `exhelper_macos_x86_64.dylib` / `exhelper_macos_arm64.dylib`
    → 给 Linux/macOS（尤其 IL2CPP/AOT）准备的原生异常处理辅助库
  - `FxResources.System.ValueTuple.SR.resources` → ILRepack 合并进来的 ValueTuple
  - `ILRepack.List` → 证实用了 ILRepack 打包
  - 注意：**没有 Windows 原生辅助库**，Windows 走托管路径

### `HarmonyMod.dll`（RimWorld 胶水层，17.5 KB）

引用 `0Harmony 2.4.1.0` + `Assembly-CSharp 1.6.9348.31746`。
反射出 **3 个 Harmony 补丁 + 2 个辅助类型**：

| 类型 | 作用 |
|---|---|
| `HarmonyMod.VersionControl_DrawInfoInCorner_Patch`（Postfix） | **游戏调试角落显示的那个 Harmony 版本号**就来自这里 |
| `HarmonyMod.Environment_GetStackTrace_Patch`（Prefix） | 在 `Environment.GetStackTrace` 前注入 Harmony 补丁信息，让异常堆栈显示"哪个 mod 的哪个补丁崩了" |
| `HarmonyMod.Log_ResetMessageCount_Patch`（Postfix） | 日志计数重置补丁 |
| `HarmonyMod.ExceptionTools` | 堆栈增强工具，通过反射抓取 Mono 内部方法（`GetFullNameForStackTrace` / `GetMethodIndex` / `GetSecureFileName` / `GetAotId`），并维护 `seenStacktraces` 缓存防止重复处理 |
| `HarmonyMod.Main` | 静态构造器扫描程序集，按 `HarmonyNames` 过滤出 Harmony 相关程序集用于版本显示 |

> 那个"崩溃堆栈里能看到是哪个 mod 的补丁出错"的功能，就是这三处补丁实现的。
> 它用的是**对 RimWorld 自己打 Harmony 补丁**的方式——自己吃自己的狗粮。

---

## 怎么验的

本 mod 只有二进制没有 Def，所以核验手段全是**反射 + 全库扫描**，没有可交叉引用的 XML。

**① 反射两个程序集**

- `HarmonyMod.dll`：类型表 + `GetReferencedAssemblies()` + `GetManifestResourceNames()`
- `0Harmony.dll`：同上。**内嵌资源清单是意外收获**——它直接暴露了
  4 个 Linux/macOS 原生辅助库（`exhelper_*.so` / `*.dylib`，各含 x64 与 arm64）
  和 `ILRepack.List`，后者解释了 2.4 MB 的体积来源

**② 全库依赖扫描**

遍历 1021 个 mod 的 `About/About.xml`，**用 XML 解析只取 `ModMetaData` 的直接子元素
`<packageId>`**——不能用子串 grep，否则会命中别的 mod 在 `modDependencies` /
`loadAfter` 里列的 packageId（`收录/README.md` §5 第 1 条）。

**③ 全库 `0Harmony.dll` 分布扫描**

按路径分类"会被游戏加载"与"仅开发产物"（排除 `Source/` `obj/` `bin/` `packages/`），
两者结论完全相反：前者 85 个 mod / 196 份，后者 21 个 mod 但无害。

**④ 与前几份记录的交叉引用**

`modify/1 美南烛` 那轮反射其他 mod 时，观察到 `SizedApparelforRJW.dll`
的引用表里没有 SizedApparel——这条线索在那边引发了两次判断反复，
教训见 `收录/1~11岁美狐贴图修正/` 的「怎么验的」。

> **阳性对照**：本轮的反射/扫描工具在同一批数据上做过阳性对照
> （`petness` 7 处、`specialTrainables` 8 处、`canArriveManhunter` 1 处均命中），
> 详见 `收录/README.md` §5。

---

## 四、⚠️ 本库最大的结构性问题：85 个 mod 自带 Harmony

全库扫描（用 XML 精确解析 mod 自身 packageId/依赖声明）：

| 统计项 | 数量 |
|---|---|
| 把 `brrainz.harmony` 声明为 **`modDependencies`（硬依赖）** | **363 个 mod** |
| 只在 **`loadAfter`（软排序）** | 243 个 mod |
| **自带"会被游戏加载的" `0Harmony.dll`** | **85 个 mod，合计 196 份** |
| 自带但只在 `Source/` `obj/` `bin/` `packages/` 等开发目录 | 21 个 mod（**无影响**） |

### 为什么这是个问题

Harmony 官方 `Readme.md` 自己写着：

> *"This means that all mods will use **the same Harmony version**."*
> （这样所有 mod 都会用**同一个 Harmony 版本**）

而实际有 85 个 mod 在自己的 `Assemblies/` 里塞了一份 `0Harmony.dll`，
和官方 Harmony mod 并存。多份同名程序集 + 不同版本，
正是 Harmony 生态最经典的两类故障来源：

- 重复程序集警告 / 后加载的版本被静默忽略
- `MissingMethodException` / `TypeLoadException`（某 mod 针对旧版 API 编译）
- 崩溃堆栈指向错误的补丁

**放肆的典型：**

| mod | 自带份数 | 说明 |
|---|---|---|
| `839005762`（HAR / Humanoid Alien Races） | **8** | 1.0–1.6 每版各一份，另加根目录 `Assemblies/` 一份 |
| `1127530465` / `1321849735` / `1446523594` / `1579516669` / `1662119905` / `1687053679` / `735268789` / `836308268` | 各 **7** | 整个版本矩阵都塞了 |
| `3512466087` | 2 | 根 `Assemblies/` **和** `Versions/v1.6/Assemblies/` 各一份，同一个 mod 内部重复 |

> **`839005762` 特别值得注意**：它既是"被最多 mod 依赖的框架之一"，
> 自己又在 8 个位置塞了 Harmony。它出现在 363 个硬依赖名单里，
> 很多 mod 是间接依赖它的——**它的 Harmony 版本会影响到半个库**。

### 建议（需要你授权，属于改动你的整个 Mods 目录）

**原则：只保留官方 Harmony mod 一份 `0Harmony.dll`，其余全部删掉。**

具体做法：
1. 逐个禁用那些自带 Harmony 的 mod，确认其补丁仍正常工作
2. 正常的话，直接删除其 `Assemblies\0Harmony.dll`（**不要删整个 Assemblies 目录**）
3. 用 VBE（ModConfigTool）检查最终启用列表里 Harmony 只出现一次，且排在最前面

⚠️ **不要盲删**。少数老 mod 可能确实依赖特定旧版 Harmony 行为，
删之前先用 `HARMONY_NO_LOG` 环境变量 + 逐个启用来定位（见 §五）。
`Source/packages/Lib.Harmony.X/lib/net*/` 下那些是 NuGet 包，**不影响运行时，不用管**。

---

## 五、`Readme.md` 里两个对 mod 作者有用的机制

**① `HARMONY_NO_LOG` 环境变量**

> *"Adding **HARMONY_NO_LOG** (any non-empty value) to your environment variables will
> suppress the creation of the `harmony.log.txt` file"*

Harmony 在发现 mod 作者忘记移除调试代码时会生成 `harmony.log.txt`。
设这个环境变量可以避免它在你硬盘上堆积日志。

**② 堆栈增强开关（Debug 模式 → 第二个调试图标 → tweak 变量）**

可以关掉"堆栈里附带补丁信息"的增强。这在**排查补丁冲突**时很好用——
关掉之后崩溃堆栈更干净，只看游戏本体调用栈。

> 这两个开关正好是排查 §四 那类重复 Harmony 问题的配套工具。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| **高** | 清理 85 个 mod 自带的 `0Harmony.dll`，只保留官方一份。**这是全库级别的操作，需单独授权，且要逐个验证** |
| — | Harmony 本体**无需任何修改**（它是基础设施，改了会影响全部 mod） |
| 低 | 若将来 RimWorld 出 1.7，只需在 `LoadFolders.xml` 加 `<v1.7><li>/</li><li>Current</li></v1.7>` |

---

## 可复用结论

1. **`Current` 目录 + LoadFolders 是"少版本目录"的标准解法。**
   本仓库 AGENTS.md 写"避免用 LoadFolders.xml"，但**原因不是 LoadFolders 本身有问题，
   而是大多数作者会在里面写出跨版本互相污染的组合**。
   Harmony 靠"一个 Current 兜底未来"把机制用对了——**收敛而非扩散**。

2. **库类 mod 应该与游戏零耦合。** `0Harmony.dll` 只引用 `mscorlib`/`System`/`System.Core`，
   游戏胶水层单独放在 17.5 KB 的 `HarmonyMod.dll` 里。
   **"库"与"适配层"分开**，是这个包结构最值得学的地方。

3. **发现 mod 依赖冲突时，先查"谁在自带这个库"。**
   本次 Harmony 分析的最大产出不是 Harmony 本身的问题，
   而是顺着它查出了 85 个自带副本的 mod——
   **一个基础 mod 的依赖图往往比它自身更值得查。**

4. **ILRepack 会让程序集体积膨胀 3–5 倍**（910 KB → 2.4 MB）。
   看到"一个库 dll 有 2 MB 以上"时，先查它是不是打包合并过的。

5. **内嵌原生库要按平台区分。** Harmony 里只有 `.so` / `.dylib`（Linux/macOS），
   **没有 Windows 版本**——因为 Windows 走托管路径。
   分析带原生扩展的 mod 时，先看它为哪些平台提供了二进制。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），Harmony 2.4.2.0 已启用*
*核验方式：反射 `HarmonyMod.dll` / `0Harmony.dll` 类型表与引用 + XML 精确解析全库依赖声明 + 全库 `0Harmony.dll` 分布扫描*
