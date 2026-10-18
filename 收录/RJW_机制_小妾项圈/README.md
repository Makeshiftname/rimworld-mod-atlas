# Peculiar Institution — 分析记录

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `Peculiar Institution` |
| packageId | `readyforjeff.RJWPeculiarInstitution` |
| 作者 | `readyforjeff` |
| 源目录 | `F:\Games\GBL\rimworld\Mods\RJW_机制_小妾项圈`（README 说预期目录名是 `RJWPeculiarInstitution`） |
| 上游 | **About.xml 无 `<url>`，README 也未给仓库地址** —— 只提到基于 [Rimworld Mod Template](https://github.com/Rimworld-Mods/Template)。没有可追溯的上游源码仓库链接 |
| 授权 | **无**。无 `LICENSE`、README 无许可声明 → 未声明许可 |
| modVersion | `1.1.2`（`<modVersion IgnoreIfNoMatchingField="True">`，这是 RimWorld 模板里的常见样板属性） |
| 规模 | **50 文件 / 1,452,974 bytes（1.39 MB）** |
| 类型 | 功能 mod（20 Def + 62 C# 类型 + 7 个 Harmony 补丁 + 随包完整源码） |
| 支持版本 | **只有 1.6** |
| 硬依赖 | `Ludeon.RimWorld.Ideology` + `brrainz.harmony` + `rim.job.world`（三条都在 `modDependencies`） |
| `loadAfter` | `Ludeon.RimWorld`、`Ludeon.RimWorld.Royalty`、`Ludeon.RimWorld.Ideology`、`Ludeon.RimWorld.Biotech`、`rim.job.world`、`brrainz.harmony` |
| `incompatibleWith` | **空元素**，内含一行模板注释 `<!-- <li>username.modname</li> -->` 未删 |
| 依赖是否已装 | ✅ 三条硬依赖与三个 DLC 全部已装（本机实测） |
| 核验深度 | **② 档**（单一机制、规模小、但随包源码 → 结论基于真实源码）+ **框架继承分析** |

### 体积分解

| 项 | 文件 | 字节 | 占比 |
|---|---|---|---|
| `About/Preview.png` | 1 | 1,257,672 | **86.6%** |
| `Source/*.cs` | 21 | 86,504 | 6.0% |
| `1.6/Assemblies/RJWPeculiarInstitution.dll` | 1 | 64,512 | 4.4% |
| `.xml`（11 Def + 11 DefInjected + 1 JobDef） | 23 | 40,026 | 2.8% |
| `README.md` / `.csproj` / `.sln` / `.gitignore` | 4 | 4,260 | 0.3% |

**零自定义贴图。** `Apparel_Concubine_Collar` 直接复用原版 Ideology 的
`Things/Pawn/Humanlike/Apparel/SlaveCollar/SlaveCollar`（`graphicData.texPath` 与 `wornGraphicPath` 都是它）。这是"不加自己的美术"而不是遗漏。

### 目录结构

```
1.6/Defs/            11 个 XML（Def）
1.6/Assemblies/      RJWPeculiarInstitution.dll  v0.1.0.0
1.6/Languages/ChineseSimplified/DefInjected/   11 个 XML
Source/              21 个 .cs + mod.csproj + mod.sln   ← 根级，不在版本目录下
About/               About.xml + Preview.png
```

`Source/` 在根级而非 `1.6/Source/`，因为本 mod 只支持 1.6，源码不需要按版本分叉。

## 它是什么

给 RJW 加一条「专属妾侍」链：**一件项圈（collar）装备 → 戴上后获得 `MaxPersonalLieges` 统计量 → 可以把奴隶/囚犯指派为某位殖民者的专属妾侍 → 建立一对 `PawnRelationDef`（Liege ↔ Concubine）→ RJW 的性行为系统据此改写**。

### 20 个具体 Def（0 抽象、0 解析错误）

| 类型 | 数量 | defName |
|---|---|---|
| `PawnRelationDef` | 2 | `PeculiarInstitutionLiege`、`PeculiarInstitutionConcubine` |
| `ThoughtDef` | 7 | `AssaultedByLiege`、`ConflictImpregnated`、`ConflictImpregnator`、`KindButImpregnator`、`ReleasedFixedMalePrisoner`、`ReleasedPregnantFemalePrisoner`、`WantsConcubineSleepingSpotsNearby` |
| `JobDef` | 3 | `RapeConcubine`、`LiegeGetRoomService`、`VassalGiveRoomService` |
| `ThingDef` | 2 | `Apparel_Concubine_Collar`、`DoulalinkSerum` |
| `ThinkTreeDef` | 2 | `LiegeCasualSexTree`、`LiegeSexualEmergencyTree` |
| `HediffDef` | 1 | `Doulalink` |
| `LetterDef` | 1 | `success_letter` |
| `StatDef` | 1 | `MaxPersonalLieges` |
| `QuestScriptDef` | 1 | `OpportunitySite_DoulalinkStash` |

**设计上的巧思**：`MaxPersonalLieges` 是**装备的 `equippedStatOffsets`**，不是种族/派系数值 —— 也就是"戴上项圈"这个动作本身就授予"可以拥有妾侍"的能力。去掉项圈能力即消失。

### C# 侧（62 个类型，0 加载错误）

**7 个 Harmony 补丁类**（8 个类型级 `HarmonyPatch` 属性，`PeculiarComp.Patch_PawnSold` 带 2 个）：

| 补丁 | 目标 | 手法 |
|---|---|---|
| `Patch_RomanceAttempt_RandomSelectionWeight` | `InteractionWorker_RomanceAttempt.RandomSelectionWeight` | Prefix 写 `__result` 后 `return false` |
| `Patch_Breakup_RandomSelectionWeight` | `InteractionWorker_Breakup.RandomSelectionWeight` | 同上 |
| `Patch_GenGuest_AddHealthyPrisonerReleasedThoughts` | `GenGuest.AddHealthyPrisonerReleasedThoughts` | Prefix 拦截并改给自定义记忆 |
| `Patch_xxx_can_masturbate` | `xxx.can_masturbate`（RJW 的方法） | Prefix 拦截 |
| `AfterSexUtility_think_about_sex_Victim` | `AfterSexUtility.think_about_sex_Victim`（8 个显式参数类型） | Prefix 给 `AssaultedByLiege` 后 `return false` |
| `PeculiarComp.Patch_PawnSold` | `Pawn.SetFaction` | Postfix |
| `PregnancyHelperAddPregnancyHediffChange` | `PregnancyHelper.AddPregnancyHediff(Pawn, Pawn)`（Biotech） | Postfix |

引用程序集：`mscorlib`、`RJW`、`Assembly-CSharp`、`0Harmony`、`UnityEngine.CoreModule`、`UnityEngine.TextRenderingModule`、`UnityEngine.IMGUIModule`、`System.Core` —— **只用了 RJW 与原版，没有第三方 mod 的 internal 反射**。

## 它是什么 · 两个值得抄的写法

### 1. 五个 Job 类型全部派生自 RJW 已有的基类

这是本 mod 最好的设计决定：

| 本 mod 的类 | 基类（来自 RJW） |
|---|---|
| `JobDriver_LiegeGetRoomService` | `JobDriver_SexQuick` |
| `JobDriver_VassalGiveRoomService` | `JobDriver_SexBaseRecieverQuickie` |
| `JobDriver_RapeConcubine` | `JobDriver_Rape` |
| `JobGiver_LiegeSex` | `JobGiver_DoQuickie` |
| `JobGiver_RapeConcubine` | `JobGiver_ComfortPrisonerRape` |

**一个 JobDriver/JobGiver 都没从零写。** 继承 RJW 已有的基类就直接拿到完整的 toil 树、预约逻辑、路径检查与失败处理，只需要覆写自己的部分。相比之下本会话早前收录的 C0ffeeRIA 那个 mod 是自己写 `JobDriver_MassageBreasts : JobDriver`（继承 `Verse.JobDriver`）—— 差了两个量级的工作量。

### 2. RJW 的 `[StandardPreference]` 是一套干净的插件 API

`O_Dickless` 与 `R_PersonalVassal` 都继承 `rjw.Modules.Attraction.AttractionPreference`，写法完全一致：

```csharp
[StandardPreference]
public static void ApplyTo(ref AttractionRequest request)
{
    request.SetPreference(new O_Dickless());
}

public O_Dickless() : base(AttractionMode.Romantic, nameof(O_Dickless), FactorOperation.Multiply) { }

protected override float GetOperand(ref AttractionRequest request, float factor) { /* 返回 0f=完全拒绝, 1f=不变, 1.25f=加成 */ }
```

**只要写一个带 `[StandardPreference]` 的静态方法 + 继承基类 + 覆写 `GetOperand`，RJW 就会把你的偏好接进它的性吸引力计算。** 返回 `0f` 就是完全否决。

`R_PersonalVassal` 的注释还记了出处与确切 commit：

> cribbed from https://gitgud.io/amevarashi/rjw-quirks/-/blob/**93c7ae6e3457f5242abfe33e257a03fffa0baafb**/Source/RJWQuirks/Attraction/AttractionInjector.cs

### 其余框架接入点

| 类型 | 基类 | 用途 |
|---|---|---|
| `MyMapComponent` | `Verse.MapComponent` | 地图级存档数据 |
| `CompSubjectAssignableToPawn_Pawn` | `CompAssignableToPawn` | 复用原版"指派给某人"的 UI 骨架 |
| `VassalConditioning` | `ITab` | 小人信息页签 |
| `ThoughtWorker_WantsConcubineSleepingSpotsNearby` | `RimWorld.ThoughtWorker` | 4 档分级想法 |
| `TickingCache<T1,T2>` | 自写泛型 | 缓存 + 500 tick 刷新 |
| `PeculiarInstitutionMod` | `Verse.Mod` | 入口 + 设置页 |
| `PeculiarInstitutionModSettings` | `Verse.ModSettings` | 7 个乘数 |

`ThoughtWorker_WantsConcubineSleepingSpotsNearby` 的算法值得单说：`ValueOfConcubinesDesired(p)` 把 7 个设置乘数叠成"这个 pawn 想要多贵的妾侍总和"（市价 × 是否自己也是妾侍 × 贪婪特质 × 是否奴隶 × 非男性 × 期望值平方根 × 社交影响力），再拿实际拥有的妾侍市价和对比，差 750 以上就出想法；另有三档前置条件（妾侍没床 / 床距超过 30 格）。这是把 RimWorld 的期望值系统玩得很深的一例。

## 它是什么 · 查出来的问题

### 1. `Dialog_AssignPawnOwner` 的「已指派」分支调错了回调

`Source/Dialog_AssignPawnOwner.cs`：

```csharp
if (update.Value == AssignmentChangesPerThing.Unassigned) { OnRemove?.Invoke(update.Key); }
if (update.Value == AssignmentChangesPerThing.Assigned)   { OnRemove?.Invoke(update.Key); }   // ← 应为 OnSelect
```

两个分支都调 `OnRemove`，`OnSelect` 永远不会被调用。

**本 mod 自己没踩到**，因为 `PeculiarComp` 传进来的 `OnAssigned`/`OnUnassigned` 都是 `null`，实际生效的是第三个回调 `OnUIChangedThing`（`ReactToUserChanges`）——它自己根据 `AssignmentChangesPerThing` 调 `ForceAddLiegeRelationFor` / `TryRemoveLiegeRelationBetween`。所以这是**潜伏缺陷**：谁按 README 那套签名传了非 null 的 `OnAssigned`，指派路径就会静默失效。

### 2. `Apparel_Collar_Concubine_CompProperties` 把自身类型当成 `compClass`

```csharp
public Apparel_Collar_Concubine_CompProperties()
{
    this.compClass = typeof(Apparel_Collar_Concubine_CompProperties);   // ← 应为 ..._Comp
}
```

对照同项目的 `PeculiarCompProperties`，那个是对的（`compClass = typeof(PeculiarComp)`）。

**同样没被触发**：`1.6/Defs/ThingDefs/Apparel.xml` 显式写了 `<compClass>RJWPeculiarInstitution.Apparel_Collar_Concubine_Comp</compClass>`，而这个无参构造只在 XML 没给 `compClass` 时才会被调用。该类的文档注释自己也说了"这些构造函数在 XML 里设了 compClass 时不是必需的"——作者知道，但留了这行错的。

### 3. 一个永久不可见、却已被注册进所有人形小人的 ITab

`Source/VassalConditioning.cs`：

```csharp
public override bool IsVisible
{
    get { return false && Prefs.DevMode && (...); }
}
```

`IsVisible` 恒为 `false`。而 `Source/PeculiarCompPatch.cs` 仍然把 `typeof(VassalConditioning)` 注册进每个 Pawn 的 `inspectorTabs` 和 `inspectorTabsResolved`。等于说：一个 7 KB 的类（含一个完整的绘制工具 `VassalConditioningCardUtility`）被完整注册、却永远不显示。

### 4. `PeculiarCompPatch` 的嵌套循环 + 完全没有去重

```csharp
foreach (ThingDef thingDef in DefDatabase<ThingDef>.AllDefs.Where(t => t.race?.Humanlike == true && ...))
{
    if (!thingDef.comps.Any(c => c.compClass == typeof(PeculiarComp)))   // ← comp 有去重
        thingDef.comps.Add(new CompProperties(typeof(PeculiarComp)));

    foreach (ThingDef current in DefDatabase<ThingDef>.AllDefsListForReading)   // ← 内层遍历全部
    {
        if (current.thingClass == typeof(Pawn))
        {
            current.inspectorTabs.Add(typeof(VassalConditioning));              // ← tab 没有去重
            current.inspectorTabsResolved.Add(...);
        }
    }
}
```

三个问题叠在一起：

- **内层循环被外层重复执行**：外层有多少个人形种族，内层"遍历全部 ThingDef"就跑多少遍。
- **tab 被重复添加**：comp 那边写了去重检查并附注释「Check if the component to avoid duplicates」，tab 那边**一个去重检查都没有**。`VassalConditioning` 会被 `Add` 多次。
- **筛选条件不一致**：外层只给人形种族加 `PeculiarComp`，但内层用 `thingClass == typeof(Pawn)` 匹配**所有** Pawn 物种（含动物、机甲），所以 ITab 被加到了动物和机甲身上，而 comp 没有。

### 5. `PeculiarComp._relations` 是一个从不被写入的存档字典

```csharp
private Dictionary<Pawn, (PawnRelationDef, float)> _relations;                      // 声明
public (PawnRelationDef, float) this[Pawn pawn] => _relations.TryGetValue(pawn);     // 索引器
// PostExposeData:
Scribe_Collections.Look(ref _relations, nameof(_relations), LookMode.Reference, LookMode.Reference, ref pawns, ref localrelations);
```

全 mod 搜 `_relations` 只有这 3 处（声明、从不被调用的索引器、Scribe）——**没有任何一处写入**。也就是说这个字段恒为空，但它会被存进存档。加上它的值类型是 `ValueTuple (PawnRelationDef, float)`，`Scribe_Collections.Look` 对 ValueTuple 的支持面较窄，属于额外风险。

真实的关系数据存在 `Pawn.relations`（走 `PawnRelationDef`），这个字典看起来是早期"关系存在 pawn 上"设计的遗留。

### 6. `ValidationFilters.PossibleLiegePawnsFrom` 的那行过滤是彻底的 no-op

```csharp
HashSet<Pawn> possibleColonists = new HashSet<Pawn>(p.Map.mapPawns.FreeColonists);   // ← 没有过滤
possibleColonists.AddRange(possibleColonists.Where(x => IsActivePawn(x)));          // ← 把自己加回自己
```

第二行的注释说"having the IsActivePawn not applied to lieges, allows for setting lieges who may be in a container"，意图是"用 `IsActivePawn` 过滤自由殖民者，再补上已有 lieges"。但实际：

- 第一行的 `HashSet` 构造**根本没有应用 `IsActivePawn`**
- 第二行 `AddRange` 把已在集合里的元素再加一遍 → `HashSet` 去重 → **完全无效**
- 而且 `Where(x => IsActivePawn(x))` 依赖 `AcceptanceReport` 的隐式 bool 转换，可读性也差

净效果：**`IsActivePawn` 从未生效**。下游的 `CreateReportingFilterForLiegeFrom` 也只检查奴隶/成年/上限，不检查 `IsActivePawn`。因此已被停用（`IsDeactivated`）、已死或未生成的 pawn 理论上可以被选为 liege。

### 7. 一个文件的文档注释是另一个类的复制粘贴

`Source/O_Dickless.cs` 里有**两个**补丁类，第二个的 XML 文档注释是第一个的原文：

```csharp
/// <summary>
/// Patches xxx.can_masturbate and prevents males with zero genitals from masturbating (e.g. using breasts or anus)
/// </summary>
[HarmonyPatch(typeof(GenGuest), "AddHealthyPrisonerReleasedThoughts")]
public static class Patch_GenGuest_AddHealthyPrisonerReleasedThoughts
```

该类实际做的是「囚犯获释时改发自定义记忆」，与自慰毫无关系。同样，`Patch_RomanceAttempts.cs` 含 `Patch_RomanceAttempt_…` 与 `Patch_Breakup_…` 两个类，`Pregnancy_Helper_Change.cs` 含 `PregnancyHelperAddPregnancyHediffChange` 一个类但文件名对不上类名。三个文件都是"文件名只对应其中一个类"。

### 8. 代码硬依赖 Biotech，但 Biotech 只写在 `loadAfter`

| 位置 | 用到的 Biotech API |
|---|---|
| `O_Dickless.cs:106` | `prisoner.IsPregnant()` |
| `Pregnancy_Helper_Change.cs:25` | `[HarmonyPatch(typeof(PregnancyHelper), ...)]` |

`PregnancyHelper` 是 Biotech 的类型。没有 Biotech 时 Harmony 找不到补丁目标会跳过该补丁，但 `IsPregnant()` 的调用点是运行时的直接方法调用，会抛异常。而 **Biotech 既不在 `modDependencies`、也不在任何 `MayRequire` 保护里**，只在 `loadAfter` —— `loadAfter` 不产生依赖校验，所以缺 Biotech 时不会有任何提示。

### 9. 约 25 处硬编码英文 UI 字符串，且作者自己知道

| 文件 | 数量 | 例子 |
|---|---|---|
| `PeculiarInstitutionSettings.cs` | 9 | `SettingsCategory() => "Peculiar Institution"`；8 个设置页标签 |
| `ValidationFilters.cs` | 6 | `new AcceptanceReport("Slave")` / `"Non-adult"` / `"Inaccessible"` / `"Max lieges assigned"` / `"Cannot be one's own master"` |
| `PeculiarComp.cs` | 2 | `defaultLabel = "Set liege"`、`defaultDesc = "Change liege of concubine"` |
| `JobGiver_RapeConcubine.cs` | 5 | `"Failed basic concubine checks"`、`"No record"` 等 |
| `Apparel_Collar_Concubine_Comp.cs` | 2 | 在已注释的代码块里 |

作者在 `CompSubjectAssignableToPawn_Pawn.GetAssignmentGizmoLabel` 里留了注释：

> `return "Set liege";`
> // hardcode in English until we have better translation for player which can be more specific

**说明是已知且有意为之的**，不是疏忽。但因为 mod 有完整的 DefInjected（18/20 覆盖），设置页和指派界面却是英文，体验上是割裂的。

### 10. 零 Keyed 目录（这次是对的）

全 mod 只有 2 处 `.Translate()` 调用，两处用的都是**原版 key**（`MessageCantSelectDeadPawn`、`MessageCantSelectOffMapPawn`），所以没有 `Languages/<lang>/Keyed/` 是合理的。反过来说，本 mod 自己的全部 UI 文案都是硬编码（见上一条），这才是真正影响本地化的地方。

### 11. 其余工程杂项

- **版本号三处不一致**：`About.xml` 的 `modVersion` 是 `1.1.2`，DLL 的程序集版本是 `0.1.0.0`，csproj 的 `VersionPrefix` 也是 `0.1.0.0`。
- **`Apparel_Concubine_Collar` 的 `ParentName` 是 `HatMakeableBase`**（帽子基类），但它的 `bodyPartGroups` 是 `Neck`（颈圈）。可能是为了拿到 `HatMakeableBase` 附带的 crafting `recipeMaker` 而故意借用的基类，但读起来像失误。
- **`CompSubjectAssignableToPawn_Pawn.CompGetGizmosExtra` 整段是 `if (false && ...)`**，纯死代码。
- **`MyMapComponent` 是空类**（只有构造函数）。
- **`Patch_RomanceAttempt` 用字符串字面量 `"Masochist"` 而不是 `TraitDefOf.Masochist`**（`AfterSexUtilityChange.cs`）。
- **`Pregnancy_Helper_Change` 在静态字段初始化器里 `DefDatabase<ThoughtDef>.GetNamed(...)`**，而同一个 mod 里另有规范的 `[DefOf]` 类 —— 两种写法并存，前者依赖类型初始化时机，更脆。
- **模板残留的 using**：`System.Security.Policy`、`Unity.Jobs`、`System.EnterpriseServices`、`System.Drawing.Printing`、`System.Runtime.InteropServices`、`System.Runtime.Remoting.Messaging`、`LudeonTK`。
- **`csproj` 的引用很脆**：`<Reference Include="$(RimWorldPath)/*.dll">` 通配整个 Managed；另有两个**写死 `RimWorldLinux_Data`** 的引用（`UnityEngine.dll`、`Assembly-CSharp.dll`），在 Windows 上必然失效 —— 作者自己注为「redundant load of Rimworld .NET Assembly just in case」；RJW 指向 `../../../Mods/rjw/1.6/Assemblies/*.dll`（README 已说明 rjw 必须在相邻位置）。`RimWorldPath` 属性算了 Windows/Linux 两套，但只被那个通配引用用到。
- **`incompatibleWith` 留着模板注释** `<!-- <li>username.modname</li> -->`。

## 怎么验的

### ① 核验方法（可复现）

| 目标 | 方法 |
|---|---|
| 规模 / 体积 | `Get-ChildItem -Recurse -File` + `[System.IO.File]::ReadAllBytes().Length`，按扩展名汇总 |
| Def 全量清点 | Python + ElementTree，脚本 `F:\temp\pi_defs.py` |
| 翻译覆盖 | 同脚本，按 defName 求交，**同时单独列出「翻译了但无对应 Def」的孤儿键** |
| DLL 反射 | 预载游戏 Managed + `0Harmony.dll` + **`RJW.dll`**（第三个必需），再 `GetTypes()` 吃 `ReflectionTypeLoadException.Types`；类型表含 `GetNestedTypes()` |
| 「孤儿字段」判定 | `grep` 工具搜字段名在 `.cs` 里的**全部出现位置**，逐条判断是声明/读取/写入 |
| 依赖装况 | 逐个 `About.xml` 直系子元素查 packageId，**同时扫 `Mods/` 与 `Data/`**（官方 DLC 在后者） |
| 硬编码 UI 字符串 | `grep` 正则匹配 `defaultLabel = "`、`defaultDesc = "`、`new AcceptanceReport("`、`SettingsCategory() => "`、`listingStandard.Label($"` |
| Biotech 依赖 | `grep` 搜 `IsPregnant|PregnancyHelper` 在源码里的出现 |

### ② 阳性对照

| 结论 | 对照 | 结果 |
|---|---|---|
| 依赖装况表可信 | `readyforjeff.RJWPeculiarInstitution` 自身必须被扫到 | PASS ✅ |
| DLC 未被误报 | 官方 DLC 的 packageId 在 `Data/<DLC>/`，必须能查到 `Ludeon.RimWorld.Ideology` 等 | 3 个 DLC 全 INSTALLED ✅ |
| 翻译覆盖可信 | DefInjected 条目数必须 > 0，且孤儿键必须为 0 | 41 条目 / 0 孤儿 ✅ |
| 反射类型表完整 | 必须 0 loader error，且正控 `HarmonyLib.HarmonyPatch` 可解析 | 62 类型 / 0 error / `True` ✅ |
| `_relations` 是死字段 | 搜出全部出现位置应为「声明 + 未被调用的索引器 + Scribe」三类，且**无任何写入** | 正好 3 处 ✅ |
| 无 Keyed 目录是合理的 | 全 mod `.Translate()` 调用数必须极少且用的都是原版 key | 2 处，均为原版 key ✅ |
| 读文件路径 | 目录名含中文与全角括号，外层一律 `-LiteralPath` | 无路径错误 ✅ |

### ③ 自查纠错（本轮 1 次）

**反射首轮报 7 个 loader error 和一串 MISSING，是我的探针环境问题。** `_sdb_attr.ps1` 只预载了游戏 Managed 与 `0Harmony.dll`，**没预载 `RJW.dll`** —— 而这个 DLL 的 REF 列表里就有 RJW，于是依赖它的类型加载失败。改用传参版脚本显式预载 `RJW.dll` 后：**62 类型、0 loader error**，`HarmonyLib.HarmonyPatch` 正控同时恢复可解析。

这条与上一轮收录 Cumpilation 时踩的是同一个坑（本机 3 个 mod 连续反射都依赖 RJW），差别只在于当时我已经在「预载清单」里写了 RJW，这次换了脚本就忘了。**凡是要反射的 DLL 的 REF 列表里出现过 mod 程序集，预载清单就必须包含那个 mod 的对应版本目录下的 DLL**（同名的还要选对版本 —— 本机 RJW 有 1.1/1.2/1.3/1.4/1.5/1.6 六份 `RJW.dll`，版本号各不相同）。

## 可复用结论

1. **接第三方 mod 的 Job 系统，能派生就别重写。** 本 mod 5 个 JobDriver/JobGiver 全部派生自 RJW 已有基类（`JobDriver_SexQuick`、`JobDriver_Rape`、`JobGiver_DoQuickie`、`JobGiver_ComfortPrisonerRape`），继承即获得完整 toil 树、预约与路径检查。**审 mod 时看到一堆 `JobDriver_… : JobDriver`（直接继承 Verse 基类）要留个心，那通常意味着作者把上游已经做好的事重写了一遍。**

2. **留意上游有没有「插件式 API」**。RJW 的 `[StandardPreference]` + `AttractionPreference` 是一套完整的注册机制：写一个带特性标注的静态 `ApplyTo(ref AttractionRequest)`、构造函数 `base(AttractionMode.X, nameof(Y), FactorOperation.Z)`、覆写 `GetOperand` 返回 0/1/1.25 这类乘数。**找这种「三个方法就能接入」的扩展点，比自己写补丁划算得多。**

3. **`AcceptanceReport` 的隐式 bool 转换很容易被误读。** `Where(x => IsActivePawn(x))` 里的 `IsActivePawn` 返回 `AcceptanceReport` 而非 `bool`，靠隐式转换才编译通过；结果又恰好是个 no-op，于是「这行在过滤什么」变得难以判断。**写 LINQ 过滤时若谓词返回非 bool 类型，读代码的人要多花一层。**

4. **往 `List` 里 `AddRange` 自己过滤出来的同一批元素是典型 no-op**，因为 `HashSet`/`List` 的去重或元素已在集合内。若这行的注释描述了一个明确意图（"过滤 X 再补 Y"），而代码第一行就没过滤，**注释与实现不符往往比 bug 更隐蔽** —— 运行时看不出任何异常，只是行为和设计意图不一致。

5. **`[StaticConstructorOnStartup]` 里遍历 `DefDatabase<ThingDef>.AllDefs` 时要特别小心嵌套循环与去重。** 本 mod 的外层（所有人形种族）套内层（全部 ThingDef），内层跑 N 遍；且 comp 那侧写了去重（还带注释说明），tab 那侧没有 —— **同一段代码里两个相邻操作一个有去重一个没有，是很容易发生的不一致**。另外 `inspectorTabsResolved` 是游戏自己解析出来的缓存，手动往里塞等于绕过了解析流程。

6. **`About.xml` 写了 `<url>` 才能追溯上游；只有 README 提到模板不算。** 本 mod 的 About.xml 无 `<url>`，README 也只说基于 RimWorld Mod Template，**没有可点击的源码仓库地址**。相比之下 C0ffeeRIA 在 About.xml、Manifest.xml、README 三处都给了 GitHub/gitgud 地址。对收录来说差别很明显：**没有仓库地址，就只能分析随包源码，无法追后续更新**。

7. **README 里记录「锁定依赖的具体 commit」是高价值习惯。** 本 mod 写明 `Built from rjw SHA dcc2c843`，并记录了 `dotnet --version`（8.0.407）。这让"上游 RJW 变了以后这个 mod 还对不对"有了可核对的具体坐标 —— 比我本会话多次遇到"REF 列表里的版本号对不上本机实际安装版本"要好查得多。

8. **`PatchAll(Assembly.GetExecutingAssembly())` 比裸 `PatchAll()` 更稳妥。** 本 mod 的 `Start` 静态构造用前者限定补丁扫描范围，避免扫到引用的第三方程序集里的 `[HarmonyPatch]`。

9. **反射要预载的不只是游戏 DLL，还有目标程序集 REF 列表里的第三方 mod DLL。** 本机连续三个 RJW 相关 mod 都因此踩坑（Harmony 不在游戏 Managed 目录里、RJW 在 mod 目录里且有六个版本）。**预载清单 = 游戏 Managed 全部 + Harmony 官方 + 目标 REF 列表里的每个第三方程序集（且要选对版本）**，并用「正控类型能否解析」当自检。

10. **一件装备的 `equippedStatOffsets` 可以承载"解锁能力"的语义。** 把 `MaxPersonalLieges: 1.0` 挂在项圈的 `equippedStatOffsets` 上，意味着"戴上项圈"这个动作本身就授予能力，脱下即失效。**比用一个全局 StatDef 加条件判断干净得多**，而且天然和物品的获取/生产链绑定。

## 修改建议

> 以下全部**未执行**。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。

| 优先级 | 事项 | 依据 |
|---|---|---|
| **P0** | 修 `Dialog_AssignPawnOwner`：`Assigned` 分支应调 `OnSelect` 而非 `OnRemove` | 两个分支都调 `OnRemove`，`OnSelect` 永不被调用；本 mod 因传 null 而掩盖 |
| **P0** | 把 `Ludeon.RimWorld.Biotech` 加进 `modDependencies` | 代码用了 `Pawn.IsPregnant()` 与 `PregnancyHelper.AddPregnancyHediff`，Biotech 只在 `loadAfter`，缺了不报错 |
| **P1** | `PeculiarCompPatch` 给 tab 加去重（对齐 comp 那侧已有的检查），并把内层循环提到外层之外 | tab 被重复 Add；内层遍历全部 ThingDef 被重复执行 N 遍 |
| **P1** | 内层的 `thingClass == typeof(Pawn)` 与外层的 `race.Humanlike` 对齐 | 现在 ITab 被加到动物/机甲上，而 comp 只给人形 |
| **P1** | 删掉 `PeculiarComp._relations`（及索引器与 `PostExposeData` 里那行 Scribe） | 全 mod 无任何写入，恒为空却会被存进存档；值类型还是 ValueTuple |
| **P1** | 修 `ValidationFilters.PossibleLiegePawnsFrom`：要么按注释的意图在第一行应用 `IsActivePawn` 再补 lieges，要么删掉那行无效的 `AddRange` | 第二行是彻底 no-op，`IsActivePawn` 实际从未生效 |
| **P2** | 决定 `VassalConditioning` 的去留：删掉整个 ITab（含 `VassalConditioningCardUtility`）与 `PeculiarCompPatch` 里的注册代码，或把 `IsVisible` 的 `false &&` 去掉并加上注释说明是调试功能 | `IsVisible` 恒 false，却已注册进所有人形小人的 `inspectorTabs` |
| **P2** | 修 `Apparel_Collar_Concubine_CompProperties()` 的 `compClass` | 现在指向自身类型；靠 XML 显式指定才没触发 |
| **P2** | 给约 25 处硬编码英文加 `.Translate()` 并建 `Languages/<lang>/Keyed/` | 设置页与指派界面目前全英文，与已完整本地化的 Def 内容割裂 |
| **P2** | `AfterSexUtilityChange.cs` 的 `"Masochist"` 换成 `TraitDefOf.Masochist`；`Pregnancy_Helper_Change` 的静态 `GetNamed` 换成本 mod 已有的 `[DefOf]` 风格 | 字面量与易脆初始化时机，两处都有更规范的写法现成 |
| **P3** | `About.xml` 补 `<url>` 指向源码仓库；补 `modVersion` 与 csproj `VersionPrefix` 的一致性说明；删掉 `incompatibleWith` 里的模板注释 | 三处小问题 |
| **P3** | 修 `O_Dickless.cs` 中 `Patch_GenGuest_…` 的复制粘贴文档注释；把三个「一文件两类」的文件拆开或改名 | 注释与实际功能完全无关 |
| **P3** | 清理模板残留 using（`System.Security.Policy`、`Unity.Jobs`、`System.EnterpriseServices`、`System.Drawing.Printing`、`System.Runtime.InteropServices`、`System.Runtime.Remoting.Messaging`、`LudeonTK`）；删除 `CompSubjectAssignableToPawn_Pawn.CompGetGizmosExtra` 的 `if (false && …)`；`Apparel_Concubine_Collar` 的 `HatMakeableBase` 换注释说明 | 均为整理项 |

## 未核实项

- **代码逻辑未逐行验证**。本轮读完了 21 个 `.cs`，但没有反编译 IL，`ReactToPawnFactionChange` 里 `!(p.Dead && p.Faction != Faction.OfPlayer)` 这类复合条件的实际语义、`JobGiver_LiegeSex`（8,508 B）与 `JobGiver_RapeConcubine`（8,724 B）两个最大的 JobGiver 的完整判定链都未逐行核实。
- **`AttractionPreference` 的确切归属未确认**。它来自 `rjw.Modules.Attraction` 命名空间（反射确认命名空间），但 `AttractionRequest.SetPreference` / `FactorOperation` 的完整语义没读。
- **README 提到的 rjw SHA `dcc2c843` 与本机安装的 RJW 是否对应未核**。本机 RJW 1.6 的 DLL 版本是 `1.6.9576.22392`，但没有 git 信息可比对 commit。
- **DLL 是否与当前源码同步未核**。62 个类型里包含源码全部的类名，看起来不陈旧；但 `modVersion 1.1.2` vs 程序集 `0.1.0.0` 的版本号不一致，无法据此判断构建时间。
- **`OpportunitySite_DoulalinkStash`（7,715 B 的 `QuestScriptDef`）与 `Doulalink` / `DoulalinkSerum` 这条任务链的完整流程未读**，只确认它们是 Def 且已被 DefInjected 覆盖。
- **本 mod 未在 1.6 实机加载验证。** 尤其 `PeculiarCompPatch` 是否真的产生重复 ITab、以及 `VassalConditioning` 是否真的不显示，都只有静态推断。
- **素材授权**：`Apparel_Concubine_Collar` 复用原版 Ideology 的 `SlaveCollar` 贴图（原版素材受 Ludeon 条款约束，随包未附带任何贴图文件，所以这个 mod 本身不涉及第三方美术授权）。
