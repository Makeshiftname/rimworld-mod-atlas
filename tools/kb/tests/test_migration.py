from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "kb"))
import migrate_mods


def sample_data() -> dict:
    return {
        "schema_version": 4,
        "objects": [
            {
                "id": "demo",
                "origin": "collected",
                "package_id": "demo.mod",
                "display_name": "Demo",
                "aliases": [],
                "code": {
                    "legacy_paths": ["collect/demo"],
                    "target_path": "mods/collected/demo",
                },
                "record": {
                    "legacy_paths": ["old-records/demo"],
                    "path": "records/demo",
                },
            }
        ],
    }


class MigrationTests(unittest.TestCase):
    def test_mods_migration_dry_run_never_writes(self):
        before = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("收集/*"))
        result = subprocess.run(
            [sys.executable, "tools/kb/migrate_mods.py"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        after = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("收集/*"))
        self.assertEqual(before, after)
        self.assertIn("dry run only", result.stdout)

    def test_record_scan_check_is_clean(self):
        result = subprocess.run(
            [sys.executable, "tools/kb/scan_records.py", "--check"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_plan_distinguishes_move_conflict_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "collect" / "demo").mkdir(parents=True)
            rows = migrate_mods.build_plan(root, sample_data())
            self.assertEqual(rows[0]["status"], "move")

            (root / "mods" / "collected" / "demo").mkdir(parents=True)
            rows = migrate_mods.build_plan(root, sample_data())
            self.assertEqual(rows[0]["status"], "conflict")

            (root / "collect" / "demo").rmdir()
            rows = migrate_mods.build_plan(root, sample_data())
            self.assertEqual(rows[0]["status"], "already")

            (root / "mods" / "collected" / "demo").rmdir()
            rows = migrate_mods.build_plan(root, sample_data())
            self.assertEqual(rows[0]["status"], "missing")

    def test_external_code_entries_are_skipped(self):
        data = sample_data()
        data["objects"].append({
            "id": "external-demo",
            "origin": "owned",
            "package_id": "Makeshiftname.ExternalDemo",
            "display_name": "External Demo",
            "aliases": [],
            "code": {
                "kind": "external",
                "repo": "https://github.com/Makeshiftname/rimworld-mod-forge",
                "path": "mods/owned/external-demo",
                "commit": "9f0af55624ced0a14a89d2161ac82a8e3d64b757",
            },
            "record": None,
        })
        rows = migrate_mods.build_plan(ROOT, data)
        self.assertEqual([row["id"] for row in rows], ["demo"])

    def test_rewrite_is_limited_to_first_party_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs" / "guide.md"
            docs.parent.mkdir(parents=True)
            docs.write_text("see `collect/demo/README.md` and old-records/demo\n", encoding="utf-8")
            record = root / "records" / "demo" / "record.json"
            record.parent.mkdir(parents=True)
            record.write_text('{"source": "old-records/demo"}\n', encoding="utf-8")
            collected = root / "mods" / "collected" / "old" / "README.md"
            collected.parent.mkdir(parents=True)
            collected.write_text("collect/demo and old-records/demo\n", encoding="utf-8")

            changed, replacements, unresolved = migrate_mods.rewrite_references(root, sample_data())
            self.assertEqual(replacements, 3)
            self.assertEqual(unresolved, [])
            self.assertIn("mods/collected/demo/README.md", docs.read_text(encoding="utf-8"))
            self.assertIn("records/demo", record.read_text(encoding="utf-8"))
            self.assertIn("collect/demo", collected.read_text(encoding="utf-8"))
            self.assertIn("old-records/demo", collected.read_text(encoding="utf-8"))
            self.assertEqual(len(changed), 2)

    def test_apply_is_idempotent_in_a_temp_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "collect" / "demo"
            source.mkdir(parents=True)
            (source / "README.md").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)

            rows = migrate_mods.build_plan(root, sample_data())
            moved = migrate_mods.apply_plan(rows, root)
            self.assertTrue(moved[0].startswith("MOVED"))
            self.assertFalse(source.exists())
            self.assertTrue((root / "mods" / "collected" / "demo" / "README.md").exists())

            rows = migrate_mods.build_plan(root, sample_data())
            self.assertEqual(rows[0]["status"], "already")
            self.assertEqual(migrate_mods.apply_plan(rows, root), [])

    def test_manifest_round_trip_and_drift_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "collect" / "demo"
            source.mkdir(parents=True)
            (source / "README.md").write_text("demo\n", encoding="utf-8")
            rows = migrate_mods.build_plan(root, sample_data())
            manifest = root / "migration.json"
            migrate_mods.write_manifest(manifest, rows, root)
            self.assertEqual(migrate_mods.validate_manifest(manifest, rows, root), [])

            (source / "extra.txt").write_text("changed\n", encoding="utf-8")
            rows = migrate_mods.build_plan(root, sample_data())
            self.assertTrue(
                any("manifest drift" in problem for problem in
                    migrate_mods.validate_manifest(manifest, rows, root))
            )


if __name__ == "__main__":
    unittest.main()
