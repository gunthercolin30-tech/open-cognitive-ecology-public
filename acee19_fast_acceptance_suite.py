#!/usr/bin/env python3
from ontology.acee_meta_analysis import ACEEMetaAnalysis


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {
                    "observation_id": "o1",
                    "effect_size": 0.20,
                    "variance": 0.04,
                    "confidence": 0.90,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                    "stability_score": 0.92,
                },
                {
                    "observation_id": "o2",
                    "effect_size": 0.24,
                    "variance": 0.05,
                    "confidence": 0.88,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                    "stability_score": 0.90,
                },
            ]
        },
        persist=False,
    )
    assert result["status"] == "ACEE_META_ANALYSIS_COMPLETE"
    assert result["included_observation_count"] == 2
    assert result["pooled_effect"] is not None
    assert result["certification_performed"] is False
    assert result["selection_performed"] is False
    assert result["execution_authorized"] is False
    print("ACEE19_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
