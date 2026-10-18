# RimJobWorld - FB（RJW 做爱感想·颜值） — 分析记录

> 收录目录 `rjw-做爱感想-颜值`，源目录 `F:\Games\GBL\rimworld\Mods\rjw-做爱感想-颜值`。
> 分档 **② 档**（去重后仅约 10 个唯一文件 / 1 个 Def / 1 个 Harmony 补丁）+ **跨版本工程审计**。
> 本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里的任何文件。

---

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `RimJobWorld - FB`（描述："applies aftersex mood boost/loss based on partner beauty"） |
| packageId | `rjw.FB` |
| 作者 | `Ed86` —— **RJW 本体作者本人**，属官方附属 |
| url | `https://gitgud.io/Ed86/rjw-fb`（`About.xml` **有 `<url>`**；`Manifest.xml` 另有 `manifestUri`） |
| Discord | `https://discord.gg/CXwHhv8` |
| 授权 | **未声明**。无 LICENSE / LICENCE 文件 |
| Manifest 版本 | `1.4.0` |
| 规模 | **38 文件 / 1,340,835 B（1.28 MB）**；去掉四版本重复后仅约 **10 个唯一文件** |
| 类型 | RJW 下游单点补丁：**1 个 `ThoughtDef` + 1 个 Harmony postfix** |
| 声明版本 | 1.3 / 1.4 / 1.5 / 1.6，**四个目录都真实存在**（这点比多数同类 mod 规范） |
| 体积分布 | `About/preview.png` 1,196,813 B = **89.3%**；VS 垃圾（`.suo` / `.csproj.user`）59,106 B = 4.4%；工程文件 33,063 B；4 份 `FB.dll` 合计 24,576 B；C# 源码 12,027 B |

### 依赖与装况（同时扫 `Mods\` 与 `Data\`）

| 关系 | packageId | 本机状态 |
|---|---|---|
| `modDependencies` | `rim.job.world` | ✅ `Mods\RJW_核心_本体` |
| `modDependencies` | `brrainz.harmony` | ✅ `Mods\2009463077`（0Harmony v2.4.1.0） |
| `modDependencies` | `UnlimitedHugs.HugsLib` | ✅ `Mods\818773962` —— **但代码里一次都没用到**（见下） |
| `loadAfter` | `erdelf.HumanoidAlienRaces` | ✅ `Mods\839005762` |

产物 `FB.dll` 的实际引用只有 4 个：`mscorlib` / `Assembly-CSharp` / `0Harmony` / `RJW`。
**`HugsLib` 不在引用列表里** —— 声明为硬依赖但运行时完全不需要。

---

## 它是什么

性行为结束后，按**伴侣的颜值**给当事人追加一条 0.5 天的心情记忆。全部逻辑 = 1 个补丁类。

### Def（`1.6/Defs/ThoughtDefs/RJW_Beautyfuck.xml`，四个版本**字节完全相同**）

`thoughtClass = Thought_Memory`，`durationDays = 0.5`，`stackLimit = 1`，`stackedEffectMultiplier = 1.0`。

| stage | label | `baseMoodEffect` |
|---|---|---|
| 0 | Fucked staggeringly ugly | **-4** |
| 1 | Fucked ugly | **-2** |
| 2 | Fucked pretty | **+2** |
| 3 | Fucked beautiful | **+4** |

### 判定逻辑（`fb.cs`，65 行）

补丁点：`rjw.AfterSexUtility.think_about_sex(Pawn, Pawn, bool, SexProps, bool)` 的 postfix。

```csharp
var p2beauty = p2.GetStatValue(StatDefOf.PawnBeauty, true);
if (p2beauty != 0)
{
    if      (p2beauty <= -2) beautystage = 0;   // -4
    else if (p2beauty <= -1) beautystage = 1;   // -2
    else if (p2beauty <  2)  beautystage = 2;   // +2
    else                     beautystage = 3;   // +4

    if (beautystage != -1)
        p1?.needs?.mood?.thoughts?.memories?.TryGainMemory(
            ThoughtMaker.MakeThought(RJW_Beautyfuck, beautystage), null);
}
```

区间实测（`p2beauty != 0` 前提）：

| 区间 | stage | mood |
|---|---|---|
| `(-∞, -2]` | 0 | -4 |
| `(-2, -1]` | 1 | -2 |
| `(-1, 0)` | 2 | +2 |
| **`== 0`** | **不给任何记忆** | — |
| `(0, 2)` | 2 | +2 |
| `[2, +∞)` | 3 | +4 |

**`== 0` 不给反应是有意设计，不是漏洞**：原版 `PawnBeauty` 的
`Data\Core\Defs\Stats\Stats_Pawns_Social.xml:41` 写的是 `<defaultBaseValue>0</defaultBaseValue>`，
所以"颜值恰好为 0"是基准值而非罕见边角。中性颜值不给心情是合理的。

`TryGainMemory(thought, null)` 第二个参数传 null → 心情气泡**不带社交对象**，
不会出现指向伴侣的连线。描述文本里写的 "Had sex with X pawn" 只是文案，没有实际关联。

### 触发面（IL 实测，比读代码更确定）

`think_about_sex` 的 5 参重载**内部直接调用** `think_about_sex_Bestiality`、
`think_about_sex_Rapist`、`think_about_sex_Victim`、`think_about_sex_Consensual`。
也就是说它是**全类型分发器**，本 mod 只补它一个就覆盖了全部行为类型。

后果：**兽交、强奸、被强奸、招嫖一样会拿到这条颜值心情**，因为 postfix 完全无视
`isReceiving`、`props`、`whoring` 三个参数（它们只在签名里出现，函数体一次都没读）。
文案也仍然是 "Had sex with beautiful pawn"。

### 调用链（IL 实测）

- 5 参重载在整个 `RJW.dll` 里**只有一个调用方**：`think_about_sex(SexProps props)`（1 参重载）
- 该 1 参重载的 IL 只有 **69 字节**，对 5 参版本的 `call` 指令出现 **2 次**（偏移 35 / 63）
  → 是**显式的双向调用，不是循环** → 双方对称：各拿一条基于对方颜值的心情

### 工程手法

- **`[StaticConstructorOnStartup]` 用在两个地方**：一个在 `InitHarmonyPatches` 里做 `PatchAll`；
  另一个**故意加在补丁类上**，目的是让 `public static readonly ThoughtDef RJW_Beautyfuck =
  DefDatabase<ThoughtDef>.GetNamed("RJW_Beautyfuck")` 这个静态字段在 Def 加载完成之后才求值。
  这是绕开"静态字段初始化早于 DefDatabase"的常用技巧。
- **整个方法体包在 `try/catch` 里**，`catch (Exception e) { Log.Error(e.ToString()); }` ——
  任何异常都降级成一条日志，不会打断 RJW 原流程。
- **Harmony 补丁写死完整参数类型数组** `new Type[] { typeof(Pawn), typeof(Pawn), typeof(bool), typeof(SexProps), typeof(bool) }`，
  精确定位那一个重载。反射确认 RJW 里该重载第 5 个参数确实叫 `whoring`，
  postfix 签名 `(... bool whoring = false)` **能正常绑定**（默认值多余但无害）。

---

## 怎么验的

### ① 核验方法

| 环节 | 做法 |
|---|---|
| 清点 | `Get-ChildItem -LiteralPath -Recurse -File` + `[System.IO.File]::ReadAllBytes().Length` |
| 跨版本 | **SHA-256 逐文件比对**（4 版本 × 6 类文件）；`fb.cs` 做**归一化 diff**（`re.sub(r"\s+"," ",l)` 后 `difflib`） |
| 字节级 | 四个 `FB.dll` 逐字节比较，输出差异区间与差异字节数，并配"同一文件自比对必须 0 差异"的正控 |
| 反射 | 每版**独立进程**预载（游戏 Managed 106 个 + `0Harmony` + RJW 1.6 + HAR 1.6 + HugsLib 1.6），读 `GetReferencedAssemblies()` / `GetTypes()` / `GetCustomAttributesData()` |
| IL | `MethodBody.GetILAsByteArray()` + `Module.ResolveMethod(token)` 自写调用图解析；再用 metadata token 全程序集反查调用方 |
| 原版核对 | `Stats_Pawns_Social.xml` 读 `PawnBeauty` 的 `defaultBaseValue` |

### ② 阳性对照

| 结论 | 对照样例 | 期望 | 实测 |
|---|---|---|---|
| Harmony 属性扫描可信 | `CherryPicker 1.6` | 7 处 | ✅ 7（6 HarmonyPatch + 1 HarmonyPriority） |
| 预载清单完整 | `HarmonyLib.HarmonyPatch` 可解析 | True | ✅ True |
| DLL 逐字节比对方法本身可信 | 同一 DLL 自比对 | 0 差异字节 | ✅ **0** |
| `RimWorld.StatDefOf.PawnBeauty` 存在 | 反射取字段 | 非 null | ✅ True（**不在 `Verse` 命名空间**） |
| IL 扫描器本身能命中 | 5 参重载的出向调用表 | 含 `think_about_sex_Bestiality` 等 | ✅ 45 条出向调用 |
| 调用方反查不是恒零 | 扫 3,446 个方法 | > 0 | ✅ 1 个方法（修好工具之后） |

### ③ 自查纠错（本轮我自己错了 4 次）

1. **又把中文写进 `.ps1`，踩了 PS 5.1 按 ANSI 解码的坑。**
   症状：脚本里所有中文字符串变成乱码，且有一个乱码字符恰好破坏了引号/反引号 →
   整个脚本 `ParserError`，一行都没跑。
   **这正是我上一轮刚写进记忆的规则（"脚本里不要出现中文路径/文字，一律从命令行传参"），
   本轮又违反了一次。** 修法：脚本内容全 ASCII，输出标签用英文，路径全部走 `param`。
   → 这条规则要的不是"知道"，是**写脚本时先看一眼有没有中文**。

2. **`$m.GetMethodBody()` 返回的已经是 `MethodBody`，它上面没有 `GetMethodBody()` 方法。**
   症状：3,446 个方法逐个抛 `MethodNotFound`，扫描"成功"跑完并报告
   **`callers found: 0`** —— 一个典型的"坏工具伪装出的零命中"。
   若不是紧跟着核 `RimWorld.StatDefOf.PawnBeauty` 时顺手看了错误流，这个 0 会被当成结论。
   修法：`$body=$m.GetMethodBody(); $il=$body.GetILAsByteArray()`，重跑得到 **2**。

3. **`FB.sln` 的路径我写成 `Source\FB\FB.sln`**，实际在 `Source\FB.sln` → 报"不存在"。
   该文件不影响结论（已归入"工程文件"体积桶），但如果我没同时做体积统计就会误判"缺 sln"。

4. **差点判 `PawnBeauty` 在 `Verse` 命名空间**。反射显示是 `RimWorld.StatDefOf.PawnBeauty`，
   `Verse.StatDefOf` 上没有该字段。源码写的是 `using RimWorld;` + `StatDefOf.PawnBeauty`，
   编译能过所以看不出差别 —— 只有反射能区分。

---

## 跨版本工程审计（这一轮的重点）

四个版本目录**都真实存在**，比上两个 mod（只发 1.6 却声明三版本）规范。
但逐项比对后，所谓"多版本支持"的成色需要拆开看：

| 文件 | 1.3 | 1.4 | 1.5 | 1.6 | 结论 |
|---|---|---|---|---|---|
| `Defs/.../RJW_Beautyfuck.xml` | 同一 sha | 同 | 同 | 同 | **四份字节完全相同**，纯重复分发 |
| `Source/FB/Properties/AssemblyInfo.cs` | 同一 sha | 同 | 同 | 同 | 四份相同（含版本号字段） |
| `Source/FB/fb.cs` | 同一 sha | 同 | 同 | **不同** | 1.6 只差 `catch(Exception e)` → `catch (Exception e)` **一个空格** |
| `Source/FB/fb.csproj` | 各异 | 各异 | 各异 | 各异 | TFM / HintPath / 引用项都变（见下） |
| `Assemblies/FB.dll` | sha A | sha B | sha C | sha D | **4 个不同哈希** —— 但见下 |

### 四个 DLL 的关键事实：哈希不同，**引用程序集却完全一样**

逐版反射 `GetReferencedAssemblies()`：

| 版本 | `Assembly-CSharp` | `0Harmony` | `RJW` | `AssemblyVersion` |
|---|---|---|---|---|
| 1.3 | **1.3.8194.1220** | **2.0.2.0** | 0.0.0.0 | 1.0.0.0 |
| 1.4 | **1.3.8194.1220** | **2.0.2.0** | 0.0.0.0 | 1.0.0.0 |
| 1.5 | **1.3.8194.1220** | **2.0.2.0** | 0.0.0.0 | 1.0.0.0 |
| 1.6 | **1.3.8194.1220** | **2.0.2.0** | 0.0.0.0 | 1.0.0.0 |

**四份 DLL 都是用 1.3 的工具链编译的**，包括 `1.6/` 那一份。
而 csproj 却显示 1.5 指向 `Lib.Harmony.2.3.3`、1.6 指向工坊路径的 `0Harmony.dll` ——
**csproj 改了，但产物没跟着重编**（或者编了但发布的仍是旧件）。

字节级比对显示四份并非逐字节相同（差异 1166 / 1268 / 1258 字节，102–130 个区间），
**但我没有反编译器，无法把差异归因到 IL 逻辑还是构建元数据**（MVID / 时间戳 / PDB 路径 / Debug-Release 形态差异）。
可确定的是：源码逻辑四版一致（只差一个空格），引用的外部程序集四版一致。

> 风险：程序集引用 `Assembly-CSharp 1.3.8194.1220` 跑在 1.6 运行时上。
> 这些程序集没有强名，.NET Framework 会放行，所以**当前能用**；
> 但它依赖"补丁只碰 `Verse.Pawn` / `StatDefOf.PawnBeauty` 这些跨版本稳定的成员"。

### csproj 的版本演进（真实体现了作者的工具链升级路径）

| 版本 | TFM | 0Harmony 来源 | HugsLib 引用 | 备注 |
|---|---|---|---|---|
| 1.3 | v4.7.2 | NuGet `Lib.Harmony.2.0.2` | `<Reference Include="HugsLib">` | |
| 1.4 | v4.7.2 | NuGet `Lib.Harmony.2.0.2` | 有，`v1.4\Assemblies` | |
| 1.5 | v4.7.2 | NuGet `Lib.Harmony.2.3.3` | 有，`v1.5\Assemblies` | 额外带内联 `Version=2.3.3.0, Culture=neutral` 说明 |
| 1.6 | **v4.8.1** | **工坊路径 `..\..\..\..\2009463077\Current\Assemblies\0Harmony.dll`** | **已删除** | `packages.config` 也一并没了 |

所有 csproj 的 `<Configuration Condition>` 默认值都是 **`Debug`** —— 不加 `-c Release` 直接编译出的是
Debug 产物。`1.3/Assemblies/FB.pdb`（17,920 B）是**唯一随包发布的 .pdb**，也只有 1.3 有，
与"1.3 是 Debug 构建、其余版本打包时删了 pdb"一致。

### 随包的开发环境垃圾

| 文件 | 大小 |
|---|---|
| `1.3/Source/.vs/FB/v16/.suo` | 39,424 B |
| `1.3/Source/.vs/STD/v16/.suo` | 19,456 B |
| `1.3/Source/FB/fb.csproj.user` | 226 B |
| `1.3|1.4|1.5/Source/FB/packages.config` | 137 / 137 / 136 B |
| `1.3/Assemblies/FB.pdb` | 17,920 B |

**只有 1.3 目录带 `.vs/`**，共 59,106 B（占全 mod 4.4%）。

### 硬伤与观察清单

| # | 问题 | 位置 | 说明 |
|---|---|---|---|
| 1 | **四个版本的 DLL 都是用 1.3 工具链编译的** | `*/Assemblies/FB.dll` | 引用 `Assembly-CSharp 1.3.8194.1220` + `0Harmony 2.0.2.0`。csproj 已按版本升级但产物没跟上 |
| 2 | **`HugsLib` 声明为硬依赖但代码零引用** | `About.xml:26-31`；1.3/1.4/1.5 的 csproj | `fb.cs` 里没有任何 HugsLib 类型；1.6 的 csproj 已经删掉该引用，但 `About.xml` 的 `modDependencies` 没同步 |
| 3 | **`AssemblyInfo.cs` 四份字节相同** → 四个 DLL 报同一个 `AssemblyVersion=1.0.0.0` | `*/Source/FB/Properties/AssemblyInfo.cs` | 无法从程序集版本判断装的是哪个游戏版本 |
| 4 | **`beautystage != -1` 是死代码** | `fb.cs:55` | 在 `p2beauty != 0` 成立的前提下，四分支 if/else 链必然给 `beautystage` 赋值，该判断永为真 |
| 5 | **postfix 完全无视 `isReceiving` / `props` / `whoring`** | `fb.cs:27` | 兽交、强奸、被强奸、卖淫一样发颜值心情；文案也不区分 |
| 6 | **`GetStatValue(PawnBeauty, true)` 的第二个参数是 `forUI=true`** | `fb.cs:41` | 取的是 UI 侧数值路径，游戏逻辑侧通常传 false。此处数值等价，但属于非惯用写法 |
| 7 | **`TryGainMemory(thought, null)` 不带社交对象** | `fb.cs:56` | 心情气泡无伴侣连线；文案 "Had sex with X pawn" 只是文字 |
| 8 | `GetNamed("RJW_Beautyfuck")` 未传 `errorOnFail:false` | `fb.cs:24` | 静态字段初始化时 Def 缺失会抛 `TypeInitializationException`，补丁静默不注册。有 `[StaticConstructorOnStartup]` 兜底，正常不会触发 |
| 9 | `catch (Exception e)` 包住全部逻辑 | `fb.cs:59` | 任何异常降级成一条 `Log.Error`，问题不显眼 |
| 10 | **`About.xml` 的 `<name>RimJobWorld - FB</name>` 与 `packageId=rjw.FB` 与目录名三处不一致** | | 本地靠中文目录名"做爱感想-颜值"辨识 |
| 11 | `Manifest.xml` 用旧式 `<dependencies><li>RimJobWorld</li></dependencies>`（显示名而非 packageId） | `About/Manifest.xml:5-7` | 已与 `About.xml` 不一致（`About.xml` 侧是 packageId 形式） |
| 12 | **1.3 目录带 `.vs/`（59,106 B）** | `1.3/Source/.vs/` | 占全 mod 4.4% |
| 13 | `About/preview.png` 单文件 1,196,813 B = **89.3%** | `About/` | 另无 `ModIcon.png` |
| 14 | csproj 的 HintPath 是作者本机的相对路径 | `*/Source/FB/fb.csproj` | 如 `..\..\..\..\..\..\..\workshop\content\294100\818773962\v1.3\Assemblies\HugsLib.dll`、`..\..\..\..\rjw\1.6\Assemblies\RJW.dll`（假设 `rjw` 与 `rjw-fb` 是同级目录）。不影响随包产物，但换机无法直接编译 |

### 顺带确认**做得好**的地方

- **四个版本目录都真实存在**，`LoadFolders` 那套"列了但不存在的目录"问题在这里不存在
- **ThoughtDef 与 AssemblyInfo 四份字节相同** —— 换版本时不会出现"Def 改了代码没改"的不一致
- **`[StaticConstructorOnStartup]` 双重使用**（打补丁 + 强制 Def 静态字段求值时机）是正确手法
- **补丁写死完整参数类型数组**精确定位重载，避免误补同名的 1 参版本
- ** Harmony ID 稳定**：`new Harmony("rjw.FB")` 与 packageId 一致，四版不变
- **Def 命名带 `RJW_` 前缀**，全库唯一，不会撞名
- 中文翻译 **8/8 全覆盖**（`stages.0..3` 的 `label` + `description`），用 `<defName.stages.N.field>` 叶路径格式，**未译 0、孤儿 0**
- `<url>` / `manifestUri` / `downloadUri` / Discord 四处追溯信息齐全 —— 收录标准里"能不能追溯上游"这一项是满分

---

## 可复用结论

1. **`GetReferencedAssemblies()` 是判定「多版本目录是真构建还是假差异化」的权威手段。**
   本例四个 `FB.dll` 哈希全不同（看起来是四次独立构建），但引用程序集**全部是
   `Assembly-CSharp 1.3.8194.1220` + `0Harmony 2.0.2.0`** → 四份都是 1.3 工具链产物。
   **只看哈希 / 文件大小 / mtime 会得出"四个版本各编译一次"的错误结论。**
   → 审多版本 mod 的固定动作：对每个版本的 DLL 各开一个独立进程反射
   （同名程序集同 AppDomain 会硬冲突），把 `Assembly-CSharp` / `RJW` / `0Harmony` 三个版本号列成表。

2. **跨版本比源码要"归一化后 diff"，不要看哈希或目测。**
   本例 1.6 的 `fb.cs` 与前三版只差 `catch(Exception e)` → `catch (Exception e)` **一个空格**。
   → `re.sub(r"\s+"," ",line)` 去掉缩进风格差异后再 `difflib`，才能看清"多版本目录到底改了什么"。
   本例结论是：**四版逻辑零差异**。

3. **Harmony postfix 的参数能否绑定，必须反射目标方法的真实参数名。**
   `[HarmonyPatch(typeof(X), "m", new Type[]{...})]` 只锁定**类型**，Harmony 实际按**名字**注入参数。
   本例目标 `think_about_sex` 第 5 个参数确实叫 `whoring`，postfix 的 `bool whoring = false` 绑定 OK；
   若上游把它改名成 `isProstitution`，Harmony 会在打补丁时抛"cannot bind parameter"。
   → 审补丁类时：把 `[HarmonyPatch]` 的类型数组与目标方法的参数名逐个对齐。

4. **没有反编译器时，可以直接扫 IL 拿调用图。**
   `MethodBody.GetILAsByteArray()` + `Module.ResolveMethod(metadataToken)` 足以回答：
   - **补丁目标是不是唯一分发入口** —— 本例 5 参 `think_about_sex` 的出向调用里直接有
     `_Bestiality` / `_Rapist` / `_Victim` / `_Consensual`，所以它覆盖全部行为类型
     （结论：兽交和强奸也会发颜值心情）
   - **同一方法被调用几次** —— 1 参重载 IL 仅 69 字节，对 5 参版的 `call` 出现 **2 次**
     → 显式双向调用，不是循环 → 双方对称
   - **调用方是谁** —— 用目标方法的 `MetadataToken`（如 `0x06000035`）全程序集反查
   → 这套三件套能替代大部分"读上游源码"的需求，成本只有几十行 PowerShell。

5. **判"某个阈值判断像 bug"之前，先查被比较 `StatDef` 的 `defaultBaseValue`。**
   本例 `if (p2beauty != 0)` 看着像多余/漏洞，实际原版 `PawnBeauty` 的
   `defaultBaseValue` 就是 `0`（`Data\Core\Defs\Stats\Stats_Pawns_Social.xml:41`），
   所以"中性颜值不给心情"是**有意设计**，不是边界漏判。
   → 反过来：看到 `<= 0` 这类判断先别急着删，先确认 0 是不是常态值。

6. **`[StaticConstructorOnStartup]` 可以加在补丁类上，用来推迟静态字段的求值时机。**
   本例 `public static readonly ThoughtDef X = DefDatabase<ThoughtDef>.GetNamed("X")`
   如果在普通类里会在类型首次被触碰时求值，可能早于 Def 加载；
   给类挂上 `[StaticConstructorOnStartup]` 就由游戏在 Def 就绪后统一触发。
   → 审"静态字段里查 DefDatabase"的 mod 时，这是一个应当存在、也容易漏掉的标记。

7. **声明为 `modDependency` 但代码零引用，是低成本的过度声明。**
   判据用产物：反射 `GetReferencedAssemblies()`，若第三方程序集不在列表里，
   就说明编译器把未使用的 `using` 省略了，运行时不需要它。
   本例 HugsLib 是硬依赖、1.3 的 csproj 还有 `<Reference Include="HugsLib">`，
   1.6 的 csproj 已经删了 —— **csproj 会随版本清理，`About.xml` 不会**。

8. **`AssemblyInfo.cs` 四份字节相同 → 四个 DLL 报同一个程序集版本号**，等于放弃了
   "从程序集版本反推游戏版本"这条线索。多版本 mod 应该让 `AssemblyVersion` 随版本变化
   （或干脆不随包发 `AssemblyInfo`）。

9. **`.suo` / `.csproj.user` / `packages.config` / `.pdb` 随包发布是常见遗留**。
   本例 1.3 独有 `.vs/`（59,106 B = 4.4%）+ `FB.pdb`（17,920 B）。
   → 审包体积时单独列一类"开发环境残留"，别混进"贴图/代码"里稀释结论。

10. **`preview.png` 单文件常占 mod 九成体积**。本例 89.3% 都在这一张图上。
    → 审体积先看 `About/`，再看有没有第二张（`ModIcon.png`）与它字节相同
    （上两个 mod 都撞上了这个问题）。另外注意本例**只有 `preview.png`、没有 `ModIcon.png`**，
    是与 `RJW_文化玩法_隐私意识` 相反的另一种情况。

---

## 修改建议

> **均未执行。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。**
> 且本 mod 是他人作品（虽是 RJW 作者本人，但归属不在本仓库）；以下仅为分析结论。

### P0 — 让"多版本支持"名副其实

1. 用各版本对应的工具链**真正重编**四份 `FB.dll`：
   1.4 → `Assembly-CSharp 1.4.*` + 对应 Harmony，1.5 → `1.5.*` + Harmony 2.3.3，
   1.6 → `1.6.*` + Harmony 2.4.x。编译完对每份 DLL 反射一次
   `GetReferencedAssemblies()`，确认三个版本号都对得上再发布。
2. 让 `AssemblyInfo.cs` 的版本号随目录版本变化，否则四份 DLL 无法区分。

### P1 — 依赖与一致性

3. 从 `About.xml` 的 `modDependencies` 里删掉 `UnlimitedHugs.HugsLib`（代码零引用），
   保留 `loadAfter` 即可；这样少一个用户必须装的依赖。
4. `Manifest.xml` 的 `<dependencies><li>RimJobWorld</li></dependencies>`（显示名形式）
   与 `About.xml` 的 packageId 形式统一，建议直接删掉 `Manifest.xml` 的 `dependencies` 段。

### P2 — 逻辑收紧（属设计取向，需作者拍板）

5. postfix 里用上手里已有但没用的三个参数，至少把 `whoring` 和 `isReceiving` 用起来：
   - `whoring == true` 时不发这条心情（卖淫场景的语义和"和谁做了"不同）
   - `props.sexType` 指向兽交 / 强奸时改为不发，或换用对应的 thought
6. 把 `TryGainMemory(thought, null)` 的第二个参数改成 `p2`，
   让心情气泡带伴侣连线（文案里写了 "with X pawn"，行为却不一致）。
7. 删掉 `fb.cs:55` 的 `if (beautystage != -1)`（死代码）。
8. `GetStatValue(StatDefOf.PawnBeauty, true)` 的 `forUI` 参数按惯用改 `false`。

### P3 — 打包清理

9. 删 `1.3/Source/.vs/`（59,106 B）、`1.3/Source/FB/fb.csproj.user`、`1.3/Assemblies/FB.pdb`。
10. `1.6/Defs/ThoughtDefs/RJW_Beautyfuck.xml` 提到根 `Defs/` 或 `Common/Defs/`，
    四份字节相同的 XML 只留一份（916 B × 4 → 916 B）。
11. `fb.csproj` 的 HintPath 换成相对本 mod 的可移植路径，或用 NuGet 包引用。

### 未核实项（如实标注）

- **四份 `FB.dll` 的 1166–1268 字节差异究竟在 IL 逻辑还是构建元数据** ——
  本机没有 ILSpy / Mono.Cecil，无法逐条归因。可确定的是源码逻辑四版一致、
  引用程序集四版一致。**验证方法**：用 ILSpy 分别反编译四份，比对 IL 文本。
- **四个版本在实机上是否都能正常加载** —— 本机只有 1.6 可验；
  尤其 1.4/1.5 上 Harmony 2.0.2 的 API 与游戏 1.4/1.5 是否兼容，未核。
- **`think_about_sex` 的 1 参重载 IL 69 字节里除两次 `call` 外的其余字节构成** ——
  能确定只有两次对 5 参版的调用，但两次调用之间的参数装载（是否交换了 `pawn`/`partner`）
  未逐字节还原。**这决定了"双方对称"结论的严格程度**：
  两次调用都传 `(p1, p2)` 还是 `(p1, p2)` / `(p2, p1)`，我只从"对称设计意图"推断，未实证。
- **兽交 / 强奸场景下这条心情是否真的弹出** —— IL 已证明 5 参重载会被调用，
  但 `GetStatValue(PawnBeauty)` 在动物伴侣上返回什么（动物没有 `PawnBeauty` → 0 → 不发？）未验。
- **`defName` 为 `RJW_Beautyfuck` 的 ThoughtDef 在全库是否有冲突** ——
  只核了带 `RJW_` 前缀这一点，未做全库字节级重名扫描。
- **本 mod 未在 1.6 实机加载过** —— 全部结论来自源码通读 + XML/DLL 静态核验 + IL 解析。
- **fork / 授权链** —— 本 mod 无 LICENSE。作者虽为 RJW 本体作者 Ed86，
  但**其明确许可条款未查**；RJW 本身的分发条款本轮也未核。
