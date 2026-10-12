#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
sys.path.insert(0, str(ROOT))

def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)

def keys(d):
    return set(d.keys()) if isinstance(d, dict) else set()

protected = [
    ROOT / "ontology/environmental_state_model.py",
    ROOT / "ontology/perception_action_feedback_loop.py",
    ROOT / "ontology/embodied_world_model_update.py",
    ROOT / "ontology/predictive_environment_simulator.py",
]
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}

from ontology.environmental_state_model import EnvironmentalStateModel
from ontology.perception_action_feedback_loop import PerceptionActionFeedbackLoop
from ontology.embodied_world_model_update import EmbodiedWorldModelUpdate
from ontology.predictive_environment_simulator import PredictiveEnvironmentSimulator

with tempfile.TemporaryDirectory(prefix="oce-p009-c2-") as td:
    sandbox = Path(td)

    s0_payload = {
        "vision": {"detected_objects": ["target"], "motion_detected": False},
        "audio": {"events": ["ambient"], "amplitude": 0.1},
        "sensors": {"temperature": 20.0, "humidity": 0.40, "light": 0.30},
        "runtime": {"p009_probe": True},
    }
    s1_payload = {
        "vision": {"detected_objects": ["target"], "motion_detected": True},
        "audio": {"events": ["ambient"], "amplitude": 0.1},
        "sensors": {"temperature": 24.0, "humidity": 0.55, "light": 0.70},
        "runtime": {"p009_probe": True},
    }

    esm = EnvironmentalStateModel(root=sandbox)
    s0 = esm.step(s0_payload, persist=False)
    s1 = esm.step(s1_payload, persist=False)
    require(isinstance(s0, dict) and isinstance(s1, dict), "environmental states not produced")
    require(s0 != s1, "state model failed to distinguish changed observations")
    print("P009_C2_STATE_TRANSITION_OBSERVED_OK")

    loop = PerceptionActionFeedbackLoop(root=sandbox)
    fb = loop.step({
        "observation": s0_payload,
        "measurement": s1_payload,
        "desired_state": {"temperature": 0.60, "humidity": 0.55, "light": 0.70},
    }, persist=False)
    require(isinstance(fb, dict), "feedback loop did not return a result")
    flat = json.dumps(fb, sort_keys=True).lower()
    require("pre_error" in flat and "post_error" in flat and "error_delta" in flat,
            "feedback loop did not compute before/after error")
    print("P009_C2_FEEDBACK_ERROR_RUNTIME_OK")

    updater = EmbodiedWorldModelUpdate(root=sandbox)
    u0 = updater.step({"current_observation": s0_payload, "events": []}, persist=True)
    u1 = updater.step({"current_observation": s1_payload, "events": [
        {"event_type": "probe_change", "channel": "sensor", "severity": 0.2}
    ]}, persist=True)
    state_path = sandbox / "embodied_world_model" / "embodied_world_model_state.json"
    require(state_path.is_file(), "world-model update did not persist state")
    persisted = json.loads(state_path.read_text(encoding="utf-8"))
    require(int(persisted.get("update_count", 0)) >= 2, "persistent model did not accumulate updates")
    print("P009_C2_WORLD_STATE_PERSISTENT_UPDATE_OK")

    sim = PredictiveEnvironmentSimulator()
    sim_input = {
        "transition_accuracy": 0.8,
        "scenario_diversity": 0.7,
        "temporal_consistency": 0.75,
        "causal_coherence": 0.8,
        "uncertainty_calibration": 0.7,
    }
    pred = sim.step(sim_input)
    require(isinstance(pred, dict), "predictive simulator did not execute")
    pred_keys = keys(pred)
    state_prediction_keys = {
        "predicted_state", "next_state", "predicted_next_state",
        "state_t_plus_1", "prediction_error", "model_parameters_updated",
    }
    produces_state_prediction = bool(pred_keys & state_prediction_keys)

    fb_keys_text = json.dumps(fb, sort_keys=True).lower()
    feedback_is_prediction_error = (
        "predicted_state" in fb_keys_text
        or "predicted_next_state" in fb_keys_text
        or "forecast_error" in fb_keys_text
    )

    update_text = json.dumps(u1, sort_keys=True).lower()
    update_consumes_prediction_error = (
        "prediction_error" in update_text
        or "forecast_error" in update_text
    )

    if produces_state_prediction and feedback_is_prediction_error and update_consumes_prediction_error:
        outcome = "CLOSED_LOOP_IMPLEMENTED"
    elif isinstance(s0, dict) and isinstance(fb, dict) and state_path.is_file() and isinstance(pred, dict):
        outcome = "CLOSED_LOOP_PARTIAL"
    else:
        outcome = "CLOSED_LOOP_NOT_IMPLEMENTED"

    # Current evidence must not be upgraded merely because metric simulators execute.
    require(outcome != "CLOSED_LOOP_IMPLEMENTED",
            "unexpected full closed-loop proof; inspect interfaces before accepting")
    require(outcome == "CLOSED_LOOP_PARTIAL",
            f"unexpected closed-loop classification: {outcome}")

    report = {
        "schema": "oce.p009.wm_closed_loop_probe.v1",
        "milestone": "P009-C2",
        "outcome": outcome,
        "state_transition_observed": True,
        "feedback_error_runtime": True,
        "persistent_world_state_update": True,
        "predictive_simulator_executes": True,
        "predictive_simulator_produces_next_state": produces_state_prediction,
        "feedback_error_is_prediction_error": feedback_is_prediction_error,
        "world_model_update_consumes_prediction_error": update_consumes_prediction_error,
        "interpretation": (
            "Existing OCE components form a functional state/feedback/persistence substrate, "
            "but this probe does not find an end-to-end contract in which a predicted next "
            "world state is compared with the observed next state and the resulting prediction "
            "error updates the future predictive model."
        ),
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    report["probe_identity_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    (ROOT / "p009_wm_closed_loop_probe_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
require(before == after, "probe mutated protected WM source")
print("P009_C2_NON_MUTATION_OK")
print("P009_C2_ANTI_OVERCLAIM_OK")
print("P009_WM_CLOSED_LOOP_PROBE_OK")
print("outcome=CLOSED_LOOP_PARTIAL")
print(f"report={ROOT / 'p009_wm_closed_loop_probe_report.json'}")
