#!/usr/bin/env python3
from ontology.acee_meta_analysis import ACEEMetaAnalysis


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {
                    "observation_id": "lock-1",
                    "effect_size": 0.1,
                    "variance": 0.1,
                },
                {
                    "observation_id": "lock-2",
                    "effect_size": 0.12,
                    "variance": 0.1,
                },
            ]
        },
        persist=False,
    )
    assert result["meta_analysis_complete"] is True
    assert result["epistemic_status"]["functional_conclusion_only"] is True
    assert result["epistemic_status"]["phenomenology_undetermined"] is True
    for field in (
        "certification_performed",
        "selection_performed",
        "execution_authorized",
        "schedule_created",
        "installation_completed",
        "mutation_executed",
        "rollback_performed",
    ):
        assert result[field] is False
    print("ACEE_META_ANALYSIS_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
