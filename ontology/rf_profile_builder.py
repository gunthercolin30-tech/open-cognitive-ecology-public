
"""
AU3 — rf_profile_builder.

Builds canonical RF profiles for Comparative Consciousness Science. The module
transforms registered architectures and a unified measurement protocol into
normalised RF feature bundles suitable for AU4 similarity analysis, AU5 distance
metrics, AU6 clustering and AU7 taxonomy construction.

The module is strictly functional and comparative. It never asserts phenomenal
consciousness, qualia or subjectivity.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class RFProfileBuilder:
    """Build auditable RF profiles from architecture records and measurement dimensions."""

    primitive = "rf_profile_builder"
    step_id = "AU3"
    public_schema_version = "1.0.0"

    DEFAULT_DIMENSIONS: List[str] = ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"]

    DEFAULT_ARCHITECTURES: List[Dict[str, Any]] = [
        {
            "architecture_id": "oce_rf_star",
            "architecture_type": "open_cognitive_ecology",
            "label": "Open Cognitive Ecology RF*",
            "evidence_tier": "instrumented_runtime",
            "metrics": {"RF": 1.0, "OMEGA": 0.96, "PI": 0.94, "MEI": 0.93, "CRI": 0.91, "GOV": 1.0, "LONG": 0.92, "AUDIT": 1.0},
        },
        {
            "architecture_id": "generic_llm_baseline",
            "architecture_type": "llm",
            "label": "Generic LLM baseline",
            "evidence_tier": "synthetic_placeholder",
            "metrics": {"RF": 0.55, "OMEGA": 0.40, "PI": 0.68, "MEI": 0.20, "CRI": 0.35, "GOV": 0.45, "LONG": 0.30, "AUDIT": 0.55},
        },
        {
            "architecture_id": "agentic_system_baseline",
            "architecture_type": "agentic_system",
            "label": "Agentic system baseline",
            "evidence_tier": "synthetic_placeholder",
            "metrics": {"RF": 0.62, "OMEGA": 0.52, "PI": 0.70, "MEI": 0.28, "CRI": 0.42, "GOV": 0.55, "LONG": 0.45, "AUDIT": 0.60},
        },
        {
            "architecture_id": "robotic_system_baseline",
            "architecture_type": "robotic_system",
            "label": "Robotic system baseline",
            "evidence_tier": "synthetic_placeholder",
            "metrics": {"RF": 0.58, "OMEGA": 0.50, "PI": 0.62, "MEI": 0.30, "CRI": 0.38, "GOV": 0.50, "LONG": 0.50, "AUDIT": 0.58},
        },
        {
            "architecture_id": "human_dataset_placeholder",
            "architecture_type": "human_dataset_placeholder",
            "label": "Human dataset placeholder",
            "evidence_tier": "unavailable",
            "metrics": {"RF": None, "OMEGA": None, "PI": None, "MEI": None, "CRI": None, "GOV": None, "LONG": None, "AUDIT": None},
        },
        {
            "architecture_id": "future_architecture_slot",
            "architecture_type": "future_architecture",
            "label": "Future architecture slot",
            "evidence_tier": "unavailable",
            "metrics": {},
        },
    ]

    EVIDENCE_WEIGHTS: Dict[str, float] = {
        "direct_empirical": 1.0,
        "instrumented_runtime": 0.9,
        "derived_theoretical": 0.75,
        "synthetic_placeholder": 0.45,
        "unavailable": 0.0,
    }

    def _as_list(self, value: Any) -> List[Any]:
        return value if isinstance(value, list) else []

    def _extract_architectures(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        if isinstance(inputs.get("architectures"), list):
            return [x for x in inputs["architectures"] if isinstance(x, dict)]
        registry = inputs.get("architecture_registry")
        if isinstance(registry, dict) and isinstance(registry.get("architectures"), list):
            return [x for x in registry["architectures"] if isinstance(x, dict)]
        return list(self.DEFAULT_ARCHITECTURES)

    def _extract_dimensions(self, inputs: Dict[str, Any]) -> List[str]:
        raw = inputs.get("measurement_dimensions")
        if not isinstance(raw, list):
            protocol = inputs.get("unified_measurement_protocol")
            if isinstance(protocol, dict):
                raw = protocol.get("measurement_dimensions")
        if not isinstance(raw, list) or not raw:
            return list(self.DEFAULT_DIMENSIONS)
        dimensions: List[str] = []
        for item in raw:
            if isinstance(item, str):
                dimensions.append(item)
            elif isinstance(item, dict) and item.get("dimension_id"):
                dimensions.append(str(item["dimension_id"]))
        return dimensions or list(self.DEFAULT_DIMENSIONS)

    def _normalise_metric(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            if value < 0:
                return 0.0
            if value > 1:
                return 1.0
            return round(float(value), 6)
        return None

    def _build_profile(self, architecture: Dict[str, Any], dimensions: List[str]) -> Dict[str, Any]:
        arch_id = str(architecture.get("architecture_id") or architecture.get("id") or architecture.get("name") or "unknown_architecture")
        arch_type = str(architecture.get("architecture_type") or architecture.get("type") or "unspecified")
        tier = str(architecture.get("evidence_tier") or architecture.get("data_availability") or "synthetic_placeholder")
        metrics = architecture.get("metrics") if isinstance(architecture.get("metrics"), dict) else {}

        vector: Dict[str, Optional[float]] = {}
        missing: List[str] = []
        for dim in dimensions:
            value = self._normalise_metric(metrics.get(dim))
            vector[dim] = value
            if value is None:
                missing.append(dim)

        available_values = [v for v in vector.values() if isinstance(v, float)]
        coverage = round(len(available_values) / float(len(dimensions) or 1), 6)
        raw_score = round(sum(available_values) / float(len(available_values) or 1), 6) if available_values else 0.0
        evidence_weight = self.EVIDENCE_WEIGHTS.get(tier, 0.45)
        confidence = round(coverage * evidence_weight, 6)
        weighted_score = round(raw_score * confidence, 6)

        return {
            "architecture_id": arch_id,
            "architecture_type": arch_type,
            "label": architecture.get("label", arch_id),
            "evidence_tier": tier,
            "rf_profile_vector": vector,
            "feature_count": len(dimensions),
            "available_feature_count": len(available_values),
            "missing_features": missing,
            "coverage": coverage,
            "raw_rf_profile_score": raw_score,
            "evidence_weight": evidence_weight,
            "profile_confidence": confidence,
            "weighted_rf_profile_score": weighted_score,
            "comparison_ready": bool(coverage > 0.0 and confidence > 0.0),
        }

    def _profile_summary(self, profiles: List[Dict[str, Any]], dimensions: List[str]) -> Dict[str, Any]:
        ready_profiles = [p for p in profiles if p.get("comparison_ready")]
        scores = [p["weighted_rf_profile_score"] for p in ready_profiles if isinstance(p.get("weighted_rf_profile_score"), float)]
        return {
            "profile_count": len(profiles),
            "comparison_ready_profile_count": len(ready_profiles),
            "dimension_count": len(dimensions),
            "mean_weighted_rf_profile_score": round(sum(scores) / float(len(scores) or 1), 6) if scores else 0.0,
            "registered_architecture_types": sorted({str(p.get("architecture_type")) for p in profiles}),
            "ready_architecture_ids": [str(p.get("architecture_id")) for p in ready_profiles],
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        architectures = self._extract_architectures(inputs)
        dimensions = self._extract_dimensions(inputs)
        profiles = [self._build_profile(architecture, dimensions) for architecture in architectures]
        summary = self._profile_summary(profiles, dimensions)

        core_dimensions_present = {"RF", "OMEGA", "PI", "MEI", "CRI"}.issubset(set(dimensions))
        oce_profile_present = any(p.get("architecture_id") == "oce_rf_star" for p in profiles)
        profile_ready = bool(core_dimensions_present and summary["comparison_ready_profile_count"] >= 1 and summary["dimension_count"] >= 5)
        readiness_score = round(
            (0.35 if core_dimensions_present else 0.0)
            + min(0.35, summary["comparison_ready_profile_count"] / 4.0 * 0.35)
            + (0.20 if oce_profile_present else 0.0)
            + min(0.10, summary["dimension_count"] / 8.0 * 0.10),
            6,
        )

        canonical_profile = next((p for p in profiles if p.get("architecture_id") == "oce_rf_star"), profiles[0] if profiles else {})
        timestamp = datetime.now(timezone.utc).isoformat()

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": "RF_PROFILE_BUILDER_READY" if profile_ready else "RF_PROFILE_BUILDER_INCOMPLETE",
            "rf_profile_builder_status": "RF_PROFILE_BUILDER_READY" if profile_ready else "RF_PROFILE_BUILDER_INCOMPLETE",
            "rf_profile_ready": profile_ready,
            "comparative_profile_ready": profile_ready,
            "canonical_profile_id": canonical_profile.get("architecture_id"),
            "canonical_profile": canonical_profile,
            "architecture_profiles": profiles,
            "profile_count": summary["profile_count"],
            "comparison_ready_profile_count": summary["comparison_ready_profile_count"],
            "feature_count": len(dimensions),
            "profile_dimensions": dimensions,
            "core_dimensions_present": core_dimensions_present,
            "registered_architecture_types": summary["registered_architecture_types"],
            "ready_architecture_ids": summary["ready_architecture_ids"],
            "mean_weighted_rf_profile_score": summary["mean_weighted_rf_profile_score"],
            "readiness_score": readiness_score,
            "profile_schema": {
                "architecture_id": "str",
                "architecture_type": "str",
                "evidence_tier": "str",
                "rf_profile_vector": "dict[str, float|None]",
                "coverage": "0_1",
                "profile_confidence": "0_1",
                "weighted_rf_profile_score": "0_1",
            },
            "normalization_contract": {
                "range": [0.0, 1.0],
                "missingness_policy": "preserve_none_and_annotate_missing_features",
                "evidence_weighting": self.EVIDENCE_WEIGHTS,
                "cross_architecture_comparability": "compare_profiles_only_after_dimension_alignment",
            },
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": [
                "comparative_similarity_engine",
                "consciousness_distance_metric",
                "clustering_engine",
                "taxonomy_builder",
                "comparative_dashboard",
                "comparative_history",
                "comparative_science_certifier",
            ],
            "validation_policy": {
                "requires_unified_measurement_protocol": True,
                "requires_architecture_registry": True,
                "requires_core_rf_dimensions": True,
                "requires_missingness_annotation": True,
                "public_invariants_only": True,
            },
            "auditability_policy": {
                "record_source_architectures": True,
                "record_dimensions": True,
                "record_profile_vectors": True,
                "record_missing_features": True,
                "record_evidence_tiers": True,
            },
            "epistemic_guards": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "no_phenomenal_claim_from_rf_profile": True,
                "no_subjectivity_inference_from_similarity": True,
            },
            "allowed_claims": [
                "rf_profile_constructed",
                "architecture_profile_comparison_ready",
                "missingness_annotated_functional_rf_vector",
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
            out_dir = ROOT / "comparative_science" / "rf_profiles"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "latest_rf_profile_builder.json"
            out_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(out_path)

        return result


def main() -> None:
    result = RFProfileBuilder().step(persist=True)
    print(result["rf_profile_builder_status"])


if __name__ == "__main__":
    main()
