from pathlib import Path

from oif.audit.redundancy_candidate_analyzer import (
    OIFRedundancyCandidateAnalyzer,
)


def main() -> None:
    root = Path.home() / "open-cognitive-ecology"

    result = OIFRedundancyCandidateAnalyzer(
        root=root,
        report_dir=root / "oif_audit",
    ).step(
        inputs={"output_dir": str(root / "oif_audit")},
        persist=True,
    )

    assert result["candidate_count"] == 341
    assert sum(result["classification_counts"].values()) == 341
    assert result["automatic_changes_made"] is False

    print(result["status"])
    print("candidate_count =", result["candidate_count"])
    print("classification_counts =", result["classification_counts"])
    print("OIF_REDUNDANCY_REPORTS_PERSISTED_OK")


if __name__ == "__main__":
    main()
