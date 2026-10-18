# records — Mod 分析记录

这里保存单个 mod 的调查档案：它是什么、如何核验、可复用结论、可选修改建议，以及当时的环境与证据。分析记录独立于 [`mods/`](../mods/README.md) 中的代码样本；也独立于 [`docs/knowledge/`](../docs/knowledge/README.md) 中经审核提炼的通用知识。

## 记录怎么用

1. 先读 [STANDARD.md](STANDARD.md)——目录命名、四档核验深度、阳性对照和记录骨架。
2. 按稳定 ID 打开记录目录：`records/<id>/README.md`。
3. 技术结论需要进入知识库时，按 [提炼规则](STANDARD.md#提炼到知识库) 显式执行，并在
   `record.json` 里登记去向；知识页的 `## 来源记录` 段由
   `tools/kb/sync_knowledge_sources.py --write` 生成。
4. 机器可读索引在 [index.json](index.json)。

## 记录列表

<!-- AUTO-GENERATED-START -->
| ID | 记录 | packageId | 作者 | 状态 | 提炼 |
|---|---|---|---|---|---|
| `abscon-privacy-please` | [Privacy, Please!（RJW 隐私意识）](abscon-privacy-please/README.md) | `abscon.privacy.please` | AbstractConcept、AblativeAbsolute | analyzed | 1 |
| `adaptive-ideology-storage` | [Adaptive Ideology Storage](adaptive-ideology-storage/README.md) | `Adaptive.Ideology.Storage` | vin | analyzed | 1 |
| `adaptive-simplestorage` | [Adaptive Simple Storage](adaptive-simplestorage/README.md) | `Adaptive.SimpleStorage` | vin | analyzed | 1 |
| `adaptive-storage-framework` | [Adaptive Storage Framework（`3033901359`）— 分析记录](adaptive-storage-framework/README.md) | `adaptive.storage.framework` | Soul、Phaneron、bradson | analyzed | — |
| `akt-ideology` | [AKT_Ideology — 扶她文化（`RJW-文化-扶她文化`）— 分析记录](akt-ideology/README.md) | `AKT.Ideology` | AKawaiiTent | analyzed | — |
| `aoba-framework` | [Fortified Features Framework（`3498575851`）— 分析记录](aoba-framework/README.md) | `AOBA.Framework` | AOBA | analyzed | 1 |
| `brrainz-harmony` | [Harmony（`2009463077`）— 分析记录](brrainz-harmony/README.md) | `brrainz.harmony` | Andreas Pardeike（Brrainz） | analyzed | 2 |
| `c0ffee-rjw-ideologyaddons` | [C0ffeeRIA（C0ffee's RJW Ideology Addons）](c0ffee-rjw-ideologyaddons/README.md) | `c0ffee.rjw.IdeologyAddons` | C0ffee | analyzed | 1 |
| `fix-miho-visualpatch` | [Miho Race Children Texture Fix](fix-miho-visualpatch/README.md) | `Fix.Miho.VisualPatch` | Ay | analyzed | 1 |
| `gt-sam-glittertech` | [Glitter Tech Classic（`725576127`）— 分析记录](gt-sam-glittertech/README.md) | `GT.Sam.GlitterTech` | Sam | analyzed | 1 |
| `haplo-miscellaneous-training` | [Misc. Training](haplo-miscellaneous-training/README.md) | `Haplo.Miscellaneous.Training` | Haplo | analyzed | 1 |
| `imranfish-xmlextensions` | [XML Extensions（`2574315206`）— 分析记录](imranfish-xmlextensions/README.md) | `imranfish.xmlextensions` | Imranfish | analyzed | 1 |
| `mlie-sdbridges` | [[sd] Bridges (Continued)](mlie-sdbridges/README.md) | `Mlie.SDBridges` | Mlie、sulusdacors | analyzed | 1 |
| `nera-spawnthosegenes` | [[BT] SpawnThoseGenes!（`2898044088`）— 分析记录](nera-spawnthosegenes/README.md) | `Nera.SpawnThoseGenes` | Nera | analyzed | — |
| `owlchemist-cherrypicker` | [Cherry Picker（`3521312241`）— 分析记录](owlchemist-cherrypicker/README.md) | `Owlchemist.CherryPicker` | Owlchemist | analyzed | — |
| `readyforjeff-rjwpeculiarinstitution` | [Peculiar Institution](readyforjeff-rjwpeculiarinstitution/README.md) | `readyforjeff.RJWPeculiarInstitution` | readyforjeff | analyzed | 1 |
| `rim-job-world` | [RimJobWorld（RJW）— 分析记录](rim-job-world/README.md) | `rim.job.world` | Ed86 | analyzed | 1 |
| `rjw-fb` | [RimJobWorld - FB（RJW 做爱感想·颜值）](rjw-fb/README.md) | `rjw.FB` | Ed86 | analyzed | 1 |
| `s-g` | [P-Music（`725130005`）— 分析记录](s-g/README.md) | `s.g` | Peppsen | analyzed | — |
| `taranchuk-fastergameloading` | [Faster Game Loading - Continued（`3652938473`）— 分析记录](taranchuk-fastergameloading/README.md) | `Taranchuk.FasterGameLoading` | 綠菇（mushroomTW）—— Taranchuk 原版的维护分支 | analyzed | — |
| `unlimitedhugs-hugslib` | [HugsLib（`818773962`）— 分析记录](unlimitedhugs-hugslib/README.md) | `UnlimitedHugs.HugsLib` | UnlimitedHugs | analyzed | 1 |
| `vegapnk-cumpilation` | [Cumpilation](vegapnk-cumpilation/README.md) | `vegapnk.cumpilation` | Vegapnk、Telanda | analyzed | 1 |
| `yukiyuki-abyss` | [ABYSS / 阿比斯](yukiyuki-abyss/README.md) | `yukiyuki.ABYSS` | yukiyuki | analyzed | — |
| `yukiyuki-asebi` | [美南烛 / ASEBI](yukiyuki-asebi/README.md) | `yukiyuki.ASEBI` | yukiyuki | analyzed | — |
| `yukiyuki-borum` | [BORUM / 雪绒兽](yukiyuki-borum/README.md) | `yukiyuki.BORUM` | yukiyuki | analyzed | 1 |
| `yukiyuki-fleshia` | [FLESHIA / 弗莱西雅](yukiyuki-fleshia/README.md) | `yukiyuki.FLESHIA` | yukiyuki | analyzed | — |
| `yukiyuki-sankaandsosin` | [SANKA and SOSIN / 素心和葬歌](yukiyuki-sankaandsosin/README.md) | `yukiyuki.SANKAandSOSIN` | yukiyuki | analyzed | 1 |
| `yukiyuki-yaemu` | [YAEMU / 八重律](yukiyuki-yaemu/README.md) | `yukiyuki.YAEMU` | yukiyuki | analyzed | 1 |
<!-- AUTO-GENERATED-END -->
