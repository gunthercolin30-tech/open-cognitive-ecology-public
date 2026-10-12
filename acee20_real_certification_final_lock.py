from pathlib import Path

from ontology.acee_final_certifier import (
    ACEEFinalCertifier,
    REQUIRED_CAMPAIGNS,
)


ROOT = Path.home() / "open-cognitive-ecology"

EVIDENCE_DIR = (
    ROOT
    / "acee_runtime"
    / "ACEE20_evidence"
)

FILENAMES = {
    "mutation_score":
        "mutation_score_report.json",
    "long_duration_1000_cycles":
        "long_duration_1000_cycles_report.json",
    "memory_leak":
        "memory_leak_report.json",
    "numerical_drift":
        "numerical_drift_report.json",
    "hash_chain_drift":
        "hash_chain_drift_report.json",
    "decision_instability":
        "decision_instability_report.json",
    "global_validation":
        "global_validation_report.json",
}


def main():
    evidence_paths = [
        EVIDENCE_DIR / FILENAMES[campaign]
        for campaign in REQUIRED_CAMPAIGNS
    ]

    for path in evidence_paths:
        assert path.exists(), (
            f"missing evidence: {path}"
        )

    result = ACEEFinalCertifier().step(
        inputs={
            "evidence_paths": evidence_paths,
        },
        persist=True,
    )

    assert result["status"] == (
        "AUTONOMOUS_COGNITIVE_EVOLUTION_COMPLETE"
    )
    assert result["certification_complete"] is True
    assert result["all_campaigns_passed"] is True
    assert (
        result["evidence_integrity_verified"]
        is True
    )
    assert result["error_count"] == 0

    assert (
        result["epistemic_status"][
            "functional_conclusion_only"
        ]
        is True
    )
    assert (
        result["epistemic_status"][
            "phenomenology_undetermined"
        ]
        is True
    )

    print(
        "ACEE20_REAL_CERTIFICATION_FINAL_LOCK_OK"
    )


if __name__ == "__main__":
    main()
