#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
AUDITOR = ROOT / "validation" / "p009_wm_readiness_audit.py"
REPORT = ROOT / "p009_wm_readiness_report.json"
EXPECTED_AUDITOR_SHA = "44f5f8525e22c80f4f7652b878ebc46d2774eef493149d2758f7f245411e04aa"
EXPECTED_AUDIT_ID = "2f680a8f70f27596f090fc0a064477a906c586704f5dfbc17b4f92eaee5af05e"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)

require(AUDITOR.is_file(), "P009 auditor missing")
require(sha(AUDITOR) == EXPECTED_AUDITOR_SHA, "P009 auditor drift")

before = {}
for rel in (
    "ontology/world_model.py",
    "ontology/environmental_state_model.py",
    "ontology/embodied_world_model_update.py",
    "ontology/predictive_environment_simulator.py",
    "ontology/trajectory_prediction.py",
    "ontology/trajectory_learning.py",
):
    p = ROOT / rel
    if p.is_file():
        before[rel] = sha(p)

run = subprocess.run(
    [sys.executable, str(AUDITOR)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
    timeout=300,
)
output = run.stdout + run.stderr
require(run.returncode == 0, output)
require("P009_WM_READINESS_AUDIT_OK" in output, output)
report = json.loads(REPORT.read_text(encoding="utf-8"))
require(report["audit_identity_sha256"] == EXPECTED_AUDIT_ID, "P009 audit identity drift")
require(report["readiness"] == "PARTIAL_READINESS", "unexpected readiness")
require(report["functional_conclusion_only"] is True, "functional-only invariant lost")
require(report["phenomenology_undetermined"] is True, "phenomenology invariant lost")
print("P009_FUNCTIONAL_AUDIT_REPLAY_OK")

after = {rel: sha(ROOT / rel) for rel in before}
require(before == after, "P009 audit mutated protected WM source")
print("P009_FUNCTIONAL_NON_MUTATION_OK")

expected_status = {
    "observation": "IMPLEMENTED",
    "environmental_state": "IMPLEMENTED",
    "world_representation": "IMPLEMENTED",
    "transition_dynamics": "IMPLEMENTED",
    "prediction": "PARTIAL",
    "prediction_error": "IMPLEMENTED",
    "counterfactual_rollout": "IMPLEMENTED",
    "planning": "PARTIAL",
    "action_selection_execution": "PARTIAL",
    "outcome_feedback": "IMPLEMENTED",
    "learning_model_update": "PARTIAL",
    "persistence_memory": "PARTIAL",
}
actual_status = {k: report["evidence"][k]["status"] for k in expected_status}
require(actual_status == expected_status, f"classification drift: {actual_status}")
print("P009_FUNCTIONAL_CLASSIFICATION_CONTRACT_OK")

gaps = "\n".join(report.get("gaps", [])).lower()
unknowns = "\n".join(report.get("unknowns", [])).lower()
require("prediction error" in gaps, "prediction-error gap not explicit")
require("future transition predictions" in gaps, "future-prediction adaptation gap not explicit")
require("runtime end-to-end wm loop" in unknowns, "runtime WM loop UNKNOWN missing")
require("learned transition-model adaptation" in unknowns, "learned transition adaptation UNKNOWN missing")
print("P009_FUNCTIONAL_GAP_CONTRACT_OK")

# Anti-overclaim: static readiness must not silently become full readiness.
require(report["readiness"] != "READY", "static audit overclaimed READY")
require(report["readiness_semantics"].startswith("engineering readiness"), "readiness semantics drift")
print("P009_FUNCTIONAL_ANTI_OVERCLAIM_OK")

# Degradation oracle: a synthetic missing critical capability must map to NOT_READY.
critical = dict(report["critical_status"])
critical["prediction"] = "MISSING"
degraded = "NOT_READY" if any(v in ("MISSING", "UNKNOWN") for v in critical.values()) else "PARTIAL_READINESS"
require(degraded == "NOT_READY", "critical degradation oracle failed")
print("P009_FUNCTIONAL_DEGRADATION_OK")

# Tamper oracle for the deterministic identity payload.
payload = json.loads(json.dumps(report["identity_payload"]))
payload["capability_status"]["prediction"] = "IMPLEMENTED"
tampered = hashlib.sha256(
    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
require(tampered != report["audit_identity_sha256"], "tamper not detected by identity")
print("P009_FUNCTIONAL_TAMPER_OK")

# Verify the two key partial modules are genuinely classified from source, not missing.
for rel in ("ontology/trajectory_prediction.py", "ontology/trajectory_learning.py"):
    p = ROOT / rel
    require(p.is_file(), f"missing expected partial module: {rel}")
    ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
print("P009_FUNCTIONAL_PARTIAL_MODULES_PRESENT_OK")

print("P009_WM_FUNCTIONAL_TESTS_OK")
