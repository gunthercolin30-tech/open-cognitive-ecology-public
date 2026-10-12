#!/usr/bin/env python3
from pathlib import Path
import py_compile

from ontology.developmental_prediction_engine import (
    DevelopmentalPredictionEngine,
)

ROOT = Path.home() / "open-cognitive-ecology"

py_compile.compile(
    str(ROOT / "ontology" / "developmental_prediction_engine.py"),
    cfile="/private/tmp/developmental_prediction_engine.pyc",
    doraise=True,
)

engine = DevelopmentalPredictionEngine()


def ctx(stage, confidence=0.9, quality=0.9, trends=None, trajectory=None):
    return {
        "developmental_stage_result": {
            "developmental_stage": stage,
            "stage_confidence": confidence,
            "evidence_quality_score": quality,
            "stage_probabilities": {stage: 1.0},
        },
        "trends": trends or {},
        "trajectory": trajectory or [],
    }


empty = engine.step(inputs={}, persist=False)
assert empty["predicted_stage"] == "UNDETERMINED"
assert empty["prediction_confidence"] == 0.0

growth = engine.step(
    inputs=ctx("GENESIS", trends={"growth": 0.9}),
    persist=False,
)
assert growth["predicted_stage"] == "MATURATION"

plateau = engine.step(
    inputs=ctx("MATURATION", trends={"stability": 0.9}),
    persist=False,
)
assert plateau["predicted_stage"] in {
    "MATURATION",
    "STABLE_DEVELOPED_REGIME",
    "SPECIALIZATION",
}

bifurcation = engine.step(
    inputs=ctx("SPECIALIZATION", trends={"bifurcation": 1.0}),
    persist=False,
)
assert bifurcation["predicted_stage"] == "BIFURCATION"

degeneration = engine.step(
    inputs=ctx(
        "STABLE_DEVELOPED_REGIME",
        trends={"degeneration": 1.0},
    ),
    persist=False,
)
assert degeneration["predicted_stage"] == "DEGENERATION"

recovery = engine.step(
    inputs=ctx("DEGENERATION", trends={"recovery": 1.0}),
    persist=False,
)
assert recovery["predicted_stage"] == "RECOVERY"

stable = engine.step(
    inputs=ctx(
        "STABLE_DEVELOPED_REGIME",
        trends={"stability": 1.0},
    ),
    persist=False,
)
assert stable["predicted_stage"] == "STABLE_DEVELOPED_REGIME"

uncertain = engine.step(
    inputs=ctx("HYBRID_STAGE", confidence=0.25, quality=0.3),
    persist=False,
)
assert uncertain["prediction_uncertainty"] >= 0.5
assert uncertain["forecast_horizon"]["label"] == "SHORT"

persisted = engine.step(
    inputs=ctx("GENESIS", trends={"growth": 0.9}),
    persist=True,
)
assert persisted["persisted"] is True
assert Path(persisted["output_path"]).is_file()

for result in (
    empty,
    growth,
    plateau,
    bifurcation,
    degeneration,
    recovery,
    stable,
    uncertain,
    persisted,
):
    assert result["prediction_status"] == "DEVELOPMENTAL_PREDICTION_READY"
    assert result["alternative_scenarios"]
    assert result["falsification_conditions"]
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True

print("AV8_FAST_ACCEPTANCE_OK")
