# [BT] SpawnThoseGenes!（`2898044088`）— 分析记录

| | |
|---|---|
| 本记录目录 | `收录/2898044088-SpawnThoseGenes/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\2898044088\` |
| mod 名 | **[BT] SpawnThoseGenes!**（BT = Biotech） |
| packageId | `Nera.SpawnThoseGenes` |
| 作者 | Nera（致谢 Operator） |
| 工坊 ID | `2898044088`（`PublishedFileId.txt` 恰 10 字节 ✅） |
| 程序集版本 | `1.0.0.0`，编译于 **RimWorld 1.5.9214.33606** / Harmony 2.3.6.0 / .NET Framework 4.7.2 |
| 许可 | **CC BY 4.0**（Creative Commons Attribution 4.0 International）—— 见「授权」 |
| 支持版本 | 声明 1.4 / 1.5 / 1.6，**单一构建**（无版本目录） |
| 语言 | **零翻译**（且**无 `Languages/` 目录**）——因为它没有任何界面 |
| 分析日期 | 2026-10-17 |

> 本 mod **无禁再分发声明**；CC BY 4.0 允许再分发，**但要求署名**。

**它在你库里的位置**：收录记录里**最小的一个"框架型" mod**——
真正的源码只有 **10,664 字节（占全 mod 1.4%）**，一个 Harmony 补丁，一个自定义 Def 类型。
而且**开箱即用是空转的**：它给 12 个种族都建了配置，但 `<Groups>` 全是空的。

---

## 身份卡

| 项 | 值 |
|---|---|
| 规模 | **42 文件 / 735,914 字节（718.7 KB）** |
| 结构 | `About/` + `Assemblies/` + `Defs/` + **`Examples/`** + **`Source/`（完整源码 + 构建残留）** |
| 类型 | Biotech 基因框架 / 工具 |
| 主 DLL | `SpawnThoseGenes.dll` **8,192 字节**（+ PDB 19,968 B） |
| Harmony 补丁 | **1 个** |
| 自定义 Def 类型 | **1 个**：`SpawnThoseGenes.SpawnThoseGenesXenotypes` |
| 自带 Def | **12 个**（Biotech 11 + Odyssey 1），**全部 `<Groups>` 为空** |
| 引用程序集 | `0Harmony 2.3.6.0`、`Assembly-CSharp 1.5.9214.33606`、`mscorlib 4.0`、`System.Core 4.0`、`System.Xml 4.0` |
| `modDependencies` | `Ludeon.RimWorld.Biotech`（DLC）、`brrainz.harmony` ✅ 已装 |
| `loadAfter` | `ludeon.rimworld`、`ludeon.rimworld.biotech`、`brrainz.harmony`（全小写，见「怎么验的」） |
| 是否自带 `0Harmony.dll` | **否** ✅ |
| 是否有贴图 | **零**（连 ModIcon 都没有） |

### 目录字节分布——重点

| 项 | 字节 | 占全 mod |
|---|---|---|
| `About/`（其中 Preview.png 516 KB） | 517,390 | 70.3% |
| **`Source/` 合计** | **166,685** | **22.7%** |
| ├─ **真正的源码 + 工程文件**（`.cs` / `.csproj` / `.sln`） | **10,664** | **1.4%** |
| ├─ **`obj/`（Debug + Release 构建产物）** | **117,179** | **15.9%** |
| └─ **`.idea/` + `.vs/`（IDE 工作区）** | **37,857** | **5.1%** |
| `Assemblies/` | 28,160 | 3.8% |
| `Defs/` | 2,836 | 0.4% |
| `Examples/` | 1,792 | 0.2% |
| `LICENSE.txt` | 19,051 | 2.6% |

> **IDE + 构建残留合计 155,036 字节，是真正源码的 14.5 倍。**
> 工坊包里原封不动躺着 `obj/Debug/`、`obj/Release/`、三个 `.idea.*` 工作区
> 以及 Visual Studio 的 `.vsidx` 索引。

---

## 它是什么

一句话：**让指定的种族在生成时"天生带上"某些内源基因（endogene）**——
典型用途是让动物/科幻种族自带毛色、瞳色、皮肤色等外观基因。

### 全部实现：1 个补丁 + 140 行代码

`Source/SpawnThoseGenes/SpawnThoseGenes.cs` 全文 140 行：

- `[StaticConstructorOnStartup] public static class SpawnThoseGenesMod`
- Harmony 补丁：**`PawnGenerator.GenerateGenes` 的 Postfix**。
  注意目标是 **private static** 方法，代码用
  `typeof(PawnGenerator).GetMethod("GenerateGenes", BindingFlags.NonPublic | BindingFlags.Static).Name`
  反射取名——这是绕过访问限制的标准写法。
- 三个类：`SpawnThoseGenesXenotypes : Def`、`EndogeneGroup`、`EndogeneChance`。

Postfix 的判定链（逐条对照源码）：

1. `request.AllowedDevelopmentalStages == DevelopmentalStage.Newborn` → **跳过**（新生儿不加）
2. `pawn.genes.UniqueXenotype` → **跳过**（唯一基因种族有自己的完整基因集）
3. 按 `xenotype.defName`（`CurrentCultureIgnoreCase`）找 `SpawnThoseGenesXenotypes` 配置
4. 找不到 → `Log.Message("[SpawnThoseGenes] No possible endogenes found in config for: …")`
5. 遍历该配置的每个 `EndogeneGroup`：
   - 掷骰：`Rand.Value < Σ chance`
   - 通过则按 `chance` 权重随机取一个 `EndogeneChance`
   - pawn 已有该内源基因 → 记日志跳过
   - **同类替换**：若新基因的 `endogeneCategory != None`，
     遍历已有基因，**移除第一个同 `endogeneCategory` 的基因**（源码注释：*"Get rid of duplicate genes like double hair color"*）
   - `pawn.genes.AddGene(geneDef, false)`

### XML 语法：元素名即 defName，文本即概率

`EndogeneChance` 实现了 `LoadDataFromXmlCustom`：

```csharp
DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "geneDef", xmlRoot.Name);
this.chance = ParseHelper.FromString<float>(xmlRoot.FirstChild.Value);
```

即**用 XML 元素名承载交叉引用**——于是写出来是这样：

```xml
<Endogenes>
  <Hair_Blue>0.5</Hair_Blue>
  <Hair_Red>0.5</Hair_Red>
</Endogenes>
```

这是个挺巧的写法：省掉了"基因名写两遍"的冗余。
`Examples/Example_Patch.xml` 里的注释同时说明了**概率语义**：

> Going over 1 means one of these genes will ALWAYS SPAWN,
> under 1 will mean there is a chance that it will not gain a gene from this list

因为代码是 `Rand.Value < Σ chance`（`Rand.Value ∈ [0,1)`），**一组概率之和 ≥ 1 就必出**。

### 12 个种族配置，但全是空的

`Defs/Biotech.xml` 给出 11 个、`Defs/Odyssey.xml` 给出 1 个 `SpawnThoseGenesXenotypes`：

`Baseliner`、`Dirtmole`、`Genie`、`Hussar`、`Neanderthal`、`Pigskin`、`Impid`、
`Waster`、`Yttakin`、`Highmate`、`Sanguophage`（Biotech）
+ `Starjack`（Odyssey）

**每一个的 `<Groups>` 都是空的**——只有 `Baseliner` 里有一段被注释掉的示例。
所以：**这个 mod 装上去什么都不做**，它是一张空表，等着你或别的 mod 用 XML 往里填。

`Examples/` 里两个文件就是填法说明：
- `Example_DefNewXenotype.xml` —— 新建一个种族的配置
- `Example_Patch.xml` —— 用 `PatchOperationSequence` + `PatchOperationAdd`
  往**已有**种族的 `Groups` 里追加（而不是覆盖），
  注释明确写 *"Please do not overwrite groups, instead add into them for the best mod compatibility"*

> 顺便：`Example_DefNewXenotype.xml` 里同一个 `<Endogenes>` 下把 `<YourGenes>` **写了两次**、
> 三个 `<li>` 也完全相同。作为模板有点糙（重复元素名），但因为每个元素独立解析所以不报错。

### 一个行为后果：日志噪音

第 4 步用的是 `Log.Message` 而不是 `Log.Warning`，且**没有节流**。
本 mod 只配置了 12 个原版种族；一旦装了别的种族 mod（如 HAR），
那些种族的 pawn 每次生成都会打一行
`[SpawnThoseGenes] No possible endogenes found in config for: …`。
装了 100 个种族 mod 就是每次生成刷一串。

---

## 怎么验的

### ① 核验方法（可复现）

| 要确认的 | 手法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse` + `ReadAllBytes().Length`；按 `Extension` 过滤区分源码与构建残留 |
| 功能实现 | **完整读源码**（140 行）——本记录的功能描述全部来自源码逐行对照，非推断 |
| XML 语法 | 读 `Defs/*.xml` + `Examples/*.xml` 全部 4 个文件 |
| 构建来源 | 读 `SpawnThoseGenes.csproj`（含 `HintPath` / `OutputPath`）、`Properties/AssemblyInfo.cs` |
| 打包 DLL 是哪个构建 | 三份 DLL **SHA256 对照**：`Assemblies/` vs `obj/Debug/` vs `obj/Release/` |
| 真实编译目标 | `ReflectionOnlyLoadFrom` 读 `GetReferencedAssemblies()` |
| Def 正确性 | 把 12 个 defName 拿去**游戏数据**里 `<defName>` 精确匹配，**分 Biotech / Odyssey 两个目录** |
| Biotech 是否已装 | 反射 `Assembly-CSharp` 查 Biotech 类型 |
| 依赖图 | `[xml]` 解析全库 `About/About.xml`，取直接子元素 `<packageId>` |
| 许可 | 读 `LICENSE.txt` 开头辨认许可家族 |

### ② 阳性对照

| 工具 | 阳性对照 | 结果 |
|---|---|---|
| 游戏 Def 匹配 | `Baseliner` 必须在 `Data/Biotech/XenotypeDefs.xml` 命中 | ✅ **12/12 全部命中** |
| Biotech 存在性 | 见纠错 1（我第一版对照写错了命名空间） | ✅ 修正后通过 |
| 三份 DLL 哈希 | 必须能区分出 Release 与 Debug 不同 | ✅ `4A256B6E…` = `obj/Release`，≠ `obj/Debug` |
| 依赖扫描 | `brrainz.harmony` 必须命中 | ✅ |
| 源码体积统计 | `.cs`/`.csproj`/`.sln` 三种扩展名必须都能取到 | ✅ 10,664 字节 |

### ③ 自查纠错（本轮我的工具错了 2 次）

**1. 阳性对照本身写错了命名空间，差点得出"Biotech 没装"的结论。**
我用 `Verse.XenotypeDef` 做对照，结果返回"不存在"，正控 FAIL。
换成 `RimWorld.XenotypeDef` 与 `Verse.EndogeneCategory` 后确认 Biotech 就在 `Assembly-CSharp` 里。
**教训**：对照项选错时，失败的是对照而不是被测对象——**先怀疑对照，再怀疑数据**。
最终结论靠**第二个独立证据**交叉确认：12 个 defName 全部在 `Data/Biotech/XenotypeDefs.xml`
和 `Data/Odyssey/XenotypeDefs.xml` 里精确命中。

**2. 安全策略把正则里的 `\\` 当成网络共享路径，整条命令被拦截。**
我写 `Where-Object { $_.FullName -match '\\(\.idea|\.vs)\\' }`，
结果触发 "direct access to the network share" 的硬安全策略。
改成 `$_.DirectoryName.Contains('.idea')` 之类**不含反斜杠的写法**即通过。
→ 在本机写路径匹配时，**避免以 `\\` 开头的正则**。

### ④ 未核实

- **CC BY 4.0 用于源代码的效力**：该许可属 Creative Commons 家族，
  并非 OSI 认证的软件许可（对"软件"这一客体适用性存疑）。
  本记录只陈述事实（`LICENSE.txt` 写的是 CC BY 4.0，19,051 字节全文），不作法律判断。
- **`loadAfter` 全小写**（`ludeon.rimworld` / `ludeon.rimworld.biotech`）：
  本库 DLC 没有 `About.xml`，扫不到真实 packageId；
  但按已确认的 `Verse.ModMetaData.packageIdLowerCase` + `SamePackageId`，
  **packageId 匹配大小写不敏感**，写法无害。
- **`Examples/Example_DefNewXenotype.xml` 的重复元素名**在实机上的确切表现，
  未实机验证（按 `LoadDataFromXmlCustom` 逐元素解析的逻辑推断为可用）。

---

## 上下游与冲突面

### 谁依赖它：**没有**

全库扫描 `Nera.SpawnThoseGenes` 只命中它自己的 `<packageId>`。
它是一片叶子，**不构成任何其它 mod 的前置条件**。

### 作者生态：本库仅此一个 mod

`Nera.*` 前缀下只有它自己。致谢里提到的 "Operator" 不是本库中的 mod 作者标识。

### 结构风险：本轮未发现

- 不自带 `0Harmony.dll` ✅
- 不带 `0MultiplayerAPI.dll` ✅
- 引用程序集只有 5 个，**且不含 `UnityEngine` 任何模块**——
  虽然 `.csproj` 里写了一个单体 `UnityEngine.dll` 的引用，但**打包的 DLL 并未引用它**（未使用的引用不进入程序集引用表）。所以那份 csproj 引用是纯遗留。
- 它引用 Harmony 的 csproj 路径写的是 `..\..\..\2009463077\Current\Assemblies\0Harmony.dll`
  ——**直接用工坊 ID 当目录名**，且是 `Current` 而非版本目录。这是作者本机的路径约定，不可移植。

### 一处工程上的继承痕迹

`SpawnThoseGenes.csproj` 里：

```xml
<RootNamespace>Eyextended</RootNamespace>
```

而 `.idea/` 下有三个工作区目录：`.idea.Eyextended.dir\`、`.idea.Eyextended\`、
`.idea.SpawnThoseGenes.dir\`。

即：**这个工程是从另一个名为 "Eyextended" 的项目复制来的**，
`RootNamespace` 和两个旧工作区都没清。
无功能影响（`RootNamespace` 只是 IDE 用的命名空间前缀，
实际 `namespace` 在 `.cs` 里写死是 `SpawnThoseGenes`），
但说明发布前没做过工程清理——这也解释了 `.idea/` `.vs/` 为什么被一起打包。

---

## 可复用结论

1. **`LoadDataFromXmlCustom` 可以把"XML 元素名"变成交叉引用，从而省掉重复。**
   本 mod 的 `EndogeneChance` 用 `RegisterObjectWantsCrossRef(this, "geneDef", xmlRoot.Name)`
   把 `<Hair_Blue>0.5</Hair_Blue>` 的**元素名**当成 `geneDef`、**文本**当 `chance`。
   凡是"列表里每项需要引用一个 Def + 带一个参数"的场景，都能用这招消掉一层冗余。

2. **概率写成"一组权重之和 vs 一个随机数"，天然支持"必出"与"或有或无"两档。**
   `Rand.Value < Σ chance`：`Σ ≥ 1` 必出、`< 1` 是概率。
   比给每项写独立概率更好解释，也不用做归一化。

3. **同类别替换是外观基因的通用需求。**
   加"第二套头发颜色"前先移除同 `endogeneCategory` 的旧基因——
   否则pawn 会同时带两套互相矛盾的外观基因。
   这是 Biotech 基因系统的固有约束，凡批量加基因的 mod 都要处理。

4. **框架型 mod 可以合法地"什么都不做"。**
   本 mod 给 12 个种族建了空配置，只提供挂载点，等用户/别的 mod 填 XML。
   配合 `Examples/` 目录讲清填法——**"空表 + 示例 + patch 入口"是低侵入式框架的最小形态**，
   比替别人写一套预设基因友好得多。

5. **发到工坊前跑一次 `.gitignore` 检查。**
   本 mod 打包了 `obj/Debug`（含 50 KB 的 `.csproj.AssemblyReference.cache`）、
   `obj/Release`、三个 `.idea.*` 工作区和 Visual Studio 的 `.vsidx`——
 合计 **155,036 字节，是真正源码的 14.5 倍**。
 通常只需在发布目录加 `.gitignore`（`obj/` `.idea/` `.vs/` `*.user`）
 或让构建输出到包外即可避免。

6. **csproj 里的引用和真正的程序集引用会不一致。**
   本 mod 的 csproj 引用了单体 `UnityEngine.dll`，
 但**打包 DLL 的引用表里根本没有 UnityEngine**——
 未使用的引用不会进入 `AssemblyRef` 表。
 → 判断"这个 mod 到底碰了什么引擎 API"，要看 `GetReferencedAssemblies()`，**不要看 csproj**。

7. **用 SHA256 能证明"工坊里那个 DLL 到底是 Debug 还是 Release 构建"。**
   本 mod 的 `Assemblies/SpawnThoseGenes.dll` 与 `obj/Release/` **字节一致**、
 与 `obj/Debug/` 不同——既证明了发布的是 Release，也顺便证明了 `obj/` 是同一次构建留下的。

8. **打包的源码树会暴露工程继承痕迹。**
   `RootNamespace` 写着 `Eyextended`、`.idea/` 下留着三个工作区——
 说明工程是复制来的。发布前清一次 `.idea/` `.vs/` `obj/`，
 顺带也能发现这类没清理干净的痕迹。

---

## 修改建议

> 以下**均未执行**。按用户当前要求，本轮只收录分析，不动任何 mod 文件。

| 优先级 | 项 | 说明 |
|---|---|---|
| 高 | **清掉 `obj/` `.idea/` `.vs/`** | 可减 **155,036 字节（全 mod 21.1%）**，且不影响功能。需用户授权后再动 |
| 高 | **`Examples/Example_DefNewXenotype.xml` 的重复元素名** | 同一 `<Endogenes>` 下写了两次 `<YourGenes>`，三个 `<li>` 也完全相同；作为给人抄的模板会误导 |
| 中 | **日志噪音** | 对未配置的种族每次生成都 `Log.Message` 一行，无节流。装了多个种族 mod 时会刷屏。建议改 `Log.Warning` 或加一次性提示 |
| 中 | 澄清授权 | CC BY 4.0 通常用于内容而非源代码。补一句说明"源码以何种许可释出"会更清楚 |
| 低 | `RootNamespace` 与 `.idea` 遗留 | 留着 `Eyextended`；无功能影响，但清理时顺手改掉 |
| 低 | 1.4 支持存疑 | 打包 DLL 引用 `Assembly-CSharp 1.5.9214`，却声明支持 1.4。若 1.4 的 `PawnGenerator.GenerateGenes` 签名不同则 1.4 上会失效——**未实机验证** |

---

*2026-10-17 收录。② 档（单一机制 + 完整源码可精读）。
功能描述全部来自 140 行源码逐行对照；12 个种族 defName 全部与游戏数据交叉核对命中；
三份 DLL 用 SHA256 证明发布的是 Release 构建。
本轮工具自查纠错 2 次（阳性对照写错命名空间、正则 `\\` 触发安全策略），均已留档。*
