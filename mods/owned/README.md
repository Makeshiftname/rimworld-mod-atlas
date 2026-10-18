# Owned Mods

本目录不再保存本地生产代码。Makeshiftname 的原创 mod 位于
[`rimworld-mod-forge`](https://github.com/Makeshiftname/rimworld-mod-forge)，
目录名使用稳定 ID。

Atlas 通过 [`../registry.json`](../registry.json) 的 `code.kind: external`
登记仓库、相对路径和固定 commit；不复制代码，也不让 `scan_mods.py` 扫描外部仓库。
