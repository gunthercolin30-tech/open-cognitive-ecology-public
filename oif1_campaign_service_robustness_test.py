from __future__ import annotations

import json
import os
import stat
import tempfile
import threading
from pathlib import Path

from oif.review.governed_redundancy_review import _entry_hash
from oif.ui.campaign_service import OIFReviewCampaignService, WORKBOOK_NAME


def build_fixture(root: Path, count: int = 8) -> Path:
    campaign = root / "oif_review/campaigns/OIF-B4-crown"
    campaign.mkdir(parents=True)
    entries = []
    for index in range(count):
        entry = {
            "position": index + 1,
            "candidate_id": f"candidate-{index}",
            "proposed_classification": "PARTIAL_OVERLAP",
            "confidence": "MEDIUM",
            "combined_score": 0.5,
            "decision_rule": "crown_rule",
            "recommendation": "review",
            "automatic_change_authorized": False,
            "evidence": ["one"],
            "contradicting_evidence": [],
            "left": f"ontology.left{index}",
            "right": f"ontology.right{index}",
            "left_dossier": {"path": f"ontology/left{index}.py"},
            "right_dossier": {"path": f"ontology/right{index}.py"},
            "candidate_payload_hash": f"a{index}",
            "source_pair_hash": f"b{index}",
            "human_decision": {
                "decision": "", "reviewer_id": "",
                "reviewer_role": "principal_investigator", "rationale": "",
            },
        }
        entry["entry_hash"] = _entry_hash(entry)
        entries.append(entry)
    workbook = {
        "campaign_id": "OIF-B4-crown",
        "candidate_count": len(entries),
        "automatic_changes_made": False,
        "entries": entries,
        "workbook_hash": "baseline",
    }
    path = campaign / WORKBOOK_NAME
    path.write_text(json.dumps(workbook), encoding="utf-8")
    return path


def _assert_no_temp_files(path: Path) -> None:
    leftovers = list(path.parent.glob(f".{path.name}.*"))
    assert not leftovers, leftovers


def _permission_probe(directory: Path) -> bool:
    """Return True only when this runtime actually enforces directory denial."""
    probe = directory / ".oif-permission-probe"
    try:
        probe.write_text("probe", encoding="utf-8")
    except OSError:
        return True
    else:
        try:
            probe.unlink()
        except OSError:
            pass
        return False


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        path = build_fixture(root)
        service = OIFReviewCampaignService(root, path)
        before_snapshot = service.immutable_snapshot()

        errors = []

        def worker(index: int) -> None:
            try:
                service.save_decision(
                    f"candidate-{index}", "DISTINCT", f"reviewer-{index}",
                    "principal_investigator",
                    "This decision records a distinct measurable functional responsibility.",
                )
            except Exception as exc:  # pragma: no cover - asserted below
                errors.append(repr(exc))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert not errors, errors
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert sum(bool(e["human_decision"]["decision"]) for e in payload["entries"]) == 8
        assert service.immutable_snapshot() == before_snapshot
        _assert_no_temp_files(path)
        print("OIF1_CAMPAIGN_CONCURRENCY_OK")

        outside = root / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        try:
            OIFReviewCampaignService(root, outside)
        except ValueError:
            pass
        else:
            raise AssertionError("path escape accepted")

        symlink = path.parent / "linked_workbook.json"
        symlink.symlink_to(outside)
        try:
            OIFReviewCampaignService(root, symlink)
        except (ValueError, FileNotFoundError):
            pass
        else:
            raise AssertionError("hostile symlink accepted")
        print("OIF1_CAMPAIGN_HOSTILE_PATHS_OK")

        # A read-only target file may still be atomically replaced on POSIX when
        # the parent directory is writable. Record that semantics instead of
        # treating it as a service defect.
        readonly_root = root / "readonly-file-case"
        readonly_path = build_fixture(readonly_root, count=1)
        readonly_service = OIFReviewCampaignService(readonly_root, readonly_path)
        original_mode = stat.S_IMODE(readonly_path.stat().st_mode)
        readonly_path.chmod(0o444)
        try:
            try:
                readonly_service.save_decision(
                    "candidate-0", "DISTINCT", "reviewer",
                    "principal_investigator",
                    "A complete governed decision remains valid after atomic replacement.",
                )
            except OSError:
                # Also acceptable on platforms that enforce target permissions.
                pass
            json.loads(readonly_path.read_text(encoding="utf-8"))
            _assert_no_temp_files(readonly_path)
        finally:
            readonly_path.chmod(original_mode)
        print("OIF1_CAMPAIGN_READONLY_FILE_SEMANTICS_OK")

        # The meaningful denial boundary for mkstemp + os.replace is the parent
        # directory. Probe enforcement first because privileged runtimes and
        # some filesystems can bypass chmod-based denial.
        denied_root = root / "readonly-directory-case"
        denied_path = build_fixture(denied_root, count=1)
        denied_service = OIFReviewCampaignService(denied_root, denied_path)
        parent = denied_path.parent
        parent_mode = stat.S_IMODE(parent.stat().st_mode)
        original_bytes = denied_path.read_bytes()
        parent.chmod(0o555)
        try:
            enforced = _permission_probe(parent)
            if enforced:
                try:
                    denied_service.save_decision(
                        "candidate-0", "COMPLEMENTARY", "reviewer",
                        "principal_investigator",
                        "The interfaces cooperate while retaining separate governed contracts.",
                    )
                except OSError:
                    pass
                else:
                    raise AssertionError("read-only directory write unexpectedly succeeded")
                assert denied_path.read_bytes() == original_bytes
                _assert_no_temp_files(denied_path)
                print("OIF1_CAMPAIGN_READONLY_DIRECTORY_FAIL_CLOSED_OK")
            else:
                print("OIF1_CAMPAIGN_PERMISSION_ENFORCEMENT_UNAVAILABLE")
                print("OIF1_CAMPAIGN_PERMISSION_TEST_SKIPPED_WITH_EVIDENCE")
        finally:
            parent.chmod(parent_mode)
        assert parent.exists()
        print("OIF1_CAMPAIGN_PERMISSION_CLEANUP_OK")
        print("OIF1_CAMPAIGN_SERVICE_ROBUSTNESS_TEST_OK")


if __name__ == "__main__":
    main()
