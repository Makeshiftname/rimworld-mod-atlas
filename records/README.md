# records — Mod 分析记录

这里保存单个 mod 的调查档案：初步档记录核验边界与下一步，深度档记录可复用结论、可选修改建议以及当时的环境与证据。记录分两档：**初步分析**用于快速分流，**深度分析**用于支撑修改、发布和知识提炼。分析记录独立于 [`mods/`](../mods/README.md) 中的代码样本；也独立于 [`docs/knowledge/`](../docs/knowledge/README.md) 中经审核提炼的通用知识。

## 记录怎么用

1. 先读 [STANDARD.md](STANDARD.md)——两档骨架、条件性证据、状态与提炼规则。
2. 按稳定 ID 打开记录目录：`records/<id>/README.md`；先看索引里的“档”列，判断是初步还是深度。
3. 技术结论需要进入知识库时，按 [提炼规则](STANDARD.md#52-提炼) 显式执行，并在
   `record.json` 里登记去向；知识页的 `## 来源记录` 段由
   `tools/kb/sync_knowledge_sources.py --write` 生成。
4. 新建记录从 `tools/kb/templates/record/initial/` 或 `deep/` 复制；机器可读索引在 [index.json](index.json)。

## 记录列表

<!-- AUTO-GENERATED-START -->
| ID | 档 | 记录 | packageId | 作者 | 状态 | 提炼 |
|---|---|---|---|---|---|---|
| `abscon-privacy-please` | 深度 | [Privacy, Please!（RJW 隐私意识）](abscon-privacy-please/README.md) | `abscon.privacy.please` | AbstractConcept、AblativeAbsolute | analyzed | 1 |
| `adaptive-ideology-storage` | 深度 | [Adaptive Ideology Storage](adaptive-ideology-storage/README.md) | `Adaptive.Ideology.Storage` | vin | analyzed | 1 |
| `adaptive-simplestorage` | 深度 | [Adaptive Simple Storage](adaptive-simplestorage/README.md) | `Adaptive.SimpleStorage` | vin | analyzed | 1 |
| `adaptive-storage-framework` | 深度 | [Adaptive Storage Framework（`3033901359`）— 分析记录](adaptive-storage-framework/README.md) | `adaptive.storage.framework` | Soul、Phaneron、bradson | analyzed | — |
| `akt-ideology` | 深度 | [AKT_Ideology — 扶她文化（`RJW-文化-扶她文化`）— 分析记录](akt-ideology/README.md) | `AKT.Ideology` | AKawaiiTent | analyzed | — |
| `aoba-framework` | 深度 | [Fortified Features Framework（`3498575851`）— 分析记录](aoba-framework/README.md) | `AOBA.Framework` | AOBA | analyzed | 1 |
| `brrainz-harmony` | 深度 | [Harmony（`2009463077`）— 分析记录](brrainz-harmony/README.md) | `brrainz.harmony` | Andreas Pardeike（Brrainz） | analyzed | 2 |
| `c0ffee-rjw-ideologyaddons` | 深度 | [C0ffeeRIA（C0ffee's RJW Ideology Addons）](c0ffee-rjw-ideologyaddons/README.md) | `c0ffee.rjw.IdeologyAddons` | C0ffee | analyzed | 1 |
| `fix-miho-visualpatch` | 深度 | [Miho Race Children Texture Fix](fix-miho-visualpatch/README.md) | `Fix.Miho.VisualPatch` | Ay | analyzed | 1 |
| `gt-sam-glittertech` | 深度 | [Glitter Tech Classic（`725576127`）— 分析记录](gt-sam-glittertech/README.md) | `GT.Sam.GlitterTech` | Sam | analyzed | 1 |
| `haplo-miscellaneous-training` | 深度 | [Misc. Training](haplo-miscellaneous-training/README.md) | `Haplo.Miscellaneous.Training` | Haplo | analyzed | 1 |
| `imranfish-xmlextensions` | 深度 | [XML Extensions（`2574315206`）— 分析记录](imranfish-xmlextensions/README.md) | `imranfish.xmlextensions` | Imranfish | analyzed | 1 |
| `mlie-sdbridges` | 深度 | [[sd] Bridges (Continued)](mlie-sdbridges/README.md) | `Mlie.SDBridges` | Mlie、sulusdacors | analyzed | 1 |
| `nera-spawnthosegenes` | 深度 | [[BT] SpawnThoseGenes!（`2898044088`）— 分析记录](nera-spawnthosegenes/README.md) | `Nera.SpawnThoseGenes` | Nera | analyzed | — |
| `owlchemist-cherrypicker` | 深度 | [Cherry Picker（`3521312241`）— 分析记录](owlchemist-cherrypicker/README.md) | `Owlchemist.CherryPicker` | Owlchemist | analyzed | — |
| `readyforjeff-rjwpeculiarinstitution` | 深度 | [Peculiar Institution](readyforjeff-rjwpeculiarinstitution/README.md) | `readyforjeff.RJWPeculiarInstitution` | readyforjeff | analyzed | 1 |
| `rim-job-world` | 深度 | [RimJobWorld（RJW）— 分析记录](rim-job-world/README.md) | `rim.job.world` | Ed86 | analyzed | 1 |
| `rjw-fb` | 深度 | [RimJobWorld - FB（RJW 做爱感想·颜值）](rjw-fb/README.md) | `rjw.FB` | Ed86 | analyzed | 1 |
| `s-g` | 深度 | [P-Music（`725130005`）— 分析记录](s-g/README.md) | `s.g` | Peppsen | analyzed | — |
| `taranchuk-fastergameloading` | 深度 | [Faster Game Loading - Continued（`3652938473`）— 分析记录](taranchuk-fastergameloading/README.md) | `Taranchuk.FasterGameLoading` | 綠菇（mushroomTW）—— Taranchuk 原版的维护分支 | analyzed | — |
| `unlimitedhugs-hugslib` | 深度 | [HugsLib（`818773962`）— 分析记录](unlimitedhugs-hugslib/README.md) | `UnlimitedHugs.HugsLib` | UnlimitedHugs | analyzed | 1 |
| `vegapnk-cumpilation` | 深度 | [Cumpilation](vegapnk-cumpilation/README.md) | `vegapnk.cumpilation` | Vegapnk、Telanda | analyzed | 1 |
| `yukiyuki-abyss` | 深度 | [ABYSS / 阿比斯](yukiyuki-abyss/README.md) | `yukiyuki.ABYSS` | yukiyuki | analyzed | — |
| `yukiyuki-asebi` | 深度 | [美南烛 / ASEBI](yukiyuki-asebi/README.md) | `yukiyuki.ASEBI` | yukiyuki | analyzed | — |
| `yukiyuki-borum` | 深度 | [BORUM / 雪绒兽](yukiyuki-borum/README.md) | `yukiyuki.BORUM` | yukiyuki | analyzed | 1 |
| `yukiyuki-fleshia` | 深度 | [FLESHIA / 弗莱西雅](yukiyuki-fleshia/README.md) | `yukiyuki.FLESHIA` | yukiyuki | analyzed | — |
| `yukiyuki-sankaandsosin` | 深度 | [SANKA and SOSIN / 素心和葬歌](yukiyuki-sankaandsosin/README.md) | `yukiyuki.SANKAandSOSIN` | yukiyuki | analyzed | 1 |
| `yukiyuki-yaemu` | 深度 | [YAEMU / 八重律](yukiyuki-yaemu/README.md) | `yukiyuki.YAEMU` | yukiyuki | analyzed | 1 |
<!-- AUTO-GENERATED-END -->
