from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


class TaxonomyBuilder:
    """Build an auditable hierarchical RF functional taxonomy from AU1-AU6 outputs."""

    primitive = "taxonomy_builder"
    step_id = "AU7"
    public_schema_version = "1.0.0"
    taxonomy_version = "AU7-RF-TAXONOMY-1.0"

    FAMILY_MAP = {
        "OCE": "open_cognitive_ecology",
        "open_cognitive_ecology": "open_cognitive_ecology",
        "LLM": "language_model",
        "llm": "language_model",
        "agentic_system": "agentic_computational_system",
        "robotic_system": "embodied_robotic_system",
        "human_dataset_when_available": "human_empirical_dataset",
        "human_dataset_placeholder": "human_empirical_dataset",
        "future_architecture": "future_or_unclassified_architecture",
    }

    @staticmethod
    def _clamp01(value, default=0.0):
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return round(max(0.0, min(1.0, float(value))), 6)
        return default

    @staticmethod
    def _dict(value):
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _list(value):
        return value if isinstance(value, list) else []

    def _extract(self, inputs, *keys):
        for key in keys:
            value = inputs.get(key)
            if isinstance(value, dict):
                return value
        return {}

    def _build_pipeline(self, inputs):
        registry = self._extract(inputs, "architecture_registry", "registry_result")
        profiles = self._extract(inputs, "rf_profile_builder", "profile_result")
        similarity = self._extract(inputs, "comparative_similarity_engine", "similarity_result")
        distance = self._extract(inputs, "consciousness_distance_metric", "distance_result")
        clustering = self._extract(inputs, "clustering_engine", "clustering_result")

        try:
            if not profiles:
                from ontology.rf_profile_builder import RFProfileBuilder
                profiles = RFProfileBuilder().step(
                    inputs=inputs.get("profile_inputs", {}), persist=False
                )
            if not similarity:
                from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
                similarity = ComparativeSimilarityEngine().step(
                    inputs={"architecture_profiles": profiles.get("architecture_profiles", [])},
                    persist=False,
                )
            if not distance:
                from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
                distance = ConsciousnessDistanceMetric().step(
                    inputs={"comparative_similarity_engine": similarity}, persist=False
                )
            if not clustering:
                from ontology.clustering_engine import ClusteringEngine
                clustering = ClusteringEngine().step(
                    inputs={
                        "consciousness_distance_metric": distance,
                        "clustering_threshold": inputs.get("clustering_threshold", 0.35),
                    },
                    persist=False,
                )
        except Exception:
            pass

        return registry, profiles, similarity, distance, clustering

    @staticmethod
    def _architecture_records(registry, profiles):
        records = {}
        raw_registry = registry.get("architectures", registry.get("registry", []))
        for item in raw_registry if isinstance(raw_registry, list) else []:
            if isinstance(item, dict):
                arch_id = str(item.get("architecture_id") or item.get("id") or "")
                if arch_id:
                    records[arch_id] = dict(item)
        for profile in profiles.get("architecture_profiles", []):
            if not isinstance(profile, dict):
                continue
            arch_id = str(profile.get("architecture_id") or "")
            if not arch_id:
                continue
            records.setdefault(arch_id, {})
            records[arch_id].setdefault("architecture_id", arch_id)
            records[arch_id].setdefault("architecture_type", profile.get("architecture_type", "unspecified"))
            records[arch_id].setdefault("label", profile.get("label", arch_id))
        return records

    @staticmethod
    def _profiles_by_id(profiles):
        return {
            str(item.get("architecture_id")): item
            for item in profiles.get("architecture_profiles", [])
            if isinstance(item, dict) and item.get("architecture_id")
        }

    def _family(self, record):
        arch_type = str(record.get("architecture_type") or record.get("type") or "unspecified")
        return self.FAMILY_MAP.get(arch_type, "other_computational_architecture")

    @staticmethod
    def _functional_regime(profile):
        if not profile or not profile.get("comparison_ready"):
            return "insufficient_functional_data"
        score = profile.get("raw_rf_profile_score", profile.get("weighted_rf_profile_score"))
        if not isinstance(score, (int, float)):
            vector = profile.get("rf_profile_vector", {})
            values = [float(v) for v in vector.values() if isinstance(v, (int, float))]
            score = sum(values) / float(len(values) or 1) if values else 0.0
        score = float(score)
        if score >= 0.75:
            return "high_rf_functional_regime"
        if score >= 0.50:
            return "intermediate_rf_functional_regime"
        if score > 0.0:
            return "low_rf_functional_regime"
        return "insufficient_functional_data"

    @staticmethod
    def _rf_proximity(architecture_id, distance_matrix, canonical_id):
        if architecture_id == canonical_id:
            return "canonical_reference"
        value = distance_matrix.get(canonical_id, {}).get(architecture_id)
        if not isinstance(value, (int, float)):
            value = distance_matrix.get(architecture_id, {}).get(canonical_id)
        if not isinstance(value, (int, float)):
            return "proximity_unavailable"
        value = float(value)
        if value <= 0.20:
            return "very_close_rf_proximity"
        if value <= 0.40:
            return "close_rf_proximity"
        if value <= 0.65:
            return "moderate_rf_proximity"
        return "distant_rf_proximity"

    @staticmethod
    def _metric_profile(profile):
        vector = profile.get("rf_profile_vector", {}) if isinstance(profile, dict) else {}
        available = {
            str(key): float(value)
            for key, value in vector.items()
            if isinstance(value, (int, float))
        }
        if not available:
            return "metric_profile_unavailable"
        values = list(available.values())
        if max(values) - min(values) <= 0.15:
            return "balanced_metric_profile"
        dominant = sorted(available.items(), key=lambda item: (-item[1], item[0]))[0][0]
        return f"{dominant.lower()}_dominant_metric_profile"

    @staticmethod
    def _data_quality(profile):
        if not profile:
            return "data_unavailable"
        coverage = profile.get("coverage")
        if not isinstance(coverage, (int, float)):
            vector = profile.get("rf_profile_vector", {})
            values = list(vector.values()) if isinstance(vector, dict) else []
            available = [v for v in values if isinstance(v, (int, float))]
            coverage = len(available) / float(len(values) or 1) if values else 0.0
        confidence = profile.get("profile_confidence", 0.0)
        coverage = float(coverage)
        confidence = float(confidence) if isinstance(confidence, (int, float)) else 0.0
        if coverage >= 0.95 and confidence >= 0.75:
            return "high_quality_instrumented_data"
        if coverage >= 0.75 and confidence >= 0.35:
            return "moderate_quality_comparative_data"
        if coverage > 0.0:
            return "limited_or_synthetic_data"
        return "data_unavailable"

    @staticmethod
    def _node_id(level, value):
        safe = "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")
        return f"{level}:{safe or 'unspecified'}"

    def step(self, inputs=None, persist=False):
        inputs = inputs if isinstance(inputs, dict) else {}
        registry, profiles, similarity, distance, clustering = self._build_pipeline(inputs)
        architectures = self._architecture_records(registry, profiles)
        profiles_by_id = self._profiles_by_id(profiles)
        assignments = self._dict(clustering.get("cluster_assignments"))
        outlier_ids = {
            str(item.get("architecture_id") if isinstance(item, dict) else item)
            for item in self._list(clustering.get("outliers"))
        }
        distance_matrix = self._dict(distance.get("distance_matrix"))
        canonical_id = str(
            inputs.get("canonical_architecture_id")
            or profiles.get("canonical_profile_id")
            or "oce_rf_star"
        )

        taxonomy_entries = []
        unclassified = []
        for architecture_id in sorted(architectures):
            record = architectures[architecture_id]
            profile = profiles_by_id.get(architecture_id, {})
            entry = {
                "architecture_id": architecture_id,
                "label": record.get("label", architecture_id),
                "architecture_type": record.get("architecture_type", "unspecified"),
                "architecture_family": self._family(record),
                "functional_regime": self._functional_regime(profile),
                "rf_proximity": self._rf_proximity(architecture_id, distance_matrix, canonical_id),
                "metric_profile": self._metric_profile(profile),
                "data_quality": self._data_quality(profile),
                "cluster_id": assignments.get(architecture_id),
                "outlier": architecture_id in outlier_ids,
                "profile_coverage": self._clamp01(
                    profile.get("coverage") if isinstance(profile.get("coverage"), (int, float))
                    else (
                        len([v for v in profile.get("rf_profile_vector", {}).values() if isinstance(v, (int, float))])
                        / float(len(profile.get("rf_profile_vector", {})) or 1)
                    ),
                    0.0,
                ),
                "profile_confidence": self._clamp01(profile.get("profile_confidence"), 0.0),
                "functional_classification_only": True,
            }
            if not profile or entry["rf_proximity"] == "proximity_unavailable":
                unclassified.append(architecture_id)
            taxonomy_entries.append(entry)

        nodes = {}
        edges = set()
        root_id = "taxonomy:comparative_rf_architectures"
        nodes[root_id] = {"node_id": root_id, "level": 0, "label": "comparative_rf_architectures"}
        level_fields = [
            (1, "architecture_family"),
            (2, "functional_regime"),
            (3, "rf_proximity"),
            (4, "metric_profile"),
            (5, "data_quality"),
        ]
        for entry in taxonomy_entries:
            parent = root_id
            for level, field in level_fields:
                value = str(entry[field])
                node_id = self._node_id(f"L{level}", value)
                nodes.setdefault(node_id, {"node_id": node_id, "level": level, "label": value})
                edges.add((parent, node_id))
                parent = node_id
            leaf_id = self._node_id("architecture", entry["architecture_id"])
            nodes[leaf_id] = {
                "node_id": leaf_id,
                "level": 6,
                "label": entry["architecture_id"],
                "architecture_id": entry["architecture_id"],
            }
            edges.add((parent, leaf_id))

        sorted_nodes = sorted(nodes.values(), key=lambda item: (item["level"], item["node_id"]))
        sorted_edges = [
            {"parent": parent, "child": child}
            for parent, child in sorted(edges)
        ]
        hierarchy = {
            "root": root_id,
            "levels": [
                "architecture_family",
                "functional_regime",
                "rf_proximity",
                "metric_profile",
                "data_quality",
                "architecture",
            ],
            "nodes": sorted_nodes,
            "edges": sorted_edges,
        }

        architecture_count = len(taxonomy_entries)
        classified_count = sum(
            1 for item in taxonomy_entries
            if item["functional_regime"] != "insufficient_functional_data"
        )
        coverage_score = round(classified_count / float(architecture_count or 1), 6)
        assignments_complete = all(item["cluster_id"] is not None for item in taxonomy_entries if item["profile_coverage"] > 0.0)
        source_ready = bool(
            profiles.get("rf_profile_ready")
            and distance.get("consciousness_distance_metric_ready")
            and clustering.get("clustering_engine_ready")
        )
        ready = bool(source_ready and architecture_count >= 2 and classified_count >= 2 and assignments_complete)

        hash_payload = json.dumps(
            {
                "version": self.taxonomy_version,
                "entries": taxonomy_entries,
                "hierarchy": hierarchy,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        taxonomy_hash = hashlib.sha256(hash_payload).hexdigest()
        status = "TAXONOMY_BUILDER_READY" if ready else "TAXONOMY_BUILDER_INCOMPLETE"

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": status,
            "taxonomy_builder_status": status,
            "taxonomy_builder_ready": ready,
            "taxonomy_status": status,
            "taxonomy_version": self.taxonomy_version,
            "taxonomy_depth": 6,
            "taxonomy": hierarchy,
            "taxonomy_nodes": sorted_nodes,
            "taxonomy_edges": sorted_edges,
            "taxonomy_entries": taxonomy_entries,
            "architecture_assignments": {
                item["architecture_id"]: {
                    key: item[key]
                    for key in (
                        "architecture_family", "functional_regime", "rf_proximity",
                        "metric_profile", "data_quality", "cluster_id", "outlier"
                    )
                }
                for item in taxonomy_entries
            },
            "architecture_count": architecture_count,
            "classified_architecture_count": classified_count,
            "unclassified_architectures": sorted(set(unclassified)),
            "unclassified_architecture_count": len(set(unclassified)),
            "taxonomy_node_count": len(sorted_nodes),
            "taxonomy_edge_count": len(sorted_edges),
            "coverage_score": coverage_score,
            "auditability_score": 1.0 if taxonomy_hash and sorted_nodes and sorted_edges else 0.0,
            "extensibility_score": 1.0,
            "assignments_complete": assignments_complete,
            "source_modules_ready": source_ready,
            "canonical_architecture_id": canonical_id,
            "taxonomy_hash": taxonomy_hash,
            "taxonomy_policy": {
                "hierarchy": "family>functional_regime>RF_proximity>metric_profile>data_quality>architecture",
                "deterministic_ordering": True,
                "missing_data_class": "insufficient_functional_data",
                "outliers_preserved": True,
                "future_architectures_supported": True,
                "classification_scope": "functional_RF_comparison_only",
            },
            "validation_policy": {
                "requires_AU3_profiles": True,
                "requires_AU5_distances": True,
                "requires_AU6_clusters": True,
                "requires_two_classified_architectures": True,
                "requires_complete_ready_profile_assignments": True,
                "requires_deterministic_hash": True,
            },
            "auditability_policy": {
                "versioned": True,
                "hashed": True,
                "source_architecture_ids_recorded": True,
                "classification_path_recorded": True,
                "missingness_preserved": True,
            },
            "allowed_claims": [
                "functional_RF_taxonomy_constructed",
                "architectures_hierarchically_classified_by_AU1_AU6_outputs",
                "comparative_data_quality_explicitly_classified",
            ],
            "blocked_claims": [
                "consciousness_proven",
                "qualia_proven",
                "subjectivity_proven",
                "phenomenology_proven",
                "taxonomy_membership_proves_consciousness",
                "RF_proximity_implies_phenomenal_similarity",
            ],
            "epistemic_guards": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "taxonomy_membership_is_not_consciousness_proof": True,
                "RF_proximity_is_not_phenomenal_proximity": True,
                "data_quality_is_not_ontological_status": True,
            },
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": [
                "comparative_dashboard",
                "comparative_history",
                "comparative_science_certifier",
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
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        if persist:
            output_dir = ROOT / "comparative_science" / "taxonomy"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "latest_taxonomy.json"
            output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(output_path)

        return result


if __name__ == "__main__":
    print(TaxonomyBuilder().step(inputs={}, persist=True)["taxonomy_builder_status"])
