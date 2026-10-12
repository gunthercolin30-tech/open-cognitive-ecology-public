from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oif.audit.active_interface_auditor import AuditError, OIFActiveInterfaceAuditor


class OIFActiveInterfaceAuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "ontology").mkdir()
        (self.root / "validation").mkdir()
        (self.root / "ontology_inventory.txt").write_text(
            "demo_interface\n", encoding="utf-8"
        )
        (self.root / "dependency_registry.py").write_text(
            "DEPENDENCY_REGISTRY = {}\n", encoding="utf-8"
        )
        (self.root / "ontology" / "demo_interface.py").write_text(
            "from ontology.human_review_gate import HumanReviewGate\n"
            "from pathlib import Path\n"
            "class DemoInterface:\n"
            "    def step(self, inputs=None):\n"
            "        Path('state.json').write_text('x')\n"
            "        return {'ok': True}\n",
            encoding="utf-8",
        )
        (self.root / "ontology" / "supreme_representative_runtime.py").write_text(
            "class SupremeRepresentativeRuntime:\n"
            "    def run(self):\n"
            "        return True\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_static_discovery_and_boundaries(self) -> None:
        result = OIFActiveInterfaceAuditor(self.root).build()
        modules = result["reports"]["oif_active_interface_inventory.json"]["modules"]
        names = {item["module"] for item in modules}
        self.assertIn("ontology.demo_interface", names)

        persistence = result["reports"][
            "oif_persistence_boundary_report.json"
        ]["modules"]
        self.assertTrue(
            any(item["module"] == "ontology.demo_interface" for item in persistence)
        )

        gates = result["reports"]["oif_gate_map.json"]["modules"]
        self.assertTrue(
            any(item["module"] == "ontology.demo_interface" for item in gates)
        )

    def test_deterministic_output(self) -> None:
        auditor = OIFActiveInterfaceAuditor(self.root)
        first = auditor.write()
        hashes_a = self._hash_outputs(Path(first["output_dir"]))
        second = auditor.write()
        hashes_b = self._hash_outputs(Path(second["output_dir"]))
        self.assertEqual(hashes_a, hashes_b)
        self.assertEqual(
            first["source_fingerprint"],
            second["source_fingerprint"],
        )

    def test_degradation_syntax_error_is_reported(self) -> None:
        bad = self.root / "ontology" / "broken_dashboard.py"
        bad.write_text("def broken(:\n", encoding="utf-8")
        built = OIFActiveInterfaceAuditor(self.root).build()
        self.assertEqual(len(built["syntax_errors"]), 1)
        self.assertIn(
            "broken_dashboard",
            built["syntax_errors"][0]["module"],
        )

    def test_non_persistent_step_does_not_create_output(self) -> None:
        result = OIFActiveInterfaceAuditor(
            self.root
        ).step(inputs={}, persist=False)
        self.assertFalse((self.root / "oif_audit").exists())
        self.assertFalse(result["persisted"])

    def test_output_must_stay_inside_root(self) -> None:
        outside = Path(self.tmp.name).parent / "outside_oif_audit"
        with self.assertRaises(AuditError):
            OIFActiveInterfaceAuditor(self.root, outside)

    def test_source_files_are_not_modified(self) -> None:
        source = self.root / "ontology" / "demo_interface.py"
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        OIFActiveInterfaceAuditor(self.root).write()
        after = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(before, after)

    def test_unknown_step_input_is_rejected(self) -> None:
        with self.assertRaises(AuditError):
            OIFActiveInterfaceAuditor(self.root).step(
                inputs={"unsupported": True},
                persist=False,
            )

    def test_manifest_is_stable_and_complete(self) -> None:
        result = OIFActiveInterfaceAuditor(self.root).write()
        output = Path(result["output_dir"])
        manifest = output / "oif_baseline_manifest.sha256"
        lines = [
            line for line in manifest.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        names = {line.split("  ", 1)[1] for line in lines}
        expected = {
            "oif_active_interface_inventory.json",
            "oif_baseline_report.md",
            "oif_dependency_map.json",
            "oif_gate_map.json",
            "oif_persistence_boundary_report.json",
            "oif_redundancy_report.json",
            "oif_representative_entrypoint_map.json",
        }
        self.assertEqual(names, expected)

        for line in lines:
            digest, name = line.split("  ", 1)
            actual = hashlib.sha256((output / name).read_bytes()).hexdigest()
            self.assertEqual(digest, actual)

    def test_no_temporary_files_remain_after_write(self) -> None:
        result = OIFActiveInterfaceAuditor(self.root).write()
        output = Path(result["output_dir"])
        leftovers = [
            path.name for path in output.iterdir()
            if path.name.startswith(".")
        ]
        self.assertEqual(leftovers, [])

    @staticmethod
    def _hash_outputs(directory: Path) -> dict[str, str]:
        return {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.iterdir())
            if path.is_file()
        }


if __name__ == "__main__":
    unittest.main()
