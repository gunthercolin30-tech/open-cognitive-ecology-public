from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oif.audit.redundancy_candidate_analyzer import OIFRedundancyCandidateAnalyzer, STATUS


class RedundancyCandidateAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "mods").mkdir()
        (self.root / "oif_audit").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_case(self, sources, candidates, metadata=None):
        modules = []
        metadata = metadata or {}
        for rel, text in sources.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            module = rel[:-3].replace("/", ".")
            extra = metadata.get(module, {})
            modules.append({
                "module": module, "path": rel,
                "classification": extra.get("classification", "interface_source"),
                "entrypoints": extra.get("entrypoints", []),
                "gate_references": extra.get("gate_references", []),
                "representative_entrypoint": extra.get("representative_entrypoint", False),
            })
        fingerprint = "f" * 64
        (self.root / "oif_audit" / "oif_active_interface_inventory.json").write_text(
            json.dumps({"source_fingerprint": fingerprint, "modules": modules}), encoding="utf-8")
        (self.root / "oif_audit" / "oif_redundancy_report.json").write_text(
            json.dumps({"source_fingerprint": fingerprint, "candidates": candidates}), encoding="utf-8")

    def _single(self):
        result = OIFRedundancyCandidateAnalyzer(self.root, self.root / "oif_audit").build()
        self.assertEqual(result["candidate_count"], 1)
        return result["analyses"][0]

    def test_true_view_requires_convergent_structure(self):
        self._write_case(
            {
                "mods/core.py": '"""Core producer."""\ndef collect():\n    return {"x": 1}\n',
                "mods/dashboard_view.py": '"""Render dashboard view."""\nfrom mods.core import collect\ndef render_dashboard():\n    return str(collect())\n',
            },
            [{"left": "mods.core", "right": "mods.dashboard_view", "name_jaccard": 0.45}],
        )
        item = self._single()
        self.assertEqual(item["classification"], "VIEW")
        self.assertEqual(item["decision_rule"], "multi_evidence_view_relation")

    def test_dashboard_name_alone_is_not_view(self):
        self._write_case(
            {
                "mods/core.py": 'def compute():\n    return 1\n',
                "mods/dashboard.py": 'def autonomous_policy():\n    return 2\n',
            },
            [{"left": "mods.core", "right": "mods.dashboard", "name_jaccard": 0.40}],
        )
        self.assertNotEqual(self._single()["classification"], "VIEW")

    def test_true_adapter_requires_delegation_or_transformation(self):
        self._write_case(
            {
                "mods/core.py": 'def execute(value):\n    return value\n',
                "mods/core_adapter.py": '"""Transform and delegate values."""\nfrom mods.core import execute\ndef transform(value):\n    return execute(str(value))\n',
            },
            [{"left": "mods.core", "right": "mods.core_adapter", "name_jaccard": 0.70}],
        )
        self.assertEqual(self._single()["classification"], "ADAPTER")

    def test_interface_name_alone_is_not_adapter(self):
        self._write_case(
            {
                "mods/core.py": 'def compute():\n    return 1\n',
                "mods/interface.py": 'def independent():\n    return 2\n',
            },
            [{"left": "mods.core", "right": "mods.interface", "name_jaccard": 0.45}],
        )
        self.assertNotEqual(self._single()["classification"], "ADAPTER")

    def test_probable_redundancy_is_reachable(self):
        source = '"""Same service."""\ndef execute(value):\n    return value + 1\n'
        self._write_case(
            {"mods/a.py": source, "mods/b.py": source},
            [{"left": "mods.a", "right": "mods.b", "name_jaccard": 0.95}],
        )
        self.assertEqual(self._single()["classification"], "PROBABLE_REDUNDANCY")

    def test_partial_overlap_is_reachable(self):
        self._write_case(
            {
                "mods/a.py": 'def shared():\n    helper()\ndef only_a():\n    return 1\ndef helper():\n    return 0\n',
                "mods/b.py": 'def shared():\n    helper()\ndef only_b():\n    return 2\ndef helper():\n    return 0\n',
            },
            [{"left": "mods.a", "right": "mods.b", "name_jaccard": 0.65}],
        )
        self.assertEqual(self._single()["classification"], "PARTIAL_OVERLAP")

    def test_human_review_is_reachable(self):
        self._write_case(
            {
                "mods/a.py": 'def alpha():\n    return 1\n',
                "mods/b.py": 'def beta():\n    return 2\n',
            },
            [{"left": "mods.a", "right": "mods.b", "name_jaccard": 1.00}],
        )
        self.assertEqual(self._single()["classification"], "HUMAN_REVIEW_REQUIRED")

    def test_deterministic_and_no_automatic_change(self):
        self._write_case(
            {"mods/a.py": 'def a():\n    return 1\n', "mods/b.py": 'def b():\n    return 2\n'},
            [{"left": "mods.a", "right": "mods.b", "name_jaccard": 0.1}],
        )
        analyzer = OIFRedundancyCandidateAnalyzer(self.root, self.root / "oif_audit")
        first, second = analyzer.build(), analyzer.build()
        self.assertEqual(first, second)
        self.assertEqual(first["status"], STATUS)
        self.assertFalse(first["automatic_changes_made"])
        self.assertTrue(all(not item["automatic_change_authorized"] for item in first["analyses"]))

    def test_duplicate_pair_fails_closed(self):
        self._write_case(
            {"mods/a.py": 'def a():\n    return 1\n', "mods/b.py": 'def b():\n    return 2\n'},
            [
                {"left": "mods.a", "right": "mods.b", "name_jaccard": 0.1},
                {"left": "mods.b", "right": "mods.a", "name_jaccard": 0.1},
            ],
        )
        with self.assertRaises(ValueError):
            OIFRedundancyCandidateAnalyzer(self.root, self.root / "oif_audit").build()

    def test_persisted_outputs_and_manifest(self):
        self._write_case(
            {"mods/a.py": 'def a():\n    return 1\n', "mods/b.py": 'def b():\n    return 2\n'},
            [{"left": "mods.a", "right": "mods.b", "name_jaccard": 0.1}],
        )
        out = self.root / "out"
        result = OIFRedundancyCandidateAnalyzer(self.root, self.root / "oif_audit").write(out)
        self.assertEqual(result["candidate_count"], 1)
        self.assertTrue((out / "oif_redundancy_qualitative_manifest.sha256").is_file())
        self.assertEqual(len(list(out.glob("oif_redundancy_*"))), 6)

    def test_external_output_is_rejected(self):
        self._write_case(
            {"mods/a.py": 'def a():\n    return 1\n', "mods/b.py": 'def b():\n    return 2\n'},
            [{"left": "mods.a", "right": "mods.b", "name_jaccard": 0.1}],
        )
        external = Path(tempfile.mkdtemp())
        try:
            with self.assertRaises(ValueError):
                OIFRedundancyCandidateAnalyzer(self.root, self.root / "oif_audit").step(
                    inputs={"output_dir": str(external)}, persist=True)
        finally:
            external.rmdir()


if __name__ == "__main__":
    unittest.main()
