from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from oif.review.governed_redundancy_review import _entry_hash
from oif.ui import campaign_service as campaign_module
from oif.ui.campaign_service import OIFReviewCampaignService, WORKBOOK_NAME

LOCK_VERSION = "oif1-atomic-persistence-crash-restart-final-lock-v1"


def build_fixture(root: Path) -> Path:
    campaign = root / "oif_review/campaigns/OIF-B4-atomic"
    campaign.mkdir(parents=True)
    entry = {
        "position": 1,
        "candidate_id": "candidate-0",
        "proposed_classification": "PARTIAL_OVERLAP",
        "confidence": "MEDIUM",
        "combined_score": 0.5,
        "decision_rule": "atomic_rule",
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
            "decision": "", "reviewer_id": "",
            "reviewer_role": "principal_investigator", "rationale": "",
        },
    }
    entry["entry_hash"] = _entry_hash(entry)
    workbook = {
        "campaign_id": "OIF-B4-atomic",
        "candidate_count": 1,
        "automatic_changes_made": False,
        "entries": [entry],
        "workbook_hash": "baseline",
    }
    path = campaign / WORKBOOK_NAME
    path.write_text(json.dumps(workbook), encoding="utf-8")
    return path


def assert_clean(path: Path) -> None:
    assert not list(path.parent.glob(f".{path.name}.*"))


def save(service: OIFReviewCampaignService) -> None:
    service.save_decision(
        "candidate-0", "DISTINCT", "reviewer",
        "principal_investigator",
        "The candidate retains a distinct measurable functional responsibility.",
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        path = build_fixture(root)
        service = OIFReviewCampaignService(root, path)
        baseline = path.read_bytes()

        # Failure while serializing: target remains byte-identical and temp is cleaned.
        with patch.object(campaign_module.json, "dump", side_effect=OSError("injected-json-dump")):
            try:
                save(service)
            except OSError:
                pass
            else:
                raise AssertionError("json.dump failure was not propagated")
        assert path.read_bytes() == baseline
        assert_clean(path)
        print("OIF1_ATOMIC_CRASH_DURING_SERIALIZATION_OK")

        # Failure at fsync: target remains byte-identical and temp is cleaned.
        with patch.object(campaign_module.os, "fsync", side_effect=OSError("injected-fsync")):
            try:
                save(service)
            except OSError:
                pass
            else:
                raise AssertionError("fsync failure was not propagated")
        assert path.read_bytes() == baseline
        assert_clean(path)
        print("OIF1_ATOMIC_CRASH_BEFORE_REPLACE_OK")

        # Failure at replace: target remains byte-identical and temp is cleaned.
        with patch.object(campaign_module.os, "replace", side_effect=OSError("injected-replace")):
            try:
                save(service)
            except OSError:
                pass
            else:
                raise AssertionError("replace failure was not propagated")
        assert path.read_bytes() == baseline
        assert_clean(path)
        print("OIF1_ATOMIC_REPLACE_FAILURE_ROLLBACK_OK")

        # Successful persistence must survive a fresh service instance.
        save(service)
        after = json.loads(path.read_text(encoding="utf-8"))
        assert after["entries"][0]["human_decision"]["decision"] == "DISTINCT"
        restarted = OIFReviewCampaignService(root, path)
        reloaded = restarted.load()
        assert reloaded == after
        assert restarted.summary(reloaded)["decided_count"] == 1
        assert_clean(path)
        print("OIF1_ATOMIC_RESTART_ROUNDTRIP_OK")

        # Corrupt workbooks fail closed and are never silently rewritten.
        corrupt_cases = [b"", b"{", b"[]", b'{"entries": []}']
        for index, data in enumerate(corrupt_cases):
            corrupt_root = root / f"corrupt-{index}"
            corrupt_path = build_fixture(corrupt_root)
            corrupt_path.write_bytes(data)
            before = corrupt_path.read_bytes()
            corrupt_service = OIFReviewCampaignService(corrupt_root, corrupt_path)
            try:
                corrupt_service.load()
            except (ValueError, TypeError, json.JSONDecodeError):
                pass
            else:
                raise AssertionError(f"corrupt workbook accepted: {index}")
            assert corrupt_path.read_bytes() == before
            assert_clean(corrupt_path)
        print("OIF1_ATOMIC_CORRUPTION_FAIL_CLOSED_OK")

        print("OIF1_ATOMIC_PERSISTENCE_CRASH_RESTART_FINAL_LOCK_OK")
        print({"lock_version": LOCK_VERSION, "failure_injection_count": 3, "corrupt_case_count": 4})


if __name__ == "__main__":
    main()
