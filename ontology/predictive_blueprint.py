"""
AT0 — predictive_blueprint.

Foundational predictive-science blueprint for RF*.
This module defines the public rules by which RF* may be treated as a
predictive theory without ever asserting phenomenological proof.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class PredictiveBlueprint:
    """Define the RF* predictive-science charter for axis AT."""

    primitive = "PREDICTIVE_BLUEPRINT"
    step_id = "AT0"
    public_schema_version = "1.0"
    output_dir = ROOT / "predictive_science" / "AT0_predictive_blueprint"

    prediction_types: List[str] = [
        "structural",
        "dynamic",
        "topological",
        "spectral",
        "developmental",
        "collective",
    ]

    confidence_levels: Dict[str, Dict[str, Any]] = {
        "low": {"range": [0.0, 0.49], "interpretation": "hypothesis_only"},
        "medium": {"range": [0.50, 0.74], "interpretation": "provisionally_supported"},
        "high": {"range": [0.75, 0.89], "interpretation": "strong_functional_support"},
        "critical": {"range": [0.90, 1.0], "interpretation": "requires_independent_replication"},
    }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _blueprint(self) -> Dict[str, Any]:
        return {
            "prediction_definition": {
                "definition": "A prediction is a pre-registered, observable consequence that should follow if RF* is functionally adequate within its stated scope.",
                "requires_observable": True,
                "requires_time_ordering": True,
                "requires_refutation_path": True,
                "requires_epistemic_scope": "functional_only",
            },
            "confidence_model": {
                "scale": "0.0_to_1.0",
                "levels": self.confidence_levels,
                "default_confidence": 0.0,
                "upgrade_rule": "confidence increases only through successful independent validation and cross-context replication",
                "downgrade_rule": "confidence decreases after failed validation, countermodel success, or missing observability",
            },
            "prediction_types": list(self.prediction_types),
            "validation_rules": {
                "validated": "observable signature matches the registered prediction under stated conditions",
                "invalidated": "observable signature contradicts the registered prediction or a countermodel explains the observation better",
                "unknown": "insufficient, unavailable, or non-discriminative evidence",
                "replication_required": True,
                "statistical_support_required": True,
            },
            "refutation_rules": {
                "refutable": True,
                "refutation_requires": [
                    "explicit condition set",
                    "measurable signature",
                    "negative observation criterion",
                    "countermodel or competing-theory comparison",
                ],
                "blocked_refutations": [
                    "purely verbal disagreement without observable consequence",
                    "phenomenological claims without empirical access criteria",
                ],
            },
            "competing_theories": [
                "IIT",
                "GWT",
                "HOT",
                "Predictive Processing",
                "classical_functionalism",
            ],
            "scientific_output_contract": {
                "registry_required": True,
                "falsification_protocol_required": True,
                "public_dashboard_required": True,
                "longitudinal_tracking_required": True,
                "independent_replication_required_for_certification": True,
            },
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        blueprint = self._blueprint()
        readiness_score = 1.0 if blueprint["prediction_types"] and blueprint["refutation_rules"]["refutable"] else 0.0
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "status": "PREDICTIVE_BLUEPRINT_READY",
            "predictive_blueprint_status": "PREDICTIVE_BLUEPRINT_READY",
            "rf_star_predictive_program_ready": True,
            "blueprint": blueprint,
            "prediction_types": list(self.prediction_types),
            "confidence_levels": self.confidence_levels,
            "validation_policy": blueprint["validation_rules"],
            "refutation_policy": blueprint["refutation_rules"],
            "readiness_score": readiness_score,
            "inputs_observed": sorted(inputs.keys()),
            "allowed_claims": [
                "RF* predictive program initialized",
                "functional predictions may be registered, tested, validated, invalidated, or left unknown",
                "all conclusions remain within functional-scientific scope",
            ],
            "blocked_claims": [
                "phenomenology proven",
                "qualia proven",
                "subjectivity proven",
                "consciousness proven beyond empirical criteria",
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persisted": False,
            "output_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_predictive_blueprint.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
