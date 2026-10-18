# Knowledge Base Toolchain (`tools/kb/`)

Tools that keep code samples, analysis records and the knowledge base in sync.
Pure Python 3 standard library — no third-party dependencies. Run from the
repository root.

## Main commands

| Command | Purpose |
|---|---|
| `python tools/kb/check_all.py` | Run every acceptance gate in order. |
| `python tools/kb/check_registry.py` | Validate registry schema, IDs, aliases and filesystem coverage. |
| `python tools/kb/scan_mods.py` | Regenerate `docs/knowledge/indexes/mods.{md,json}`. |
| `python tools/kb/scan_records.py` | Regenerate `records/index.json` and the records README table. |
| `python tools/kb/migrate_mods.py --json` | Read-only migration plan with file counts and conflicts. |
| `python tools/kb/migrate_mods.py --manifest PATH` | Freeze a plan for later apply. |
| `python tools/kb/migrate_mods.py --apply` | Move code, rewrite first-party references, then print verification commands. |
| `python tools/kb/check_records.py` | Validate record anchors, metadata, IDs and distilled links. |
| `python tools/kb/check_links.py` | Validate relative links in first-party documentation. |
| `python tools/kb/check_knowledge.py` | Fail on orphan pages in knowledge layers. |
| `python tools/kb/sync_knowledge_sources.py --check` | Verify the generated `## 来源记录` sections match `record.json.distilled_to`. |
| `python tools/kb/sync_knowledge_sources.py --write` | Regenerate the reverse source lists in knowledge pages. |
| `python tools/kb/check_repo_hygiene.py` | Reject duplicate paths, placeholder IDs and structural problems. |
| `python tools/kb/validate_readme.py` | Audit code-sample README quality by stable ID. |

## Registry and migration

`mods/registry.json` is the single source of identity and is manually
maintained:

- `id` is stable and used by records and knowledge links.
- `origin` is `owned` or `collected`.
- `code.legacy_paths` and `code.target_path` describe the code sample.
- `record` describes the analysis; `code: null` means the object has a record
  but no local code sample.
- `aliases` handle old directory names and renamed IDs.

`gen_registry.py` only writes `mods/registry.proposed.json`; it never overwrites
the authority. `migrate_registry_schema.py` is the explicit v2 → v3 metadata
migration.

```powershell
python tools/kb/migrate_registry_schema.py          # check v2 -> v3
python tools/kb/migrate_registry_schema.py --write  # explicit one-way migration
python tools/kb/gen_registry.py --write             # proposal only
```

## Acceptance

```powershell
python tools/kb/check_all.py
```

The gate checks registry coverage, links, record identity, bidirectional
record/knowledge source links, knowledge reachability, repository hygiene,
generated-index drift and the unit tests. Generated files are rebuilt by
scripts and must not be edited manually.
