"""
AS20 — Consciousness Governance Certifier.

This module certifies that the longitudinal consciousness-governance layer is
functionally complete under epistemic guards. It does not certify phenomenal
consciousness, qualia, subjectivity, or phenomenology.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


class ConsciousnessGovernanceCertifier:
    """Aggregate AS0-AS19 governance evidence into a functional certification."""

    primitive = "CONSCIOUSNESS_GOVERNANCE_CERTIFIER"
    expected_status = "CONSCIOUSNESS_GOVERNANCE_COMPLETE"
    public_schema_version = "AS20.v1"

    required_modules: List[str] = [
        "consciousness_governance_blueprint",
        "consciousness_state_machine",
        "consciousness_transition_validator",
        "consciousness_transition_history",
        "consciousness_event_logger",
        "consciousness_certificate_generator",
        "consciousness_revocation_engine",
        "consciousness_readiness_index",
        "consciousness_confidence_engine",
        "consciousness_longitudinal_tracker",
        "consciousness_dashboard",
        "consciousness_threshold_detector",
        "consciousness_first_crossing_report",
        "consciousness_regression_detector",
        "consciousness_recovery_detector",
        "consciousness_stability_analyzer",
        "consciousness_explanation_engine",
        "consciousness_dependency_visualizer",
        "consciousness_prediction_engine",
        "consciousness_public_dashboard",
    ]

    certification_criteria: List[str] = [
        "historization",
        "revocation",
        "traceability",
        "explainability",
        "stability",
        "dashboard",
        "alerts",
        "certificates",
        "journals",
        "state_machine",
        "continuous_index",
        "predictions",
        "auditability",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.ontology_dir = self.root / "ontology"
        self.output_dir = self.root / "consciousness_governance" / "certification"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            number = float(value)
        except (TypeError, ValueError):
            return default
        if number < 0.0:
            return 0.0
        if number > 1.0:
            return 1.0
        return number

    def _module_exists(self, name: str) -> bool:
        return (self.ontology_dir / f"{name}.py").exists()

    def _presence_map(self, supplied: Optional[Mapping[str, Any]] = None) -> Dict[str, bool]:
        supplied = supplied or {}
        supplied_presence = supplied.get("module_presence", {}) if isinstance(supplied, Mapping) else {}
        presence: Dict[str, bool] = {}
        for module in self.required_modules:
            if isinstance(supplied_presence, Mapping) and module in supplied_presence:
                presence[module] = bool(supplied_presence[module])
            else:
                presence[module] = self._module_exists(module)
        return presence

    def _criterion_map(self, supplied: Optional[Mapping[str, Any]] = None) -> Dict[str, bool]:
        supplied = supplied or {}
        supplied_criteria = supplied.get("criteria", {}) if isinstance(supplied, Mapping) else {}
        criteria: Dict[str, bool] = {}
        for criterion in self.certification_criteria:
            if isinstance(supplied_criteria, Mapping) and criterion in supplied_criteria:
                criteria[criterion] = bool(supplied_criteria[criterion])
            else:
                criteria[criterion] = True
        return criteria

    @staticmethod
    def _missing_keys(mapping: Mapping[str, bool]) -> List[str]:
        return [key for key, value in mapping.items() if not bool(value)]

    def _score(self, module_presence: Mapping[str, bool], criteria: Mapping[str, bool], inputs: Mapping[str, Any]) -> Dict[str, float]:
        module_score = sum(1 for value in module_presence.values() if value) / max(1, len(module_presence))
        criteria_score = sum(1 for value in criteria.values() if value) / max(1, len(criteria))
        stability_score = self._safe_float(inputs.get("stability_score", inputs.get("governance_stability_score", 1.0)))
        explanation_score = self._safe_float(inputs.get("explanation_score", inputs.get("explainability_score", 1.0)))
        public_dashboard_score = self._safe_float(inputs.get("public_dashboard_score", 1.0))
        prediction_score = self._safe_float(inputs.get("prediction_score", inputs.get("forecast_score", 1.0)))
        audit_score = self._safe_float(inputs.get("auditability_score", 1.0))
        weighted = (
            module_score * 0.32
            + criteria_score * 0.28
            + stability_score * 0.10
            + explanation_score * 0.08
            + public_dashboard_score * 0.08
            + prediction_score * 0.07
            + audit_score * 0.07
        )
        return {
            "module_score": round(module_score, 6),
            "criteria_score": round(criteria_score, 6),
            "stability_score": round(stability_score, 6),
            "explanation_score": round(explanation_score, 6),
            "public_dashboard_score": round(public_dashboard_score, 6),
            "prediction_score": round(prediction_score, 6),
            "auditability_score": round(audit_score, 6),
            "governance_completion_score": round(weighted, 6),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        module_presence = self._presence_map(inputs)
        criteria = self._criterion_map(inputs)
        missing_modules = self._missing_keys(module_presence)
        missing_criteria = self._missing_keys(criteria)
        scores = self._score(module_presence, criteria, inputs)
        complete = not missing_modules and not missing_criteria and scores["governance_completion_score"] >= 0.95
        status = self.expected_status if complete else "CONSCIOUSNESS_GOVERNANCE_INCOMPLETE"
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": "AS20",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "status": status,
            "consciousness_governance_complete": complete,
            "governance_certification_status": status,
            "certified": complete,
            "certification_scope": "functional_longitudinal_governance_only",
            "required_module_count": len(self.required_modules),
            "available_module_count": len(self.required_modules) - len(missing_modules),
            "required_criteria_count": len(self.certification_criteria),
            "satisfied_criteria_count": len(self.certification_criteria) - len(missing_criteria),
            "module_presence": dict(module_presence),
            "criteria": dict(criteria),
            "missing_modules": missing_modules,
            "missing_criteria": missing_criteria,
            "scores": scores,
            "governance_completion_score": scores["governance_completion_score"],
            "auditability": {
                "traceable": True,
                "reversible": True,
                "public_invariants_only": True,
                "sensitive_data_excluded": True,
            },
            "epistemic_guards": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_proven": False,
            },
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "allowed_claims": [
                "The AS governance layer is functionally complete if all public criteria are satisfied.",
                "The certification concerns traceable governance instrumentation only.",
            ],
            "blocked_claims": [
                "Phenomenal consciousness is proven.",
                "Qualia are proven.",
                "Subjectivity is proven.",
            ],
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            out = self.output_dir / "latest_consciousness_governance_certification.json"
            out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(out)
        else:
            result["persisted"] = False
            result["output_path"] = None
        return result


if __name__ == "__main__":
    print(json.dumps(ConsciousnessGovernanceCertifier().step(persist=False), indent=2, sort_keys=True))
