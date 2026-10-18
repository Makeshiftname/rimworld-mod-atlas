from __future__ import annotations
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


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


if __name__ == "__main__":
    unittest.main()
