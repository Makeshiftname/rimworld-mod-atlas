from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "kb"))
import check_records
import migrate_records_schema


def metadata(tier: str, status: str = "analyzed", distilled: list[str] | None = None) -> dict:
    return {
        "analysis_tier": tier,
        "status": status,
        "distilled_to": distilled or [],
    }


INITIAL = """# Demo

## 身份卡

identity

## 它是什么

what

## 初步核验

### 已核验

checked

### 未核验

not checked

## 下一步

next
"""

DEEP = """# Demo

## 身份卡

identity

## 它是什么

what

## 怎么验的

### 范围

scope

### 阳性对照

control

### 未核验

boundary

## 可复用结论

- [已确认] conclusion
"""


class RecordSchemaTests(unittest.TestCase):
    def test_valid_initial_record(self):
        problems, warnings = check_records.validate_structure(metadata("initial"), INITIAL)
        self.assertEqual(problems, [])
        self.assertEqual(warnings, [])

    def test_initial_requires_verified_and_unverified_subsections(self):
        text = INITIAL.replace("### 未核验\n\nnot checked\n", "")
        problems, _ = check_records.validate_structure(metadata("initial"), text)
        self.assertTrue(any("### 未核验" in item for item in problems))

    def test_initial_rejects_conclusions_and_distillation(self):
        text = INITIAL + "\n## 可复用结论\n\n- something\n\n## 修改建议\n\n- do it\n"
        problems, _ = check_records.validate_structure(
            metadata("initial", distilled=["docs/knowledge/guides/example.md"]), text
        )
        self.assertTrue(any("可复用结论" in item for item in problems))
        self.assertTrue(any("修改建议" in item for item in problems))
        self.assertTrue(any("distilled_to" in item for item in problems))

    def test_valid_deep_record(self):
        problems, warnings = check_records.validate_structure(metadata("deep"), DEEP)
        self.assertEqual(problems, [])
        self.assertEqual(warnings, [])

    def test_deep_optional_evidence_must_be_non_empty(self):
        text = DEEP.replace("### 阳性对照\n\ncontrol\n", "### 阳性对照\n\n")
        problems, _ = check_records.validate_structure(metadata("deep"), text)
        self.assertTrue(any("阳性对照" in item and "empty" in item for item in problems))

    def test_deep_distilled_link_warns_when_status_is_not_analyzed(self):
        problems, warnings = check_records.validate_structure(
            metadata("deep", status="needs-recheck",
                     distilled=["docs/knowledge/guides/example.md"]),
            DEEP,
        )
        self.assertEqual(problems, [])
        self.assertTrue(any("needs-recheck" in item for item in warnings))

    def test_invalid_tier_is_rejected(self):
        problems, _ = check_records.validate_structure(metadata("raw"), INITIAL)
        self.assertTrue(any("analysis_tier" in item for item in problems))

    def test_initial_subsection_must_be_under_initial_check(self):
        text = INITIAL.replace("### 未核验\n\nnot checked\n", "") + \
            "\n## 可复用结论\n\n### 未核验\n\nwrong place\n"
        problems, _ = check_records.validate_structure(metadata("initial"), text)
        self.assertTrue(any("### 未核验" in item for item in problems))

    def test_schema_migration_sets_deep_and_removes_verification_tier(self):
        migrated = migrate_records_schema.normalize_record({
            "schema_version": 2,
            "status": "raw",
            "verification_tier": 3,
        })
        self.assertEqual(migrated["schema_version"], 3)
        self.assertEqual(migrated["status"], "analyzed")
        self.assertEqual(migrated["analysis_tier"], "deep")
        self.assertNotIn("verification_tier", migrated)

    def test_schema_migration_preserves_initial_tier(self):
        migrated = migrate_records_schema.normalize_record({
            "schema_version": 2,
            "status": "analyzed",
            "analysis_tier": "initial",
        })
        self.assertEqual(migrated["analysis_tier"], "initial")


if __name__ == "__main__":
    unittest.main()
