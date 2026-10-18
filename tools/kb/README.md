# Knowledge Base Toolchain (`tools/kb/`)

Tools that keep code samples, analysis records and the knowledge base in sync.
Pure Python 3 standard library — no third-party dependencies. Run from the
repository root.

## Main commands

| Command | Purpose |
|---|---|
| `python tools/kb/check_all.py` | Run every acceptance gate in order. |
| `python tools/kb/scan_mods.py` | Regenerate `docs/knowledge/indexes/mods.{md,json}` from the registry. |
| `python tools/kb/scan_records.py` | Regenerate `records/index.json` and the records README table. |
| `python tools/kb/migrate_mods.py` | Dry-run legacy `自建/收集` → stable-ID `mods/` migration. |
| `python tools/kb/check_records.py` | Validate record anchors, metadata and source paths. |
| `python tools/kb/check_links.py` | Validate relative links in first-party documentation. |
| `python tools/kb/check_knowledge.py` | Fail on orphan pages in knowledge layers. |
| `python tools/kb/check_repo_hygiene.py` | Reject duplicate paths, placeholder IDs and structural problems. |
| `python tools/kb/validate_readme.py` | Audit code-sample README quality by stable ID. |

## Registry and migration

`mods/registry.json` is the single source of identity:

- `id` is stable and used by records and knowledge links.
- `legacy_paths` allow tools to read the current `自建/收集` layout.
- `record_paths` identify record-only objects that have no code sample.
- `migrate_mods.py` never edits code; it emits `git mv` operations and refuses
  to proceed when a target and legacy path both exist.

```powershell
python tools/kb/gen_registry.py --write     # preserve IDs, add missing entries
python tools/kb/migrate_mods.py             # dry run
python tools/kb/migrate_mods.py --apply     # after reviewing the mapping
python tools/kb/scan_mods.py               # refresh generated indexes
```

## Legacy utilities

The historical rename helpers were superseded by `migrate_mods.py`; use the
registry-driven migration path for all future moves.

## Acceptance

```powershell
python tools/kb/check_all.py
```

The gate checks links, record identity, knowledge reachability, repository
hygiene, mod index drift and record index drift. Generated files are rebuilt by
scripts and must not be edited manually.
