#!/usr/bin/env python3
from pathlib import Path
import py_compile

from ontology.developmental_stage_classifier import (
    DevelopmentalStageClassifier,
)


ROOT = Path.home() / "open-cognitive-ecology"

py_compile.compile(
    str(ROOT / "ontology" / "developmental_stage_classifier.py"),
    cfile="/private/tmp/developmental_stage_classifier.pyc",
    doraise=True,
)

classifier = DevelopmentalStageClassifier()


def base(**overrides):
    context = {
        "genesis_result": {
            "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
            "genesis_detected": True,
            "data_quality_score": 0.95,
        },
        "maturation_result": {
            "maturation_status": "FUNCTIONAL_MATURATION_PROGRESSING",
            "maturation_score": 0.70,
            "data_quality_score": 0.95,
        },
        "specialization_result": {},
        "bifurcation_result": {},
        "degeneration_result": {},
        "recovery_result": {},
    }
    context.update(overrides)
    return context


empty = classifier.step(
    inputs={},
    persist=False,
)
assert empty["developmental_stage"] == "UNDETERMINED"

pre_genesis = classifier.step(
    inputs={
        "genesis_result": {
            "genesis_status": "FUNCTIONAL_GENESIS_NOT_DETECTED",
            "data_quality_score": 0.95,
        },
    },
    persist=False,
)
assert pre_genesis["developmental_stage"] == "PRE_GENESIS"

genesis = classifier.step(
    inputs={
        "genesis_result": {
            "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
            "genesis_detected": True,
            "genesis_score": 0.85,
            "data_quality_score": 0.95,
        },
    },
    persist=False,
)
assert genesis["developmental_stage"] == "GENESIS"

maturation = classifier.step(
    inputs=base(),
    persist=False,
)
assert maturation["developmental_stage"] == "MATURATION"

stable = classifier.step(
    inputs=base(
        maturation_result={
            "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
            "data_quality_score": 0.95,
        },
        specialization_result={
            "specialization_status": "FUNCTIONAL_SPECIALIZATION_STRONG",
            "specialization_strength": 0.90,
            "data_quality_score": 0.95,
        },
    ),
    persist=False,
)
assert stable["developmental_stage"] == "STABLE_DEVELOPED_REGIME"

bifurcation = classifier.step(
    inputs=base(
        bifurcation_result={
            "bifurcation_status": "FUNCTIONAL_BIFURCATION_DETECTED",
            "bifurcation_detected": True,
            "bifurcation_score": 0.91,
            "data_quality_score": 0.96,
        },
    ),
    persist=False,
)
assert bifurcation["developmental_stage"] == "BIFURCATION"

degeneration = classifier.step(
    inputs=base(
        degeneration_result={
            "degeneration_status": (
                "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED"
            ),
            "degeneration_detected": True,
            "degeneration_score": 0.90,
            "data_quality_score": 0.96,
        },
    ),
    persist=False,
)
assert degeneration["developmental_stage"] == "DEGENERATION"

recovery = classifier.step(
    inputs=base(
        recovery_result={
            "recovery_status": (
                "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE"
            ),
            "recovery_detected": True,
            "recovery_score": 0.95,
            "data_quality_score": 0.96,
        },
    ),
    persist=False,
)
assert recovery["developmental_stage"] == "RECOVERY"

hybrid = classifier.step(
    inputs=base(
        degeneration_result={
            "degeneration_status": (
                "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED"
            ),
            "degeneration_detected": True,
            "degeneration_score": 0.74,
            "data_quality_score": 0.96,
        },
        recovery_result={
            "recovery_status": (
                "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED"
            ),
            "recovery_detected": True,
            "recovery_score": 0.72,
            "data_quality_score": 0.96,
        },
    ),
    persist=False,
)
assert hybrid["developmental_stage"] == "HYBRID_STAGE"
assert hybrid["hybrid_stage"] is True

transition = classifier.step(
    inputs=base(
        previous_stage="GENESIS",
        stage_duration=3,
    ),
    persist=False,
)
assert transition["stage_transition_detected"] is True
assert transition["previous_stage"] == "GENESIS"

persisted = classifier.step(
    inputs=base(),
    persist=True,
)
recomputed = classifier.step(
    inputs=base(),
    persist=False,
)
assert persisted["stage_hash"] == recomputed["stage_hash"]
assert Path(persisted["output_path"]).exists()

for result in (
    pre_genesis,
    genesis,
    maturation,
    stable,
    bifurcation,
    degeneration,
    recovery,
    hybrid,
    transition,
):
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True

print("AV7_FAST_ACCEPTANCE_OK")
