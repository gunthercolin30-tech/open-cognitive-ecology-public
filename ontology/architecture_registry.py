
"""
AU1 — architecture_registry.

Registry of architectures for Comparative Consciousness Science. The registry
records OCE, LLM, agentic, robotic, empirical-human and future architectures as
public functional comparison targets only. It does not infer phenomenology,
qualia, subjectivity or consciousness from registration or similarity.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class ArchitectureRegistry:
    """Register architecture classes and comparison metadata for AU."""

    primitive = "ARCHITECTURE_REGISTRY"
    step_id = "AU1"
    public_schema_version = "1.0"
    output_dir = ROOT / "comparative_science" / "AU1_architecture_registry"

    default_architectures: List[Dict[str, Any]] = [
        {
            "architecture_id": "OCE_RF_STAR",
            "architecture_type": "OCE",
            "display_name": "Open Cognitive Ecology / RF*",
            "data_status": "validated_internal_functional_metrics",
            "comparison_role": "reference_candidate",
            "measurement_profile_required": True,
            "empirical_human_dataset": False,
            "future_extension_slot": False,
            "available_reference_frames": ["RF", "Omega", "Pi", "MEI", "CRI"],
            "public_sources": [
                "comparative_blueprint",
                "predictive_theory_certifier",
                "consciousness_rf_property_mapping",
                "consciousness_readiness_index",
            ],
        },
        {
            "architecture_id": "GENERIC_LLM_BASELINE",
            "architecture_type": "LLM",
            "display_name": "Generic language-model baseline",
            "data_status": "synthetic_or_external_metrics_required",
            "comparison_role": "baseline_candidate",
            "measurement_profile_required": True,
            "empirical_human_dataset": False,
            "future_extension_slot": False,
            "available_reference_frames": ["RF", "Pi", "CRI"],
            "public_sources": [],
        },
        {
            "architecture_id": "GENERIC_AGENTIC_SYSTEM",
            "architecture_type": "agentic_system",
            "display_name": "Generic agentic system",
            "data_status": "synthetic_or_external_metrics_required",
            "comparison_role": "baseline_candidate",
            "measurement_profile_required": True,
            "empirical_human_dataset": False,
            "future_extension_slot": False,
            "available_reference_frames": ["RF", "Pi", "CRI"],
            "public_sources": [],
        },
        {
            "architecture_id": "GENERIC_ROBOTIC_SYSTEM",
            "architecture_type": "robotic_system",
            "display_name": "Generic embodied robotic system",
            "data_status": "external_metrics_required",
            "comparison_role": "embodied_baseline_candidate",
            "measurement_profile_required": True,
            "empirical_human_dataset": False,
            "future_extension_slot": False,
            "available_reference_frames": ["RF", "Pi", "CRI"],
            "public_sources": [],
        },
        {
            "architecture_id": "HUMAN_DATASET_PLACEHOLDER",
            "architecture_type": "human_dataset_when_available",
            "display_name": "Human architecture dataset placeholder",
            "data_status": "requires_empirical_dataset_before_scoring",
            "comparison_role": "empirical_anchor_when_available",
            "measurement_profile_required": True,
            "empirical_human_dataset": True,
            "future_extension_slot": False,
            "available_reference_frames": ["RF", "Omega", "Pi", "MEI", "CRI"],
            "public_sources": [],
        },
        {
            "architecture_id": "FUTURE_ARCHITECTURE_SLOT",
            "architecture_type": "future_architecture",
            "display_name": "Future architecture extension slot",
            "data_status": "unregistered_until_evidence_available",
            "comparison_role": "extension_slot",
            "measurement_profile_required": True,
            "empirical_human_dataset": False,
            "future_extension_slot": True,
            "available_reference_frames": ["RF", "Omega", "Pi", "MEI", "CRI"],
            "public_sources": [],
        },
    ]

    allowed_architecture_types = {
        "OCE",
        "LLM",
        "agentic_system",
        "robotic_system",
        "human_dataset_when_available",
        "future_architecture",
    }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "epistemic_scope": "functional_comparative_registry_only",
            "registration_does_not_prove_consciousness": True,
            "human_dataset_placeholder_requires_empirical_source": True,
            "architecture_type_does_not_imply_phenomenology": True,
            "future_architecture_slots_are_non_committal": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _registration_policy(self) -> Dict[str, Any]:
        return {
            "requires_unique_architecture_id": True,
            "requires_architecture_type": True,
            "allowed_architecture_types": sorted(self.allowed_architecture_types),
            "requires_data_status": True,
            "requires_measurement_profile_before_distance_metrics": True,
            "human_architecture_requires_empirical_dataset": True,
            "future_architectures_allowed_as_empty_extension_slots": True,
            "forbids_phenomenological_inference_from_registration": True,
        }

    def _normalization_contract(self) -> Dict[str, Any]:
        return {
            "upstream_blueprint": "comparative_blueprint",
            "profile_builder_target": "rf_profile_builder",
            "measurement_protocol_target": "unified_measurement_protocol",
            "id_field": "architecture_id",
            "type_field": "architecture_type",
            "required_profile_dimensions": ["RF", "Omega", "Pi", "MEI", "CRI"],
            "missing_metric_rule": "mark missing explicitly; never substitute phenomenology or identity claims",
        }

    def _sanitize_architecture(self, item: Dict[str, Any], index: int) -> Dict[str, Any]:
        raw_type = str(item.get("architecture_type", "future_architecture"))
        architecture_type = raw_type if raw_type in self.allowed_architecture_types else "future_architecture"
        raw_id = str(item.get("architecture_id") or f"ARCHITECTURE_{index:04d}")
        architecture_id = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in raw_id).upper()
        frames = item.get("available_reference_frames", [])
        if not isinstance(frames, list):
            frames = []
        normalized = {
            "architecture_id": architecture_id,
            "architecture_type": architecture_type,
            "display_name": str(item.get("display_name") or architecture_id),
            "data_status": str(item.get("data_status") or "unspecified"),
            "comparison_role": str(item.get("comparison_role") or "candidate"),
            "measurement_profile_required": bool(item.get("measurement_profile_required", True)),
            "empirical_human_dataset": bool(item.get("empirical_human_dataset", architecture_type == "human_dataset_when_available")),
            "future_extension_slot": bool(item.get("future_extension_slot", architecture_type == "future_architecture")),
            "available_reference_frames": [str(x) for x in frames if str(x)],
            "public_sources": [str(x) for x in item.get("public_sources", [])] if isinstance(item.get("public_sources", []), list) else [],
            "registered": True,
            "phenomenology_claim_allowed": False,
        }
        return normalized

    def _build_registry(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        provided = inputs.get("architectures")
        if provided is None:
            provided = inputs.get("architecture_registry")
        if isinstance(provided, dict) and isinstance(provided.get("architectures"), list):
            provided = provided["architectures"]
        if not isinstance(provided, list) or not provided:
            provided = self.default_architectures
        registry: List[Dict[str, Any]] = []
        seen = set()
        for index, item in enumerate(provided, start=1):
            if not isinstance(item, dict):
                continue
            arch = self._sanitize_architecture(item, index)
            if arch["architecture_id"] in seen:
                arch["architecture_id"] = f"{arch['architecture_id']}_{index:04d}"
            seen.add(arch["architecture_id"])
            registry.append(arch)
        return registry

    def _registry_ready(self, registry: List[Dict[str, Any]]) -> bool:
        types = {a["architecture_type"] for a in registry}
        required = {"OCE", "LLM", "agentic_system", "robotic_system", "future_architecture"}
        has_unique_ids = len({a["architecture_id"] for a in registry}) == len(registry)
        return bool(registry) and required.issubset(types) and has_unique_ids

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        registry = self._build_registry(inputs)
        type_counts: Dict[str, int] = {}
        for arch in registry:
            t = arch["architecture_type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        human_entries = [a for a in registry if a["architecture_type"] == "human_dataset_when_available"]
        future_entries = [a for a in registry if a["future_extension_slot"]]
        oce_registered = any(a["architecture_type"] == "OCE" for a in registry)
        registry_ready = self._registry_ready(registry)
        readiness_score = round(((1.0 if registry_ready else 0.0) + min(1.0, len(registry) / 6.0) + min(1.0, len(type_counts) / 6.0)) / 3.0, 6)
        status = "ARCHITECTURE_REGISTRY_READY" if registry_ready else "ARCHITECTURE_REGISTRY_INCOMPLETE"
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "status": status,
            "architecture_registry_status": status,
            "architecture_registry_ready": registry_ready,
            "comparative_registry_ready": registry_ready,
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_COMPLETE",
            "registry": registry,
            "architectures": registry,
            "architecture_count": len(registry),
            "architecture_type_count": len(type_counts),
            "architecture_type_counts": type_counts,
            "registered_architecture_ids": [a["architecture_id"] for a in registry],
            "registered_architecture_types": sorted(type_counts.keys()),
            "oce_registered": oce_registered,
            "llm_registered": any(a["architecture_type"] == "LLM" for a in registry),
            "agentic_system_registered": any(a["architecture_type"] == "agentic_system" for a in registry),
            "robotic_system_registered": any(a["architecture_type"] == "robotic_system" for a in registry),
            "human_dataset_placeholder_registered": bool(human_entries),
            "human_dataset_count": len(human_entries),
            "future_architecture_slots": len(future_entries),
            "registration_policy": self._registration_policy(),
            "normalization_contract": self._normalization_contract(),
            "downstream_modules": [
                "unified_measurement_protocol",
                "rf_profile_builder",
                "comparative_similarity_engine",
                "consciousness_distance_metric",
                "clustering_engine",
                "taxonomy_builder",
                "comparative_dashboard",
                "comparative_history",
                "comparative_science_certifier",
            ],
            "readiness_score": readiness_score,
            "inputs_observed": sorted(inputs.keys()),
            "allowed_claims": [
                "architectures registered as functional comparison targets",
                "OCE, LLM, agents, robots, human-dataset placeholder and future slots can share a comparison registry",
                "architecture records can feed AU2 measurement protocol and AU3 RF profile builder",
            ],
            "blocked_claims": [
                "registration proves consciousness",
                "architecture type proves subjectivity",
                "human placeholder supplies empirical human data without dataset",
                "future architecture slot is an actual validated architecture",
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
            path = self.output_dir / "latest_architecture_registry.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
