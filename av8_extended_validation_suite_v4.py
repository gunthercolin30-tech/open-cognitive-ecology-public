#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from ontology.developmental_prediction_engine import DevelopmentalPredictionEngine


def guards(result: dict) -> None:
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def context(
    stage: str,
    *,
    confidence: float,
    quality: float,
    trends: dict,
    trajectory: list | None = None,
    config: dict | None = None,
) -> dict:
    payload = {
        "developmental_stage_result": {
            "developmental_stage": stage,
            "stage_confidence": confidence,
            "evidence_quality_score": quality,
            "stage_probabilities": {stage: 1.0},
        },
        "trends": trends,
        "trajectory": trajectory or [],
    }
    if config is not None:
        payload["config"] = config
    return payload


engine = DevelopmentalPredictionEngine()

short = engine.step(
    inputs=context(
        "HYBRID_STAGE",
        confidence=0.30,
        quality=0.35,
        trends={},
    ),
    persist=False,
)
assert short["forecast_horizon"]["label"] == "SHORT"
assert short["forecast_horizon"]["windows"] == 1
guards(short)

medium = engine.step(
    inputs=context(
        "MATURATION",
        confidence=0.90,
        quality=0.92,
        trends={
            "growth": 0.82,
            "specialization": 0.74,
            "stability": 0.35,
        },
        trajectory=[
            {"developmental_stage": "GENESIS", "stage_confidence": 0.72},
            {"developmental_stage": "MATURATION", "stage_confidence": 0.86},
        ],
    ),
    persist=False,
)
assert medium["forecast_horizon"]["label"] in {"MEDIUM", "LONG"}
assert medium["forecast_horizon"]["windows"] in {3, 6}
guards(medium)

stable = engine.step(
    inputs=context(
        "STABLE_DEVELOPED_REGIME",
        confidence=0.98,
        quality=0.99,
        trends={"stability": 1.0},
        trajectory=[
            {"developmental_stage": "STABLE_DEVELOPED_REGIME", "stage_confidence": 0.95},
            {"developmental_stage": "STABLE_DEVELOPED_REGIME", "stage_confidence": 0.97},
        ],
    ),
    persist=False,
)
assert stable["forecast_horizon"]["label"] in {"MEDIUM", "LONG"}
assert stable["forecast_horizon"]["windows"] in {3, 6}
assert stable["predicted_stage"] == "STABLE_DEVELOPED_REGIME"
assert stable["prediction_confidence"] >= medium["prediction_confidence"]
assert stable["prediction_uncertainty"] <= medium["prediction_uncertainty"]
guards(stable)

custom = engine.step(
    inputs=context(
        "STABLE_DEVELOPED_REGIME",
        confidence=0.98,
        quality=0.99,
        trends={"stability": 1.0},
        config={
            "short_horizon": 2,
            "medium_horizon": 4,
            "long_horizon": 9,
        },
    ),
    persist=False,
)
assert custom["forecast_horizon"]["label"] in {"MEDIUM", "LONG"}
assert custom["forecast_horizon"]["windows"] in {4, 9}
guards(custom)

invalid_horizons = (
    float("inf"),
    float("-inf"),
    float("nan"),
    "invalid",
    None,
)
for bad in invalid_horizons:
    result = engine.step(
        inputs=context(
            "MATURATION",
            confidence=0.85,
            quality=0.90,
            trends={"growth": 0.80},
            config={
                "short_horizon": bad,
                "medium_horizon": bad,
                "long_horizon": bad,
            },
        ),
        persist=False,
    )
    assert result["forecast_horizon"]["windows"] in {1, 3, 6}
    assert result["predicted_stage"] in engine.STAGES
    guards(result)

competing = engine.step(
    inputs=context(
        "BIFURCATION",
        confidence=0.86,
        quality=0.91,
        trends={
            "bifurcation": 0.75,
            "stability": 0.62,
            "degeneration": 0.55,
            "recovery": 0.42,
        },
    ),
    persist=False,
)
assert len(competing["alternative_scenarios"]) >= 3
scenario_probabilities = [
    item["probability"] for item in competing["alternative_scenarios"]
]
assert scenario_probabilities == sorted(scenario_probabilities, reverse=True)
assert abs(sum(competing["prediction_probabilities"].values()) - 1.0) < 1e-5
guards(competing)

base = context(
    "STABLE_DEVELOPED_REGIME",
    confidence=0.90,
    quality=0.92,
    trends={"stability": 0.50},
)
low_deg = engine.step(inputs=deepcopy(base), persist=False)
high_deg_input = deepcopy(base)
high_deg_input["trends"]["degeneration"] = 1.0
high_deg = engine.step(inputs=high_deg_input, persist=False)

assert (
    high_deg["prediction_probabilities"].get("DEGENERATION", 0.0)
    >
    low_deg["prediction_probabilities"].get("DEGENERATION", 0.0)
)
assert high_deg["prediction_hash"] != low_deg["prediction_hash"]
guards(low_deg)
guards(high_deg)

source = context(
    "SPECIALIZATION",
    confidence=0.88,
    quality=0.93,
    trends={"stability": 0.61, "bifurcation": 0.31},
    trajectory=[
        {"developmental_stage": "MATURATION", "stage_confidence": 0.74},
        {"developmental_stage": "SPECIALIZATION", "stage_confidence": 0.88},
    ],
)
snapshot = deepcopy(source)
first = engine.step(inputs=source, persist=False)
second = engine.step(inputs=deepcopy(source), persist=False)

assert source == snapshot
assert first["prediction_hash"] == second["prediction_hash"]
assert first["predicted_stage"] == second["predicted_stage"]
assert first["prediction_probabilities"] == second["prediction_probabilities"]
guards(first)
guards(second)

reordered = {
    "trajectory": deepcopy(source["trajectory"]),
    "trends": {"bifurcation": 0.31, "stability": 0.61},
    "developmental_stage_result": {
        "stage_probabilities": {"SPECIALIZATION": 1.0},
        "evidence_quality_score": 0.93,
        "stage_confidence": 0.88,
        "developmental_stage": "SPECIALIZATION",
    },
}
third = engine.step(inputs=reordered, persist=False)
assert third["prediction_hash"] == first["prediction_hash"]
guards(third)

with tempfile.TemporaryDirectory(prefix="oce_av8_") as tmp:
    local = DevelopmentalPredictionEngine()
    local.output_dir = Path(tmp)

    persisted_1 = local.step(inputs=deepcopy(source), persist=True)
    path = Path(persisted_1["output_path"])
    assert persisted_1["persisted"] is True
    assert path.is_file()

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["prediction_hash"] == persisted_1["prediction_hash"]
    assert payload["persisted"] is False
    assert payload["output_path"] is None

    persisted_2 = local.step(inputs=deepcopy(source), persist=True)
    assert persisted_2["prediction_hash"] == persisted_1["prediction_hash"]
    assert Path(persisted_2["output_path"]) == path
    assert len(list(Path(tmp).glob("*.json"))) == 1
    guards(persisted_1)
    guards(persisted_2)

assert len(first["falsification_conditions"]) >= 4
assert all(
    isinstance(item, dict)
    and item.get("id")
    and item.get("condition")
    and item.get("evaluation")
    for item in first["falsification_conditions"]
)
assert first["condition_results"]["no_upstream_recalculation"] is True
assert first["audit_trace"]["upstream_recalculation_performed"] is False

malformed = engine.step(
    inputs={
        "developmental_stage_result": {
            "developmental_stage": "MATURATION",
            "stage_confidence": float("nan"),
            "evidence_quality_score": float("inf"),
            "stage_probabilities": "invalid",
        },
        "trends": {
            "growth": "invalid",
            "degeneration": -999,
            "recovery": float("nan"),
        },
        "trajectory": [
            None,
            "invalid",
            {"developmental_stage": "UNKNOWN", "stage_confidence": "bad"},
        ],
        "config": {
            "short_horizon": "bad",
            "medium_horizon": -7,
            "long_horizon": float("inf"),
        },
    },
    persist=False,
)
assert malformed["predicted_stage"] in engine.STAGES
assert 0.0 <= malformed["prediction_confidence"] <= 1.0
assert 0.0 <= malformed["prediction_uncertainty"] <= 1.0
assert malformed["forecast_horizon"]["windows"] >= 1
guards(malformed)

print("AV8_EXTENDED_VALIDATION_V4_OK")
