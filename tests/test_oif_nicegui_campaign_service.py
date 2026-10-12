from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from oif.review.governed_redundancy_review import _entry_hash
from oif.ui.campaign_service import OIFReviewCampaignService


class TestOIFNiceGUICampaignService(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.campaign = self.root / "oif_review/campaigns/OIF-B4-test"
        self.campaign.mkdir(parents=True)
        entry = {
            "position": 1,
            "candidate_id": "candidate-1",
            "proposed_classification": "PARTIAL_OVERLAP",
            "confidence": "MEDIUM",
            "combined_score": 0.5,
            "decision_rule": "test_rule",
            "recommendation": "review",
            "automatic_change_authorized": False,
            "evidence": ["one"],
            "contradicting_evidence": [],
            "left": "ontology.left",
            "right": "ontology.right",
            "left_dossier": {"path": "ontology/left.py"},
            "right_dossier": {"path": "ontology/right.py"},
            "candidate_payload_hash": "a",
            "source_pair_hash": "b",
            "human_decision": {
                "decision": "",
                "reviewer_id": "",
                "reviewer_role": "principal_investigator",
                "rationale": "",
            },
        }
        entry["entry_hash"] = _entry_hash(entry)
        workbook = {
            "campaign_id": "OIF-B4-test",
            "candidate_count": 1,
            "automatic_changes_made": False,
            "entries": [entry],
            "workbook_hash": "baseline",
        }
        self.path = self.campaign / "governed_redundancy_review_workbook.json"
        self.path.write_text(json.dumps(workbook), encoding="utf-8")
        self.service = OIFReviewCampaignService(self.root, self.path)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_functional_save_and_resume(self) -> None:
        result = self.service.save_decision(
            "candidate-1",
            "DISTINCT",
            "tester",
            "principal_investigator",
            "These interfaces expose distinct measurable functional responsibilities.",
        )
        self.assertTrue(result["saved"])
        self.assertFalse(result["registry_write_performed"])
        resumed = OIFReviewCampaignService(self.root, self.path).load()
        self.assertEqual(resumed["entries"][0]["human_decision"]["decision"], "DISTINCT")

    def test_degradation_rejects_short_rationale(self) -> None:
        with self.assertRaisesRegex(ValueError, "rationale"):
            self.service.save_decision(
                "candidate-1",
                "DISTINCT",
                "tester",
                "principal_investigator",
                "too short",
            )

    def test_degradation_rejects_path_escape(self) -> None:
        outside = self.root / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "escapes"):
            OIFReviewCampaignService(self.root, outside)

    def test_non_regression_immutable_hashes_unchanged(self) -> None:
        before = self.service.immutable_snapshot()
        self.service.save_decision(
            "candidate-1",
            "COMPLEMENTARY",
            "tester",
            "principal_investigator",
            "The interfaces cooperate while retaining separate functional contracts.",
        )
        after = self.service.immutable_snapshot()
        self.assertEqual(before, after)

    def test_filtering(self) -> None:
        workbook = self.service.load()
        self.assertEqual(len(self.service.filtered_entries(workbook, query="left")), 1)
        self.assertEqual(len(self.service.filtered_entries(workbook, decision_state="DECIDED")), 0)


if __name__ == "__main__":
    unittest.main()
