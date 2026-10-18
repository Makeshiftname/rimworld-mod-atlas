# C0ffeeRIA（C0ffee's RJW Ideology Addons） — 分析记录

## 身份卡

| 项 | 值 |
|---|---|
| 名字 | `C0ffeeRIA`（描述里叫「C0ffee的RJW意识形态扩展模组」） |
| packageId | `c0ffee.rjw.IdeologyAddons` |
| 作者 | `C0ffee`（`About.xml` 写 `<author>` 单数） |
| 源目录 | `F:\Games\GBL\rimworld\Mods\RJW_文化_咖啡的人奶文化` |
| 上游 | <https://gitgud.io/c0ffeeeeeeee/coffees-rjw-ideology-addons>（GitLab，非 GitHub；仓库里带 `.gitignore` / `.gitattributes`，是完整开发树直接发布） |
| 授权 | **无**。无 `LICENSE`、无 `README`、无 `<url>` 之外的法律声明 |
| 版本 | `About/Manifest.xml` 写 **0.0.6**；`About.xml` **无 `modVersion`** |
| 规模 | **105 文件 / 3,170,856 bytes（3.02 MB）** |
| 类型 | **随包完整 C# 源码的多程序集功能 mod**（3 个 csproj / 1 个 sln / 9 个预编译 DLL） |
| 声明支持版本 | `1.3` `1.4` `1.5` `1.6`（`LoadFolders.xml` 四组对应） |
| 硬依赖 | `brrainz.harmony` + `rim.job.world`（`modDependencies` 两条） |
| `loadAfter`（8 项） | `UnlimitedHugs.HugsLib`、`brrainz.harmony`、`erdelf.HumanoidAlienRaces`、`nals.FacialAnimation`、`rim.job.world`、`shauaputa.RimNudeWorld`、`abraxas.rjw.RaceSupport`、`akaster.equalmilking` |
| 核验深度 | **② 档**（单一 mod，但随包源码 → 结论基于**真实源码**而非 IL 推断；另加跨版本 DLL 演进对比与依赖装况核验） |

### 体积分解

| 项 | 字节 | 占比 |
|---|---|---|
| `About/Preview.png` | 2,558,722 | **80.7%** |
| `About/Preview.jpg` | 221,232 | 7.0% |
| 全部 9 个 DLL | 161,664 | 5.1% |
| 其余（源码 / Def / 贴图 / 工程文件） | 约 229,238 | 7.2% |

**80.7% 的体积是一张预览图。** 代码 + Def + 贴图加起来不到 240 KB。

### 三程序集 × 四版本

| 程序集 | 工程 | 1.3 | 1.4 | 1.5 | 1.6 |
|---|---|---|---|---|---|
| `C0ffee's RJW Ideology Addons` | 根 csproj | — | — | — | **12,800 B** |
| `CRIALactation` | `CRIALactation/CRIALactation.csproj` | 25,088 B | 24,064 B | 23,552 B | **24,576 B** |
| `CRIAOrgy` | `CRIAOrgy/CRIAOrgy.csproj` | 5,120 B | 5,120 B | 5,120 B | **5,120 B** |

九份 SHA256 前 16 位**两两不同**，所以不是同一二进制复制；`CRIAOrgy` 四份大小相同但哈希不同。

## 它是什么

给 RimJobWorld 的 Ideology 文化系统加两套可玩内容：**一套「人乳」信仰体系**（`CRIALactation`，条件加载）和**一套「群交」仪式**（`CRIAOrgy`，条件加载）；主程序集本身做的是**给 RJW 的性行为加 Ideology 意愿门控**。

**全部 36 个具体 Def**（`CRIALactation/Defs` + `CRIAOrgy/Defs`，不含抽象父）：

| 类型 | 数量 | 代表 |
|---|---|---|
| `ThoughtDef` | 16 | 两个 precept 各配 1 个处境想法 + 1 个社交想法 + 4 个记忆想法；群交 4 个 `Thought_AttendedRitual` |
| `HistoryEventDef` | 3 | `DrankMilkRaw` / `DrankMilkMeal` / `DrankNonMilkMeal` |
| `PreceptDef` | 2 | `Lactating_Essential`、`Lactating_MandatoryHucow`、`IdeoRole_HucowHandler`（后者在 CRIAOrgy 之外，属 Lactation） |
| `IssueDef` | 2 | `Lactating`、`HucowHandling` |
| `SpecialThingFilterDef` | 2 | `AllowWithHumanMilk` / `AllowWithoutHumanMilk` |
| `AbilityDef` | 2 | `ConvertToHucow`（CD 30000 tick）、`BeginInducingLactation`（CD 3000 tick） |
| `HediffDef` | 2 | `Hucow`、`InducingLactationCooldown`（`InducingLactation` 也是，见下） |
| `StatDef` | 2 | `MilkProductionSpeed`、`MilkProductionYield` |
| `MemeDef` / `MemeGroupDef` | 1 / 1 | `Hucow` + 重定义原版 `Sexuality` 分组 |
| `RitualBehaviorDef` / `RitualOutcomeEffectDef` | 1 / 1 | `FertilityRitual`（10000 tick）+ 4 档结果（0.05/0.15/0.6/0.2，合计 1.0 ✓） |
| `WorkGiverDef` | 1 | `MassageBreasts`（`workType=Handling`，`priorityInType=91`，需 `Manipulation`） |

### 主程序集：给 RJW 加 Ideology 意愿门控

源码 `Source/Base/`，5 个编译单元（其中一个整体注释掉）：

1. **`CRIAUtility.TwoPawnsWillingToHaveSex(doer, target)`** —— 意愿判定核心。依次放行：自己（自慰）、`DesignatorsData.rjwComfort` 里被指定的、`IsSlaveOfColony`/`IsPrisonerOfColony`、`PawnsAreDesperate`（frustrated）；否则要求双方 `IdeoUtility.DoerWillingToDo`，并按 `Spouse` 关系分 `SharedBed_Spouse` / `SharedBed_NonSpouse` 两档。
2. **`HarmonyPatch_JobDriver_SexBaseInitiator`**（`[HarmonyPatch(typeof(...))]` + 方法级 `[HarmonyPatch(nameof(Start), HarmonyPrefix)]` / `End`）——记录 `InitiatedLovin` / `GotLovin` / `GotLovin_Spouse` / `GotLovin_NonSpouse` 历史事件；显式排除 `JobDriver_Rape` 与 mechanoid。
3. **`HarmonyPatch_CasualSex_Helper`** —— **Transpiler**，把原方法里对 `CasualSex_Helper.HookupAllowedViaSettings` 的 `call` 指令**整条替换**成自己的 `HookupAllowed`，后者再回调原方法，构成 AND 门（不是绕过）。
4. **`HarmonyPatch_RMB_Menu`** —— `[StaticConstructorOnStartup]`，手动 `new Harmony("C0ffeeRIA").PatchAll()` 之后**再单独 `Patch()`** `RMB_Menu.GetOptionsForTarget` 的 postfix，把不满足意愿的选项标签追加 `" (sinful)"`。
5. **`SoftDependencyChecker`** —— **整份被 `/* removed because not working */` 注释掉**，但 csproj 仍保留 `<Compile Include>`。

### CRIALactation：人乳体系（35+ 类型）

- **质量/产量 Stat**：`MilkProductionSpeed`、`MilkProductionYield`，`Hucow` hediff 给 ×1.5 / ×2.5，代价 `WorkSpeedGlobal 0.7` + `MoveSpeed 0.7`。
- **催乳链路**：`BeginInducingLactation` 技能给 `InducingLactation` hediff（`initialSeverity 0.01`）→ `WorkGiver_MassageBreasts`（Handling 工作）→ `JobDriver_MassageBreasts` 每次完成把 severity 加 `1 / totalMassagesUntilLactation` → 满 1 时 `StartLactating` 并移除催乳 hediff → 追加 `InducingLactationCooldown`（`severityPerDay -1`，初始 severity = `LactationSettings.massageCooldown`，即**冷却时长以天计**）。
- **`ConvertToHucow` 技能**：校验用 RJW 的 `AbilityUtility.ValidateMustBeHuman/NoMentalState/SameIdeo`，再要求已催乳且非 hucow；`Apply` 里调 `ExtendLactationDuration`（同时兼顾 Biotech 原版 `Lactating` hediff）并按 `hucowBreastSizeBonus/Minimum` 调整 `Hediff_NaturalSexPart` 尺寸。
- **`HarmonyPatch_FoodUtility`** —— 本 mod 技术含量最高的一块：
  - `AddThoughtsFromIdeo_Patch` 用 **`[HarmonyReversePatch(HarmonyReversePatchType.Snapshot)]`**：在打补丁的瞬间快照原方法体，之后可以当普通方法调用原逻辑。这是 Harmony 里"把原方法变成可调用函数"的标准手法。
  - 三个 postfix 分别拦 `ThoughtsFromIngesting`、`AddIngestThoughtsFromIngredient`、`GenerateGoodIngredients`，把饮食行为记成 Ideology 历史事件，并让"人乳"成为生成好饭的成分。
- **Precept 体系**：`Lactating_Essential`（5 档想法 +7/+3/−2/−5/−8）与 `Lactating_MandatoryHucow`（同构）；`PreceptComp_Lactation.Notify_MemberGenerated` 让新生成的成员**自动开始泌乳**；`IdeoRole_HucowHandler` 角色要求 `Animals` 技能 6 + 头巾/兜帽/长袍/帽等 6 条着装要求，并授予两个技能。
- **食物过滤器**：`AllowWithHumanMilk` / `AllowWithoutHumanMilk`，通过 `CompIngredients.ingredients` 判断是否含 `EM_HumanMilk`。

### CRIAOrgy：群交仪式（1 个类型）

`RitualOutcomeEffectWorker_Orgy : RitualOutcomeEffectWorker_FromQuality`，`Apply` 里对每个参与者调 `Notify_OutfitChanged()` + `GlobalTextureAtlasManager.TryMarkPawnFrameSetDirty()` + `renderTree.SetDirty()`，再 `base.Apply`。

## 跨版本工程：条件加载是这套 mod 的核心机制

`LoadFolders.xml` 用了 RimWorld 的 **`IfModActive=` 条件条目**（`Verse.LoadFolder` 的 `requiredAnyOfPackageIds` / `ShouldLoad` 就是这个）：

```
v1.3 / v1.4 :  /  +  1.x  +  [IfModActive="rjw.milk.humanoid"]     CRIALactation(+ /1.x)
                         +  [IfModActive="c0ffee.rjw.events"]      CRIAOrgy(+ /1.x)
v1.5 / v1.6 :  /  +  1.x  +  [IfModActive="akaster.equalmilking"]  CRIALactation(+ /1.x)
                         +  [IfModActive="c0ffee.rjw.events"]      CRIAOrgy(+ /1.x)
```

**CRIALactation 的门槛依赖在 1.4→1.5 之间换了 mod**（`rjw.milk.humanoid` → `akaster.equalmilking`）。这与 DLL 的 REF 列表完全对应：

| 版本 | Harmony 属性 | 额外引用程序集 |
|---|---|---|
| 1.3 | **10** | `HugsLib`、**`Milk`** |
| 1.4 | 7 | **`Milk`** |
| 1.5 | 7 | **`EqualMilking`** |
| 1.6 | 7 | **`EqualMilking`** |

`Milk` → `EqualMilking` 的切换点与 LoadFolders 条件切换点完全重合，说明这不是巧合而是同一件事的两面（换了上游产奶 mod，编译引用跟着换）。

**1.3 的 DLL 里还留着 3 个当前源码中已被注释掉的 Harmony 补丁**：`HarmonyPatch_Milk_HumanCompHasGatherableBodyResource`、`HarmonyPatch_IncreaseYieldForHucowHyperMilkable`、`HarmonyPatch_IncreaseYieldForHucowMilkable`。也就是说**这三个补丁在 1.3 下仍然实际生效**，而在 1.4+ 消失——版本之间的功能差异比目录结构看起来更大。

⚠️ **1.3 引用 `HugsLib`，但它只在 `loadAfter` 里、不在 `modDependencies` 里。**

### 构建方式值得抄

两个 csproj 都用**编译配置决定输出目录**：

- `Debug` → `OutputPath = 1.5\Assemblies\`
- `Release` → `OutputPath = 1.6\Assemblies\`

配合 `<AssemblyName>C0ffee%27s RJW Ideology Addons</AssemblyName>`（**URL 编码的撇号**）让产物文件名带 `'`，以及三个项目全部开启 `<Publicize>`：

```xml
<Publicize Include="RJW" IncludeVirtualMembers="false" />
<Publicize Include="Assembly-CSharp" IncludeVirtualMembers="false" />
```

配合 `packages.config` 里的 **Krafs.Publicizer 2.3.0**（NuGet）——这让代码能直接访问 RJW 与 Assembly-CSharp 的 internal/private 成员，而不需要自己写 `AccessTools` 反射。这是**编译期**手段，与 Harmony 运行期补丁互补。`CRIALactation` 额外引用了 `EqualMilking.dll` 与 `RJW.dll`，两者都 `<Private>False</Private>`（不复制到输出，符合 mod 开发惯例）。

两个项目的 `TargetFrameworkVersion` 还不一致：主项目 `v4.8`，`CRIALactation` 是 `v4.8.1`。

## 它是什么 · 查出来的问题

### 1. 本机当前状态：CRIALactation 完全不加载

条件依赖装况（按 XML 直系子元素核 `packageId`，正控 `c0ffee.rjw.IdeologyAddons` 自身必须命中）：

| packageId | 状态 |
|---|---|
| `brrainz.harmony` | ✅ INSTALLED（`2009463077`） |
| `rim.job.world` | ✅ INSTALLED |
| `UnlimitedHugs.HugsLib` | ✅ INSTALLED（`818773962`） |
| `erdelf.HumanoidAlienRaces` | ✅ INSTALLED（`839005762`） |
| `nals.FacialAnimation` | ✅ INSTALLED（真实大小写是 **`Nals.FacialAnimation`**，模组写全小写 —— RimWorld 匹配 packageId 大小写不敏感，无问题） |
| `c0ffee.rjw.events` | ✅ INSTALLED |
| **`shauaputa.RimNudeWorld`** | ❌ 未装 |
| **`abraxas.rjw.RaceSupport`** | ❌ 未装 |
| **`akaster.equalmilking`** | ❌ **未装** |
| **`rjw.milk.humanoid`** | ❌ 未装 |

所以在 1.6 下：**主程序集与 `CRIAOrgy` 会加载；`CRIALactation` 的 Def 与 DLL 都不会加载**（门槛依赖 `akaster.equalmilking` 未满足）。

而 **`akaster.equalmilking` 只写在 `loadAfter`、不在 `modDependencies`** —— 游戏不会给任何"缺少依赖"的提示，`CRIALactation` 就是安静地消失。`rjw.milk.humanoid` 连 `loadAfter` 都没有。这是本 mod 最实际的一个使用陷阱。

### 2. `CRIAOrgy` 的中文翻译放错了层级

mod 内有两棵 `ChineseSimplified`：

| 位置 | 条目 | 形态 |
|---|---|---|
| `Languages/ChineseSimplified/` | **111** | ✅ 标准形态（根目录，RimWorld 原生可读） |
| `CRIAOrgy/ChineseSimplified/DefInjected/` | 24 | ❌ **少了 `Languages/` 这一层** |

同一个 mod 里的 `CRIALactation` 就写对了：`CRIALactation/1.4|Languages/English/Keyed/`。RimWorld 对 LoadFolders 条目按 `<loadFolder>/Languages/<lang>/` 找翻译，`CRIAOrgy/ChineseSimplified/` 匹配不上 → **这 24 条翻译极可能从不生效**（`CRIAOrgy/Defs` 本身能正常加载，因为 LoadFolders 会把 `CRIAOrgy` 当作内容根）。

按 `Languages/` 那棵单独统计，有 **8 个 Def 完全没有中文**：`BoringOrgy`、`FertilityRitual`、`FertilityRitualOutcome`、`FunOrgy`、`OrgyCeremony`、`Sexuality`、`TerribleOrgy`、`UnforgettableOrgy`——其中 6 个正好是放错那棵树想覆盖的。

顺带一个整理问题：放错那棵的 `RitualOutcomeEffectDef/AutoTranslated_Defs.xml` 里混进了 `spectatorsLabel` / `spectatorGerund` / `defaultDuty`（**`RitualBehaviorDef`** 的字段）和 `participant_count.label` / `room_impressiveness.label`（outcome comp 的字段）。DefInjected 的文件夹名只是装饰（Def 类型取自元素名），所以能生效，但组织上很随意。

### 3. 4 个类已成孤儿 / 4 个文件是死代码

| 类 / 文件 | 状态 | 依据 |
|---|---|---|
| `RoleRequirement_Lactating` | **孤儿** | 唯一引用在 `Precepts_Lactating_Role.xml:11`，而那一整段在 `<!-- -->` 里 |
| `RoleEffect_Hucow` | **孤儿** | 唯一引用在 `Precepts_Lactating_Role.xml:17`，同样在注释块里 |
| `HediffComp_LactationInduction` | **死代码** | 整份注释；引用只在两处行尾注释里 |
| `HediffCompProperties_LactationInduction` | **死代码** | 整份注释；XML 里对应 `<li>` 也被注释 |
| `SoftDependencyChecker.cs` | **死代码** | 整份注释（`removed because not working`），csproj 仍 `<Compile>` |
| `HarmonyPatch_Ideo.cs` | **死代码** | 整份 `/** //to be implemented next update **/`，csproj 仍 `<Compile>` |
| `HarmonyPatch_Milk_HumanCompHasGatherableBodyResource.cs` | **死代码（1.6）/ 仍生效（1.3）** | 源码全注释，但 1.3 的 DLL 里还在 |
| `CRIALactation/UI/*.png` | **死文件（57,695 B）** | 路径缺 `Textures/` 层，游戏读不到；且与根 `Textures/UI/` 下同名文件**内容不同**（sha `12C7F9B5…` vs `B52E29DD…`、`D24486E0…` vs `880EE573…`），是旧版开发素材 |

另外 `LactationSettings` 里 `height_modifier = 300f` 给滚动区预留了 300 px 的"隐藏选项"空间，但界面上并没有隐藏选项；`CompProperties_Lactation` 与 `HediffComp_LactationInduction` 的字段全被注释。都是重构后的残留。

### 4. `JobDefOf` 静态构造指错了类

`Source/JobDefOf/JobDefOf_CRIALactation.cs`：

```csharp
static JobDefOf_CRIALactation()
{
    DefOfHelper.EnsureInitializedInCtor(typeof(HediffDefOf_Milk));   // ← 应该是 typeof(JobDefOf_CRIALactation)
}
```

从 `HediffDefOf_Milk.cs` 复制粘贴漏改。同文件里其他 5 个 `[DefOf]` 类都写对了自己。后果取决于 `EnsureInitializedInCtor` 的实现（未反编译），但**意图明确是笔误**。

### 5. 三处硬编码英文，不可翻译

| 位置 | 字符串 |
|---|---|
| `HarmonyPatch_RMB_Menu.ModifyOptionLabels` | `" (sinful)"` |
| `RoleEffect_Hucow.Label` | `"Greatly increased milk yield, permenant lactation, slower speed"`（原文还有拼写错 `permenent`） |
| `RoleRequirement_Lactating.GetLabel` | `"must be lactating"` |
| `CompLactation.CompInspectStringExtra` | `"Ready to stimulate breasts for lactation."` |

四者都没有 `.Translate()`，而 mod 本身有 9 条 Keyed 译文和完整的中文 DefInjected，说明作者知道怎么本地化——这四处是漏了。

### 6. 三处健壮性隐患（未实机验证）

- **`CompAbilityEffect_ConvertHucow.Apply`**：`breasts.TryGetComp<HediffComp_SexPart>()` 之后**直接 `comp.SetSeverity(...)`**，没有 null 检查。
- **`HarmonyPatch_FoodUtility` 的 `GenerateGoodIngredients` postfix**：`meal.TryGetComp<CompIngredients>()` 后直接 `compIngredients.ingredients.Add(...)`，comp 为 null 会 NRE；且**每次调用都 Add**，重复调用会累积重复项。
- **`WorkGiver_MassageBreasts`**：`PotentialWorkThingsGlobal` 与 `ShouldSkip` 都直接 `pawn.Map.mapPawns`，`pawn.Map` 为 null（在商队/世界层）会 NRE；且 `ShouldSkip` 每次都对全图 pawn 线性扫描。
- **`ThoughtWorker_Precept_NoRecentHumanMilk`**：`p.TryGetComp<CompLactation>().lastHumanLactationIngestedTick` 无 null 检查——不过 `Patch_LactationInduction.xml` 给 `BasePawn` 挂了 `CompProperties_Lactation`，**所有 pawn 种族都有这个 comp**，所以实际大概率安全。

### 7. 工程杂项

- `0Harmony` 的 HintPath 指向 `Mods\2009463077\**1.5**\Assemblies\0Harmony.dll`——即使编译 1.6 版本也指向 1.5 的 Harmony。
- 所有 HintPath 硬编码作者本机的 `C:\RimWorld\...`；`RJW.dll` 用相对路径 `..\rjw\1.6\Assemblies\RJW.dll`，要求 mod 与一个名为 `rjw` 的目录同级。
- `CRIALactation.csproj` 有 `<Folder Include="Defs\Thingdef\" />`（空文件夹声明），实际既无该目录也无对应 Content 条目。
- `Precepts_Lactating_Role.xml` 里重定义了 `MemeGroupDef Sexuality`（`maxRows 1`、自定义 `drawOffset`）——原版已有的分组被 mod 覆盖，`Hucow` meme 因此出现在"性取向"一栏。
- `roleApparelRequirementCountCurve` 的两点是 `(0, 1)` 与 `(1, 1)`，曲线恒为 1，看起来是退化写法。
- `ThoughtWorker_Precept_NoRecentHumanMilk` 里 `MinDaysSinceLastHumanMeatForThought = 8` 只是给描述做占位符，实际比较用的是硬编码的 `480000`；改常量不会有任何效果。
- `About.xml` 写 `<supportedVersions>` 1.3–1.6，但 `Manifest.xml` 版本 `0.0.6`、无 `modVersion`——工坊页看不出版本。

## 怎么验的

### ① 核验方法（可复现）

| 目标 | 方法 |
|---|---|
| 规模 / 字节 | `Get-ChildItem -Recurse -File` + `[System.IO.File]::ReadAllBytes().Length` |
| 源码分析 | **直接读随包 `.cs`（45 个文件全部读完）**，不依赖 IL 推断 |
| DLL 演进 | 9 个 DLL 各自**独立进程**反射（同名程序集跨版本不能同 AppDomain），脚本 `F:\temp\_sdb_attr.ps1`；Harmony 属性用 `AttributeType.FullName` 判并显式统计读取异常 |
| 依赖装况 | Python + ElementTree，取 `ModMetaData` **直接子元素** `<packageId>`，脚本 `F:\temp\c0ffee_deps.py` |
| 翻译盘点 | Python 按 defName 求交，脚本 `F:\temp\c0ffee_trans.py` |
| 原版 Def 核对 | `grep` 工具 + 逐行读 `Core\Defs\ThingDefs_Races\Races_Animal_Base.xml` |
| 孤儿类核对 | `grep` 工具全 mod 搜类名，人工判断引用是否在注释块内 |

### ② 阳性对照

| 结论 | 对照 | 结果 |
|---|---|---|
| 依赖装况表可信 | `c0ffee.rjw.IdeologyAddons` 自身必须被扫到 | PASS ✅ |
| Harmony 属性计数可信 | 扫描器内置异常计数必须为 0；且 `CRIALactation` 1.6 报出 7 处非 0 | `ATTRIBUTE READ ERRORS = 0` ✅ |
| `PackageId` 扫描面 | 1028 个 `About.xml` → 1026 个不同 packageId，并报出 2 组重复（`fxz.ratkin.facialanimation`、`stm.shellabackgrounds`） | 说明确实逐个读到直系子元素 ✅ |
| 中文翻译非空 | `ChineseSimplified` 条目数必须 > 0 | 111 ✅ |
| 原版 `BasePawn` 有 `<comps>` | 同法统计 Core 的 `<comps>` 出现次数 | 398 次 ✅ |
| 原版 `<Author>` 单数写法对照 | 同一 mod 内 `CRIALactation` 目录的英文 Keyed 是否被扫到 | 3 个版本各 9 keys ✅ |
| `Publicizer` 确实启用 | csproj 里 `<Publicize Include=` 条目 | 2 条 ✅ |

### ③ 自查纠错

1. **怀疑 `Patch_LactationInduction.xml` 的第二个操作会落空，差点写成 bug。** 补丁先用一个 `PatchOperationConditional`（xpath `/Defs/ThingDef/comps`）判断"没有任何 ThingDef 有 comps"才补 `<comps/>`，再往 `/Defs/ThingDef[@Name="BasePawn"]/comps` 里加组件。我的推理是：合并后的 Defs 树里几乎必然有别的 ThingDef 带 `<comps>`，条件会命中 → nomatch 分支不跑 → `BasePawn` 又没有 `<comps/>` → 补丁失败。
   **实测否定了这个推理**：原版 `Core\Defs\ThingDefs_Races\Races_Animal_Base.xml:41-45` 里 `BasePawn` **本来就带 `<comps>`**（内容是 `CompAttachBase`），所以 `PatchOperationAdd` 能正常命中。差一步就写出一条假缺陷。附带结论：那个 `PatchOperationConditional` 的 nomatch 分支才是**真正的死代码**（Core 单独就有 398 处 `<comps>`，永远命中不到 nomatch）——它大概是为"原版还没给 BasePawn 加 comps 的老版本"准备的防御。

2. **DefInjected 文件夹名不能当依据判断内容类型。** 放错位置的 `CRIAOrgy/ChineseSimplified/DefInjected/PreceptDef/AutoTranslated_Defs.xml` 里装的是 `TerribleOrgy.stages.0.label` ——**ThoughtDef 的字段**，却放在 `PreceptDef` 目录下。第一反应是"作者放错 Def 类型了"，但 DefInjected 的目录名只是装饰，Def 类型取自元素名，所以它能正常解析。**真正的错误在外层：整个 `ChineseSimplified` 少了 `Languages/` 层级。** 同一个坑我这轮已经踩过一次（上一份记录里 `Defs/TerrainDefs` 复数 vs `DefInjected/TerrainDef` 单数）。

3. **第一次列 DLL 字节数时把 4 个 `CRIAOrgy` 看成"大小相同 = 同一份二进制"。** 哈希一比四份全不同——大小相同只是因为这个类极小（1 个类型）。凡是"大小相同"就别急着合并结论，哈希才是同一性的判据。

## 可复用结论

1. **随包完整 C# 源码的 mod，证据质量远高于只能反编译的 mod。** 这份记录里几乎所有结论（孤儿类、死代码、复制粘贴笔误、运算符优先级、NRE 隐患、硬编码英文）都是**直接读源码**得到的，不是 IL 推断。收录时优先找这类 mod——GitLab/GitHub 上作者常把整个开发树（含 `.gitignore`、`.sln`）直接发布，这类 mod 的**价值在于可读性**。

2. **`LoadFolders.xml` 支持 `IfModActive=` 条件加载条目**，这让"把子 mod 做成软依赖而不打扰硬依赖检查"成为可能。但**代价必须自己补**：条件依赖只写在 `LoadFolders` 里时，缺依赖**不产生任何游戏提示**，功能安静消失。本 mod 的 `akaster.equalmilking` 就是这样（只进 `loadAfter`，没进 `modDependencies`），本机实测它没装 → `CRIALactation` 整个不加载。想给用户提示，就得把条件依赖也写进 `modDependencies`，或者用 `SoftDependencyChecker` 那样的 `[StaticConstructorOnStartup]` 打日志警告（本 mod 写了，但被注释掉了，注释里还留着 `"removed because not working"`）。

3. **`<Publicize>`（Krafs.Publicizer）是"编译期访问 internal"的正解**，比在运行时写 `AccessTools` 反射更干净：代码里可以直接 `AccessTools.DeclaredMethod(typeof(rjw.CasualSex_Helper), ...)` 或直接调 publicized 类型。前提是 csproj 里对每个要 publicize 的程序集写 `<Publicize Include="..." />`，并把该包加进 `packages.config` + `EnsureNuGetPackageBuildImports` 目标。`<Private>False</Private>` 是引用第三方 mod DLL 的必需项，否则会把对方 DLL 复制进自己的输出，造成类型身份分裂。

4. **用编译配置决定输出目录**（`Debug → 1.5\Assemblies\`、`Release → 1.6\Assemblies\`）是多版本 mod 维护成本最低的做法之一：源码只有一份，切版本只是改 `OutputPath`。比维护多个 csproj 干净得多。

5. **`AssemblyName` 里要带撇号就 URL 编码成 `%27`**，产物文件名会还原成 `'`。这是小众但省事的技巧。

6. **`[HarmonyReversePatch(HarmonyReversePatchType.Snapshot)]` 值得单独记一笔**：它在打补丁的瞬间快照原方法体，使该方法在补丁类里可以像普通方法一样被调用，从而实现"在 postfix 里复用原逻辑 + 追加自己的逻辑"，而不是靠 Prefix/Prefix 返回值去模拟。这是本 mod 最值得抄的一处 Harmony 用法。

7. **Transpiler 替换 `call` 目标、并在替换后的方法里回调原方法**，是"给第三方库的判定加附加条件"最干净的写法。`HarmonyPatch_CasualSex_Helper` 就是范例：把 `HookupAllowedViaSettings` 的调用换成 `HookupAllowed`，后者内部仍然调用 `HookupAllowedViaSettings`（AND，不是 OR）。比"在调用点前后插判定"稳，也比 `Prefix` + `__result` 覆盖直观。

8. **版本间的功能差异可能藏在已注释掉的源码里。** 本 mod 的三个 Harmony 补丁在当前源码中全被注释，但 **1.3 的 DLL 里还在**（Harmony 属性计数 10 vs 1.4+ 的 7）。如果你只看源码，会以为 1.3 和 1.4 行为一致。**读多版本 mod 必须同时反射每个版本的 DLL，并和源码对照。**

9. **`ref` 列表的变化能反推出依赖迁移**。本 mod 的 `CRIALactation` 在 1.5 从 REF `Milk` 变成 `EqualMilking`，正好对上 `LoadFolders` 里条件依赖从 `rjw.milk.humanoid` 换成 `akaster.equalmilking`。两条独立证据对上，结论才敢下。

10. **翻译放多项目 mod 里时，每个项目的语言树要各自带 `Languages/` 层**。因为 LoadFolders 是把每个条目当作独立的内容根，翻译按 `<条目>/Languages/<lang>/` 解析。少一层就整棵失效，而且**不会有任何报错**。同一个 mod 里两个项目一个写对一个写错，正是最容易被漏掉的情况。

11. **提交开发树时 `Preview.png` 可能成为体积大头**。本 mod 3.02 MB 里 2.56 MB（80.7%）是预览图，代码+Def+贴图不到 240 KB。审 mod 体积先看 `About/`，能立刻判断"这个 mod 大是因为内容还是因为图"。

12. **贴图三格式（`.png` + `.dds` + `.dds.zstd`）是 1.5+ 的正常形态**：`.dds.zstd` 是压缩后的 DDS（1.5+ 优先读），未压缩 `.dds` 给旧版本，`.png` 兜底。三份同名共存不代表冗余——但同名的**不同内容**副本（像本 mod `CRIALactation/UI/` 与根 `Textures/UI/` 那样 sha 不同）就要查路径是否可达。

## 修改建议

> 以下全部**未执行**。本轮只收录分析，不动 `F:\Games\GBL\rimworld\Mods` 里任何文件。

| 优先级 | 事项 | 依据 |
|---|---|---|
| **P0** | 把 `akaster.equalmilking` / `rjw.milk.humanoid` / `c0ffee.rjw.events` / `shauaputa.RimNudeWorld` / `abraxas.RJW.RaceSupport` 补进 `modDependencies`（或至少恢复 `SoftDependencyChecker` 的警告） | 本机实测 `akaster.equalmilking` 未装 → `CRIALactation` 静默不加载，且游戏零提示 |
| **P0** | 把 `CRIAOrgy/ChineseSimplified/` 整棵移到 `CRIAOrgy/Languages/ChineseSimplified/` | 少 `Languages/` 层，24 条翻译极可能从不生效；可补上 8 个 Def 的缺口 |
| **P1** | 修 `JobDefOf_CRIALactation` 静态构造里的 `typeof(HediffDefOf_Milk)` → `typeof(JobDefOf_CRIALactation)` | 明确的复制粘贴笔误 |
| **P1** | 4 处硬编码英文加 `.Translate()` 并补 Keyed：`" (sinful)"`、`RoleEffect_Hucow.Label`、`RoleRequirement_Lactating.GetLabel`、`CompLactation.CompInspectStringExtra`；顺手修 `permenent` → `permanent` | 四处均不可翻译 |
| **P1** | 给三处补 null 检查：`CompAbilityEffect_ConvertHucow` 的 `comp`、`GenerateGoodIngredients` postfix 的 `compIngredients`、`WorkGiver_MassageBreasts` 的 `pawn.Map` | NRE 隐患，未实机验证 |
| **P2** | 删除死文件与死引用：`SoftDependencyChecker.cs`、`HarmonyPatch_Ideo.cs`、`HediffComp_LactationInduction.cs`、`HediffCompProperties_LactationInduction.cs`（及 csproj 的 `<Compile>`），以及 `CRIALactation/UI/` 两张旧素材（57,695 B） | 已确认无任何活跃引用 |
| **P2** | `GenerateGoodIngredients` postfix 加去重（`if (!compIngredients.ingredients.Contains(...))`） | 重复调用会累积重复人乳成分 |
| **P2** | 清理 csproj：`<Folder Include="Defs\Thingdef\" />`；`0Harmony` 的 HintPath 别指向 1.5；两个项目 TargetFramework 统一 | 均为工程残留 |
| **P2** | `About.xml` 补 `modVersion`（与 `Manifest.xml` 的 `0.0.6` 对齐） | 目前工坊页看不出版本 |

## 未核实项

- **`Verse.DefOfHelper.EnsureInitializedInCtor` 的实际行为**未反编译，所以 `JobDefOf_CRIALactation` 那处笔误的**运行时后果**未定（可能无影响，也可能导致该 `[DefOf]` 类的字段不被填充而抛 NRE）。只确认了意图是笔误。
- **三处 NRE 隐患是否真的会在游戏里触发**未实机验证。`CompProperties_Lactation` 挂在 `BasePawn` 上（所有种族都有 comp）这一条已核实，因此 `ThoughtWorker_Precept_NoRecentHumanMilk` 的无保护解引用**大概率安全**。
- **本 mod 未在 1.6 实机加载验证**。特别是：`CRIALactation` 未加载时，`MemeDef Hucow` 引用的 `requireOne` 指向 `Lactating_Essential` / `Lactating_MandatoryHucow` 是否会让 Ideology 初始化报错——这两个 precept 来自不加载的 `CRIALactation/Defs`。**这是当前配置下最值得实机验证的一点**。
- **`CRIAOrgy/ChineseSimplified` 是否真的不生效**。推理依据是 `CRIALactation/1.x/Languages/English/Keyed/` 这个同 mod 内的正确样本 + RimWorld 对 LoadFolders 条目按 `<条目>/Languages/<lang>/` 解析的常规；但没有实机日志佐证。
- **重定义原版 `MemeGroupDef Sexuality` 的影响范围**未评估（会不会挤掉其它 mod 的性取向 meme、影响 maxRows）。
- **`HarmonyPatch_Milk_HumanCompHasGatherableBodyResource` 在 1.3 下的实际效果**：源码已注释，只能从 1.3 的 DLL 属性计数推断它还在，不能确认它打的目标方法在 1.3 的 RJW 上是否仍存在。
- **素材与源码的许可条款**未查（无 LICENSE，`<description>` 未提）。上游仓库 `gitgud.io/c0ffeeeeeeee/coffees-rjw-ideology-addons` 的 LICENSE 未访问核实。
