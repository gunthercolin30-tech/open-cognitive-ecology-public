from pathlib import Path
from pprint import pprint

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

    print("Evidence paths:")

    for campaign, path in zip(
        REQUIRED_CAMPAIGNS,
        evidence_paths,
    ):
        print(
            campaign,
            path.exists(),
            path,
        )

    result = ACEEFinalCertifier().step(
        inputs={
            "evidence_paths": evidence_paths,
        },
        persist=False,
    )

    pprint({
        "status":
            result.get("status"),
        "certification_complete":
            result.get("certification_complete"),
        "all_campaigns_passed":
            result.get("all_campaigns_passed"),
        "evidence_integrity_verified":
            result.get(
                "evidence_integrity_verified"
            ),
        "error_count":
            result.get("error_count"),
        "missing_campaigns":
            result.get("missing_campaigns"),
        "failed_campaigns":
            result.get("failed_campaigns"),
        "invalid_campaigns":
            result.get("invalid_campaigns"),
        "duplicate_campaigns":
            result.get("duplicate_campaigns"),
        "unknown_campaigns":
            result.get("unknown_campaigns"),
        "evidence":
            result.get("evidence"),
        "diagnostics":
            result.get("diagnostics"),
        "limitations":
            result.get("limitations"),
    })


if __name__ == "__main__":
    main()
