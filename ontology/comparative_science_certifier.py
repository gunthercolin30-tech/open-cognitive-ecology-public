from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


class ComparativeScienceCertifier:
    """AU10 final functional certification of the AU comparative RF science axis."""

    primitive = "comparative_science_certifier"
    step_id = "AU10"
    public_schema_version = "1.0.0"
    complete_status = "COMPARATIVE_RF_SCIENCE_COMPLETE"
    incomplete_status = "COMPARATIVE_RF_SCIENCE_INCOMPLETE"

    expected_statuses = {
        "comparative_blueprint": "COMPARATIVE_BLUEPRINT_READY",
        "architecture_registry": "ARCHITECTURE_REGISTRY_READY",
        "unified_measurement_protocol": "UNIFIED_MEASUREMENT_PROTOCOL_READY",
        "rf_profile_builder": "RF_PROFILE_BUILDER_READY",
        "comparative_similarity_engine": "COMPARATIVE_SIMILARITY_ENGINE_READY",
        "consciousness_distance_metric": "CONSCIOUSNESS_DISTANCE_METRIC_READY",
        "clustering_engine": "CLUSTERING_ENGINE_READY",
        "taxonomy_builder": "TAXONOMY_BUILDER_READY",
        "comparative_dashboard": "COMPARATIVE_DASHBOARD_READY",
        "comparative_history": "COMPARATIVE_HISTORY_READY",
    }

    @staticmethod
    def _hash(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _guard_ok(payload: dict[str, Any]) -> bool:
        return (
            payload.get("functional_conclusion_only") is True
            and payload.get("phenomenology_undetermined") is True
            and payload.get("consciousness_proven") is False
            and payload.get("qualia_proven") is False
            and payload.get("subjectivity_proven") is False
            and payload.get("phenomenology_proven") is False
        )

    def _build_sources(self) -> dict[str, dict[str, Any]]:
        from ontology.comparative_blueprint import ComparativeBlueprint
        from ontology.architecture_registry import ArchitectureRegistry
        from ontology.unified_measurement_protocol import UnifiedMeasurementProtocol
        from ontology.rf_profile_builder import RFProfileBuilder
        from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
        from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
        from ontology.clustering_engine import ClusteringEngine
        from ontology.taxonomy_builder import TaxonomyBuilder
        from ontology.comparative_dashboard import ComparativeDashboard
        from ontology.comparative_history import ComparativeHistory
        dashboard = ComparativeDashboard().step(inputs={}, persist=False)
        history = ComparativeHistory().step(inputs={"comparative_dashboard": dashboard}, persist=False)
        return {
            "comparative_blueprint": ComparativeBlueprint().step(inputs={}, persist=False),
            "architecture_registry": ArchitectureRegistry().step(inputs={}, persist=False),
            "unified_measurement_protocol": UnifiedMeasurementProtocol().step(inputs={}, persist=False),
            "rf_profile_builder": RFProfileBuilder().step(inputs={}, persist=False),
            "comparative_similarity_engine": ComparativeSimilarityEngine().step(inputs={}, persist=False),
            "consciousness_distance_metric": ConsciousnessDistanceMetric().step(inputs={}, persist=False),
            "clustering_engine": ClusteringEngine().step(inputs={}, persist=False),
            "taxonomy_builder": TaxonomyBuilder().step(inputs={}, persist=False),
            "comparative_dashboard": dashboard,
            "comparative_history": history,
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        supplied = dict(inputs or {})
        sources = self._build_sources() if not supplied else {
            name: dict(supplied.get(name) or {}) for name in self.expected_statuses
        }
        status_keys = {
            "comparative_blueprint": "comparative_blueprint_status",
            "architecture_registry": "architecture_registry_status",
            "unified_measurement_protocol": "unified_measurement_protocol_status",
            "rf_profile_builder": "rf_profile_builder_status",
            "comparative_similarity_engine": "comparative_similarity_status",
            "consciousness_distance_metric": "consciousness_distance_metric_status",
            "clustering_engine": "clustering_engine_status",
            "taxonomy_builder": "taxonomy_builder_status",
            "comparative_dashboard": "comparative_dashboard_status",
            "comparative_history": "comparative_history_status",
        }
        module_statuses = {n: str(sources[n].get(status_keys[n]) or sources[n].get("status") or "MISSING") for n in self.expected_statuses}
        module_completeness = {n: module_statuses[n] == expected for n, expected in self.expected_statuses.items()}
        dashboard = sources["comparative_dashboard"]
        history = sources["comparative_history"]
        coverage_score = float((dashboard.get("dashboard_summary") or {}).get("coverage_score") or 0.0)
        quality_score = float((dashboard.get("dashboard_summary") or {}).get("mean_profile_confidence") or 0.0)
        export_integrity = dashboard.get("export_integrity") if isinstance(dashboard.get("export_integrity"), dict) else {}
        export_ok = all(export_integrity.get(k) is True for k in ("json_valid", "markdown_nonempty", "html_document_valid"))
        chain_integrity = (
            history.get("chain_integrity")
            if isinstance(history.get("chain_integrity"), dict)
            else {}
        )
        effective_record_hash = (
            history.get("record_hash")
            or chain_integrity.get("head_hash")
        )
        hash_integrity = (
            isinstance(dashboard.get("dashboard_hash"), str)
            and len(dashboard.get("dashboard_hash")) == 64
            and isinstance(history.get("snapshot_hash"), str)
            and len(history.get("snapshot_hash")) == 64
            and history.get("dashboard_hash") == dashboard.get("dashboard_hash")
            and isinstance(effective_record_hash, str)
            and len(effective_record_hash) == 64
        )
        chain_ok = bool(chain_integrity.get("chain_valid"))
        guards = {name: self._guard_ok(payload) for name, payload in sources.items()}
        checks = {
            "completeness": all(module_completeness.values()),
            "coherence": bool(dashboard.get("dependencies_ready") and history.get("dashboard_ready")),
            "auditability": bool((dashboard.get("auditability") or {}).get("ready")),
            "extensibility": any(bool(x.get("future_extension_slot")) for x in dashboard.get("architecture_registry", []) if isinstance(x, dict)),
            "coverage": coverage_score >= 0.30,
            "data_quality": quality_score >= 0.30,
            "historization": bool(history.get("append_only") and chain_ok),
            "export_integrity": export_ok,
            "hash_integrity": hash_integrity,
            "epistemic_guards": all(guards.values()),
            "absence_of_phenomenal_conclusions": all(not bool(p.get("consciousness_proven") or p.get("qualia_proven") or p.get("subjectivity_proven") or p.get("phenomenology_proven")) for p in sources.values()),
        }
        certified = all(checks.values())
        core = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": self.complete_status if certified else self.incomplete_status,
            "comparative_science_certification_status": self.complete_status if certified else self.incomplete_status,
            "comparative_rf_science_complete": certified,
            "certified": certified,
            "module_statuses": module_statuses,
            "module_completeness": module_completeness,
            "certification_checks": checks,
            "coverage_score": coverage_score,
            "data_quality_score": quality_score,
            "dashboard_hash": dashboard.get("dashboard_hash"),
            "history_snapshot_hash": history.get("snapshot_hash"),
            "history_record_hash": effective_record_hash,
            "history_record_created_in_call": bool(history.get("record_hash")),
            "guard_compliance": guards,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "epistemic_scope": "functional_comparative_science_only",
            "allowed_claims": ["comparative functional RF science completed under explicit thresholds and epistemic guards"] if certified else [],
            "blocked_claims": ["phenomenal consciousness proven", "qualia proven", "subjectivity proven"],
            "persist_requested": bool(persist),
            "persisted": False,
            "output_paths": {},
        }
        core["certification_hash"] = self._hash({k: v for k, v in core.items() if k not in {"persist_requested", "persisted", "output_paths"}})
        if persist:
            out = ROOT / "comparative_science" / "certification"
            out.mkdir(parents=True, exist_ok=True)
            path = out / "latest_comparative_science_certification.json"
            path.write_text(json.dumps(core, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            core["persisted"] = True
            core["output_paths"] = {"json": str(path)}
        return core


if __name__ == "__main__":
    print(ComparativeScienceCertifier().step(inputs={}, persist=False)["comparative_science_certification_status"])
