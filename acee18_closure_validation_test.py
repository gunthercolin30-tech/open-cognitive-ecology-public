import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def base_candidate(candidate_id, **overrides):
    candidate = {
        "candidate_id": candidate_id,
        "predicted_gain": 0.20,
        "confidence": 0.85,
        "risk": 0.10,
        "reversibility": 0.90,
        "validation": 0.90,
        "robustness": 0.85,
        "non_closure": 0.90,
        "closure_pressure_delta": 0.0,
        "governance_compatible": True,
    }
    candidate.update(overrides)
    return candidate


def test_cross_type_identifier_collision():
    try:
        ACEEPredictionEngine().step(
            inputs={
                "candidates": [
                    base_candidate(1),
                    base_candidate("1"),
                ]
            },
            persist=False,
        )
    except ValueError as exc:
        assert str(exc) == (
            "duplicate_candidate_id:1"
        )
    else:
        raise AssertionError(
            "cross-type candidate ID collision accepted"
        )

    print(
        "ACEE18_CROSS_TYPE_ID_COLLISION_OK"
    )


def test_recommendation_precedence():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                base_candidate(
                    "governance-first",
                    governance_compatible=False,
                    closure_pressure_delta=0.50,
                    risk=0.90,
                ),
                base_candidate(
                    "closure-before-risk",
                    closure_pressure_delta=0.20,
                    risk=0.90,
                ),
                base_candidate(
                    "risk-only",
                    closure_pressure_delta=0.0,
                    risk=0.90,
                ),
            ]
        },
        persist=False,
    )

    by_id = {
        item["candidate_id"]: item
        for item in result["ranked_candidates"]
    }

    assert (
        by_id["governance-first"]["recommendation"]
        == "reject_from_prediction_pipeline"
    )
    assert (
        by_id["closure-before-risk"]["recommendation"]
        == "require_non_closure_review"
    )
    assert (
        by_id["risk-only"]["recommendation"]
        == "sandbox_longer"
    )

    print(
        "ACEE18_RECOMMENDATION_PRECEDENCE_OK"
    )


def test_score_boundaries():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                base_candidate(
                    "minimum",
                    predicted_gain=-100,
                    confidence=-100,
                    risk=100,
                    reversibility=-100,
                    validation=-100,
                    robustness=-100,
                    non_closure=-100,
                    closure_pressure_delta=100,
                    governance_compatible=False,
                ),
                base_candidate(
                    "maximum",
                    predicted_gain=100,
                    confidence=100,
                    risk=-100,
                    reversibility=100,
                    validation=100,
                    robustness=100,
                    non_closure=100,
                    closure_pressure_delta=-100,
                ),
            ]
        },
        persist=False,
    )

    for item in result["ranked_candidates"]:
        assert 0.0 <= item["prediction_score"] <= 1.0
        assert 0.0 <= item["predicted_gain"] <= 1.0
        assert 0.0 <= item["confidence"] <= 1.0
        assert 0.0 <= item["risk"] <= 1.0
        assert 0.0 <= item["reversibility"] <= 1.0
        assert 0.0 <= item["validation"] <= 1.0
        assert 0.0 <= item["robustness"] <= 1.0
        assert 0.0 <= item["non_closure"] <= 1.0

    assert (
        result["ranked_candidates"][0]["candidate_id"]
        == "maximum"
    )

    print(
        "ACEE18_SCORE_BOUNDARIES_OK"
    )


def test_derived_candidate_collision():
    try:
        ACEEPredictionEngine().step(
            inputs={
                "improvement_plan": {
                    "projected_gain": 0.20,
                    "improvement_confidence": 0.90,
                    "recommended_actions": [
                        {
                            "recommended_action":
                                "same-derived-id"
                        },
                        {
                            "recommended_action":
                                "same-derived-id"
                        },
                    ],
                }
            },
            persist=False,
        )
    except ValueError as exc:
        assert str(exc) == (
            "duplicate_candidate_id:"
            "same-derived-id"
        )
    else:
        raise AssertionError(
            "derived candidate collision accepted"
        )

    print(
        "ACEE18_DERIVED_ID_COLLISION_OK"
    )


def test_atomic_persistence_cleanup():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = (
            root
            / "acee_runtime"
            / "ACEE18_acee_prediction_engine"
        )

        engine = ACEEPredictionEngine(
            root=root,
            runtime_dir=runtime,
        )

        for index in range(5):
            result = engine.step(
                inputs={
                    "candidates": [
                        base_candidate(
                            f"atomic-{index}"
                        )
                    ]
                },
                persist=True,
            )

            path = Path(
                result["artifacts"]["json_path"]
            )

            payload = json.loads(
                path.read_text(encoding="utf-8")
            )

            assert payload["persisted"] is True
            assert (
                payload["prediction_hash"]
                == result["prediction_hash"]
            )

        temporary_files = list(
            runtime.glob(".*.tmp")
        )

        assert temporary_files == []

    print(
        "ACEE18_ATOMIC_PERSISTENCE_CLEANUP_OK"
    )


def main():
    test_cross_type_identifier_collision()
    test_recommendation_precedence()
    test_score_boundaries()
    test_derived_candidate_collision()
    test_atomic_persistence_cleanup()

    print(
        "ACEE18_CLOSURE_VALIDATION_OK"
    )


if __name__ == "__main__":
    main()
