# 许可证说明

本仓库混合了三类内容，不能用一个顶层许可证一概而论。

## 根 LICENSE

根目录的 [`../LICENSE`](../LICENSE) 是从原项目继承的 MIT 许可证文本
（Copyright (c) 2023 Sanhu Li）。它只覆盖原项目有权按 MIT 授权的部分，
**不会自动把第三方 mod、贴图、音频或其它素材重新授权为 MIT**。

## 内容分类

| 内容 | 许可证边界 |
|---|---|
| `收集/` / 未来 `mods/collected/` | 各自保留上游 LICENSE 与作者声明；无 LICENSE 的 mod 默认保留所有权利，仅供本地学习 |
| `records/` 中的分析记录 | Makeshiftname 的原创分析；目前尚未单独声明公开复用许可，默认保留所有权利 |
| `docs/knowledge/` 中的知识文档 | 同上；其中引用的第三方事实仍受原始来源和上游许可约束 |
| `rimworld-mod-forge` | 独立仓库，原创代码使用该仓库自己的 MIT 许可 |
| `rimworld-mod-forks` | 每个 fork 沿用其上游许可证；该仓库不设统一顶层许可证 |

## 明确禁止

- 不得把 `收集/` 或 `mods/collected/` 的代码、贴图、音频直接复制进原创 mod。
- 不得把第三方素材标注为 MIT 或 Makeshiftname 原创。
- 不得因为 Atlas 的根 LICENSE 是 MIT，就认为整个仓库都可以按 MIT 再分发。

## 待决定

Makeshiftname 尚未为 `records/` 和 `docs/knowledge/` 的原创文字单独选择许可证。
在明确选择之前，默认保留所有权利，不构成公开复用授权。以后可以选择例如
CC BY 4.0、CC BY-SA 4.0 或 MIT，但需要同时确认第三方引用和素材的边界。
