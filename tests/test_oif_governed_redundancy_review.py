from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from oif.review.governed_redundancy_review import (
    CONFIRMATION_PHRASE,
    GovernedRedundancyReview,
    build_workbook,
)


class GovernedRedundancyReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "oif_audit").mkdir()
        (self.root / "ontology").mkdir()
        left = self.root / "ontology/left.py"
        right = self.root / "ontology/right.py"
        left.write_text("def step():\n    return 'left'\n", encoding="utf-8")
        right.write_text("def step():\n    return 'right'\n", encoding="utf-8")
        import hashlib
        def h(path: Path) -> str:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        inventory = {
            "modules": [
                {"module": "ontology.left", "path": "ontology/left.py", "classification": "interface_source", "source_sha256": h(left), "functions": ["step"], "classes": [], "imports": [], "entrypoints": ["step"], "gate_references": [], "persistence_calls": [], "representative_entrypoint": False},
                {"module": "ontology.right", "path": "ontology/right.py", "classification": "interface_source", "source_sha256": h(right), "functions": ["step"], "classes": [], "imports": [], "entrypoints": ["step"], "gate_references": [], "persistence_calls": [], "representative_entrypoint": False},
            ]
        }
        analysis = {
            "source_fingerprint": "fixture",
            "automatic_changes_made": False,
            "analyses": [
                {"candidate_id": "c1", "classification": "HUMAN_REVIEW_REQUIRED", "confidence": "LOW", "combined_score": 0.5, "decision_rule": "uncertain", "recommendation": "manual", "automatic_change_authorized": False, "evidence": ["x"], "contradicting_evidence": [], "left": "ontology.left", "right": "ontology.right"},
                {"candidate_id": "c2", "classification": "DISTINCT", "confidence": "HIGH", "combined_score": 0.1, "decision_rule": "distinct", "recommendation": "retain", "automatic_change_authorized": False, "evidence": ["y"], "contradicting_evidence": [], "left": "ontology.left", "right": "ontology.right"},
            ],
        }
        (self.root / "oif_audit/oif_active_interface_inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
        (self.root / "oif_audit/oif_redundancy_qualitative_analysis.json").write_text(json.dumps(analysis), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _prepared(self) -> Path:
        return GovernedRedundancyReview(self.root).prepare(self.root / "out")

    def _complete(self, path: Path) -> None:
        workbook = json.loads(path.read_text(encoding="utf-8"))
        decision = workbook["entries"][0]["human_decision"]
        decision.update({"decision": "DISTINCT", "reviewer_id": "tester", "reviewer_role": "principal_investigator", "rationale": "The two interfaces expose measurably distinct functional responsibilities."})
        path.write_text(json.dumps(workbook, indent=2), encoding="utf-8")

    def test_prepare_filters_distinct_and_is_deterministic(self) -> None:
        first = build_workbook(self.root)
        second = build_workbook(self.root)
        self.assertEqual(first, second)
        self.assertEqual(first["candidate_count"], 1)
        self.assertFalse(first["automatic_changes_made"])

    def test_functional_apply_and_replay(self) -> None:
        path = self._prepared()
        self._complete(path)
        engine = GovernedRedundancyReview(self.root)
        first = engine.apply(path, CONFIRMATION_PHRASE)
        second = engine.apply(path, CONFIRMATION_PHRASE)
        self.assertEqual(first["appended_count"], 1)
        self.assertEqual(second["appended_count"], 0)
        self.assertEqual(second["replayed_count"], 1)
        self.assertFalse(first["code_change_performed"])

    def test_degradation_source_drift_fails_closed(self) -> None:
        path = self._prepared()
        self._complete(path)
        (self.root / "ontology/left.py").write_text("def changed():\n    return True\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "source drift"):
            GovernedRedundancyReview(self.root).apply(path, CONFIRMATION_PHRASE)

    def test_tampered_immutable_candidate_fails_closed(self) -> None:
        path = self._prepared()
        self._complete(path)
        workbook = json.loads(path.read_text(encoding="utf-8"))
        workbook["entries"][0]["left"] = "ontology.other"
        path.write_text(json.dumps(workbook), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "immutable candidate"):
            GovernedRedundancyReview(self.root).apply(path, CONFIRMATION_PHRASE)

    def test_confirmation_and_rationale_are_required(self) -> None:
        path = self._prepared()
        self._complete(path)
        with self.assertRaises(PermissionError):
            GovernedRedundancyReview(self.root).apply(path, "wrong")
        workbook = json.loads(path.read_text(encoding="utf-8"))
        workbook["entries"][0]["human_decision"]["rationale"] = "too short"
        path.write_text(json.dumps(workbook), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "rationale"):
            GovernedRedundancyReview(self.root).apply(path, CONFIRMATION_PHRASE)


if __name__ == "__main__":
    unittest.main()
