from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "kb"))
import registry


class RegistryTests(unittest.TestCase):
    def test_normalize_id_collapses_separators(self):
        self.assertEqual(registry.normalize_id("RimTalk.Style_Expand"), "rimtalk-style-expand")
        self.assertEqual(registry.normalize_id("Maiya.RimTalkDynamicColors"), "maiya-rimtalkdynamiccolors")

    def test_initial_id_uses_suffix_for_duplicate_package(self):
        self.assertEqual(
            registry.initial_id("dup.pid", {"dup.pid": 2}, "03-standalone-RecipeBook"),
            "dup-pid-recipebook",
        )

    def test_initial_id_uses_legacy_name_when_package_missing(self):
        self.assertEqual(
            registry.initial_id("", {}, "06-empty-ColonyManager_zh"),
            "colonymanager-zh",
        )

    def test_aliases_resolve(self):
        data = {"mods": [{"id": "x", "aliases": ["old-x"]}]}
        self.assertEqual(registry.resolve_id(data, "old-x"), "x")
        self.assertIsNone(registry.resolve_id(data, "missing"))

    def test_duplicate_alias_is_rejected(self):
        data = {"mods": [
            {"id": "a", "aliases": ["same"]},
            {"id": "b", "aliases": ["same"]},
        ]}
        with self.assertRaises(registry.RegistryError):
            registry.aliases_for(data)

    def test_record_only_has_no_target_path(self):
        self.assertIsNone(registry.target_path_for({"id": "x", "category": "record-only"}))

    def test_active_path_rejects_duplicate_legacy_and_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / "自建" / "01-xml-Demo"
            new = root / "mods" / "owned" / "demo"
            old.mkdir(parents=True)
            new.mkdir(parents=True)
            original_root = registry.REPO_ROOT
            registry.REPO_ROOT = root
            try:
                entry = {"id": "demo", "category": "owned", "legacy_paths": ["自建/01-xml-Demo"]}
                with self.assertRaises(registry.RegistryError):
                    registry.active_path_for(entry)
            finally:
                registry.REPO_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
