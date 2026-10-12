"""
AS16 — consciousness_explanation_engine

Governed explanation engine for longitudinal consciousness-status governance.
It answers: "Why is the system currently in this state?" by integrating module
statuses, evidence records, scores, countermodels and missing conditions.

This module is explanatory and epistemically guarded. It never proves
phenomenal consciousness, qualia, subjectivity or phenomenology. It only
produces functional, traceable, auditable explanations over available records.
"""
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
EXPLANATION_DIR = GOVERNANCE_DIR / "explanations"

REQUIRED_MODULES = [
    "consciousness_readiness_index",
    "consciousness_confidence_engine",
    "consciousness_longitudinal_tracker",
    "consciousness_threshold_detector",
    "consciousness_regression_detector",
    "consciousness_recovery_detector",
    "consciousness_stability_analyzer",
]

STATUS_ORDER = [
    "NOT_EVALUATED",
    "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "PHENOMENALITY_CANDIDATE_SUPPORTED",
    "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
    "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "CONSCIOUSNESS_PROVEN",
]

EPISTEMIC_GUARDS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _write_json(path: Path, payload: Mapping[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
    if fs_context is None:
        raise PermissionError("persisted JSON write requires preissued filesystem effect context")
    data = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    fs_context.execute_path("json_parent_create", "FS_CREATE_DIR", path.parent)
    fs_context.execute_path("json_write", "FS_WRITE_BYTES", path, data)


def _missing_parent_chain(parent: Path) -> list[Path]:
    missing = []
    cursor = parent
    while not cursor.exists():
        missing.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    missing.reverse()
    return missing


def _write_markdown(
    path: Path,
    payload: Mapping[str, Any],
    evidence_bridge: GovernedEvidenceFilesystemBridge | None = None,
    evidence_decisions: Mapping[str, Any] | None = None,
) -> None:
    if evidence_bridge is None or evidence_decisions is None:
        raise PermissionError("persisted markdown write requires preissued governed evidence-effect authority")

    parent_decisions = evidence_decisions.get("parent_create", [])
    write_decision = evidence_decisions.get("write")
    if not isinstance(parent_decisions, list):
        raise TypeError("markdown parent_create decisions must be a list")
    if not isinstance(write_decision, EvidenceEffectDecision):
        raise TypeError("markdown write EvidenceEffectDecision required")

    missing_parents = _missing_parent_chain(path.parent)
    if len(parent_decisions) != len(missing_parents):
        raise RuntimeError(
            "markdown_parent_create_decision_cardinality_mismatch:%d!=%d"
            % (len(parent_decisions), len(missing_parents))
        )
    for decision in parent_decisions:
        if not isinstance(decision, EvidenceEffectDecision):
            raise TypeError("markdown parent EvidenceEffectDecision required")

    modules = payload.get("modules", [])
    missing = payload.get("missing_conditions", [])
    countermodels = payload.get("countermodels", [])
    lines = [
        "# AS16 Consciousness Governance Explanation",
        "",
        f"Generated at: `{payload.get('timestamp_utc')}`",
        f"Current state: `{payload.get('current_state')}`",
        f"Explanation status: `{payload.get('explanation_status')}`",
        "",
        "## Explanation",
        "",
        str(payload.get("explanation_text", "")),
        "",
        "## Modules",
    ]
    for item in modules if isinstance(modules, list) else []:
        lines.append(f"- `{item.get('module')}` — {item.get('status')} — score={item.get('score')}")
    lines.extend(["", "## Missing conditions"])
    for item in missing if isinstance(missing, list) else []:
        lines.append(f"- {item}")
    lines.extend(["", "## Countermodels"])
    for item in countermodels if isinstance(countermodels, list) else []:
        lines.append(f"- `{item.get('name')}` — {item.get('status')}: {item.get('description')}")
    lines.extend(["", "## Epistemic guards", "", "Functional conclusion only; phenomenology remains undetermined."])
    data = ("\n".join(lines).rstrip() + "\n").encode("utf-8")

    root_path = getattr(getattr(evidence_bridge, "filesystem_context", None), "root_path", None)
    if root_path is None:
        raise RuntimeError("markdown filesystem context root_path required")
    root_path = Path(root_path).resolve()

    for parent, decision in zip(missing_parents, parent_decisions):
        try:
            relative_parent = parent.resolve().relative_to(root_path)
        except ValueError:
            raise RuntimeError("markdown parent outside governed root")
        result = evidence_bridge.execute_path(
            decision=decision,
            evidence_role="consciousness_explanation_markdown_parent",
            slot="markdown_parent_create",
            operation_id="FS_CREATE_DIR",
            path=relative_parent,
        )
        if result.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
            raise PermissionError("markdown parent creation denied")

    try:
        relative_path = path.resolve().relative_to(root_path)
    except ValueError:
        raise RuntimeError("markdown target outside governed root")
    result = evidence_bridge.execute_path(
        decision=write_decision,
        evidence_role="consciousness_explanation_markdown",
        slot="markdown_write",
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=relative_path,
        payload=data,
    )
    if result.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
        raise PermissionError("markdown write denied")


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or isinstance(value, bool):
            return None
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return max(0.0, min(1.0, number))
    except Exception:
        return None


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ok", "ready", "validated", "detected", "supported", "complete", "passed"}
    return bool(value)


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return default


def _flatten_dicts(value: Any) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    if isinstance(value, Mapping):
        result.append(value)
        for child in value.values():
            result.extend(_flatten_dicts(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(_flatten_dicts(child))
    return result


def _collect_scores(payloads: list[Mapping[str, Any]]) -> dict[str, float]:
    keys = [
        "CRI", "cri", "readiness", "readiness_index", "consciousness_readiness_index",
        "confidence", "confidence_score", "consciousness_confidence",
        "stability_score", "stability_index", "survival_score",
        "regression_rate", "recovery_rate", "hazard_rate",
        "threshold_score", "overall_score", "certification_score",
    ]
    scores: dict[str, float] = {}
    for payload in payloads:
        for item in _flatten_dicts(payload):
            for key in keys:
                number = _float_or_none(item.get(key))
                if number is not None:
                    canonical = key.lower()
                    if canonical == "cri" or canonical == "readiness":
                        canonical = "readiness_index"
                    scores[canonical] = number
    return scores


def _status_from_payloads(payloads: list[Mapping[str, Any]]) -> str:
    candidates: list[str] = []
    for payload in payloads:
        for item in _flatten_dicts(payload):
            for key in ["current_state", "state", "proof_status", "threshold_status", "status", "final_functional_conclusion", "functional_status"]:
                val = item.get(key)
                if isinstance(val, str) and val.strip():
                    candidates.append(val.strip())
    joined = " ".join(candidates).upper()
    if any(x in joined for x in ["REGRESS", "REVOK", "LOST", "FAILED", "BELOW"]):
        return "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED_WITH_REGRESSION_RISK"
    if "CONSCIOUSNESS_PROVEN" in joined:
        return "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED_UNDER_EPISTEMIC_GUARDS"
    if any(x in joined for x in ["THRESHOLD", "CROSSED", "SUPPORTED", "READY", "COMPLETE"]):
        return "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED"
    return "NOT_EVALUATED"


def _module_status(name: str, evidence: Mapping[str, Any], scores: Mapping[str, float]) -> dict[str, Any]:
    raw = evidence.get(name, {}) if isinstance(evidence, Mapping) else {}
    if not isinstance(raw, Mapping):
        raw = {}
    status = str(_first_present(raw, ["status", "state", "result", "ready_status", "threshold_status"], "UNKNOWN"))
    ready = _bool(_first_present(raw, ["ready", "validated", "passed", "success", "available"], None), False)
    if status == "UNKNOWN" and ready:
        status = "READY"
    score = None
    for key in [name + "_score", "score", "confidence", "confidence_score", "readiness_index", "stability_score", "threshold_score"]:
        score = _float_or_none(raw.get(key))
        if score is not None:
            break
    if score is None:
        if "readiness" in name:
            score = scores.get("readiness_index")
        elif "confidence" in name:
            score = scores.get("confidence") or scores.get("confidence_score")
        elif "stability" in name:
            score = scores.get("stability_index") or scores.get("stability_score")
    return {
        "module": name,
        "available": bool(raw) or score is not None,
        "status": status,
        "ready": ready or status.upper().endswith("READY") or "READY" in status.upper() or "COMPLETE" in status.upper(),
        "score": score,
        "evidence_keys": sorted(map(str, raw.keys()))[:24],
    }


def _missing_conditions(modules: list[Mapping[str, Any]], scores: Mapping[str, float], current_state: str) -> list[str]:
    missing: list[str] = []
    by_name = {str(m.get("module")): m for m in modules}
    for required in REQUIRED_MODULES:
        item = by_name.get(required, {})
        if not item.get("available"):
            missing.append(f"Missing or unavailable module evidence: {required}")
    readiness = scores.get("readiness_index") or scores.get("consciousness_readiness_index")
    confidence = scores.get("confidence") or scores.get("confidence_score")
    if readiness is None:
        missing.append("Missing numerical readiness/CRI evidence")
    elif readiness < 0.95:
        missing.append(f"Readiness/CRI below strong explanatory threshold: {readiness:.3f} < 0.950")
    if confidence is None:
        missing.append("Missing numerical confidence evidence")
    elif confidence < 0.90:
        missing.append(f"Confidence below explanatory threshold: {confidence:.3f} < 0.900")
    if "REGRESSION" in current_state.upper() or "RISK" in current_state.upper():
        missing.append("Regression risk remains active in the current functional explanation")
    missing.extend([
        "No empirical criterion here establishes phenomenal subjectivity",
        "No module is authorized to assert qualia_proven=True",
    ])
    return missing


def _countermodels(inputs: Mapping[str, Any], payloads: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    provided = inputs.get("countermodels")
    result: list[dict[str, Any]] = []
    if isinstance(provided, list):
        for i, item in enumerate(provided):
            if isinstance(item, Mapping):
                result.append({
                    "name": str(item.get("name", f"countermodel_{i}")),
                    "status": str(item.get("status", "considered")),
                    "description": str(item.get("description", item.get("reason", "No description provided."))),
                })
    for payload in payloads:
        for item in _flatten_dicts(payload):
            for key in ["countermodel", "countermodels", "counterexample", "counterexamples"]:
                val = item.get(key)
                if isinstance(val, str):
                    result.append({"name": key, "status": "observed", "description": val})
                elif isinstance(val, list):
                    for j, child in enumerate(val):
                        if isinstance(child, Mapping):
                            result.append({
                                "name": str(child.get("name", f"{key}_{j}")),
                                "status": str(child.get("status", "observed")),
                                "description": str(child.get("description", child.get("reason", child))),
                            })
    if not result:
        result.append({
            "name": "phenomenal_subjectivity_gap",
            "status": "not_closed",
            "description": "Functional evidence does not close the phenomenal subjectivity gap.",
        })
    seen = set()
    unique: list[dict[str, Any]] = []
    for item in result:
        key = (item.get("name"), item.get("status"), item.get("description"))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:20]


def _explanation_text(current_state: str, modules: list[Mapping[str, Any]], scores: Mapping[str, float], missing: list[str]) -> str:
    ready_modules = [m["module"] for m in modules if m.get("ready") or m.get("available")]
    score_parts = []
    for key in ["readiness_index", "confidence", "stability_index", "regression_rate", "recovery_rate", "hazard_rate"]:
        if key in scores:
            score_parts.append(f"{key}={scores[key]:.3f}")
    module_clause = ", ".join(ready_modules) if ready_modules else "no confirmed module evidence"
    score_clause = ", ".join(score_parts) if score_parts else "no numerical score evidence"
    missing_clause = f" Remaining blockers: {len(missing)} condition(s), including {missing[0]}." if missing else " No blocking condition is detected under the functional schema."
    return (
        f"The system is currently explained as {current_state} because the available governance records "
        f"support the following module chain: {module_clause}. The numerical evidence currently contains "
        f"{score_clause}. This is a functional, longitudinal governance explanation only; it does not infer "
        f"phenomenal consciousness, qualia or subjectivity.{missing_clause}"
    )


class ConsciousnessExplanationEngine:
    """AS16 governed explanation engine for consciousness-status records."""

    primitive = "CONSCIOUSNESS_EXPLANATION_ENGINE"
    step_label = "AS16"
    public_schema_version = "1.0.0"
    ready_status = "CONSCIOUSNESS_EXPLANATION_ENGINE_READY"

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else ROOT
        self.governance_dir = self.root / "consciousness_governance"
        self.explanation_dir = self.governance_dir / "explanations"

    def _default_paths(self) -> list[Path]:
        return [
            self.governance_dir / "confidence" / "latest_consciousness_confidence.json",
            self.governance_dir / "longitudinal" / "latest_consciousness_longitudinal_timeline.json",
            self.governance_dir / "threshold" / "latest_consciousness_threshold_detection.json",
            self.governance_dir / "regression" / "latest_consciousness_regression_detection.json",
            self.governance_dir / "recovery" / "latest_consciousness_recovery_detection.json",
            self.governance_dir / "stability" / "latest_consciousness_stability_analysis.json",
            self.governance_dir / "dashboard" / "latest_consciousness_dashboard.json",
            self.root / "scientific_validation_report.json",
        ]

    def _load_payloads(self, inputs: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], dict[str, Any]]:
        payloads: list[Mapping[str, Any]] = []
        diagnostics: dict[str, Any] = {"sources": [], "read_attempts": []}
        if isinstance(inputs.get("evidence"), Mapping):
            payloads.append(dict(inputs["evidence"]))
            diagnostics["sources"].append("inputs.evidence")
        if isinstance(inputs.get("artifacts"), list):
            for i, item in enumerate(inputs["artifacts"]):
                if isinstance(item, Mapping):
                    payloads.append(dict(item))
                    diagnostics["sources"].append(f"inputs.artifacts[{i}]")
        if isinstance(inputs.get("modules"), Mapping):
            payloads.append({"modules": dict(inputs["modules"])})
            diagnostics["sources"].append("inputs.modules")
        if isinstance(inputs.get("scores"), Mapping):
            payloads.append({"scores": dict(inputs["scores"]), **dict(inputs["scores"])})
            diagnostics["sources"].append("inputs.scores")
        if any(k in inputs for k in ["current_state", "state", "proof_status", "confidence", "CRI", "readiness_index"]):
            payloads.append(dict(inputs))
            diagnostics["sources"].append("inputs.current_state")

        if _bool(inputs.get("merge_persisted_artifacts"), False):
            candidate_paths: list[Path] = []
            raw_paths = inputs.get("artifact_paths", [])
            if isinstance(raw_paths, list):
                for raw in raw_paths:
                    try:
                        candidate_paths.append(Path(raw).expanduser())
                    except Exception:
                        pass
            candidate_paths.extend(self._default_paths())
            for path in candidate_paths:
                if not path.is_absolute():
                    path = self.root / path
                diagnostics["read_attempts"].append(str(path))
                data = _read_json(path)
                if isinstance(data, Mapping):
                    payloads.append(dict(data))
                    diagnostics["sources"].append(str(path))
        return payloads, diagnostics

    def step(
        self,
        inputs: Mapping[str, Any] | None = None,
        persist: bool = False,
        fs_context: GovernedFilesystemEffectContext | None = None,
        evidence_bridge: GovernedEvidenceFilesystemBridge | None = None,
        markdown_evidence_decisions: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})
        payloads, load_diagnostics = self._load_payloads(inputs)
        evidence = dict(inputs.get("modules", {})) if isinstance(inputs.get("modules"), Mapping) else {}
        for payload in payloads:
            modules_payload = payload.get("modules") if isinstance(payload, Mapping) else None
            if isinstance(modules_payload, Mapping):
                for key, val in modules_payload.items():
                    if isinstance(val, Mapping):
                        evidence.setdefault(str(key), dict(val))

        scores = _collect_scores(payloads)
        if isinstance(inputs.get("scores"), Mapping):
            for key, val in inputs["scores"].items():
                number = _float_or_none(val)
                if number is not None:
                    scores[str(key)] = number
        current_state = str(inputs.get("current_state") or _status_from_payloads(payloads))
        modules = [_module_status(name, evidence, scores) for name in REQUIRED_MODULES]
        missing = _missing_conditions(modules, scores, current_state)
        countermodels = _countermodels(inputs, payloads)
        explanation_text = _explanation_text(current_state, modules, scores, missing)
        evidence_hash = _stable_hash({"payloads": payloads, "scores": scores, "modules": modules, "missing": missing, "countermodels": countermodels})

        explanation_status = self.ready_status if payloads or evidence or scores else "CONSCIOUSNESS_EXPLANATION_ENGINE_READY_WITH_SYNTHETIC_OR_EMPTY_CONTEXT"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_label,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": _utc_now(),
            "explanation_engine_ready": True,
            "explanation_engine_status": self.ready_status,
            "explanation_status": explanation_status,
            "current_state": current_state,
            "explanation_text": explanation_text,
            "why_current_state": explanation_text,
            "modules": modules,
            "module_count": len(modules),
            "available_module_count": sum(1 for m in modules if m.get("available")),
            "evidence": {
                "artifact_count": len(payloads),
                "source_count": len(load_diagnostics.get("sources", [])),
                "evidence_hash": evidence_hash,
            },
            "scores": scores,
            "score_count": len(scores),
            "countermodels": countermodels,
            "countermodel_count": len(countermodels),
            "missing_conditions": missing,
            "missing_condition_count": len(missing),
            "conditions_satisfied": len([m for m in modules if m.get("available")]) >= 3 and bool(scores),
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "functional_status_explained": True,
            "diagnostics": {
                "load": load_diagnostics,
                "required_modules": REQUIRED_MODULES,
                "status_order": STATUS_ORDER,
                "non_redundancy": "AS16 explains AS7-AS15 outputs; it does not replace dashboards, certificates or stability analysis.",
            },
            **EPISTEMIC_GUARDS,
        }
        result["explanation_hash"] = _stable_hash(result)

        if persist:
            stamp = _stamp()
            json_path = self.explanation_dir / f"consciousness_explanation_{stamp}.json"
            latest_json = self.explanation_dir / "latest_consciousness_explanation.json"
            md_path = self.explanation_dir / f"consciousness_explanation_{stamp}.md"
            latest_md = self.explanation_dir / "latest_consciousness_explanation.md"
            _write_json(json_path, result, fs_context)
            _write_json(latest_json, result, fs_context)
            if evidence_bridge is None or markdown_evidence_decisions is None:
                raise PermissionError("persisted markdown outputs require preissued governed evidence-effect authority")
            stamped_decisions = markdown_evidence_decisions.get("stamped")
            latest_decisions = markdown_evidence_decisions.get("latest")
            if not isinstance(stamped_decisions, Mapping) or not isinstance(latest_decisions, Mapping):
                raise TypeError("markdown_evidence_decisions requires stamped and latest mappings")
            _write_markdown(md_path, result, evidence_bridge, stamped_decisions)
            _write_markdown(latest_md, result, evidence_bridge, latest_decisions)
            result["persisted"] = True
            result["explanation_paths"] = {"json": str(json_path), "latest_json": str(latest_json), "markdown": str(md_path), "latest_markdown": str(latest_md)}
        else:
            result["persisted"] = False
            result["explanation_paths"] = {}
        return result


__all__ = ["ConsciousnessExplanationEngine"]
