from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from oif.audit.redundancy_candidate_analyzer import (
    CLASSES,
    OIFRedundancyCandidateAnalyzer,
    SCHEMA_VERSION,
)

LOCK_VERSION = "oif-redundancy-structural-final-lock-v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_pair(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((str(left), str(right))))


def main() -> None:
    root = Path.home() / "open-cognitive-ecology"
    inventory_path = root / "ontology_inventory.txt"
    baseline_inventory_path = root / "oif_audit" / "oif_active_interface_inventory.json"
    baseline_candidates_path = root / "oif_audit" / "oif_redundancy_report.json"

    for required in (inventory_path, baseline_inventory_path, baseline_candidates_path):
        assert required.is_file(), "missing required file: %s" % required

    before_inventory = digest(inventory_path)
    baseline_inventory = json.loads(baseline_inventory_path.read_text(encoding="utf-8"))
    baseline_candidates = json.loads(baseline_candidates_path.read_text(encoding="utf-8"))

    expected_fingerprint = baseline_inventory["source_fingerprint"]
    assert baseline_candidates.get("source_fingerprint") == expected_fingerprint

    raw_candidates = baseline_candidates.get("candidates")
    assert isinstance(raw_candidates, list)
    expected_pairs = [canonical_pair(item["left"], item["right"]) for item in raw_candidates]
    assert len(expected_pairs) == len(set(expected_pairs)), "duplicate baseline candidate pair"

    analyzer = OIFRedundancyCandidateAnalyzer(root=root, report_dir=root / "oif_audit")
    first = analyzer.build()
    second = analyzer.build()

    assert first == second, "analyzer is not deterministic"
    assert first["schema_version"] == SCHEMA_VERSION
    assert first["source_fingerprint"] == expected_fingerprint
    assert first["candidate_count"] == len(first["analyses"])
    assert first["candidate_count"] == len(expected_pairs)
    assert sum(first["classification_counts"].values()) == first["candidate_count"]
    assert set(first["classification_counts"]) == set(CLASSES)
    assert first["automatic_changes_made"] is False

    analysis_pairs = [canonical_pair(item["left"], item["right"]) for item in first["analyses"]]
    assert set(analysis_pairs) == set(expected_pairs), "candidate coverage drift"
    assert len(analysis_pairs) == len(set(analysis_pairs)), "duplicate analyzed pair"

    candidate_ids = [item["candidate_id"] for item in first["analyses"]]
    assert len(candidate_ids) == len(set(candidate_ids)), "duplicate candidate_id"

    required_item_keys = {
        "candidate_id", "left", "right", "classification", "confidence",
        "combined_score", "evidence", "contradicting_evidence",
        "decision_rule", "recommendation", "automatic_change_authorized",
    }
    for item in first["analyses"]:
        assert required_item_keys <= set(item)
        assert item["classification"] in CLASSES
        assert item["automatic_change_authorized"] is False
        assert isinstance(item["evidence"], list)
        assert isinstance(item["contradicting_evidence"], list)
        assert item["decision_rule"]
        assert item["recommendation"]

    review_ids = [item["candidate_id"] for item in first["review_queue"]]
    assert len(review_ids) == len(set(review_ids))
    assert set(review_ids) <= set(candidate_ids)
    assert all(
        item["classification"] in {
            "PROBABLE_REDUNDANCY", "PARTIAL_OVERLAP", "HUMAN_REVIEW_REQUIRED"
        }
        for item in first["review_queue"]
    )

    with tempfile.TemporaryDirectory(dir=str(root)) as tmp:
        output = Path(tmp) / "reports"
        written = analyzer.write(output)
        assert written == first

        manifest_path = output / "oif_redundancy_qualitative_manifest.sha256"
        manifest_lines = manifest_path.read_text(encoding="utf-8").splitlines()
        assert manifest_lines
        manifested_names = set()
        for line in manifest_lines:
            expected, name = line.split("  ", 1)
            manifested_names.add(name)
            assert digest(output / name) == expected

        expected_outputs = {
            "oif_redundancy_qualitative_analysis.json",
            "oif_redundancy_review_queue.json",
            "oif_redundancy_clusters.json",
            "oif_redundancy_evidence_matrix.csv",
            "oif_redundancy_qualitative_report.md",
        }
        assert manifested_names == expected_outputs

        payload = json.loads(
            (output / "oif_redundancy_qualitative_analysis.json").read_text(encoding="utf-8")
        )
        assert payload["candidate_count"] == first["candidate_count"]
        assert payload["classification_counts"] == first["classification_counts"]
        assert len(payload["analyses"]) == first["candidate_count"]

    assert digest(inventory_path) == before_inventory

    print("OIF_REDUNDANCY_STRUCTURAL_DETERMINISM_OK")
    print("OIF_REDUNDANCY_STRUCTURAL_COVERAGE_OK")
    print("OIF_REDUNDANCY_STRUCTURAL_MANIFEST_OK")
    print("OIF_REDUNDANCY_STRUCTURAL_ONTOLOGY_IMMUTABILITY_OK")
    print("OIF_REDUNDANCY_CANDIDATE_ANALYZER_FINAL_LOCK_OK")
    print(json.dumps({
        "lock_version": LOCK_VERSION,
        "candidate_count": first["candidate_count"],
        "classification_counts": first["classification_counts"],
        "source_fingerprint": first["source_fingerprint"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
