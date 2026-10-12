from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_ID = "P001"
TITLE = "Objectif directeur d'OCE"
SPEC_VERSION = "1.1.0"

FUNCTIONAL_INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

CANONICAL_LOOP = (
    "Problem",
    "Observation",
    "World State",
    "World Models",
    "Prediction+Uncertainty",
    "Cognitive Budget",
    "Capabilities/Individuals",
    "Planning/Crowd",
    "Action/Experiment",
    "Outcome",
    "Prediction Error",
    "Learning",
    "AY/ACEE",
    "Cognitive Compilation",
    "Civilizational Memory",
)

# P001 is doctrinal/architectural. This map proves representability by
# existing implementation surfaces; it does NOT claim that later V2 points
# have already reached their own acceptance gates.
REPRESENTATION_MAP = {
    "Problem": (
        "civilizational_research_director",
        "civilizational_strategic_planner",
    ),
    "Observation": (
        "embodied_world_model_update",
        "civilizational_metrics_synthesizer",
    ),
    "World State": (
        "embodied_world_model_update",
        "hierarchical_world_model_engine",
    ),
    "World Models": (
        "hierarchical_world_model_engine",
        "embodied_predictive_planning_bridge",
    ),
    "Prediction+Uncertainty": (
        "acee_prediction_engine",
        "embodied_predictive_planning_bridge",
    ),
    "Cognitive Budget": (
        "civilizational_strategic_planner",
        "civilizational_strategy_orchestrator",
    ),
    "Capabilities/Individuals": (
        "integrated_civilizational_runtime",
        "population_ecological_extraction",
    ),
    "Planning/Crowd": (
        "embodied_planning_engine",
        "civilizational_strategy_orchestrator",
    ),
    "Action/Experiment": (
        "runtime_native_autonomous_execution_loop",
        "runtime_native_scientific_autonomy_loop",
    ),
    "Outcome": (
        "civilizational_metrics_synthesizer",
        "runtime_native_auto_improvement_integration",
    ),
    "Prediction Error": (
        "acee_prediction_engine",
        "runtime_native_auto_improvement_integration",
    ),
    "Learning": (
        "learning",
        "civilizational_meta_learning_engine",
    ),
    "AY/ACEE": (
        "auto_improvement_runtime_bridge",
        "runtime_native_auto_improvement_integration",
    ),
    "Cognitive Compilation": (
        "civilizational_meta_learning_engine",
        "civilizational_memory_engine",
    ),
    "Civilizational Memory": (
        "civilizational_memory",
        "civilizational_memory_engine",
        "civilizational_memory_archive",
    ),
}

GUARD_MODULES = (
    "future_openness",
    "architectural_non_closure_index",
    "constraint_constitution_layer",
    "constitutional_compliance_check",
    "constitutional_integrity_index",
    "civilizational_continuity_guardian",
    "civilizational_identity_preservation",
)

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "UNKNOWN"

def _module_path(root: Path, module: str) -> Path | None:
    candidates = (root / "ontology" / f"{module}.py", root / f"{module}.py")
    for path in candidates:
        if path.is_file():
            return path
    return None

def _module_record(root: Path, module: str) -> dict:
    path = _module_path(root, module)
    if path is None:
        return {
            "module": module,
            "status": "UNKNOWN",
            "reason": "module_file_not_found",
        }
    raw = path.read_bytes()
    try:
        tree = ast.parse(raw.decode("utf-8"))
    except Exception:
        return {
            "module": module,
            "status": "UNKNOWN",
            "path": str(path.relative_to(root)),
            "sha256": _sha256(raw),
            "reason": "syntax_invalid",
        }
    definitions = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for node in ast.walk(tree)
    )
    if definitions < 1:
        return {
            "module": module,
            "status": "UNKNOWN",
            "path": str(path.relative_to(root)),
            "sha256": _sha256(raw),
            "reason": "no_function_or_class_definition",
            "static_definitions": definitions,
        }
    return {
        "module": module,
        "status": "REPRESENTABLE",
        "path": str(path.relative_to(root)),
        "sha256": _sha256(raw),
        "evidence_kind": "static_structural_definition",
        "static_definitions": definitions,
    }

def audit(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"OCE root not found: {root}")

    loop = {}
    unknown = []
    for stage in CANONICAL_LOOP:
        records = [_module_record(root, m) for m in REPRESENTATION_MAP[stage]]
        represented = any(r["status"] == "REPRESENTABLE" for r in records)
        status = "REPRESENTABLE" if represented else "UNKNOWN"
        if status == "UNKNOWN":
            unknown.append(stage)
        loop[stage] = {
            "status": status,
            "evidence": records,
        }

    guards = {}
    for module in GUARD_MODULES:
        record = _module_record(root, module)
        guards[module] = record
        if record["status"] == "UNKNOWN":
            unknown.append(f"guard:{module}")

    result = {
        "canonical_id": CANONICAL_ID,
        "title": TITLE,
        "spec_version": SPEC_VERSION,
        "audit_kind": "functional_architectural_representability",
        "epistemic_scope": "functional_only",
        "canonical_loop": list(CANONICAL_LOOP),
        "loop_coverage": loop,
        "guard_coverage": guards,
        "functional_invariants": FUNCTIONAL_INVARIANTS,
        "unknown": sorted(set(unknown)),
        "all_stages_representable": all(
            item["status"] == "REPRESENTABLE" for item in loop.values()
        ),
        "all_guards_representable": all(
            item["status"] == "REPRESENTABLE" for item in guards.values()
        ),
        "git": {
            "head": _git(root, "rev-parse", "HEAD"),
            "branch": _git(root, "branch", "--show-current"),
        },
        "cwd_independent": True,
        "modifies_production_code": False,
        "baseline_comparison": {
            "status": "DEFERRED_TO_P007",
            "reason": (
                "P001 executes before P007 in W0->W1 order; this audit records "
                "its exact Git/module hashes now and does not falsely claim a "
                "P007 frozen-baseline comparison."
            ),
        },
        "decision": "UNKNOWN",
    }

    if (
        result["all_stages_representable"]
        and result["all_guards_representable"]
        and not result["unknown"]
    ):
        result["decision"] = "P001_REPRESENTABLE"

    stable = dict(result)
    stable.pop("result_hash", None)
    result["result_hash"] = _sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    )
    return result

def main() -> int:
    root = Path(
        os.environ.get("OCE_ROOT", str(Path.home() / "open-cognitive-ecology"))
    )
    result = audit(root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "P001_REPRESENTABLE" else 2

if __name__ == "__main__":
    raise SystemExit(main())
