# Miho Race Children Texture Fix — 分析记录

| | |
|---|---|
| 本记录目录 | `修改/1~11岁美狐贴图修正/` |
| mod 本体目录 | `F:\Games\GBL\rimworld\Mods\1~11岁美狐贴图修正(本体更新修复版)\` |
| mod 名 / packageId | Miho Race Children Texture Fix / `Fix.Miho.VisualPatch` |
| 作者 | Ay |

> 本 mod **有值得动手的地方**（见 §六，高优先级两条），
> 是三份记录里第一份真正属于"修改"而非"留档"的。

---

## 身份卡

| 项 | 值 |
|---|---|
| 支持版本 | **仅 1.6** |
| 规模 | 4 个文件，**零贴图、零 C#** |
| 硬依赖 | `erdelf.HumanoidAlienRaces`（HAR）→ 已装 `839005762`<br>`miho.fortifiedoutremer`（本体）→ 已装 `2816826107` |
| `loadAfter` | 上述两者 + `Ludeon.RimWorld.Biotech` |

### 文件构成

```
1.6/Defs/Race_Miho.xml               81.3 KB  ← 本体种族 Def 的完整 fork（2356 行）
1.6/Defs/SkeletonDef/Miho_SkeletonDef.xml   9.0 KB  ← 本体没有的全新 Def
1.6/Patches/Baby_patch.xml            2.1 KB  ← 6 个 PatchOperation
About/About.xml
About/Preview.png
```

**贴图全部来自本体 `Cont/` 目录**（3439 文件，RimWorld 工坊续传机制），
本 mod 只改 Def 指向，自己一张图都没有。

---

## 它是什么

这个 mod 同时用三种手段改同一批东西，这是理解它的关键。

### 2.1 完整 fork 种族 Def（主体）

`1.6/Defs/Race_Miho.xml` 是本体 `2816826107\1.6\Defs\Race_Miho.xml` 的**逐行拷贝**
——两边都是 2356 行、81.3 KB。18 个 defName 全部重复
（`Alien_Miho`、`Gene_CelestialMiho`、`Miho_Tail_Hediff` 等）。
靠 `loadAfter miho.fortifiedoutremer` 让自己的副本赢下同名冲突。

**实际 diff 只有 15 行**：

| 改动 | 内容 |
|---|---|
| `Child` 身体贴图 | `Miho/Body/Naked_Child` → **`Miho/Blank`** |
| headOffset × 7 处 | `0.55→0.65`、`0.2→0.25`、`0.2→0.3`、`-0.028→0.65`… （Baby / Child 各一组） |

原本体的问题：`Child` 与 `Baby` 两个 BodyType **都指向同一张 `Naked_Child`**——重复调用。
对应描述里的"删除 Race_Miho.xml 第 325 行额外调用的一个身体"。

### 2.2 `Patches/Baby_patch.xml`（6 个 PatchOperation）

对同一批东西再改一遍：

- `Replace`：`BodyType[@For="Baby"]/path` → `Miho/Body/Naked_Baby`
- `Add`：Baby → east/west 的 headOffset
- `Replace`：north/south/east/west 的 Child headOffset

### 2.3 `Miho_SkeletonDef.xml`（全新 Def）

本体**完全没有** SkeletonDef。`<SizedApparel.SkeletonDef>`，defName=`Alien_Miho`，
3 组骨骼 `Child` / `Female` / `Thin`——对应描述里的"SA 器官微调"（SA = SizedApparel）。

---

## 三、四个问题

### 3.1 fork 里那行 `Baby` 是死配置

fork 写 `Baby → Miho/Body/Naked_Child`，紧接着 `Baby_patch.xml` 用 `PatchOperationReplace`
把**同一个 xpath** 改成 `Miho/Body/Naked_Baby`。
补丁在所有 Def 加载完之后才应用，所以最终生效值是 `Naked_Baby`——fork 里那行纯属白写。

**净效果**：

| BodyType | 最终贴图 | 贴图是否存在 |
|---|---|---|
| `Child`（3–11 岁） | `Miho/Blank` | ✓ `Cont\Textures\Miho\Blank_*.dds` |
| `Baby`（1–3 岁） | `Miho/Body/Naked_Baby` | ✓ |

> ⚠️ 3–11 岁最终指向 **`Miho/Blank`**（本体的空白贴图约定，头部也用 `Miho/HeadBlank/Normal`），
> 即"无身体贴图、只有头 + 服装"。这与"修复"的表述之间的视觉关系**无法静态判断，需在游戏里看**。

### 3.2 架构风险：fork 会冻结本体版本 ⚠️ 高

因为它复制了**整个**种族 Def 且 defName 全同名，其副本会**整体覆盖**本体的定义。

> **Miho 本体一更新，这个 mod 立刻变成旧版本，并把本体所有新内容一起挡掉**
> ——不只是它改的那 15 行。

两份文件都是 2026/4 的快照。作者显然需要每次本体更新都重新 fork 一次。

用 `PatchOperation` 只改那 15 行会安全得多，也不会冻结本体。

### 3.3 未声明的隐式依赖：`SizedApparel` 高

`Miho_SkeletonDef.xml` 用了 `<SizedApparel.SkeletonDef>`，
但 About.xml **既没声明 SizedApparel 依赖，也没有 `MayRequire`**。

实际状态：SizedApparel 框架**存在**，但被打包在
**`RJW-Sar0-本体核心\1.6\Assemblies\SizedApparelforRJW.dll`**（v5.3.2.0）里——
那份 DLL **自己定义了完整的 `SizedApparel.*` 命名空间，96 个类型**，
含 `SkeletonDef` / `Bone` / `BoneTransform` 及全套 Harmony patch。

> 也就是说：**本 mod 的 SkeletonDef 隐式依赖「RJW 本体核心」这个 mod**。
> 关掉 RJW 本体核心，这个 Def 就解析失败。

修法二选一：根节点加 `MayRequire`，或用 `PatchOperationFindMod` 条件包裹。

### 3.4 SkeletonDef 缺 `Baby` —— 已知限制，非 bug

只定义 `Child` / `Female` / `Thin` 三组骨骼。作者在描述里自己交代了：
*"本mod对 4~11 岁 miho 儿童效果最好，1~3 岁头部偏低无法单独调整"*。

另外 `Bone` 类有 `west` 字段，SkeletonDef 只写了 south/north/east——
合理，RimWorld 不渲染西面（用 east 镜像）。

---

## 怎么验的

拿到 SizedApparel 类型表后，SkeletonDef 的 XML 结构与真实类**逐项对得上**：

| XML | 真实字段 |
|---|---|
| `<skeletons><li>` | `SkeletonDef.skeletons : List<Skeleton>` ✓ |
| `<bodyType>` / `<Bones>` | `Skeleton.bodyType : String` / `.Bones : List<Bone>` ✓ |
| `<name>` / `<south><north><east>` | `Bone.name` / `.south` `.north` `.east` : BoneTransform ✓ |
| `<InitialPosition>` / `<InitialAngle>` / `<PivotCenter>` | `Vector3` / `Single` / `Vector2` ✓ |

贴图路径也全部核实存在：`Miho/Blank_*`、`Miho/Body/Naked_Baby_*`、`Miho/Body/Naked_Child_*`
均在本体 `Cont/Textures/Miho/` 下。

---

## 五、方法论纠错（本记录必须留档的部分）

本次分析里有**两次方向性错误的结论**，都是方法问题而非眼力问题。记下来以免后人重走。

### 5.1 子串 grep 判依赖

grep `About.xml` 里的 `erdelf.HumanoidAlienRaces` 命中了这个 mod **自己** `modDependencies`
里**嵌套**的 packageId，于是误判成"已安装"。

> **规则**：判断某 packageId 是否安装，必须用 XML 解析取 `ModMetaData` 的
> **直接子元素** `<packageId>`（嵌套在 `<li>` 里的不算），不能子串 grep。

（同一轮里 `Haplo.Miscellaneous.Core` 也踩过同样的坑，详见 `修改/717575199-MiscTraining/README.md`。）

### 5.2 扫 DLL 字符串判"是否定义了某类型"

两处证据都指向"框架未安装"：

1. `SizedApparelforRJW.dll` 的 `GetReferencedAssemblies()` 里**没有** `SizedApparel`
2. 全库二进制扫描含 `SizedApparel` 元数据串的只有 4 个 dll，且都是 RJW 适配

据此判"SizedApparel 框架未安装，本 mod 的 Def 会解析失败"——**完全错了**。

> **规则**：DLL 字节里的命名空间串，**定义方和引用方都会命中**，区分不了；
> 而且**定义方不会出现在自己的 `GetReferencedAssemblies()` 里**。
> 判断"某 dll 是否*定义*了某类型"只有一个可靠办法：
> 先 `LoadFrom` 预加载游戏 Managed + 该 dll 的全部引用程序集，再 `GetTypes()`
> （吃 `ReflectionTypeLoadException.Types` 拿部分类型），直接查类型名。
> **预加载这步不能省**，否则 `GetTypes()` 失败返回 0 类型。

实测：`SizedApparelforRJW.dll` 加载出 96 个类型，整个 `SizedApparel.*` 都在里面。

> 附带收益：拿到 Def 类的字段表后，**可以直接用来验证某个 XML Def 写得对不对**（见 §四）。

---

## 修改建议

| 优先级 | 事项 |
|---|---|
| 高 | fork 改为纯 `PatchOperation`，只打那 15 行——否则会冻结 Miho 本体版本 |
| 高 | `Miho_SkeletonDef.xml` 加 `MayRequire` 或条件补丁，补上对 RJW 本体核心的隐式依赖声明 |
| 中 | 进游戏确认 3–11 岁指向 `Miho/Blank` 的视觉效果是否符合预期 |
| 低 | 删掉 fork 里那行会被补丁覆盖的 `Baby` 死配置，减少误读 |

改动范围应限制在 `1.6/Defs/` 与 `1.6/Patches/`，
**不涉及 `2816826107`（本体）与任何贴图**。

---

## 可复用结论

1. **fork 式修正 mod 的通病**：复制整个上游 Def + 改几行，靠 `loadAfter` 赢下同名冲突。
   代价是**冻结上游版本**——上游更新时，被挡掉的不只是你改的那几行，而是全部。
   判断一个 patch mod 是否属于这种类型：看它的 `Defs` 里有没有和上游**同名 defName 的大文件**。

2. **补丁在 Def 之后应用**：同一份数据被 fork 和 patch 各改一次时，
   **patch 永远赢**。fork 里对应的行是死配置——读这类 mod 时要先确认谁最后生效。

3. **Def 类不在游戏程序集里 ≠ 没装**：第三方 Def 类（如 `<SizedApparel.SkeletonDef>`）
   来自 mod 提供的 dll，而且可能被**打包进一个名字完全无关的 mod**
   （本例：`SizedApparel` 打包在 `RJW-Sar0-本体核心` 里）。
   判据只能是 §5.2 的 `GetTypes()`。

4. **未声明的隐式依赖**：用了第三方 Def 类却在 About.xml 不声明依赖、
   也不写 `MayRequire`，是 patch mod 常见的坑——
   对方 mod 被关掉/卸载时，这个 Def 直接解析失败。

---

*记录时间：2026-10-16*
*核验环境：RimWorld 1.6.9655.19392（本机），未在游戏内实机验证视觉效果*
