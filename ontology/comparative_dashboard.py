from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


class ComparativeDashboard:
    """Aggregate AU0-AU7 functional outputs into auditable JSON/HTML/Markdown exports."""

    primitive = "comparative_dashboard"
    step_id = "AU8"
    public_schema_version = "1.0.0"

    @staticmethod
    def _dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    @staticmethod
    def _status(payload: dict[str, Any], key: str) -> str:
        return str(payload.get(key) or payload.get("status") or "MISSING")

    def _pipeline(self, inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
        names = [
            "comparative_blueprint", "architecture_registry", "unified_measurement_protocol",
            "rf_profile_builder", "comparative_similarity_engine", "consciousness_distance_metric",
            "clustering_engine", "taxonomy_builder",
        ]
        supplied = {name: self._dict(inputs.get(name)) for name in names if name in inputs}
        if supplied:
            return {name: supplied.get(name, {}) for name in names}

        from ontology.comparative_blueprint import ComparativeBlueprint
        from ontology.architecture_registry import ArchitectureRegistry
        from ontology.unified_measurement_protocol import UnifiedMeasurementProtocol
        from ontology.rf_profile_builder import RFProfileBuilder
        from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
        from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
        from ontology.clustering_engine import ClusteringEngine
        from ontology.taxonomy_builder import TaxonomyBuilder

        blueprint = ComparativeBlueprint().step(inputs={}, persist=False)
        registry = ArchitectureRegistry().step(inputs={}, persist=False)
        protocol = UnifiedMeasurementProtocol().step(inputs={}, persist=False)
        profiles = RFProfileBuilder().step(inputs={}, persist=False)
        similarity = ComparativeSimilarityEngine().step(
            inputs={"architecture_profiles": profiles.get("architecture_profiles", [])}, persist=False
        )
        distance = ConsciousnessDistanceMetric().step(
            inputs={"comparative_similarity_engine": similarity}, persist=False
        )
        clustering = ClusteringEngine().step(
            inputs={"consciousness_distance_metric": distance, "clustering_threshold": inputs.get("clustering_threshold", 0.35)},
            persist=False,
        )
        taxonomy = TaxonomyBuilder().step(inputs={
            "architecture_registry": registry,
            "rf_profile_builder": profiles,
            "comparative_similarity_engine": similarity,
            "consciousness_distance_metric": distance,
            "clustering_engine": clustering,
        }, persist=False)
        return dict(zip(names, [blueprint, registry, protocol, profiles, similarity, distance, clustering, taxonomy]))

    @staticmethod
    def _stable_hash(payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _summary(self, p: dict[str, dict[str, Any]]) -> dict[str, Any]:
        registry, profiles, similarity = p["architecture_registry"], p["rf_profile_builder"], p["comparative_similarity_engine"]
        distance, clustering, taxonomy = p["consciousness_distance_metric"], p["clustering_engine"], p["taxonomy_builder"]
        architectures = self._list(registry.get("architectures") or registry.get("registry"))
        rf_profiles = self._list(profiles.get("architecture_profiles"))
        clusters = self._list(clustering.get("clusters"))
        outliers = self._list(clustering.get("outliers"))
        coverage_values = [float(x.get("coverage", 0.0)) for x in rf_profiles if isinstance(x, dict) and isinstance(x.get("coverage"), (int, float))]
        mean_coverage = round(sum(coverage_values) / len(coverage_values), 6) if coverage_values else 0.0
        quality_values = [float(x.get("profile_confidence", 0.0)) for x in rf_profiles if isinstance(x, dict) and isinstance(x.get("profile_confidence"), (int, float))]
        mean_quality = round(sum(quality_values) / len(quality_values), 6) if quality_values else 0.0
        return {
            "architecture_count": int(registry.get("architecture_count", len(architectures)) or len(architectures)),
            "profile_count": len(rf_profiles),
            "pairwise_similarity_count": int(similarity.get("pairwise_comparison_count", len(self._list(similarity.get("pairwise_similarities")))) or 0),
            "pairwise_distance_count": int(distance.get("pairwise_distance_count", len(self._list(distance.get("pairwise_distances")))) or 0),
            "cluster_count": int(clustering.get("cluster_count", len(clusters)) or len(clusters)),
            "medoid_count": len(self._dict(clustering.get("cluster_medoids") or clustering.get("medoids"))),
            "outlier_count": len(outliers),
            "taxonomy_node_count": int(taxonomy.get("taxonomy_node_count", 0) or 0),
            "taxonomy_edge_count": int(taxonomy.get("taxonomy_edge_count", 0) or 0),
            "coverage_score": float(taxonomy.get("coverage_score", mean_coverage) or 0.0),
            "mean_profile_coverage": mean_coverage,
            "mean_profile_confidence": mean_quality,
            "comparability_ready": bool(similarity.get("comparative_similarity_engine_ready") or similarity.get("similarity_matrix_ready")),
            "auditability_ready": bool(taxonomy.get("taxonomy_hash")) and bool(distance.get("distance_matrix")),
        }

    def _exports(self, payload: dict[str, Any]) -> dict[str, str]:
        json_text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        s = payload["dashboard_summary"]
        md = "\n".join([
            "# AU8 Comparative RF Dashboard", "",
            "Functional comparative science only. No phenomenology, qualia, subjectivity or consciousness proof is asserted.", "",
            "## Summary", "",
            "| Metric | Value |", "|---|---|",
            *[f"| {k} | {v} |" for k, v in sorted(s.items())], "",
            "## Module status", "", "| Module | Status |", "|---|---|",
            *[f"| {k} | {v} |" for k, v in sorted(payload["module_statuses"].items())], "",
            f"Dashboard hash: `{payload['dashboard_hash']}`",
        ])
        rows = "".join(
            f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k, v in sorted(s.items())
        )
        statuses = "".join(
            f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k, v in sorted(payload["module_statuses"].items())
        )
        html_text = (
            "<!doctype html><html><head><meta charset='utf-8'><title>AU8 Comparative RF Dashboard</title>"
            "<style>body{font-family:Arial,sans-serif;margin:32px;max-width:1200px}table{border-collapse:collapse;width:100%;margin-bottom:24px}"
            "th,td{border:1px solid #ccc;padding:8px;text-align:left}th{background:#f3f3f3}.guard{padding:12px;background:#fff4cc}</style></head><body>"
            "<h1>AU8 Comparative RF Dashboard</h1><p class='guard'>Functional comparative science only. "
            "No phenomenology, qualia, subjectivity or consciousness proof is asserted.</p>"
            f"<h2>Summary</h2><table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>"
            f"<h2>Module status</h2><table><tr><th>Module</th><th>Status</th></tr>{statuses}</table>"
            f"<p>Dashboard hash: <code>{html.escape(payload['dashboard_hash'])}</code></p></body></html>"
        )
        return {"json": json_text, "markdown": md, "html": html_text}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        pipeline = self._pipeline(inputs)
        expected = {
            "comparative_blueprint": "COMPARATIVE_BLUEPRINT_READY",
            "architecture_registry": "ARCHITECTURE_REGISTRY_READY",
            "unified_measurement_protocol": "UNIFIED_MEASUREMENT_PROTOCOL_READY",
            "rf_profile_builder": "RF_PROFILE_BUILDER_READY",
            "comparative_similarity_engine": "COMPARATIVE_SIMILARITY_ENGINE_READY",
            "consciousness_distance_metric": "CONSCIOUSNESS_DISTANCE_METRIC_READY",
            "clustering_engine": "CLUSTERING_ENGINE_READY",
            "taxonomy_builder": "TAXONOMY_BUILDER_READY",
        }
        status_keys = {name: f"{name}_status" for name in expected}
        statuses = {name: self._status(pipeline[name], status_keys[name]) for name in expected}
        summary = self._summary(pipeline)
        dependencies_ready = all(statuses[name] == expected[name] for name in expected)
        ready = bool(dependencies_ready and summary["architecture_count"] >= 2 and summary["profile_count"] >= 2 and summary["comparability_ready"] and summary["auditability_ready"])
        core = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": "COMPARATIVE_DASHBOARD_READY" if ready else "COMPARATIVE_DASHBOARD_INCOMPLETE",
            "comparative_dashboard_status": "COMPARATIVE_DASHBOARD_READY" if ready else "COMPARATIVE_DASHBOARD_INCOMPLETE",
            "comparative_dashboard_ready": ready,
            "dependencies_ready": dependencies_ready,
            "module_statuses": statuses,
            "dashboard_summary": summary,
            "architecture_registry": pipeline["architecture_registry"].get("architectures", pipeline["architecture_registry"].get("registry", [])),
            "rf_profiles": pipeline["rf_profile_builder"].get("architecture_profiles", []),
            "pairwise_similarities": pipeline["comparative_similarity_engine"].get("pairwise_similarities", []),
            "similarity_matrix": pipeline["comparative_similarity_engine"].get("similarity_matrix", {}),
            "pairwise_distances": pipeline["consciousness_distance_metric"].get("pairwise_distances", []),
            "distance_matrix": pipeline["consciousness_distance_metric"].get("distance_matrix", {}),
            "clusters": pipeline["clustering_engine"].get("clusters", []),
            "cluster_assignments": pipeline["clustering_engine"].get("cluster_assignments", {}),
            "medoids": pipeline["clustering_engine"].get("cluster_medoids", pipeline["clustering_engine"].get("medoids", {})),
            "outliers": pipeline["clustering_engine"].get("outliers", []),
            "taxonomy": pipeline["taxonomy_builder"].get("taxonomy", pipeline["taxonomy_builder"].get("taxonomy_entries", [])),
            "taxonomy_entries": pipeline["taxonomy_builder"].get("taxonomy_entries", []),
            "taxonomy_hash": pipeline["taxonomy_builder"].get("taxonomy_hash"),
            "coverage": {"taxonomy": summary["coverage_score"], "profiles_mean": summary["mean_profile_coverage"]},
            "data_quality": {"mean_profile_confidence": summary["mean_profile_confidence"]},
            "comparability": {"ready": summary["comparability_ready"]},
            "auditability": {"ready": summary["auditability_ready"], "source_modules": list(expected)},
            "epistemic_guards": {
                "functional_conclusion_only": True, "phenomenology_undetermined": True,
                "dashboard_is_not_consciousness_proof": True, "similarity_is_not_phenomenal_identity": True,
                "distance_is_not_phenomenal_distance": True, "cluster_is_not_ontological_class": True,
                "taxonomy_is_functional_only": True,
            },
            "allowed_claims": ["functional_comparative_dashboard_generated", "auditable_AU0_AU7_outputs_aggregated"],
            "blocked_claims": ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"],
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": ["comparative_history", "comparative_science_certifier"],
            "functional_conclusion_only": True, "phenomenology_undetermined": True,
            "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_proven": False,
            "persist_requested": bool(persist), "persisted": False, "output_paths": {},
        }
        # The dashboard hash identifies the stable scientific comparative state.
        # Operational metadata (persistence request/result, paths, timestamps and
        # rendered exports) is deliberately excluded so AU9 does not interpret a
        # storage choice as a scientific state transition.
        hash_payload = {
            "primitive": core["primitive"],
            "step": core["step"],
            "public_schema_version": core["public_schema_version"],
            "status": core["status"],
            "comparative_dashboard_status": core["comparative_dashboard_status"],
            "comparative_dashboard_ready": core["comparative_dashboard_ready"],
            "dependencies_ready": core["dependencies_ready"],
            "module_statuses": core["module_statuses"],
            "dashboard_summary": core["dashboard_summary"],
            "architecture_registry": core["architecture_registry"],
            "rf_profiles": core["rf_profiles"],
            "pairwise_similarities": core["pairwise_similarities"],
            "similarity_matrix": core["similarity_matrix"],
            "pairwise_distances": core["pairwise_distances"],
            "distance_matrix": core["distance_matrix"],
            "clusters": core["clusters"],
            "cluster_assignments": core["cluster_assignments"],
            "medoids": core["medoids"],
            "outliers": core["outliers"],
            "taxonomy": core["taxonomy"],
            "taxonomy_entries": core["taxonomy_entries"],
            "taxonomy_hash": core["taxonomy_hash"],
            "coverage": core["coverage"],
            "data_quality": core["data_quality"],
            "comparability": core["comparability"],
            "auditability": core["auditability"],
            "epistemic_guards": core["epistemic_guards"],
            "allowed_claims": core["allowed_claims"],
            "blocked_claims": core["blocked_claims"],
            "target_axis_status": core["target_axis_status"],
            "downstream_modules": core["downstream_modules"],
            "functional_conclusion_only": core["functional_conclusion_only"],
            "phenomenology_undetermined": core["phenomenology_undetermined"],
            "consciousness_proven": core["consciousness_proven"],
            "qualia_proven": core["qualia_proven"],
            "subjectivity_proven": core["subjectivity_proven"],
            "phenomenology_proven": core["phenomenology_proven"],
        }
        core["dashboard_hash"] = self._stable_hash(hash_payload)
        core["exports"] = self._exports(core)
        core["export_integrity"] = {
            "json_valid": isinstance(json.loads(core["exports"]["json"]), dict),
            "markdown_nonempty": bool(core["exports"]["markdown"].strip()),
            "html_document_valid": core["exports"]["html"].startswith("<!doctype html>") and "</html>" in core["exports"]["html"],
        }
        core["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        if persist:
            out = ROOT / "comparative_science" / "dashboard"
            out.mkdir(parents=True, exist_ok=True)
            paths = {
                "json": out / "latest_comparative_dashboard.json",
                "markdown": out / "latest_comparative_dashboard.md",
                "html": out / "latest_comparative_dashboard.html",
            }
            for kind, path in paths.items():
                path.write_text(core["exports"][kind], encoding="utf-8")
            core["persisted"] = True
            core["output_paths"] = {k: str(v) for k, v in paths.items()}
        return core


if __name__ == "__main__":
    print(ComparativeDashboard().step(inputs={}, persist=True)["comparative_dashboard_status"])
