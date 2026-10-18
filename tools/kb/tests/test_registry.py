from __future__ import annotations

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

    def test_initial_id_marks_chinese_only_name_for_manual_review(self):
        self.assertEqual(
            registry.initial_id("", {}, "01-xml-中文模块"),
            "unidentified-01",
        )
        self.assertEqual(
            registry.initial_id("RunningBugs.modname", {}, "45-standalone-TargetLine"),
            "targetline",
        )

    def test_v2_registry_normalizes_to_v3(self):
        data = {
            "mods": [
                {
                    "id": "legacy-record",
                    "category": "record-only",
                    "package_id": "example.mod",
                    "legacy_paths": [],
                    "record_paths": ["收录/example"],
                }
            ]
        }
        normalized = registry.normalize_registry(data)
        entry = normalized["objects"][0]
        self.assertEqual(entry["origin"], "collected")
        self.assertIsNone(entry["code"])
        self.assertEqual(entry["record"]["path"], "records/legacy-record")
        self.assertEqual(entry["record"]["legacy_paths"], ["收录/example"])

    def test_v3_code_and_record_are_independent(self):
        entry = registry.normalize_entry({
            "id": "demo",
            "origin": "owned",
            "package_id": "demo.mod",
            "display_name": "Demo",
            "aliases": [],
            "code": {"legacy_paths": ["自建/01-xml-Demo"], "target_path": "mods/owned/demo"},
            "record": {"path": "records/demo"},
        })
        self.assertEqual(registry.entry_kind(entry), "code+record")
        self.assertEqual(entry["code"]["target_path"], "mods/owned/demo")
        self.assertEqual(entry["record"]["path"], "records/demo")

    def test_aliases_resolve(self):
        data = {"objects": [{"id": "x", "aliases": ["old-x"]}]}
        self.assertEqual(registry.resolve_id(data, "old-x"), "x")
        self.assertIsNone(registry.resolve_id(data, "missing"))

    def test_duplicate_alias_is_rejected(self):
        data = {"objects": [
            {"id": "a", "aliases": ["same"]},
            {"id": "b", "aliases": ["same"]},
        ]}
        with self.assertRaises(registry.RegistryError):
            registry.aliases_for(data)

    def test_record_only_has_no_target_path(self):
        self.assertIsNone(
            registry.target_path_for({"id": "x", "category": "record-only"})
        )

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
                entry = {
                    "id": "demo",
                    "origin": "owned",
                    "code": {
                        "legacy_paths": ["自建/01-xml-Demo"],
                        "target_path": "mods/owned/demo",
                    },
                }
                with self.assertRaises(registry.RegistryError):
                    registry.active_path_for(entry)
            finally:
                registry.REPO_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
