from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set


class CollectiveConsciousnessAnalyzer:
    """AW9 functional analyzer of collective RF structure.

    Historical name retained for compatibility. The implementation makes only
    functional claims and never infers collective phenomenology.
    """

    primitive = "COLLECTIVE_CONSCIOUSNESS_ANALYZER"
    step_id = "AW9"
    public_schema_version = "1.0"

    default_thresholds = {
        "minimum_population_size": 2,
        "minimum_interaction_density": 0.20,
        "minimum_shared_rf_score": 0.20,
        "minimum_distributed_coordination_score": 0.45,
        "minimum_functional_collective_integration": 0.55,
        "maximum_centralization_risk": 0.75,
        "maximum_conflict_pressure": 0.75,
        "maximum_fragmentation_pressure": 0.75,
        "minimum_memory_sharing_score": 0.50,
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "rf_ecology" / "collective_analysis"
        self.output_path = self.output_dir / "latest_collective_rf_analysis.json"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _bounded(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return default
        if number != number or number in (float("inf"), float("-inf")):
            return default
        return round(max(0.0, min(1.0, number)), 6)

    @staticmethod
    def _hash(payload: Any) -> str:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def _list(value: Any) -> List[Any]:
        return list(value) if isinstance(value, (list, tuple)) else []

    @staticmethod
    def _mapping(value: Any) -> Dict[str, Any]:
        return deepcopy(dict(value)) if isinstance(value, Mapping) else {}

    @staticmethod
    def _ids(items: Iterable[Any], key: str) -> Set[str]:
        result: Set[str] = set()
        for item in items:
            if isinstance(item, Mapping):
                value = str(item.get(key, "")).strip()
                if value:
                    result.add(value)
        return result

    def _thresholds(self, raw: Any) -> Dict[str, float]:
        thresholds = dict(self.default_thresholds)
        if isinstance(raw, Mapping):
            for key in thresholds:
                if key in raw:
                    thresholds[key] = self._bounded(raw[key], thresholds[key])
        thresholds["minimum_population_size"] = max(2, int(round(float(
            raw.get("minimum_population_size", thresholds["minimum_population_size"])
        ))) if isinstance(raw, Mapping) else 2)
        return thresholds

    @staticmethod
    def _registry_records(registry: Mapping[str, Any]) -> List[Dict[str, Any]]:
        records = registry.get("registry", registry.get("rf_records", []))
        return [dict(item) for item in records if isinstance(item, Mapping)] if isinstance(records, list) else []

    @staticmethod
    def _detected(items: Sequence[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        return [item for item in items if bool(item.get("detected", False)) or any(
            str(item.get(k, "")).endswith("DETECTED_FUNCTIONALLY")
            for k in ("coalition_status", "conflict_status", "merge_status", "fragmentation_status")
        )]

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        safe_inputs = deepcopy(inputs) if isinstance(inputs, dict) else {}
        thresholds = self._thresholds(safe_inputs.get("thresholds", {}))

        registry = self._mapping(safe_inputs.get("multi_rf_registry"))
        graph = self._mapping(safe_inputs.get("interaction_graph"))
        shared = self._mapping(safe_inputs.get("shared_reference_frame_detection"))
        coalitions_result = self._mapping(safe_inputs.get("coalition_detection"))
        conflicts_result = self._mapping(safe_inputs.get("conflict_detection"))
        merges_result = self._mapping(safe_inputs.get("reference_frame_merging"))
        fragments_result = self._mapping(safe_inputs.get("reference_frame_fragmentation"))
        memory = self._mapping(safe_inputs.get("civilizational_memory"))

        records = self._registry_records(registry)
        member_rf_ids = sorted(self._ids(records, "rf_id"))
        population_size = len(member_rf_ids)
        population_valid = population_size >= thresholds["minimum_population_size"]

        raw_edges = [
            dict(item)
            for item in self._list(
                graph.get("edges", graph.get("interactions", []))
            )
            if isinstance(item, Mapping)
        ]

        valid_edge_map: Dict[tuple, Dict[str, Any]] = {}
        orphan_edge_count = 0
        for edge in raw_edges:
            source = str(edge.get("source_rf_id", "")).strip()
            target = str(edge.get("target_rf_id", "")).strip()
            if (
                not source
                or not target
                or source == target
                or source not in member_rf_ids
                or target not in member_rf_ids
            ):
                orphan_edge_count += 1
                continue

            key = tuple(sorted((source, target)))
            current = valid_edge_map.get(key)
            if current is None:
                valid_edge_map[key] = edge
                continue

            current_strength = self._bounded(
                current.get("interaction_strength", 0.0)
            )
            candidate_strength = self._bounded(
                edge.get("interaction_strength", 0.0)
            )
            if candidate_strength > current_strength:
                valid_edge_map[key] = edge

        edges = [
            valid_edge_map[key]
            for key in sorted(valid_edge_map)
        ]
        duplicate_edge_count = max(
            0,
            len(raw_edges) - orphan_edge_count - len(edges),
        )
        edge_count = len(edges)
        possible_edges = max(
            1,
            population_size * (population_size - 1) // 2,
        )
        interaction_density = self._bounded(
            edge_count / possible_edges
            if population_size > 1
            else 0.0
        )

        degrees = {rf_id: 0 for rf_id in member_rf_ids}
        for edge in edges:
            source = str(edge.get("source_rf_id", "")).strip()
            target = str(edge.get("target_rf_id", "")).strip()
            degrees[source] += 1
            degrees[target] += 1

        if population_size <= 2:
            centralization_risk_score = (
                1.0 if edge_count == 1 else 0.0
            )
        else:
            maximum_degree = max(degrees.values()) if degrees else 0
            numerator = sum(
                maximum_degree - degree
                for degree in degrees.values()
            )
            denominator = (population_size - 1) * (
                population_size - 2
            )
            centralization_risk_score = self._bounded(
                numerator / denominator
                if denominator
                else 0.0
            )

        local_autonomy_score = self._bounded(
            1.0 - centralization_risk_score
        )

        detected_shared_count = int(shared.get("detected_pair_count", 0) or 0)
        shared_rf_score = self._bounded(detected_shared_count / possible_edges)

        coalitions = [dict(item) for item in self._list(coalitions_result.get("coalitions")) if isinstance(item, Mapping)]
        detected_coalitions = self._detected(coalitions)
        coalition_members: Set[str] = set()
        coalition_scores: List[float] = []
        for coalition in detected_coalitions:
            coalition_members.update(str(v) for v in self._list(coalition.get("member_rf_ids")) if str(v))
            coalition_scores.append(self._bounded(coalition.get("coalition_score", 0.0)))
        coalition_coverage_score = self._bounded(len(coalition_members) / population_size if population_size else 0.0)
        coalition_coherence_score = self._bounded(sum(coalition_scores) / len(coalition_scores) if coalition_scores else 0.0)

        conflicts = [dict(item) for item in self._list(conflicts_result.get("conflicts")) if isinstance(item, Mapping)]
        detected_conflicts = self._detected(conflicts)
        conflict_scores = [self._bounded(item.get("conflict_score", 0.0)) for item in detected_conflicts]
        conflict_pressure_score = self._bounded(sum(conflict_scores) / len(conflict_scores) if conflict_scores else 0.0)

        merges = [dict(item) for item in self._list(merges_result.get("merges")) if isinstance(item, Mapping)]
        fragments = [dict(item) for item in self._list(fragments_result.get("fragmentations")) if isinstance(item, Mapping)]
        detected_merges = self._detected(merges)
        detected_fragments = self._detected(fragments)
        merge_activity_score = self._bounded(len(detected_merges) / max(1, population_size))
        fragmentation_pressure_score = self._bounded(len(detected_fragments) / max(1, population_size))

        memory_ready = bool(memory.get("civilizational_memory_ready", False))
        memory_sharing_score = self._bounded(sum([
            1.0 if memory_ready else 0.0,
            self._bounded(memory.get("availability_score", 0.0)),
            self._bounded(memory.get("lineage_preservation_score", 0.0)),
            self._bounded(memory.get("future_openness_preservation_score", 0.0)),
        ]) / 4.0)

        distributed_coordination_score = self._bounded(
            0.35 * interaction_density
            + 0.25 * shared_rf_score
            + 0.20 * coalition_coverage_score
            + 0.20 * local_autonomy_score
        )

        positive = (
            0.25 * distributed_coordination_score
            + 0.20 * shared_rf_score
            + 0.20 * memory_sharing_score
            + 0.15 * coalition_coherence_score
            + 0.10 * local_autonomy_score
            + 0.10 * self._bounded(1.0 - fragmentation_pressure_score)
        )
        penalties = 0.20 * conflict_pressure_score + 0.15 * centralization_risk_score
        functional_collective_integration = self._bounded(positive - penalties)

        blockers: List[str] = []
        if not population_valid:
            blockers.append("INSUFFICIENT_MULTI_RF_POPULATION")
        if interaction_density < thresholds["minimum_interaction_density"]:
            blockers.append("INSUFFICIENT_OBSERVED_INTERACTION")
        if shared_rf_score < thresholds["minimum_shared_rf_score"]:
            blockers.append("NO_REPRODUCIBLE_SHARED_REFERENCE_FRAME")
        if distributed_coordination_score < thresholds["minimum_distributed_coordination_score"]:
            blockers.append("INSUFFICIENT_DISTRIBUTED_COORDINATION")
        if memory_sharing_score < thresholds["minimum_memory_sharing_score"]:
            blockers.append("INSUFFICIENT_CIVILIZATIONAL_MEMORY_SHARING")
        if centralization_risk_score > thresholds["maximum_centralization_risk"]:
            blockers.append("SINGLE_CONTROLLER_OR_CENTRALIZATION_RISK")
        if conflict_pressure_score > thresholds["maximum_conflict_pressure"]:
            blockers.append("CONFLICT_PRESSURE_DOMINATES")
        if fragmentation_pressure_score > thresholds["maximum_fragmentation_pressure"]:
            blockers.append("FRAGMENTATION_PRESSURE_DOMINATES")
        if functional_collective_integration < thresholds["minimum_functional_collective_integration"]:
            blockers.append("FUNCTIONAL_INTEGRATION_BELOW_THRESHOLD")

        ready = not blockers
        status = "COLLECTIVE_RF_ANALYSIS_READY" if ready else "COLLECTIVE_RF_ANALYSIS_NOT_READY"
        collective_structure_id = "COLLECTIVE-RF-" + self._hash(member_rf_ids)[:16].upper() if member_rf_ids else None

        collective_reference_frame = {
            "collective_structure_id": collective_structure_id,
            "member_rf_ids": member_rf_ids,
            "population_size": population_size,
            "shared_reference_frame_score": shared_rf_score,
            "functional_only": True,
        }
        distributed_coordination_structure = {
            "edge_count": edge_count,
            "raw_edge_count": len(raw_edges),
            "duplicate_edge_count": duplicate_edge_count,
            "orphan_edge_count": orphan_edge_count,
            "interaction_density": interaction_density,
            "degree_distribution": dict(sorted(degrees.items())),
            "distributed_coordination_score": (
                distributed_coordination_score
            ),
            "centralization_risk_score": centralization_risk_score,
            "local_autonomy_score": local_autonomy_score,
            "single_controller_required": False,
        }
        collective_rf_structure = {
            "coalition_count": len(detected_coalitions),
            "conflict_count": len(detected_conflicts),
            "merge_count": len(detected_merges),
            "fragmentation_count": len(detected_fragments),
            "coalition_coverage_score": coalition_coverage_score,
            "coalition_coherence_score": coalition_coherence_score,
            "conflict_pressure_score": conflict_pressure_score,
            "merge_activity_score": merge_activity_score,
            "fragmentation_pressure_score": fragmentation_pressure_score,
            "memory_sharing_score": memory_sharing_score,
        }

        hash_payload = {
            "thresholds": thresholds,
            "collective_reference_frame": collective_reference_frame,
            "distributed_coordination_structure": distributed_coordination_structure,
            "collective_rf_structure": collective_rf_structure,
            "functional_collective_integration": functional_collective_integration,
            "blockers": sorted(blockers),
            "source_hashes": {
                "registry_hash": registry.get("registry_hash"),
                "graph_hash": graph.get("graph_hash"),
                "shared_rf_hash": shared.get("detection_hash"),
                "coalition_hash": coalitions_result.get("detection_hash"),
                "conflict_hash": conflicts_result.get("detection_hash"),
                "merge_hash": merges_result.get("result_hash"),
                "fragmentation_hash": fragments_result.get("result_hash"),
                "memory_hash": memory.get("memory_hash"),
            },
        }
        analysis_hash = self._hash(hash_payload)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "status": status,
            "collective_rf_analysis_status": status,
            "collective_rf_analysis_ready": ready,
            "collective_reference_frame": collective_reference_frame,
            "collective_rf_structure": collective_rf_structure,
            "distributed_coordination_structure": distributed_coordination_structure,
            "functional_collective_integration": functional_collective_integration,
            "integration_score": functional_collective_integration,
            "distributed_coordination_score": distributed_coordination_score,
            "shared_memory_score": memory_sharing_score,
            "shared_reference_frame_score": shared_rf_score,
            "coalition_coherence_score": coalition_coherence_score,
            "conflict_pressure_score": conflict_pressure_score,
            "fragmentation_pressure_score": fragmentation_pressure_score,
            "merge_activity_score": merge_activity_score,
            "local_autonomy_score": local_autonomy_score,
            "centralization_risk_score": centralization_risk_score,
            "member_rf_ids": member_rf_ids,
            "population_size": population_size,
            "false_positive_blockers": sorted(blockers),
            "thresholds": thresholds,
            "analysis_hash": analysis_hash,
            "collective_structure_hash": analysis_hash,
            "source_hashes": hash_payload["source_hashes"],
            "epistemic_scope": "functional_multi_rf_ecology_only",
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
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
            result["persisted"] = True
            result["output_path"] = str(self.output_path)
            self.output_path.write_text(
                json.dumps(
                    result,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        return result
