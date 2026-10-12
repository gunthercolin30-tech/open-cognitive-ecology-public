import json
import multiprocessing
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def candidate(
    candidate_id,
    *,
    gain=0.20,
    confidence=0.85,
    risk=0.10,
    reversibility=0.90,
    validation=0.90,
    robustness=0.85,
    non_closure=0.90,
    closure_delta=0.0,
    governance_compatible=True,
):
    return {
        "candidate_id": candidate_id,
        "predicted_gain": gain,
        "confidence": confidence,
        "risk": risk,
        "reversibility": reversibility,
        "validation": validation,
        "robustness": robustness,
        "non_closure": non_closure,
        "closure_pressure_delta": closure_delta,
        "governance_compatible": governance_compatible,
    }


def score_of(result, candidate_id):
    for item in result["ranked_candidates"]:
        if item["candidate_id"] == candidate_id:
            return item["prediction_score"]

    raise AssertionError(
        f"candidate_not_found:{candidate_id}"
    )


def test_producer_derivation():
    engine = ACEEPredictionEngine()

    result = engine.step(
        inputs={
            "improvement_plan": {
                "projected_gain": 0.18,
                "improvement_confidence": 0.82,
                "recommended_actions": [
                    {
                        "recommended_action":
                            "improve-runtime-stability"
                    }
                ],
            },
            "parameter_optimization": {
                "optimization_gain": 0.12,
                "parameter_stability_index": 0.91,
                "optimization_trace": {
                    "optimization_id":
                        "parameter-optimization-01"
                },
            },
        },
        persist=False,
    )

    assert result["candidate_count"] == 2

    sources = {
        item["source"]
        for item in result["ranked_candidates"]
    }

    assert (
        "performance_improvement_planner"
        in sources
    )
    assert (
        "self_parameter_optimization_engine"
        in sources
    )


def test_gain_monotonicity():
    engine = ACEEPredictionEngine()

    result = engine.step(
        inputs={
            "candidates": [
                candidate("low-gain", gain=0.10),
                candidate("high-gain", gain=0.30),
            ]
        },
        persist=False,
    )

    assert (
        score_of(result, "high-gain")
        >
        score_of(result, "low-gain")
    )

    assert (
        result["recommended_candidate_id"]
        == "high-gain"
    )


def test_risk_penalty():
    engine = ACEEPredictionEngine()

    result = engine.step(
        inputs={
            "candidates": [
                candidate("low-risk", risk=0.05),
                candidate("high-risk", risk=0.75),
            ]
        },
        persist=False,
    )

    assert (
        score_of(result, "low-risk")
        >
        score_of(result, "high-risk")
    )

    high_risk = next(
        item
        for item in result["ranked_candidates"]
        if item["candidate_id"] == "high-risk"
    )

    assert (
        high_risk["recommendation"]
        == "sandbox_longer"
    )


def test_closure_pressure_penalty():
    engine = ACEEPredictionEngine()

    result = engine.step(
        inputs={
            "candidates": [
                candidate(
                    "opening",
                    closure_delta=-0.10,
                ),
                candidate(
                    "closing",
                    closure_delta=0.25,
                ),
            ]
        },
        persist=False,
    )

    assert (
        score_of(result, "opening")
        >
        score_of(result, "closing")
    )

    closing = next(
        item
        for item in result["ranked_candidates"]
        if item["candidate_id"] == "closing"
    )

    assert (
        closing["recommendation"]
        == "require_non_closure_review"
    )


def test_governance_incompatibility():
    engine = ACEEPredictionEngine()

    result = engine.step(
        inputs={
            "candidates": [
                candidate(
                    "compatible",
                    governance_compatible=True,
                ),
                candidate(
                    "incompatible",
                    gain=0.40,
                    governance_compatible=False,
                ),
            ]
        },
        persist=False,
    )

    incompatible = next(
        item
        for item in result["ranked_candidates"]
        if item["candidate_id"] == "incompatible"
    )

    assert (
        incompatible["recommendation"]
        == "reject_from_prediction_pipeline"
    )

    assert (
        score_of(result, "compatible")
        >
        score_of(result, "incompatible")
    )

    assert result["execution_authorized"] is False
    assert result["selection_performed"] is False


def test_tamper_detection():
    engine = ACEEPredictionEngine()

    result = engine.step(
        inputs={
            "candidates": [
                candidate("tamper-target")
            ]
        },
        persist=False,
    )

    assert engine.verify_prediction(
        result
    )["verified"] is True

    corrupted = deepcopy(result)
    corrupted["ranked_candidates"][0][
        "prediction_score"
    ] = 1.0

    verification = engine.verify_prediction(
        corrupted
    )

    assert verification["verified"] is False
    assert (
        "prediction_hash_mismatch"
        in verification["verification_errors"]
    )


def test_restart_continuity():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = (
            root
            / "acee_runtime"
            / "ACEE18_acee_prediction_engine"
        )

        first_engine = ACEEPredictionEngine(
            root=root,
            runtime_dir=runtime,
        )

        first = first_engine.step(
            inputs={
                "candidates": [
                    candidate("restart-candidate")
                ]
            },
            persist=True,
        )

        path = Path(
            first["artifacts"]["json_path"]
        )

        persisted = json.loads(
            path.read_text(encoding="utf-8")
        )

        second_engine = ACEEPredictionEngine(
            root=root,
            runtime_dir=runtime,
        )

        verification = (
            second_engine.verify_prediction(
                persisted
            )
        )

        assert verification["verified"] is True
        assert (
            persisted["prediction_hash"]
            == first["prediction_hash"]
        )
        assert persisted["persisted"] is True
        assert persisted["candidate_count"] == 1


def persistence_worker(
    root_text,
    candidate_id,
):
    root = Path(root_text)

    engine = ACEEPredictionEngine(
        root=root,
        runtime_dir=(
            root
            / "acee_runtime"
            / "ACEE18_acee_prediction_engine"
        ),
    )

    engine.step(
        inputs={
            "candidates": [
                candidate(candidate_id)
            ]
        },
        persist=True,
    )


def test_multiprocess_persistence():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        processes = [
            multiprocessing.Process(
                target=persistence_worker,
                args=(
                    str(root),
                    f"process-{index}",
                ),
            )
            for index in range(4)
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()
            assert process.exitcode == 0

        path = (
            root
            / "acee_runtime"
            / "ACEE18_acee_prediction_engine"
            / "latest_prediction.json"
        )

        assert path.exists()

        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

        verification = (
            ACEEPredictionEngine(
                root=root,
                runtime_dir=path.parent,
            ).verify_prediction(payload)
        )

        assert verification["verified"] is True
        assert payload["persisted"] is True
        assert payload["candidate_count"] == 1


def main():
    test_producer_derivation()
    print(
        "ACEE18_PRODUCER_DERIVATION_OK"
    )

    test_gain_monotonicity()
    print(
        "ACEE18_GAIN_MONOTONICITY_OK"
    )

    test_risk_penalty()
    print(
        "ACEE18_RISK_PENALTY_OK"
    )

    test_closure_pressure_penalty()
    print(
        "ACEE18_CLOSURE_PRESSURE_PENALTY_OK"
    )

    test_governance_incompatibility()
    print(
        "ACEE18_GOVERNANCE_INCOMPATIBILITY_OK"
    )

    test_tamper_detection()
    print(
        "ACEE18_TAMPER_DETECTION_OK"
    )

    test_restart_continuity()
    print(
        "ACEE18_RESTART_CONTINUITY_OK"
    )

    test_multiprocess_persistence()
    print(
        "ACEE18_MULTIPROCESS_PERSISTENCE_OK"
    )

    print(
        "ACEE18_EXTENDED_VALIDATION_OK"
    )


if __name__ == "__main__":
    main()
