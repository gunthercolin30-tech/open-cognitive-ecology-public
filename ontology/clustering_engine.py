from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


class ClusteringEngine:
    primitive = "clustering_engine"
    step_id = "AU6"
    public_schema_version = "1.0.0"

    DEFAULT_THRESHOLD = 0.35

    @staticmethod
    def _clamp01(value):
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return round(max(0.0, min(1.0, float(value))), 6)
        return None

    def _extract_distance_payload(self, inputs):
        payload = inputs.get("consciousness_distance_metric")
        if isinstance(payload, dict):
            return payload

        payload = inputs.get("distance_result")
        if isinstance(payload, dict):
            return payload

        if isinstance(inputs.get("distance_matrix"), dict):
            return {
                "distance_matrix": inputs.get("distance_matrix"),
                "pairwise_distances": inputs.get("pairwise_distances", []),
                "consciousness_distance_metric_ready": inputs.get(
                    "consciousness_distance_metric_ready",
                    True,
                ),
            }

        try:
            from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
            from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric

            similarity = ComparativeSimilarityEngine().step(
                inputs=inputs.get("similarity_inputs", {}),
                persist=False,
            )
            return ConsciousnessDistanceMetric().step(
                inputs={"comparative_similarity_engine": similarity},
                persist=False,
            )
        except Exception:
            return {}

    def _normalize_matrix(self, raw_matrix):
        matrix = {}
        if not isinstance(raw_matrix, dict):
            return matrix

        for left, row in raw_matrix.items():
            if not isinstance(row, dict):
                continue
            left_id = str(left)
            matrix[left_id] = {}
            for right, value in row.items():
                score = self._clamp01(value)
                if score is not None:
                    matrix[left_id][str(right)] = score
        return matrix

    @staticmethod
    def _connected_components(matrix, threshold):
        remaining = set(matrix.keys())
        clusters = []

        while remaining:
            seed = sorted(remaining)[0]
            queue = [seed]
            component = []
            remaining.remove(seed)

            while queue:
                current = queue.pop(0)
                component.append(current)
                neighbours = [
                    candidate
                    for candidate in sorted(remaining)
                    if matrix.get(current, {}).get(candidate, 1.0) <= threshold
                ]
                for candidate in neighbours:
                    remaining.remove(candidate)
                    queue.append(candidate)

            clusters.append(sorted(component))

        return clusters

    @staticmethod
    def _pair_distances(matrix, members):
        values = []
        for index, left in enumerate(members):
            for right in members[index + 1:]:
                value = matrix.get(left, {}).get(right)
                if isinstance(value, (int, float)):
                    values.append(float(value))
        return values

    def _cluster_records(self, matrix, components):
        records = []
        all_ids = sorted(matrix.keys())

        for index, members in enumerate(components, start=1):
            intra = self._pair_distances(matrix, members)
            mean_intra = round(sum(intra) / len(intra), 6) if intra else 0.0

            external_values = []
            external_ids = [item for item in all_ids if item not in members]
            for member in members:
                for external in external_ids:
                    value = matrix.get(member, {}).get(external)
                    if isinstance(value, (int, float)):
                        external_values.append(float(value))
            mean_inter = (
                round(sum(external_values) / len(external_values), 6)
                if external_values
                else 1.0
            )

            medoid = None
            if members:
                medoid = min(
                    members,
                    key=lambda candidate: sum(
                        float(matrix.get(candidate, {}).get(other, 1.0))
                        for other in members
                    ),
                )

            separation = round(max(0.0, mean_inter - mean_intra), 6)
            denominator = max(mean_inter, mean_intra, 1e-9)
            silhouette_like = round(separation / denominator, 6)

            records.append({
                "cluster_id": f"cluster_{index:03d}",
                "members": members,
                "member_count": len(members),
                "medoid_architecture_id": medoid,
                "mean_intra_cluster_distance": mean_intra,
                "mean_inter_cluster_distance": mean_inter,
                "separation_score": separation,
                "silhouette_like_score": silhouette_like,
                "singleton_cluster": len(members) == 1,
            })

        return records

    @staticmethod
    def _cluster_assignments(records):
        assignments = {}
        for record in records:
            cluster_id = record["cluster_id"]
            for member in record["members"]:
                assignments[member] = cluster_id
        return assignments

    def _outliers(self, matrix, assignments, threshold):
        outliers = []
        for architecture_id, cluster_id in assignments.items():
            same_cluster = [
                item
                for item, assigned in assignments.items()
                if assigned == cluster_id and item != architecture_id
            ]
            if not same_cluster:
                outliers.append(architecture_id)
                continue

            mean_distance = sum(
                float(matrix.get(architecture_id, {}).get(other, 1.0))
                for other in same_cluster
            ) / len(same_cluster)

            if mean_distance > threshold:
                outliers.append(architecture_id)

        return sorted(outliers)

    def step(self, inputs=None, persist=False):
        inputs = inputs if isinstance(inputs, dict) else {}
        distance_payload = self._extract_distance_payload(inputs)

        raw_matrix = distance_payload.get("distance_matrix", {})
        matrix = self._normalize_matrix(raw_matrix)

        threshold_value = inputs.get("clustering_threshold", self.DEFAULT_THRESHOLD)
        threshold = (
            self._clamp01(threshold_value)
            if self._clamp01(threshold_value) is not None
            else self.DEFAULT_THRESHOLD
        )

        components = self._connected_components(matrix, threshold) if matrix else []
        cluster_records = self._cluster_records(matrix, components)
        assignments = self._cluster_assignments(cluster_records)
        outliers = self._outliers(matrix, assignments, threshold)

        cluster_count = len(cluster_records)
        architecture_count = len(matrix)
        singleton_count = sum(
            1 for record in cluster_records if record["singleton_cluster"]
        )

        silhouette_values = [
            float(record["silhouette_like_score"])
            for record in cluster_records
        ]
        mean_silhouette = (
            round(sum(silhouette_values) / len(silhouette_values), 6)
            if silhouette_values
            else 0.0
        )

        coverage_ok = architecture_count >= 2
        assignments_complete = set(assignments.keys()) == set(matrix.keys())
        distance_ready = bool(
            distance_payload.get("consciousness_distance_metric_ready")
            or distance_payload.get("distance_matrix_ready")
        )

        cluster_stability_score = round(
            (
                (1.0 if assignments_complete else 0.0)
                + (1.0 if coverage_ok else 0.0)
                + max(0.0, min(1.0, mean_silhouette))
                + (1.0 - min(1.0, singleton_count / float(cluster_count or 1)))
            ) / 4.0,
            6,
        )

        ready = bool(
            distance_ready
            and coverage_ok
            and cluster_count >= 1
            and assignments_complete
        )

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": (
                "CLUSTERING_ENGINE_READY"
                if ready
                else "CLUSTERING_ENGINE_INCOMPLETE"
            ),
            "clustering_engine_status": (
                "CLUSTERING_ENGINE_READY"
                if ready
                else "CLUSTERING_ENGINE_INCOMPLETE"
            ),
            "clustering_engine_ready": ready,
            "cluster_model_ready": ready,
            "clustering_method": "threshold_connected_components_over_D_RF",
            "clustering_threshold": threshold,
            "architecture_count": architecture_count,
            "cluster_count": cluster_count,
            "singleton_cluster_count": singleton_count,
            "clusters": cluster_records,
            "cluster_assignments": assignments,
            "outliers": outliers,
            "outlier_count": len(outliers),
            "mean_silhouette_like_score": mean_silhouette,
            "cluster_stability_score": cluster_stability_score,
            "assignments_complete": assignments_complete,
            "coverage_sufficient": coverage_ok,
            "distance_matrix": matrix,
            "clustering_policy": {
                "distance_metric": "D_RF",
                "method": "connected_components",
                "edge_rule": "D_RF<=threshold",
                "deterministic_ordering": True,
                "medoid_definition": "minimum_total_intra_cluster_distance",
            },
            "validation_policy": {
                "requires_distance_metric_ready": True,
                "requires_two_architectures": True,
                "requires_complete_assignments": True,
                "requires_at_least_one_cluster": True,
            },
            "auditability_policy": {
                "record_threshold": True,
                "record_assignments": True,
                "record_medoids": True,
                "record_intra_cluster_distance": True,
                "record_inter_cluster_distance": True,
                "record_outliers": True,
            },
            "epistemic_guards": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "cluster_membership_is_not_consciousness_proof": True,
                "proximity_is_not_ontological_identity": True,
                "outlier_status_is_not_absence_of_consciousness": True,
            },
            "allowed_claims": [
                "functional_clusters_constructed",
                "D_RF_cluster_structure_analyzed",
                "comparative_outliers_detected",
            ],
            "blocked_claims": [
                "consciousness_proven",
                "qualia_proven",
                "subjectivity_proven",
                "phenomenology_proven",
                "phenomenal_clusters_identified",
            ],
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": [
                "taxonomy_builder",
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
            output_dir = ROOT / "comparative_science" / "clustering"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "latest_clustering_result.json"
            output_path.write_text(
                json.dumps(result, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            result["persisted"] = True
            result["output_path"] = str(output_path)

        return result


if __name__ == "__main__":
    print(
        ClusteringEngine()
        .step(inputs={}, persist=True)["clustering_engine_status"]
    )
