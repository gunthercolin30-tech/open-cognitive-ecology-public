import json
from pathlib import Path
from pprint import pprint

from ontology.acee_final_certifier import (
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
    for expected_campaign in REQUIRED_CAMPAIGNS:
        path = (
            EVIDENCE_DIR
            / FILENAMES[expected_campaign]
        )

        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

        print()
        print("=" * 72)
        print(expected_campaign)
        print(path)

        pprint({
            "campaign":
                payload.get("campaign"),
            "status":
                payload.get("status"),
            "passed":
                payload.get("passed"),
            "evidence_hash":
                payload.get("evidence_hash"),
            "metrics":
                payload.get("metrics"),
            "thresholds":
                payload.get("thresholds"),
            "limitations":
                payload.get("limitations"),
            "keys":
                sorted(payload),
        })


if __name__ == "__main__":
    main()
