"""AW5 — functional conflict detector for reference-frame ecologies.

A conflict is inferred only from convergent evidence of durable functional
interference between distinct registered RFs. Difference, disagreement,
distance, competition, a single negative interaction, or temporary
incompatibility are never sufficient by themselves.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Set

ROOT = Path.home() / "open-cognitive-ecology"


class ConflictDetector:
    primitive = "CONFLICT_DETECTOR"
    step_id = "AW5"
    public_schema_version = "1.0"
    output_dir = ROOT / "rf_ecology" / "AW5_conflict_detector"

    default_thresholds = {
        "minimum_constraint_incompatibility": 0.55,
        "minimum_goal_incompatibility": 0.55,
        "minimum_resource_contention": 0.50,
        "minimum_mutual_blocking": 0.55,
        "minimum_intensity": 0.60,
        "minimum_duration": 0.55,
        "minimum_reciprocity": 0.55,
        "minimum_functional_impact": 0.60,
        "minimum_unresolvedness": 0.50,
        "minimum_evidence_quality": 0.60,
        "minimum_observations": 3,
        "minimum_causal_dimensions": 1,
        "minimum_convergent_dimensions": 7,
        "minimum_conflict_score": 0.60,
    }

    false_positive_fields = (
        "difference_only",
        "disagreement_only",
        "semantic_distance_only",
        "competition_without_blocking",
        "temporary_incompatibility",
        "single_negative_interaction",
        "common_external_constraint",
        "measurement_error",
        "synchronization_delay",
        "imposed_hierarchy",
        "accepted_asymmetric_allocation",
        "negotiation_in_progress",
        "statistical_coincidence",
        "diversity_only",
    )

    causal_score_fields = (
        "constraint_incompatibility_score",
        "goal_incompatibility_score",
        "resource_contention_score",
        "mutual_blocking_score",
    )

    evidence_score_fields = (
        "constraint_incompatibility_score",
        "goal_incompatibility_score",
        "resource_contention_score",
        "mutual_blocking_score",
        "intensity_score",
        "duration_score",
        "reciprocity_score",
        "escalation_score",
        "resolution_score",
        "functional_impact_score",
        "evidence_quality",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW5_conflict_detector"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _canonical(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def _hash(cls, value: Any) -> str:
        return hashlib.sha256(cls._canonical(value).encode("utf-8")).hexdigest()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(number):
            return default
        return round(max(0.0, min(1.0, number)), 6)

    @staticmethod
    def _safe_id(value: Any, fallback: str) -> str:
        raw = str(value or fallback).strip().upper()
        safe = re.sub(r"[^A-Z0-9._:-]+", "-", raw)
        safe = re.sub(r"-{2,}", "-", safe).strip("-")
        return safe or fallback

    @staticmethod
    def _string_list(value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        return sorted({str(item).strip() for item in value if str(item).strip()})

    @staticmethod
    def _time(value: Any) -> tuple[Optional[str], bool]:
        if value in (None, ""):
            return None, True
        text = str(value).strip()
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return text, False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"), True

    def _registry(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        supplied = inputs.get("multi_rf_registry")
        if isinstance(supplied, Mapping) and isinstance(supplied.get("registry"), list):
            return deepcopy(dict(supplied))
        from ontology.multi_rf_registry import MultiRFRegistry
        records = inputs.get("rf_records")
        return MultiRFRegistry(root=self.root).step(
            inputs={"rf_records": deepcopy(records)} if isinstance(records, list) else {},
            persist=False,
        )

    def _graph(self, inputs: Dict[str, Any], registry: Dict[str, Any]) -> Dict[str, Any]:
        supplied = inputs.get("interaction_graph")
        if isinstance(supplied, Mapping) and isinstance(supplied.get("edges"), list):
            return deepcopy(dict(supplied))
        from ontology.interaction_graph import InteractionGraph
        interactions = inputs.get("interactions")
        return InteractionGraph(root=self.root).step(
            inputs={
                "multi_rf_registry": registry,
                "interactions": deepcopy(interactions) if isinstance(interactions, list) else [],
            },
            persist=False,
        )

    def _coalitions(self, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supplied = inputs.get("coalition_detection") or inputs.get("coalition_detector")
        if isinstance(supplied, Mapping) and isinstance(supplied.get("coalitions"), list):
            return deepcopy(dict(supplied))
        return None

    def _thresholds(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(self.default_thresholds)
        supplied = inputs.get("thresholds", {})
        if isinstance(supplied, Mapping):
            for key in result:
                if key in {"minimum_observations", "minimum_causal_dimensions", "minimum_convergent_dimensions"}:
                    try:
                        result[key] = max(1, int(supplied.get(key, result[key])))
                    except (TypeError, ValueError):
                        pass
                else:
                    result[key] = self._clamp(supplied.get(key, result[key]), result[key])
        return result

    def _items(self, inputs: Dict[str, Any]) -> List[Mapping[str, Any]]:
        raw = inputs.get("conflict_candidates", inputs.get("candidate_conflicts", []))
        if isinstance(raw, Mapping):
            raw = raw.get("conflicts", raw.get("candidates", []))
        return [item for item in raw if isinstance(item, Mapping)] if isinstance(raw, list) else []

    def _graph_pair_set(self, graph: Dict[str, Any]) -> Set[frozenset[str]]:
        pairs: Set[frozenset[str]] = set()
        for edge in graph.get("edges", []):
            if not isinstance(edge, Mapping):
                continue
            a = str(edge.get("source_rf_id", "")).strip().upper()
            b = str(edge.get("target_rf_id", "")).strip().upper()
            if a and b and a != b:
                pairs.add(frozenset((a, b)))
        return pairs

    def _normalize_candidate(
        self,
        item: Mapping[str, Any],
        index: int,
        valid_rf_ids: Set[str],
        graph_pairs: Set[frozenset[str]],
        thresholds: Dict[str, Any],
    ) -> Dict[str, Any]:
        raw_participants = item.get("participant_rf_ids", item.get("rf_ids", item.get("participants", [])))
        participants = (
            sorted({str(x).strip().upper() for x in raw_participants if str(x).strip()})
            if isinstance(raw_participants, list)
            else []
        )
        missing = sorted(set(participants) - valid_rf_ids)
        valid_participants = sorted(set(participants) & valid_rf_ids)

        start, start_ok = self._time(item.get("valid_from_utc"))
        end, end_ok = self._time(item.get("valid_until_utc"))
        temporal_order_ok = True
        if start and end and start_ok and end_ok:
            temporal_order_ok = (
                datetime.fromisoformat(end.replace("Z", "+00:00"))
                >= datetime.fromisoformat(start.replace("Z", "+00:00"))
            )

        scores = {name: self._clamp(item.get(name, 0.0)) for name in self.evidence_score_fields}
        unresolvedness_score = round(1.0 - scores["resolution_score"], 6)

        observation_raw = item.get("observation_count", 0)
        try:
            observation_count = max(0, int(observation_raw))
        except (TypeError, ValueError):
            observation_count = 0

        blockers = [name for name in self.false_positive_fields if bool(item.get(name, False))]
        rival_raw = item.get("rival_explanation", "")
        rival = "" if rival_raw in (None, "") else str(rival_raw).strip()
        rival_sufficient = bool(item.get("rival_explanation_sufficient", False))
        if rival_sufficient:
            blockers.append("sufficient_rival_explanation")

        causal_pass = {
            "constraint_incompatibility": scores["constraint_incompatibility_score"]
            >= thresholds["minimum_constraint_incompatibility"],
            "goal_incompatibility": scores["goal_incompatibility_score"]
            >= thresholds["minimum_goal_incompatibility"],
            "resource_contention": scores["resource_contention_score"]
            >= thresholds["minimum_resource_contention"],
            "mutual_blocking": scores["mutual_blocking_score"]
            >= thresholds["minimum_mutual_blocking"],
        }
        dimension_pass = {
            **causal_pass,
            "intensity": scores["intensity_score"] >= thresholds["minimum_intensity"],
            "duration": scores["duration_score"] >= thresholds["minimum_duration"],
            "reciprocity": scores["reciprocity_score"] >= thresholds["minimum_reciprocity"],
            "functional_impact": scores["functional_impact_score"] >= thresholds["minimum_functional_impact"],
            "unresolvedness": unresolvedness_score >= thresholds["minimum_unresolvedness"],
            "evidence_quality": scores["evidence_quality"] >= thresholds["minimum_evidence_quality"],
            "observations": observation_count >= thresholds["minimum_observations"],
        }
        causal_dimension_count = sum(causal_pass.values())
        convergent_dimension_count = sum(dimension_pass.values())

        conflict_score = round(
            (
                max(scores["constraint_incompatibility_score"], scores["goal_incompatibility_score"])
                + scores["resource_contention_score"]
                + scores["mutual_blocking_score"]
                + scores["intensity_score"]
                + scores["duration_score"]
                + scores["reciprocity_score"]
                + scores["functional_impact_score"]
                + unresolvedness_score
                + scores["evidence_quality"]
            )
            / 9.0,
            6,
        )

        graph_pair_observed = (
            len(valid_participants) == 2 and frozenset(valid_participants) in graph_pairs
        )
        detected = bool(
            len(valid_participants) >= 2
            and not missing
            and start_ok
            and end_ok
            and temporal_order_ok
            and observation_count >= thresholds["minimum_observations"]
            and causal_dimension_count >= thresholds["minimum_causal_dimensions"]
            and convergent_dimension_count >= thresholds["minimum_convergent_dimensions"]
            and conflict_score >= thresholds["minimum_conflict_score"]
            and dimension_pass["intensity"]
            and dimension_pass["duration"]
            and dimension_pass["reciprocity"]
            and dimension_pass["functional_impact"]
            and dimension_pass["unresolvedness"]
            and dimension_pass["evidence_quality"]
            and not blockers
        )

        status = "RF_CONFLICT_DETECTED_FUNCTIONALLY" if detected else "NO_RF_CONFLICT_DETECTED"
        conflict_id = self._safe_id(item.get("conflict_id"), f"AW5-CONFLICT-{index:04d}")
        record = {
            "conflict_id": conflict_id,
            "participant_rf_ids": valid_participants,
            "participant_count": len(valid_participants),
            "missing_participant_rf_ids": missing,
            "conflict_status": status,
            "detected": detected,
            **scores,
            "unresolvedness_score": unresolvedness_score,
            "conflict_score": conflict_score,
            "causal_dimension_pass": causal_pass,
            "causal_dimension_count": causal_dimension_count,
            "dimension_pass": dimension_pass,
            "convergent_dimension_count": convergent_dimension_count,
            "observation_count": observation_count,
            "valid_from_utc": start,
            "valid_until_utc": end,
            "temporal_order_valid": start_ok and end_ok and temporal_order_ok,
            "graph_pair_observed": graph_pair_observed,
            "resource_ids": self._string_list(item.get("resource_ids", [])),
            "constraint_ids": self._string_list(item.get("constraint_ids", [])),
            "goal_ids": self._string_list(item.get("goal_ids", [])),
            "source_refs": self._string_list(item.get("source_refs", [])),
            "false_positive_blockers": sorted(set(blockers)),
            "rival_explanation": rival or None,
            "rival_explanation_sufficient": rival_sufficient,
            "escalation_detected": scores["escalation_score"] >= 0.60,
            "resolution_status": (
                "RESOLVED"
                if scores["resolution_score"] >= 0.70
                else "PARTIALLY_RESOLVED"
                if scores["resolution_score"] >= 0.35
                else "UNRESOLVED"
            ),
            "functional_only": True,
            "phenomenology_claim_allowed": False,
        }
        record["conflict_hash"] = self._hash(record)
        return record

    @staticmethod
    def _atomic_write(path: Path, payload: Dict[str, Any], fs_context: Any) -> None:
        if fs_context is None:
            raise PermissionError("preissued filesystem authority required")
        remaining = fs_context.remaining()
        required_slots = ("atomic_parent_create", "atomic_write_replace")
        if any(remaining.get(slot) != 1 for slot in required_slots):
            raise PermissionError("complete preissued filesystem authority required before persistence")
        encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        fs_context.execute_path("atomic_parent_create", "FS_CREATE_DIRS", path.parent)
        fs_context.execute_path("atomic_write_replace", "FS_WRITE_REPLACE_BYTES", path, payload=encoded)

    def _load(self) -> Optional[Dict[str, Any]]:
        path = self.output_dir / "latest_conflict_detection.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return None
        return payload if isinstance(payload, dict) and isinstance(payload.get("conflicts"), list) else None

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False, fs_context: Any = None) -> Dict[str, Any]:
        safe_inputs = deepcopy(inputs) if isinstance(inputs, dict) else {}
        load_existing = bool(safe_inputs.get("load_existing", False))
        existing = self._load() if load_existing else None
        if existing is not None:
            safe_inputs = dict(safe_inputs)
            if not self._items(safe_inputs):
                safe_inputs["conflict_candidates"] = deepcopy(existing.get("conflicts", []))

        registry = self._registry(safe_inputs)
        graph = self._graph(safe_inputs, registry)
        coalitions = self._coalitions(safe_inputs)
        valid_rf_ids = {
            str(item.get("rf_id", "")).strip().upper()
            for item in registry.get("registry", [])
            if isinstance(item, Mapping) and item.get("rf_id")
        }
        thresholds = self._thresholds(safe_inputs)
        graph_pairs = self._graph_pair_set(graph)
        conflicts = [
            self._normalize_candidate(item, index, valid_rf_ids, graph_pairs, thresholds)
            for index, item in enumerate(self._items(safe_inputs), 1)
        ]
        detected = [item for item in conflicts if item["detected"]]
        blocked = [item for item in conflicts if item["false_positive_blockers"]]
        invalid = [
            item
            for item in conflicts
            if item["missing_participant_rf_ids"] or not item["temporal_order_valid"]
        ]

        ready = bool(
            registry.get("multi_rf_registry_ready", False)
            and graph.get("interaction_graph_ready", False)
            and len(valid_rf_ids) >= 2
            and conflicts
            and not invalid
        )
        status = "RF_CONFLICT_DETECTION_READY" if ready else "RF_CONFLICT_DETECTION_INCOMPLETE"
        detection_hash = self._hash(
            {"rf_ids": sorted(valid_rf_ids), "thresholds": thresholds, "conflicts": conflicts}
        )

        policy = {
            "minimum_two_distinct_registered_rf_participants": True,
            "causal_conflict_evidence_required": True,
            "durable_interference_required": True,
            "reciprocity_required": True,
            "functional_impact_required": True,
            "difference_alone_is_insufficient": True,
            "disagreement_alone_is_insufficient": True,
            "distance_alone_is_insufficient": True,
            "competition_without_blocking_is_insufficient": True,
            "temporary_incompatibility_is_insufficient": True,
            "single_negative_interaction_is_insufficient": True,
            "rival_explanations_must_be_insufficient": True,
        }
        guards = {
            "epistemic_scope": "functional_rf_conflict_detection_only",
            "conflict_does_not_prove_collective_consciousness": True,
            "conflict_does_not_prove_collective_subjectivity": True,
            "conflict_does_not_prove_collective_qualia": True,
            "conflict_does_not_prove_collective_phenomenology": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_qualia_proven": False,
            "collective_subjectivity_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": status,
            "conflict_detection_status": status,
            "conflict_detection_ready": ready,
            "registry_ready": bool(registry.get("multi_rf_registry_ready", False)),
            "interaction_graph_ready": bool(graph.get("interaction_graph_ready", False)),
            "coalition_context_observed": coalitions is not None,
            "rf_ids": sorted(valid_rf_ids),
            "rf_count": len(valid_rf_ids),
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "detected_conflicts": detected,
            "detected_conflict_count": len(detected),
            "blocked_conflicts": blocked,
            "blocked_conflict_count": len(blocked),
            "invalid_conflicts": invalid,
            "invalid_conflict_count": len(invalid),
            "thresholds": thresholds,
            "conflict_policy": policy,
            "epistemic_guards": guards,
            "detection_hash": detection_hash,
            "inputs_observed": sorted(safe_inputs.keys()),
            "load_existing_requested": load_existing,
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "timestamp_utc": self._now(),
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_qualia_proven": False,
            "collective_subjectivity_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if persist and ready:
            path = self.output_dir / "latest_conflict_detection.json"
            payload = deepcopy(result)
            payload.update({"persisted": True, "output_path": str(path)})
            self._atomic_write(path, payload, fs_context)
            result.update({"persisted": True, "output_path": str(path)})
        return result
