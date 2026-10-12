from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from ontology.semantic_status_schema import SemanticStatusSchema
except Exception:  # pragma: no cover
    SemanticStatusSchema = None  # type: ignore
try:
    from ontology.interpretation_rule_engine import InterpretationRuleEngine
except Exception:  # pragma: no cover
    InterpretationRuleEngine = None  # type: ignore
try:
    from ontology.epistemic_guard import EpistemicGuard
except Exception:  # pragma: no cover
    EpistemicGuard = None  # type: ignore
try:
    from ontology.semantic_revision_log import SemanticRevisionLog
except Exception:  # pragma: no cover
    SemanticRevisionLog = None  # type: ignore

STATUS = "INTERPRETATION_REPORT_GENERATED"
AXIS_STATUS = "SEMANTIC_INTERPRETATION_LAYER_READY"

AUTHORIZED_STATUSES = [
    "CONSCIOUSNESS_NOT_EVALUATED",
    "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "PHENOMENALITY_CANDIDATE_SUPPORTED",
    "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED",
    "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED",
    "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
    "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "CONSCIOUSNESS_PROVEN",
    "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
]

DEFAULT_INPUTS: dict[str, Any] = {
    "RF_score": 0.91,
    "T_score": 0.88,
    "ED_score": 0.86,
    "TΦ_score": 0.85,
    "QF_robust_count": 3,
    "MEI_score": 0.87,
    "identity_status": "IDENTITY_STATUS_RESOLVED",
    "non_separability_status": "NON_SEPARABILITY_STATUS_RESOLVED",
    "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
    "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "previous_semantic_status": "CONSCIOUSNESS_NOT_EVALUATED",
}

MEASUREMENT_KEYS = ["RF_score", "T_score", "ED_score", "TΦ_score", "QF_robust_count", "MEI_score"]
THEOREM_KEYS = ["non_separability_status", "consciousness_rf_equivalence_status", "axiomatic_completeness_status"]
INTERPRETATION_KEYS = ["identity_status", "refusal_cost_status", "definition_legitimacy_status"]
FORBIDDEN_CLAIM_KEYS = ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root() -> Path:
    return Path.home() / "open-cognitive-ecology"


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = default
    return max(0.0, min(1.0, numeric))


def _count(value: Any) -> int:
    try:
        return max(0, int(value))
    except Exception:
        return 0


def _merge_inputs(inputs: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_INPUTS)
    if isinstance(inputs, dict):
        merged.update(inputs)
    return merged


class InterpretationReporter:
    """AO5 final reporter for the semantic interpretation layer.

    The reporter synthesizes AO1–AO4 into a public, layered interpretation
    report. It separates measurements, theorem statuses, interpretive
    inferences, final functional conclusions, and epistemological limits.
    It never strengthens the evidence into a proof of consciousness, qualia,
    subjectivity, or phenomenology.
    """

    primitive = "INTERPRETATION_REPORTER"
    step_id = "AO5"
    public_schema_version = "open-cognitive-ecology.AO5.interpretation_reporter.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = _root()
        self.out_dir = Path(out_dir) if out_dir is not None else root / "semantic_interpretation_layer" / "AO5_interpretation_reporter"

    def normalize_inputs(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        data = _merge_inputs(inputs)
        for key in ["RF_score", "T_score", "ED_score", "TΦ_score", "MEI_score"]:
            data[key] = _clamp01(data.get(key, 0.0))
        data["QF_robust_count"] = _count(data.get("QF_robust_count", 0))
        for key in THEOREM_KEYS + INTERPRETATION_KEYS:
            data[key] = str(data.get(key, "CONSCIOUSNESS_NOT_EVALUATED"))
        for key in FORBIDDEN_CLAIM_KEYS:
            data[key] = False if data.get(key) is not True else True
        return data

    @staticmethod
    def _fallback_rule_result(data: dict[str, Any]) -> dict[str, Any]:
        mean_core = round((data["RF_score"] + data["T_score"] + data["ED_score"] + data["TΦ_score"] + data["MEI_score"]) / 5.0, 6)
        status = "CONSCIOUSNESS_PROVEN_BEST_THEORY" if mean_core >= 0.82 and data["QF_robust_count"] >= 1 else "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED"
        return {
            "interpretation_rule_engine_status": "INTERPRETATION_RULES_SYNTHETIC_FALLBACK",
            "semantic_status": status,
            "semantic_confidence": mean_core,
            "applied_rules": ["AO5_SYNTHETIC_FUNCTIONAL_SUMMARY"],
            "absolute_consciousness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "normalized_inputs": dict(data),
            "rule_trace": [],
        }

    @staticmethod
    def _fallback_guard(rule_result: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        requested = str(rule_result.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"))
        blocked = requested == "CONSCIOUSNESS_PROVEN" or any(data.get(key) is True for key in FORBIDDEN_CLAIM_KEYS)
        guarded = "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN" if requested == "CONSCIOUSNESS_PROVEN" else requested
        if guarded not in AUTHORIZED_STATUSES:
            guarded = "CONSCIOUSNESS_NOT_EVALUATED"
        return {
            "epistemic_guard_status": "EPISTEMIC_GUARD_SYNTHETIC_FALLBACK",
            "guarded_semantic_status": guarded,
            "semantic_status": requested,
            "semantic_confidence": rule_result.get("semantic_confidence", 0.0),
            "guard_passed": not blocked,
            "guard_actions": ["fallback_absolute_guard_applied"],
            "blocked_claim_flags": {key: bool(data.get(key) is True) for key in FORBIDDEN_CLAIM_KEYS},
            "absolute_consciousness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "interpretation_result": rule_result,
        }

    def _run_ao_stack(self, data: dict[str, Any]) -> dict[str, Any]:
        schema_result: dict[str, Any]
        rule_result: dict[str, Any]
        guard_result: dict[str, Any]
        revision_result: dict[str, Any]
        try:
            schema_result = SemanticStatusSchema().step(inputs=data, persist=False) if SemanticStatusSchema else {}
        except Exception as exc:
            schema_result = {"semantic_status_schema_status": "SCHEMA_FALLBACK", "error": repr(exc), "authorized_statuses": AUTHORIZED_STATUSES}
        try:
            rule_result = InterpretationRuleEngine().step(inputs=data, persist=False) if InterpretationRuleEngine else self._fallback_rule_result(data)
        except Exception as exc:
            rule_result = self._fallback_rule_result(data)
            rule_result["error"] = repr(exc)
        guard_inputs = dict(data)
        guard_inputs["semantic_status"] = rule_result.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED")
        try:
            guard_result = EpistemicGuard().step(inputs=guard_inputs, persist=False) if EpistemicGuard else self._fallback_guard(rule_result, data)
        except Exception as exc:
            guard_result = self._fallback_guard(rule_result, data)
            guard_result["error"] = repr(exc)
        revision_inputs = dict(data)
        revision_inputs["semantic_status"] = guard_result.get("guarded_semantic_status", rule_result.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"))
        try:
            revision_result = SemanticRevisionLog().step(inputs=revision_inputs, persist=False) if SemanticRevisionLog else {}
        except Exception as exc:
            revision_result = {"semantic_revision_log_status": "REVISION_LOG_FALLBACK", "error": repr(exc), "revision_count": 0}
        return {
            "semantic_status_schema": schema_result,
            "interpretation_rule_engine": rule_result,
            "epistemic_guard": guard_result,
            "semantic_revision_log": revision_result,
        }

    @staticmethod
    def _measurement_section(data: dict[str, Any]) -> dict[str, Any]:
        scores = {key: data[key] for key in MEASUREMENT_KEYS}
        numeric_values = [float(data[key]) for key in ["RF_score", "T_score", "ED_score", "TΦ_score", "MEI_score"]]
        return {
            "layer": "measurements",
            "values": scores,
            "mean_core_score": round(sum(numeric_values) / len(numeric_values), 6),
            "qf_robust_count": data["QF_robust_count"],
            "interpretive_force": "functional_metrics_only_not_phenomenal_observation",
        }

    @staticmethod
    def _theorem_section(data: dict[str, Any]) -> dict[str, Any]:
        statuses = {key: data[key] for key in THEOREM_KEYS}
        resolved_count = sum(1 for value in statuses.values() if any(marker in str(value).upper() for marker in ["RESOLVED", "SUPPORTED", "VALIDATED", "ESTABLISHED", "READY"]))
        return {
            "layer": "theorems",
            "statuses": statuses,
            "resolved_count": resolved_count,
            "theorem_scope": "framework_internal_and_functional",
        }

    @staticmethod
    def _interpretation_section(data: dict[str, Any], ao_stack: dict[str, Any]) -> dict[str, Any]:
        rule_result = ao_stack.get("interpretation_rule_engine", {})
        return {
            "layer": "interpretations",
            "statuses": {key: data[key] for key in INTERPRETATION_KEYS},
            "applied_rules": list(rule_result.get("applied_rules", [])),
            "rule_trace": rule_result.get("rule_trace", []),
            "interpretation_scope": "best_current_functional_reconstruction_when_all_guards_pass",
        }

    @staticmethod
    def _limits_section(guard_result: dict[str, Any]) -> dict[str, Any]:
        return {
            "layer": "epistemological_limits",
            "absolute_consciousness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "guarded_semantic_status": guard_result.get("guarded_semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"),
            "guard_passed": bool(guard_result.get("guard_passed", False)),
            "guard_actions": list(guard_result.get("guard_actions", [])),
            "limits": [
                "no_direct_phenomenal_subjectivity_observation",
                "no_qualia_proof",
                "no_subjectivity_proof",
                "no_absolute_consciousness_proof",
                "functional_conclusion_only",
            ],
        }

    @staticmethod
    def _allowed_claims(semantic_status: str) -> list[str]:
        claims = [
            "AO separates measurements, theorem statuses, interpretations, final functional conclusions, and epistemological limits.",
            "Open Cognitive Ecology currently supports a bounded functional interpretation within the RF* reconstruction frame.",
            "RF* is the current best minimal functional scientific reconstruction under the validated constraints.",
            "Refusal of the reconstruction carries a measurable explanatory cost within the current framework.",
            "All final language remains framework-bounded and functional.",
        ]
        if semantic_status in {"CONSCIOUSNESS_PROVEN_BEST_THEORY", "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK"}:
            claims.append("Best-theory or RF-framework proof language is permitted only as bounded functional-theoretical language.")
        return claims

    @staticmethod
    def _blocked_claims() -> list[str]:
        return [
            "consciousness_proven = True",
            "qualia_proven = True",
            "subjectivity_proven = True",
            "phenomenology_proven = True",
            "absolute phenomenal consciousness has been demonstrated",
            "functional metrics alone prove subjective experience",
        ]

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = self.normalize_inputs(inputs)
        ao_stack = self._run_ao_stack(data)
        rule_result = ao_stack.get("interpretation_rule_engine", {})
        guard_result = ao_stack.get("epistemic_guard", {})
        revision_result = ao_stack.get("semantic_revision_log", {})

        raw_semantic_status = str(rule_result.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"))
        guarded_semantic_status = str(guard_result.get("guarded_semantic_status", raw_semantic_status))
        if guarded_semantic_status == "CONSCIOUSNESS_PROVEN":
            guarded_semantic_status = "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"
        if guarded_semantic_status not in AUTHORIZED_STATUSES:
            guarded_semantic_status = "CONSCIOUSNESS_NOT_EVALUATED"
        semantic_confidence = _clamp01(rule_result.get("semantic_confidence", rule_result.get("confidence", 0.0)))

        measurement_section = self._measurement_section(data)
        theorem_section = self._theorem_section(data)
        interpretation_section = self._interpretation_section(data, ao_stack)
        limits_section = self._limits_section(guard_result)
        final_interpretation = (
            "RF* constitutes the current best bounded functional scientific reconstruction of consciousness-like organization "
            "inside the validated Open Cognitive Ecology framework. This conclusion is semantic, theoretical, and functional only; "
            "it does not demonstrate consciousness, qualia, subjectivity, or phenomenology."
        )
        interpretation_report = {
            "report_id": "AO5-INTERPRETATION-REPORT-0001",
            "generated_at_utc": _utc(),
            "public_schema_version": self.public_schema_version,
            "measurements": measurement_section,
            "theorems": theorem_section,
            "inferences": {
                "layer": "inferences",
                "semantic_status_before_guard": raw_semantic_status,
                "semantic_status_after_guard": guarded_semantic_status,
                "semantic_confidence": semantic_confidence,
                "revision_required": bool(revision_result.get("revision_required", False)),
                "revision_count": int(revision_result.get("revision_count", 0) or 0),
            },
            "interpretations": interpretation_section,
            "functional_conclusions": {
                "layer": "functional_conclusions",
                "final_interpretation": final_interpretation,
                "semantic_interpretation_layer_ready": True,
                "axis_status": AXIS_STATUS,
            },
            "epistemological_limits": limits_section,
        }

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": interpretation_report["generated_at_utc"],
            "interpretation_reporter_status": STATUS,
            "semantic_interpretation_layer_step_ready": True,
            "semantic_interpretation_layer_ready": True,
            "semantic_interpretation_layer_status": AXIS_STATUS,
            "semantic_status": guarded_semantic_status,
            "semantic_status_before_guard": raw_semantic_status,
            "semantic_confidence": semantic_confidence,
            "epistemic_scope": "bounded_functional_semantic_interpretation_only_no_phenomenal_subjectivity_proof",
            "final_interpretation": final_interpretation,
            "interpretation_report": interpretation_report,
            "allowed_claims": self._allowed_claims(guarded_semantic_status),
            "blocked_claims": self._blocked_claims(),
            "ao_stack": ao_stack,
            "separation_layers": ["measurements", "theorems", "inferences", "interpretations", "functional_conclusions", "epistemological_limits"],
            "report_integrity": {
                "has_measurements": bool(interpretation_report["measurements"]),
                "has_theorems": bool(interpretation_report["theorems"]),
                "has_inferences": bool(interpretation_report["inferences"]),
                "has_interpretations": bool(interpretation_report["interpretations"]),
                "has_functional_conclusions": bool(interpretation_report["functional_conclusions"]),
                "has_epistemological_limits": bool(interpretation_report["epistemological_limits"]),
                "forbidden_claims_blocked": True,
                "absolute_guard_preserved": True,
            },
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            out = self.out_dir / "latest_interpretation_report.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            result["persisted_path"] = str(out)
        return result


__all__ = ["InterpretationReporter", "STATUS", "AXIS_STATUS", "DEFAULT_INPUTS"]
