#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from ontology.developmental_stage_classifier import DevelopmentalStageClassifier


def assert_guards(result: dict) -> None:
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def stage_input(
    *,
    genesis: dict | None = None,
    maturation: dict | None = None,
    specialization: dict | None = None,
    bifurcation: dict | None = None,
    degeneration: dict | None = None,
    recovery: dict | None = None,
    previous_stage: str | None = None,
    stage_duration: int = 0,
) -> dict:
    result = {
        "genesis_result": genesis or {},
        "maturation_result": maturation or {},
        "specialization_result": specialization or {},
        "bifurcation_result": bifurcation or {},
        "degeneration_result": degeneration or {},
        "recovery_result": recovery or {},
        "stage_duration": stage_duration,
    }
    if previous_stage is not None:
        result["previous_stage"] = previous_stage
    return result


classifier = DevelopmentalStageClassifier()

# 1. Matrice chronologique minimale.
genesis = classifier.step(
    inputs=stage_input(
        genesis={
            "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
            "genesis_detected": True,
            "genesis_score": 0.84,
            "data_quality_score": 0.97,
        }
    ),
    persist=False,
)
assert genesis["developmental_stage"] == "GENESIS"
assert genesis["transition_status"] == "NO_PRIOR_STAGE"
assert genesis["stage_duration"] == 1
assert_guards(genesis)

maturation = classifier.step(
    inputs=stage_input(
        genesis={
            "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
            "genesis_detected": True,
            "genesis_score": 0.75,
            "data_quality_score": 0.97,
        },
        maturation={
            "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
            "maturation_score": 0.90,
            "data_quality_score": 0.97,
        },
        previous_stage="GENESIS",
        stage_duration=3,
    ),
    persist=False,
)
assert maturation["developmental_stage"] in {"MATURATION", "HYBRID_STAGE"}
assert maturation["previous_stage"] == "GENESIS"
assert maturation["stage_duration"] in {1, 4}
assert_guards(maturation)

stable = classifier.step(
    inputs=stage_input(
        maturation={
            "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
            "maturation_score": 0.91,
            "data_quality_score": 0.98,
        },
        specialization={
            "specialization_status": "FUNCTIONAL_SPECIALIZATION_STRONG",
            "specialization_strength": 0.93,
            "data_quality_score": 0.98,
        },
        previous_stage="STABLE_DEVELOPED_REGIME",
        stage_duration=5,
    ),
    persist=False,
)
assert stable["developmental_stage"] == "STABLE_DEVELOPED_REGIME"
assert stable["transition_status"] == "DEVELOPMENTAL_STAGE_PERSISTENT"
assert stable["stage_duration"] == 6
assert_guards(stable)

# 2. Conflit fort et hybridation.
conflict = classifier.step(
    inputs=stage_input(
        genesis={
            "genesis_status": "FUNCTIONAL_GENESIS_NOT_DETECTED",
            "data_quality_score": 0.96,
        },
        maturation={
            "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
            "maturation_score": 0.94,
            "data_quality_score": 0.96,
        },
        degeneration={
            "degeneration_status": "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED",
            "degeneration_detected": True,
            "degeneration_score": 0.90,
            "data_quality_score": 0.96,
        },
    ),
    persist=False,
)
assert conflict["developmental_stage"] == "HYBRID_STAGE"
assert conflict["hybrid_stage"] is True
assert conflict["stage_conflicts"]
assert conflict["audit_trace"]["conflict_count"] >= 1
assert_guards(conflict)

# 3. Robustesse aux entrées malformées et valeurs non finies.
malformed = classifier.step(
    inputs={
        "genesis_result": {
            "genesis_status": 123,
            "genesis_score": "not-a-number",
            "data_quality_score": float("nan"),
        },
        "maturation_result": [],
        "specialization_result": "invalid",
        "bifurcation_result": None,
        "degeneration_result": {"degeneration_score": float("inf")},
        "recovery_result": {"recovery_score": -999},
        "previous_stage": "UNKNOWN_STAGE",
        "stage_duration": "invalid",
        "stage_history": "invalid",
    },
    persist=False,
)
assert malformed["developmental_stage"] == "UNDETERMINED"
assert malformed["previous_stage"] is None
assert malformed["stage_duration"] == 0
assert 0.0 <= malformed["stage_confidence"] <= 1.0
assert_guards(malformed)

# 4. Déterminisme sous changement d'ordre des dictionnaires.
ordered = stage_input(
    maturation={
        "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
        "maturation_score": 0.88,
        "data_quality_score": 0.95,
    },
    specialization={
        "specialization_status": "FUNCTIONAL_SPECIALIZATION_STABLE",
        "specialization_strength": 0.79,
        "data_quality_score": 0.95,
    },
)
reordered = {
    "specialization_result": deepcopy(ordered["specialization_result"]),
    "maturation_result": deepcopy(ordered["maturation_result"]),
    "recovery_result": {},
    "degeneration_result": {},
    "bifurcation_result": {},
    "genesis_result": {},
    "stage_duration": 0,
}
first = classifier.step(inputs=ordered, persist=False)
second = classifier.step(inputs=reordered, persist=False)
assert first["stage_hash"] == second["stage_hash"]
assert first["stage_probabilities"] == second["stage_probabilities"]
assert first["developmental_stage"] == second["developmental_stage"]
assert_guards(first)
assert_guards(second)

# 5. Persistance réelle, contenu JSON, écrasement idempotent.
with tempfile.TemporaryDirectory(prefix="oce_av7_") as tmp:
    local = DevelopmentalStageClassifier()
    local.output_dir = Path(tmp)

    persisted_first = local.step(inputs=ordered, persist=True)
    path = Path(persisted_first["output_path"])
    assert persisted_first["persisted"] is True
    assert path.is_file()

    payload_first = json.loads(path.read_text(encoding="utf-8"))
    assert payload_first["stage_hash"] == persisted_first["stage_hash"]
    assert payload_first["persisted"] is False
    assert payload_first["output_path"] is None

    persisted_second = local.step(inputs=deepcopy(ordered), persist=True)
    assert persisted_second["stage_hash"] == persisted_first["stage_hash"]
    assert Path(persisted_second["output_path"]) == path
    assert len(list(Path(tmp).glob("*.json"))) == 1
    assert_guards(persisted_first)
    assert_guards(persisted_second)

# 6. Non-mutation des entrées.
source = deepcopy(ordered)
snapshot = deepcopy(source)
classifier.step(inputs=source, persist=False)
assert source == snapshot

print("AV7_EXTENDED_VALIDATION_OK")
