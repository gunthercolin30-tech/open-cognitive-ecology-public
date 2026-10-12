from __future__ import annotations

import copy
import shutil
import tempfile
from pathlib import Path

from acee6_k6_campaign_support import FAST_DISTRIBUTION
from acee6_k7_longitudinal_runner import _run_triplet, run_reduced
from acee6_k7_report_verifier import verify_k7_report


def _assert_shared_campaign() -> dict:
    """Run the reduced K7 campaign once and reuse its immutable result."""
    out = run_reduced(False)
    assert out["verification"]["valid"], out

    report = out["report"]
    comparison = report["comparison"]

    assert comparison["valid"], comparison
    print("ACEE6_K7_FUNCTIONAL_OK")

    assert comparison["hash_drift_count"] == 0, comparison
    print("ACEE6_K7_HASH_DRIFT_OK")

    raw = [report["campaigns"][name]["raw_hashes"] for name in ("A", "B", "C")]
    normalized = [
        report["campaigns"][name]["normalized_hashes"]
        for name in ("A", "B", "C")
    ]
    assert normalized[0] == normalized[1] == normalized[2], normalized
    expected_hash_keys = {
        "transaction_chain_hash",
        "segment_chain_hash",
        "campaign_hash",
        "report_hash",
    }
    assert all(set(item) == expected_hash_keys for item in raw), raw
    assert report["public_schema_version"] == "1.1.0", report
    print("ACEE6_K7_HASH_VIEWS_OK")

    assert comparison["decision_drift_count"] == 0, comparison
    assert comparison["unexpected_numerical_drift_count"] == 0, comparison
    print("ACEE6_K7_DECISION_NUMERICAL_OK")

    assert comparison["restart_drift_count"] == 0, comparison
    print("ACEE6_K7_RESTART_DRIFT_OK")

    assert comparison["resource_drift_threshold_breach_count"] == 0, comparison
    assert comparison["performance_drift_threshold_breach_count"] == 0, comparison
    print("ACEE6_K7_RESOURCE_PERFORMANCE_OK")

    tampered = copy.deepcopy(report)
    tampered["comparison"]["hash_drift_count"] = 1
    assert not verify_k7_report(tampered)["valid"], tampered

    tampered = copy.deepcopy(report)
    tampered["campaigns"]["B"]["normalized_hashes"]["campaign_hash"] = "0" * 64
    assert not verify_k7_report(tampered)["valid"], tampered
    print("ACEE6_K7_TAMPER_OK")

    return out


def _assert_cleanup() -> None:
    workspace = Path(tempfile.mkdtemp(prefix="acee6_k7_cleanup_"))
    try:
        out = _run_triplet(
            root=workspace,
            distribution=FAST_DISTRIBUTION,
            segment_size=10,
            seed_value=6006,
            interrupt_at=7,
        )
        assert out["verification"]["valid"], out
    finally:
        shutil.rmtree(workspace, ignore_errors=False)

    assert not workspace.exists(), workspace
    print("ACEE6_K7_CLEANUP_OK")


def main() -> None:
    _assert_shared_campaign()
    _assert_cleanup()
    print("ACEE6_K7_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
