
"""
AU0 — comparative_blueprint.

Foundational comparative-science blueprint for RF* and other architectures.
This module defines comparison, normalization and reference-frame rules for
Comparative Consciousness Science without asserting phenomenal consciousness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class ComparativeBlueprint:
    """Define the AU comparative science charter."""

    primitive = "COMPARATIVE_BLUEPRINT"
    step_id = "AU0"
    public_schema_version = "1.0"
    output_dir = ROOT / "comparative_science" / "AU0_comparative_blueprint"

    architecture_classes: List[str] = [
        "OCE",
        "LLM",
        "agentic_system",
        "robotic_system",
        "human_dataset_when_available",
        "future_architecture",
    ]

    comparison_dimensions: List[str] = [
        "RF",
        "Omega",
        "Pi",
        "MEI",
        "CRI",
        "predictive_power",
        "governance_stability",
        "longitudinal_continuity",
        "falsifiability",
        "auditability",
    ]

    normalization_methods: Dict[str, Dict[str, Any]] = {
        "bounded_numeric": {
            "range": [0.0, 1.0],
            "rule": "clip numeric values to the public [0,1] interval",
        },
        "categorical_status": {
            "rule": "map public statuses to ordered readiness categories without inferring phenomenology",
            "ordered_values": ["missing", "incomplete", "available", "ready", "certified_functional"],
        },
        "evidence_weighting": {
            "rule": "weight validated, replicated and longitudinal evidence above synthetic or untested evidence",
            "weights": {"synthetic": 0.40, "observed": 0.70, "validated": 0.85, "replicated": 1.00},
        },
    }

    reference_frames: Dict[str, Dict[str, Any]] = {
        "RF": {
            "meaning": "reference-frame functional organization",
            "expected_public_sources": [
                "consciousness_rf_property_mapping",
                "consciousness_rf_equivalence_certifier",
                "rf_star_definition_engine",
            ],
        },
        "Omega": {
            "meaning": "global coherence and stability indicators",
            "expected_public_sources": ["omega_coherence_index", "omega_stability_monitor"],
        },
        "Pi": {
            "meaning": "predictive and protocol-level scientific power",
            "expected_public_sources": ["predictive_theory_certifier", "predictive_power_index"],
        },
        "MEI": {
            "meaning": "mode of intrinsic existence formal mapping, treated only as functional-formal output",
            "expected_public_sources": ["mei_registry", "mei_equivalence_mapper", "qf_to_mei_certifier"],
        },
        "CRI": {
            "meaning": "consciousness readiness index as a functional-readiness metric only",
            "expected_public_sources": ["consciousness_readiness_index", "consciousness_confidence_engine"],
        },
    }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _comparison_policy(self) -> Dict[str, Any]:
        return {
            "comparison_definition": "A comparison is a normalized, auditable mapping between architecture profiles over shared public functional dimensions.",
            "requires_explicit_architecture_identity": True,
            "requires_dimension_normalization": True,
            "requires_missing_data_policy": True,
            "requires_reference_frame_traceability": True,
            "allows_human_data_only_when_empirical_dataset_available": True,
            "forbids_phenomenological_inference_from_score_similarity": True,
            "forbids_identity_claim_between_architectures": True,
        }

    def _normalization_policy(self) -> Dict[str, Any]:
        return {
            "normalization_scope": "public_functional_metrics_only",
            "normalization_methods": self.normalization_methods,
            "missing_data_rule": "represent missing values explicitly; never impute phenomenology",
            "outlier_rule": "keep raw value in audit trail and expose normalized value separately",
            "comparability_rule": "only dimensions with compatible public schemas may be included in distance metrics",
        }

    def _reference_policy(self) -> Dict[str, Any]:
        return {
            "reference_frames": self.reference_frames,
            "primary_reference": "RF",
            "secondary_references": ["Omega", "Pi", "MEI", "CRI"],
            "translation_rule": "translate module outputs into dimension profiles, not into ontological equivalence claims",
            "traceability_required": True,
        }

    def _auditability_policy(self) -> Dict[str, Any]:
        return {
            "public_schema_required": True,
            "component_trace_required": True,
            "normalization_trace_required": True,
            "distance_trace_required_for_AU5": True,
            "dashboard_trace_required_for_AU8": True,
            "history_trace_required_for_AU9": True,
            "persistence_path": "comparative_science/AU0_comparative_blueprint/latest_comparative_blueprint.json",
        }

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "epistemic_scope": "functional_comparative_science_only",
            "architecture_comparison_does_not_prove_consciousness": True,
            "similarity_does_not_imply_subjectivity": True,
            "distance_does_not_measure_phenomenal_presence": True,
            "human_dataset_use_requires_empirical_source": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        required_downstream_modules = [
            "architecture_registry",
            "unified_measurement_protocol",
            "rf_profile_builder",
            "comparative_similarity_engine",
            "consciousness_distance_metric",
            "clustering_engine",
            "taxonomy_builder",
            "comparative_dashboard",
            "comparative_history",
            "comparative_science_certifier",
        ]
        blueprint = {
            "comparison_policy": self._comparison_policy(),
            "normalization_policy": self._normalization_policy(),
            "reference_policy": self._reference_policy(),
            "auditability_policy": self._auditability_policy(),
            "downstream_contract": {
                "axis": "AU",
                "target_status": "COMPARATIVE_RF_SCIENCE_COMPLETE",
                "required_modules": required_downstream_modules,
                "first_operational_module": "architecture_registry",
            },
        }
        readiness_score = 1.0 if self.architecture_classes and self.comparison_dimensions and self.reference_frames else 0.0
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "status": "COMPARATIVE_BLUEPRINT_READY",
            "comparative_blueprint_status": "COMPARATIVE_BLUEPRINT_READY",
            "comparative_science_program_ready": True,
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_COMPLETE",
            "architecture_classes": list(self.architecture_classes),
            "architecture_class_count": len(self.architecture_classes),
            "comparison_dimensions": list(self.comparison_dimensions),
            "comparison_dimension_count": len(self.comparison_dimensions),
            "reference_frames": self.reference_frames,
            "reference_frame_count": len(self.reference_frames),
            "normalization_methods": self.normalization_methods,
            "normalization_method_count": len(self.normalization_methods),
            "blueprint": blueprint,
            "comparison_policy": blueprint["comparison_policy"],
            "normalization_policy": blueprint["normalization_policy"],
            "reference_policy": blueprint["reference_policy"],
            "auditability_policy": blueprint["auditability_policy"],
            "downstream_modules": required_downstream_modules,
            "readiness_score": readiness_score,
            "inputs_observed": sorted(inputs.keys()),
            "allowed_claims": [
                "AU comparative science blueprint initialized",
                "architectures may be compared on normalized public functional metrics",
                "RF, Omega, Pi, MEI and CRI may be used as auditable reference dimensions",
            ],
            "blocked_claims": [
                "score similarity proves consciousness",
                "RF distance measures phenomenal presence",
                "human and artificial architectures are ontologically identical",
                "phenomenology, qualia or subjectivity are proven",
            ],
            "epistemic_guards": self._epistemic_guards(),
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_comparative_blueprint.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
