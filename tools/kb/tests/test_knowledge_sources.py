from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "kb"))
import knowledge_sources


def make_record(root: Path, mod_id: str, targets: list[str]) -> None:
    directory = root / "records" / mod_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "README.md").write_text("# demo\n", encoding="utf-8")
    (directory / "record.json").write_text(
        json.dumps({"id": mod_id, "distilled_to": targets}, ensure_ascii=False),
        encoding="utf-8",
    )


class KnowledgeSourceTests(unittest.TestCase):
    def test_target_must_be_inside_a_knowledge_layer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(knowledge_sources.is_knowledge_target(
                root, "docs/knowledge/guides/example.md"
            ))
            self.assertFalse(knowledge_sources.is_knowledge_target(
                root, "docs/knowledge/README.md"
            ))
            self.assertFalse(knowledge_sources.is_knowledge_target(
                root, "docs/knowledge/mechanics/README.md"
            ))
            self.assertFalse(knowledge_sources.is_knowledge_target(
                root, "records/demo/README.md"
            ))
            self.assertFalse(knowledge_sources.is_knowledge_target(
                root, "../outside.md"
            ))

    def test_sync_adds_and_removes_generated_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "docs" / "knowledge" / "guides" / "example.md"
            page.parent.mkdir(parents=True)
            page.write_text("# Example\n", encoding="utf-8")
            make_record(root, "demo", ["docs/knowledge/guides/example.md"])

            changed, problems = knowledge_sources.sync_all(root, write=True)
            self.assertEqual(changed, ["docs/knowledge/guides/example.md"])
            self.assertEqual(problems, [])
            text = page.read_text(encoding="utf-8")
            self.assertIn("## 来源记录", text)
            self.assertIn("`demo`", text)
            self.assertIn("../../../records/demo/README.md", text)
            self.assertEqual(knowledge_sources.check_all(root), [])

            make_record(root, "demo", [])
            problems = knowledge_sources.check_all(root)
            self.assertTrue(any("stale 来源记录" in problem for problem in problems))
            knowledge_sources.sync_all(root, write=True)
            self.assertNotIn("## 来源记录", page.read_text(encoding="utf-8"))

    def test_manual_section_without_markers_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "docs" / "knowledge" / "reference" / "manual.md"
            page.parent.mkdir(parents=True)
            page.write_text("# Manual\n\n## 来源记录\n\n- `demo`\n", encoding="utf-8")
            make_record(root, "demo", ["docs/knowledge/reference/manual.md"])

            changed, problems = knowledge_sources.sync_all(root, write=True)
            self.assertEqual(changed, [])
            self.assertTrue(any("without generated markers" in problem for problem in problems))

    def test_missing_and_outside_targets_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "knowledge" / "guides").mkdir(parents=True)
            make_record(root, "demo", ["docs/knowledge/guides/missing.md"])
            _, problems = knowledge_sources.load_links(root)
            self.assertTrue(any("target missing" in problem for problem in problems))

            make_record(root, "other", ["records/other/README.md"])
            _, problems = knowledge_sources.load_links(root)
            self.assertTrue(any("must be a Markdown page" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
