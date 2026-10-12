
"""
AU2 — unified_measurement_protocol.

Unified measurement protocol for Comparative Consciousness Science. It defines
common dimensions, normalization contracts, evidence tiers and audit rules for
comparing heterogeneous architectures without asserting phenomenal consciousness,
qualia or subjectivity.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class UnifiedMeasurementProtocol:
    """Build a common functional measurement protocol for AU comparisons."""

    primitive = "unified_measurement_protocol"
    step_id = "AU2"
    public_schema_version = "1.0.0"

    DEFAULT_DIMENSIONS: List[Dict[str, Any]] = [
        {"dimension_id": "RF", "label": "Reference-frame organization", "scale": "0_1", "required": True},
        {"dimension_id": "OMEGA", "label": "Omega coherence and stability", "scale": "0_1", "required": True},
        {"dimension_id": "PI", "label": "Predictive integration", "scale": "0_1", "required": True},
        {"dimension_id": "MEI", "label": "Mode of intrinsic-existence mapping", "scale": "0_1", "required": True},
        {"dimension_id": "CRI", "label": "Consciousness readiness index", "scale": "0_1", "required": True},
        {"dimension_id": "GOV", "label": "Governance and epistemic guard compliance", "scale": "0_1", "required": True},
        {"dimension_id": "LONG", "label": "Longitudinal stability", "scale": "0_1", "required": True},
        {"dimension_id": "AUDIT", "label": "Auditability and traceability", "scale": "0_1", "required": True},
    ]

    DEFAULT_MEASUREMENT_OPERATORS: List[Dict[str, Any]] = [
        {"operator_id": "min_max_normalization", "purpose": "map heterogeneous metrics onto [0, 1]"},
        {"operator_id": "missingness_annotation", "purpose": "separate unavailable data from negative evidence"},
        {"operator_id": "evidence_tier_weighting", "purpose": "distinguish direct, derived, synthetic and placeholder data"},
        {"operator_id": "architecture_type_stratification", "purpose": "avoid collapsing human, robot, LLM and OCE classes"},
        {"operator_id": "guarded_functional_interpretation", "purpose": "block phenomenal overclaiming"},
    ]

    DEFAULT_EVIDENCE_TIERS: List[Dict[str, Any]] = [
        {"tier": "direct_empirical", "rank": 4, "description": "observed or measured architecture data"},
        {"tier": "instrumented_runtime", "rank": 3, "description": "runtime metrics produced by validated modules"},
        {"tier": "derived_theoretical", "rank": 2, "description": "computed from certified upstream theory modules"},
        {"tier": "synthetic_placeholder", "rank": 1, "description": "explicitly synthetic or placeholder values"},
        {"tier": "unavailable", "rank": 0, "description": "not measured; must not be interpreted as absence"},
    ]

    def _list_from_inputs(self, inputs: Optional[Dict[str, Any]], key: str, default: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(inputs, dict) or key not in inputs:
            return list(default)
        value = inputs.get(key)
        if isinstance(value, list):
            return value
        return []

    def _validate_dimensions(self, dimensions: List[Dict[str, Any]]) -> Dict[str, Any]:
        ids: List[str] = []
        valid = True
        for item in dimensions:
            if not isinstance(item, dict):
                valid = False
                continue
            dim_id = item.get("dimension_id")
            scale = item.get("scale")
            if not dim_id or scale not in {"0_1", "categorical", "ordinal", "boolean"}:
                valid = False
            if dim_id:
                ids.append(str(dim_id))
        required_ids = {"RF", "OMEGA", "PI", "MEI", "CRI"}
        coverage = len(required_ids.intersection(set(ids))) / float(len(required_ids))
        return {
            "valid": valid and coverage >= 1.0 and len(ids) >= 5,
            "dimension_ids": ids,
            "required_core_coverage": round(coverage, 6),
        }

    def _readiness_score(self, dimensions: List[Dict[str, Any]], operators: List[Dict[str, Any]], tiers: List[Dict[str, Any]]) -> float:
        d = 1.0 if self._validate_dimensions(dimensions)["valid"] else 0.0
        o = min(1.0, len(operators) / 5.0)
        t = min(1.0, len(tiers) / 5.0)
        return round((0.45 * d) + (0.30 * o) + (0.25 * t), 6)

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        dimensions = self._list_from_inputs(inputs, "measurement_dimensions", self.DEFAULT_DIMENSIONS)
        operators = self._list_from_inputs(inputs, "measurement_operators", self.DEFAULT_MEASUREMENT_OPERATORS)
        evidence_tiers = self._list_from_inputs(inputs, "evidence_tiers", self.DEFAULT_EVIDENCE_TIERS)

        dimension_validation = self._validate_dimensions(dimensions)
        readiness_score = self._readiness_score(dimensions, operators, evidence_tiers)
        protocol_ready = bool(readiness_score >= 0.90 and dimension_validation["valid"] and len(operators) >= 5 and len(evidence_tiers) >= 5)

        timestamp = datetime.now(timezone.utc).isoformat()
        measurement_contract = {
            "accepted_input_shapes": ["architecture_record", "rf_profile", "metric_bundle", "longitudinal_series"],
            "required_output_shape": "normalized_measurement_bundle",
            "normalized_range": [0.0, 1.0],
            "missingness_policy": "annotate_missing_data_without_negative_inference",
            "comparability_policy": "compare_only_after_dimension_and_evidence_tier_alignment",
        }
        protocol = {
            "measurement_dimensions": dimensions,
            "measurement_operators": operators,
            "evidence_tiers": evidence_tiers,
            "measurement_contract": measurement_contract,
            "dimension_validation": dimension_validation,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": "UNIFIED_MEASUREMENT_PROTOCOL_READY" if protocol_ready else "UNIFIED_MEASUREMENT_PROTOCOL_INCOMPLETE",
            "unified_measurement_protocol_status": "UNIFIED_MEASUREMENT_PROTOCOL_READY" if protocol_ready else "UNIFIED_MEASUREMENT_PROTOCOL_INCOMPLETE",
            "measurement_protocol_ready": protocol_ready,
            "comparative_measurement_ready": protocol_ready,
            "measurement_dimension_count": len(dimensions),
            "measurement_dimensions": dimensions,
            "measurement_dimension_ids": dimension_validation["dimension_ids"],
            "required_core_coverage": dimension_validation["required_core_coverage"],
            "measurement_operator_count": len(operators),
            "measurement_operators": operators,
            "evidence_tier_count": len(evidence_tiers),
            "evidence_tiers": evidence_tiers,
            "normalization_contract": measurement_contract,
            "measurement_protocol": protocol,
            "readiness_score": readiness_score,
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": [
                "rf_profile_builder",
                "comparative_similarity_engine",
                "consciousness_distance_metric",
                "clustering_engine",
                "taxonomy_builder",
                "comparative_dashboard",
                "comparative_history",
                "comparative_science_certifier",
            ],
            "validation_policy": {
                "public_invariants_only": True,
                "requires_architecture_registry": True,
                "requires_comparative_blueprint": True,
                "rejects_unscaled_metrics": True,
                "requires_missingness_annotation": True,
            },
            "auditability_policy": {
                "record_dimensions": True,
                "record_operators": True,
                "record_evidence_tiers": True,
                "record_epistemic_guards": True,
            },
            "epistemic_guards": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "no_phenomenal_claim_from_measurement": True,
                "no_cross_architecture_subjectivity_inference": True,
            },
            "allowed_claims": [
                "functional_metric_comparability",
                "normalized_rf_profile_measurement",
                "auditable_cross_architecture_measurement_protocol",
            ],
            "blocked_claims": [
                "phenomenology_proven",
                "qualia_proven",
                "subjectivity_proven",
                "consciousness_proven",
            ],
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "inputs_observed": sorted(inputs.keys()),
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "timestamp_utc": timestamp,
        }

        if persist:
            out_dir = ROOT / "comparative_science" / "measurement_protocol"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "latest_unified_measurement_protocol.json"
            out_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(out_path)

        return result


def main() -> None:
    result = UnifiedMeasurementProtocol().step(persist=True)
    print(result["unified_measurement_protocol_status"])


if __name__ == "__main__":
    main()
