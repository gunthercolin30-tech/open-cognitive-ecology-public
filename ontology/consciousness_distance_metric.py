from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


class ConsciousnessDistanceMetric:
    primitive = "consciousness_distance_metric"
    step_id = "AU5"
    public_schema_version = "1.0.0"

    @staticmethod
    def _clamp01(value):
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return round(max(0.0, min(1.0, float(value))), 6)
        return None

    def _extract_similarity_payload(self, inputs):
        payload = inputs.get("comparative_similarity_engine")
        if isinstance(payload, dict):
            return payload

        payload = inputs.get("similarity_result")
        if isinstance(payload, dict):
            return payload

        if isinstance(inputs.get("similarity_matrix"), dict):
            return {
                "similarity_matrix": inputs.get("similarity_matrix"),
                "pairwise_similarities": inputs.get("pairwise_similarities", []),
                "comparison_dimensions": inputs.get("comparison_dimensions", []),
                "dimension_weights": inputs.get("dimension_weights", {}),
                "comparative_similarity_engine_ready": inputs.get(
                    "comparative_similarity_engine_ready",
                    True,
                ),
            }

        try:
            from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
            return ComparativeSimilarityEngine().step(
                inputs=inputs.get("similarity_inputs", {}),
                persist=False,
            )
        except Exception:
            return {}

    def _distance_matrix(self, similarity_matrix):
        distance_matrix = {}
        identity_ok = True
        symmetry_ok = True
        bounded_ok = True

        for left, row in similarity_matrix.items():
            if not isinstance(row, dict):
                continue
            left_id = str(left)
            distance_matrix[left_id] = {}
            for right, similarity in row.items():
                right_id = str(right)
                score = self._clamp01(similarity)
                if score is None:
                    continue
                distance = round(1.0 - score, 6)
                distance_matrix[left_id][right_id] = distance
                if not 0.0 <= distance <= 1.0:
                    bounded_ok = False
                if left_id == right_id and distance != 0.0:
                    identity_ok = False

        for left in distance_matrix:
            for right, value in distance_matrix[left].items():
                reverse = distance_matrix.get(right, {}).get(left)
                if reverse is None or abs(float(value) - float(reverse)) > 1e-9:
                    symmetry_ok = False

        return distance_matrix, identity_ok, symmetry_ok, bounded_ok

    def _pairwise_distances(self, pairwise_similarities):
        records = []
        for record in pairwise_similarities:
            if not isinstance(record, dict):
                continue

            similarity = self._clamp01(record.get("structural_similarity"))
            if similarity is None:
                continue

            distance = round(1.0 - similarity, 6)
            confidence = self._clamp01(record.get("evidence_confidence"))
            coverage = self._clamp01(record.get("comparison_coverage"))

            confidence = confidence if confidence is not None else 0.0
            coverage = coverage if coverage is not None else 0.0

            dimension_distances = {}
            raw_dimensions = record.get("dimension_similarities")
            if isinstance(raw_dimensions, dict):
                for dimension, value in raw_dimensions.items():
                    dimension_similarity = self._clamp01(value)
                    dimension_distances[str(dimension)] = (
                        round(1.0 - dimension_similarity, 6)
                        if dimension_similarity is not None
                        else None
                    )

            records.append({
                "pair_id": record.get("pair_id"),
                "left_architecture_id": record.get("left_architecture_id"),
                "right_architecture_id": record.get("right_architecture_id"),
                "D_RF": distance,
                "distance": distance,
                "dimension_distances": dimension_distances,
                "comparison_coverage": coverage,
                "evidence_confidence": confidence,
                "confidence_adjusted_distance": round(
                    distance * coverage * confidence,
                    6,
                ),
                "distance_valid": bool(record.get("comparison_valid", True)),
            })
        return records

    def step(self, inputs=None, persist=False):
        inputs = inputs if isinstance(inputs, dict) else {}
        similarity = self._extract_similarity_payload(inputs)

        similarity_matrix = similarity.get("similarity_matrix", {})
        if not isinstance(similarity_matrix, dict):
            similarity_matrix = {}

        pairwise_similarities = similarity.get("pairwise_similarities", [])
        if not isinstance(pairwise_similarities, list):
            pairwise_similarities = []

        distance_matrix, identity_ok, symmetry_ok, bounded_ok = self._distance_matrix(
            similarity_matrix
        )
        pairwise_distances = self._pairwise_distances(pairwise_similarities)
        valid_pairs = [item for item in pairwise_distances if item["distance_valid"]]
        distances = [float(item["D_RF"]) for item in valid_pairs]

        similarity_ready = bool(
            similarity.get("comparative_similarity_engine_ready")
            or similarity.get("similarity_matrix_ready")
        )
        architecture_count = len(distance_matrix)
        pair_count = len(pairwise_distances)

        ready = bool(
            similarity_ready
            and architecture_count >= 2
            and pair_count >= 1
            and identity_ok
            and symmetry_ok
            and bounded_ok
        )

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": (
                "CONSCIOUSNESS_DISTANCE_METRIC_READY"
                if ready
                else "CONSCIOUSNESS_DISTANCE_METRIC_INCOMPLETE"
            ),
            "consciousness_distance_metric_status": (
                "CONSCIOUSNESS_DISTANCE_METRIC_READY"
                if ready
                else "CONSCIOUSNESS_DISTANCE_METRIC_INCOMPLETE"
            ),
            "consciousness_distance_metric_ready": ready,
            "distance_matrix_ready": ready,
            "distance_metric_id": "D_RF",
            "distance_definition": "D_RF(a,b)=1-structural_similarity_RF(a,b)",
            "architecture_count": architecture_count,
            "pairwise_distance_count": pair_count,
            "valid_pairwise_distance_count": len(valid_pairs),
            "pairwise_distances": pairwise_distances,
            "distance_matrix": distance_matrix,
            "mean_distance": round(sum(distances) / len(distances), 6) if distances else 0.0,
            "minimum_distance_pair": (
                min(valid_pairs, key=lambda item: item["D_RF"])
                if valid_pairs
                else None
            ),
            "maximum_distance_pair": (
                max(valid_pairs, key=lambda item: item["D_RF"])
                if valid_pairs
                else None
            ),
            "identity_axiom_satisfied": identity_ok,
            "symmetry_axiom_satisfied": symmetry_ok,
            "boundedness_axiom_satisfied": bounded_ok,
            "triangle_inequality_status": "NOT_CERTIFIED_BY_AU5",
            "distance_range": [0.0, 1.0],
            "comparison_dimensions": similarity.get("comparison_dimensions", []),
            "dimension_weights": similarity.get("dimension_weights", {}),
            "metric_policy": {
                "identity": "distance(a,a)=0",
                "symmetry": "distance(a,b)=distance(b,a)",
                "boundedness": "0<=distance<=1",
                "triangle_inequality": "not_assumed",
                "missingness": "inherit_AU4_pairwise_complete_policy",
            },
            "validation_policy": {
                "requires_similarity_engine_ready": True,
                "requires_two_architectures": True,
                "requires_one_pairwise_distance": True,
                "requires_identity": True,
                "requires_symmetry": True,
                "requires_boundedness": True,
            },
            "auditability_policy": {
                "record_source_similarity": True,
                "record_dimension_distances": True,
                "record_coverage": True,
                "record_evidence_confidence": True,
                "record_distance_matrix": True,
            },
            "epistemic_guards": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "distance_is_not_absence_of_consciousness": True,
                "distance_is_not_proof_of_consciousness": True,
                "distance_is_not_ontological_separation": True,
            },
            "allowed_claims": [
                "functional_distance_computed",
                "cross_architecture_distance_matrix_constructed",
                "distance_axioms_checked",
            ],
            "blocked_claims": [
                "consciousness_proven",
                "qualia_proven",
                "subjectivity_proven",
                "phenomenology_proven",
                "phenomenal_distance_measured",
            ],
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": [
                "clustering_engine",
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
            output_dir = ROOT / "comparative_science" / "distance"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "latest_consciousness_distance_metric.json"
            output_path.write_text(
                json.dumps(result, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            result["persisted"] = True
            result["output_path"] = str(output_path)

        return result


if __name__ == "__main__":
    print(
        ConsciousnessDistanceMetric()
        .step(inputs={}, persist=True)["consciousness_distance_metric_status"]
    )
