#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
OUT_JSON = ROOT / "p009_wm_readiness_report.json"
OUT_TXT = ROOT / "p009_wm_readiness_report.txt"

P008_LOCK_ID = "4d05cfce3227628210b0bfcfdda60c9be1d9667a1d3f8e595418be1f86127f2e"
P008_AUDIT_FP = "366ed5ed3698d89011246a6df90b94d238f8185d046267170a3c495caddebb95"

CAPABILITIES = {
    "observation": [
        "ontology/multimodal_perception_engine.py",
        "ontology/visual_world_perception.py",
        "ontology/multimodal_observation_archive.py",
    ],
    "environmental_state": [
        "ontology/environmental_state_model.py",
        "ontology/real_world_event_detection.py",
    ],
    "world_representation": [
        "ontology/world_model.py",
        "ontology/hierarchical_world_model_engine.py",
        "ontology/embodied_world_model_update.py",
    ],
    "transition_dynamics": [
        "ontology/predictive_environment_simulator.py",
        "ontology/trajectory_simulation.py",
        "ontology/counterfactual_simulation.py",
    ],
    "prediction": [
        "ontology/trajectory_prediction.py",
        "ontology/predictive_environment_simulator.py",
    ],
    "prediction_error": [
        "ontology/perception_action_feedback_loop.py",
        "ontology/trajectory_outcome_evaluation.py",
    ],
    "counterfactual_rollout": [
        "ontology/counterfactual_simulation.py",
        "ontology/counterfactual_future_simulation.py",
        "ontology/possible_worlds_navigation.py",
        "ontology/offline_dream_simulation.py",
    ],
    "planning": [
        "ontology/planning.py",
        "ontology/embodied_planning_engine.py",
        "ontology/embodied_predictive_planning_bridge.py",
        "ontology/trajectory_horizon_planning.py",
    ],
    "action_selection_execution": [
        "ontology/autonomous_decision_engine.py",
        "ontology/trajectory_action_selection.py",
        "ontology/trajectory_action_execution.py",
        "ontology/physical_action_executor.py",
    ],
    "outcome_feedback": [
        "ontology/trajectory_outcome_evaluation.py",
        "ontology/perception_action_feedback_loop.py",
        "ontology/persistent_physical_feedback_loop.py",
    ],
    "learning_model_update": [
        "ontology/trajectory_learning.py",
        "ontology/trajectory_policy_update.py",
        "ontology/embodied_world_model_update.py",
    ],
    "persistence_memory": [
        "ontology/persistent_multi_scale_memory.py",
        "ontology/memory_consolidation.py",
        "ontology/embodied_world_model_update.py",
        "ontology/environmental_state_model.py",
    ],
}

TEST_MAP = {
    "world_representation": ["tests/test_world_model.py"],
    "transition_dynamics": ["tests/test_counterfactual_simulation.py"],
    "counterfactual_rollout": [
        "tests/test_counterfactual_simulation.py",
        "tests/test_possible_worlds_navigation.py",
    ],
    "persistence_memory": ["tests/test_memory_consolidation.py"],
}

DECLARATIVE_MARKERS = (
    "Conceptual module for ",
    "Auto-generated activation class for ",
)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    functions = []
    classes = []
    imports = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                calls.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                calls.append(fn.attr)
    return text, sorted(set(functions)), sorted(set(classes)), sorted(set(imports)), sorted(set(calls))

def classify(rel: str) -> dict:
    path = ROOT / rel
    if not path.is_file():
        return {"path": rel, "status": "MISSING", "confidence": 1.0}
    try:
        text, funcs, classes, imports, calls = parse(path)
    except Exception as exc:
        return {
            "path": rel, "status": "UNKNOWN", "confidence": 0.0,
            "error": f"{type(exc).__name__}: {exc}", "sha256": sha(path),
        }

    declarative = any(m in text for m in DECLARATIVE_MARKERS)
    has_step = "step" in funcs
    persistence = any(k in text for k in ("write_text(", "json.dump", "jsonl", "mkdir(", "open("))
    substantive = len(text.splitlines()) >= 45 and (has_step or len(funcs) >= 3)
    if declarative and not substantive:
        status, confidence = "DECLARATIVE", 0.98
    elif substantive and persistence:
        status, confidence = "IMPLEMENTED", 0.90
    elif substantive:
        status, confidence = "IMPLEMENTED", 0.82
    elif has_step or funcs:
        status, confidence = "PARTIAL", 0.72
    else:
        status, confidence = "DECLARATIVE", 0.75

    return {
        "path": rel,
        "status": status,
        "confidence": confidence,
        "sha256": sha(path),
        "line_count": len(text.splitlines()),
        "functions": funcs,
        "classes": classes,
        "imports": imports,
        "calls": calls,
        "persistence_signal": persistence,
        "declarative_marker": declarative,
    }

p008 = json.loads((ROOT / "p008_final_lock_report.json").read_text(encoding="utf-8"))
if p008.get("lock_identity_sha256") != P008_LOCK_ID:
    raise RuntimeError("P008 Final Lock identity drift")
if p008.get("audit_fingerprint_sha256") != P008_AUDIT_FP:
    raise RuntimeError("P008 audit fingerprint drift")
if p008.get("status") != "LOCKED":
    raise RuntimeError("P008 is not LOCKED")

evidence = {}
for cap, files in CAPABILITIES.items():
    items = [classify(rel) for rel in files]
    present = [x for x in items if x["status"] != "MISSING"]
    implemented = [x for x in items if x["status"] == "IMPLEMENTED"]
    partial = [x for x in items if x["status"] == "PARTIAL"]
    declarative = [x for x in items if x["status"] == "DECLARATIVE"]
    unknown = [x for x in items if x["status"] == "UNKNOWN"]
    tests = [t for t in TEST_MAP.get(cap, []) if (ROOT / t).is_file()]

    if not present:
        overall = "MISSING"
    elif unknown and not implemented:
        overall = "UNKNOWN"
    elif implemented and not (partial or declarative or unknown):
        overall = "IMPLEMENTED"
    elif implemented or partial:
        overall = "PARTIAL"
    else:
        overall = "DECLARATIVE"

    evidence[cap] = {
        "status": overall,
        "files": items,
        "direct_tests_present": tests,
        "counts": {
            "implemented": len(implemented),
            "partial": len(partial),
            "declarative": len(declarative),
            "unknown": len(unknown),
            "missing": len(items) - len(present),
        },
    }

critical = ["environmental_state", "world_representation", "transition_dynamics", "prediction",
            "prediction_error", "learning_model_update", "persistence_memory"]
critical_status = {k: evidence[k]["status"] for k in critical}

# Readiness is deliberately conservative: existence of modules is not proof of a learned,
# integrated state-transition model or closed-loop prediction-error learning.
if any(v in ("MISSING", "UNKNOWN") for v in critical_status.values()):
    readiness = "NOT_READY"
elif all(v == "IMPLEMENTED" for v in critical_status.values()):
    readiness = "PARTIAL_READINESS"
else:
    readiness = "PARTIAL_READINESS"

gaps = []
if evidence["prediction"]["status"] != "IMPLEMENTED":
    gaps.append("prediction capability is not uniformly substantive")
if evidence["transition_dynamics"]["status"] != "IMPLEMENTED":
    gaps.append("state-transition/dynamics capability is not uniformly substantive")
if evidence["prediction_error"]["status"] != "IMPLEMENTED":
    gaps.append("prediction-error computation is not established as a dedicated end-to-end contract")
if evidence["learning_model_update"]["status"] != "IMPLEMENTED":
    gaps.append("prediction-error-driven learning/model update is not established end-to-end")
gaps.append("static audit does not prove that prediction error updates future transition predictions")
gaps.append("static audit does not prove learned latent dynamics or neural world-model substrate")
gaps.append("runtime closed-loop WM exercise remains UNKNOWN until dedicated P009 functional tests")

identity_payload = {
    "schema": "oce.p009.wm_readiness.identity.v1",
    "p008_lock_identity_sha256": P008_LOCK_ID,
    "p008_audit_fingerprint_sha256": P008_AUDIT_FP,
    "capability_status": {k: evidence[k]["status"] for k in sorted(evidence)},
    "readiness": readiness,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}
identity = hashlib.sha256(
    json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()

report = {
    "schema": "oce.p009.wm_readiness.v1",
    "milestone": "P009",
    "audit_execution_status": "COMPLETED",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "audit_identity_sha256": identity,
    "identity_payload": identity_payload,
    "readiness": readiness,
    "readiness_semantics": "engineering readiness for further WM implementation; not phenomenal or consciousness evidence",
    "evidence": evidence,
    "critical_status": critical_status,
    "gaps": gaps,
    "unknowns": [
        "runtime end-to-end WM loop exercise",
        "dynamic dependency resolution beyond inspected modules",
        "learned transition-model adaptation from prediction error",
        "latent-state predictive representation",
    ],
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}
OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

lines = [
    "P009 — WM READINESS AUDIT",
    f"status={report['audit_execution_status']}",
    f"readiness={readiness}",
    f"audit_identity_sha256={identity}",
    "",
]
for cap in CAPABILITIES:
    lines.append(f"{cap}={evidence[cap]['status']}")
lines += ["", "GAPS"] + [f"- {g}" for g in gaps] + ["", "UNKNOWNS"] + [f"- {u}" for u in report["unknowns"]]
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("P009_WM_READINESS_AUDIT_OK")
print(f"readiness={readiness}")
print(f"audit_identity_sha256={identity}")
for cap in CAPABILITIES:
    print(f"{cap}={evidence[cap]['status']}")
print(f"report={OUT_JSON}")
