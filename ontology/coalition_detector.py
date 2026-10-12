"""AW4 — functional coalition detector for populations of reference frames.

A coalition is inferred only from convergent group-level evidence. Graph density,
shared RF detection, similarity, alignment, externally imposed synchronization,
or a common controller are never sufficient by themselves.
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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set

ROOT = Path.home() / "open-cognitive-ecology"


class CoalitionDetector:
    primitive = "COALITION_DETECTOR"
    step_id = "AW4"
    public_schema_version = "1.0"
    output_dir = ROOT / "rf_ecology" / "AW4_coalition_detector"

    default_thresholds = {
        "minimum_cohesion": 0.65,
        "minimum_reciprocity": 0.60,
        "minimum_shared_goal": 0.65,
        "minimum_coordination": 0.65,
        "minimum_temporal_stability": 0.60,
        "minimum_resilience": 0.55,
        "minimum_boundary": 0.55,
        "minimum_member_contribution": 0.45,
        "minimum_evidence_quality": 0.60,
        "minimum_observations": 3,
        "minimum_convergent_dimensions": 7,
        "minimum_coalition_score": 0.64,
    }

    false_positive_fields = (
        "dense_cluster_only",
        "shared_rf_only",
        "alignment_only",
        "common_controller",
        "copy_or_clone_explanation",
        "translation_only",
        "external_synchronization",
        "statistical_coincidence",
        "semantic_proximity_only",
        "single_interaction_only",
        "imposed_hierarchy",
        "technical_dependency_only",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW4_coalition_detector"

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

    def _shared(self, inputs: Dict[str, Any], registry: Dict[str, Any], graph: Dict[str, Any]) -> Dict[str, Any]:
        supplied = inputs.get("shared_reference_frame_detection") or inputs.get("shared_reference_frame_detector")
        if isinstance(supplied, Mapping) and isinstance(supplied.get("pair_results"), list):
            return deepcopy(dict(supplied))
        from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector
        return SharedReferenceFrameDetector(root=self.root).step(
            inputs={
                "multi_rf_registry": registry,
                "interaction_graph": graph,
                "pair_evidence": deepcopy(inputs.get("pair_evidence", {})),
            },
            persist=False,
        )

    def _thresholds(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(self.default_thresholds)
        supplied = inputs.get("thresholds", {})
        if isinstance(supplied, Mapping):
            for key in result:
                if key in {"minimum_observations", "minimum_convergent_dimensions"}:
                    try:
                        result[key] = max(1, int(supplied.get(key, result[key])))
                    except (TypeError, ValueError):
                        pass
                else:
                    result[key] = self._clamp(supplied.get(key, result[key]), result[key])
        return result

    def _items(self, inputs: Dict[str, Any]) -> List[Mapping[str, Any]]:
        raw = inputs.get("coalition_candidates", inputs.get("candidate_coalitions", []))
        if isinstance(raw, Mapping):
            raw = raw.get("coalitions", raw.get("candidates", []))
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

    def _shared_pair_set(self, shared: Dict[str, Any]) -> Set[frozenset[str]]:
        pairs: Set[frozenset[str]] = set()
        for item in shared.get("detected_pairs", []):
            if not isinstance(item, Mapping):
                continue
            ids = [str(x).strip().upper() for x in item.get("rf_ids", []) if str(x).strip()]
            if len(set(ids)) == 2:
                pairs.add(frozenset(ids))
        return pairs

    @staticmethod
    def _coverage(member_ids: Sequence[str], observed_pairs: Set[frozenset[str]]) -> float:
        members = sorted(set(member_ids))
        possible = len(members) * (len(members) - 1) // 2
        if possible <= 0:
            return 0.0
        actual = sum(frozenset((members[i], members[j])) in observed_pairs for i in range(len(members)) for j in range(i + 1, len(members)))
        return round(actual / possible, 6)

    def _normalize_candidate(
        self,
        item: Mapping[str, Any],
        index: int,
        valid_rf_ids: Set[str],
        graph_pairs: Set[frozenset[str]],
        shared_pairs: Set[frozenset[str]],
        thresholds: Dict[str, Any],
    ) -> Dict[str, Any]:
        raw_members = item.get("member_rf_ids", item.get("members", []))
        members = sorted({str(x).strip().upper() for x in raw_members if str(x).strip()}) if isinstance(raw_members, list) else []
        missing = sorted(set(members) - valid_rf_ids)
        valid_members = sorted(set(members) & valid_rf_ids)
        contributions_raw = item.get("member_contributions", {})
        contributions = {
            member: self._clamp(contributions_raw.get(member, contributions_raw.get(member.lower(), 0.0)))
            for member in valid_members
        } if isinstance(contributions_raw, Mapping) else {member: 0.0 for member in valid_members}
        minimum_contribution = min(contributions.values()) if contributions else 0.0
        mean_contribution = round(sum(contributions.values()) / len(contributions), 6) if contributions else 0.0

        start, start_ok = self._time(item.get("valid_from_utc"))
        end, end_ok = self._time(item.get("valid_until_utc"))
        temporal_order_ok = True
        if start and end and start_ok and end_ok:
            temporal_order_ok = datetime.fromisoformat(end.replace("Z", "+00:00")) >= datetime.fromisoformat(start.replace("Z", "+00:00"))

        scores = {
            "cohesion_score": self._clamp(item.get("cohesion_score", 0.0)),
            "reciprocity_score": self._clamp(item.get("reciprocity_score", 0.0)),
            "shared_goal_score": self._clamp(item.get("shared_goal_score", 0.0)),
            "coordination_score": self._clamp(item.get("coordination_score", 0.0)),
            "temporal_stability_score": self._clamp(item.get("temporal_stability_score", 0.0)),
            "resilience_score": self._clamp(item.get("resilience_score", 0.0)),
            "boundary_score": self._clamp(item.get("boundary_score", 0.0)),
            "evidence_quality": self._clamp(item.get("evidence_quality", 0.0)),
        }
        observation_count = max(0, int(item.get("observation_count", 0))) if str(item.get("observation_count", 0)).lstrip("-").isdigit() else 0
        blockers = [name for name in self.false_positive_fields if bool(item.get(name, False))]
        rival = str(item.get("rival_explanation", "")).strip()
        rival_sufficient = bool(item.get("rival_explanation_sufficient", False))
        if rival_sufficient:
            blockers.append("sufficient_rival_explanation")

        dimension_pass = {
            "cohesion": scores["cohesion_score"] >= thresholds["minimum_cohesion"],
            "reciprocity": scores["reciprocity_score"] >= thresholds["minimum_reciprocity"],
            "shared_goal": scores["shared_goal_score"] >= thresholds["minimum_shared_goal"],
            "coordination": scores["coordination_score"] >= thresholds["minimum_coordination"],
            "temporal_stability": scores["temporal_stability_score"] >= thresholds["minimum_temporal_stability"],
            "resilience": scores["resilience_score"] >= thresholds["minimum_resilience"],
            "boundary": scores["boundary_score"] >= thresholds["minimum_boundary"],
            "member_contribution": minimum_contribution >= thresholds["minimum_member_contribution"],
            "evidence_quality": scores["evidence_quality"] >= thresholds["minimum_evidence_quality"],
            "observations": observation_count >= thresholds["minimum_observations"],
        }
        convergent = sum(dimension_pass.values())
        coalition_score = round((sum(scores.values()) + mean_contribution) / 9.0, 6)
        graph_coverage = self._coverage(valid_members, graph_pairs)
        shared_rf_coverage = self._coverage(valid_members, shared_pairs)
        detected = bool(
            len(valid_members) >= 2
            and not missing
            and start_ok
            and end_ok
            and temporal_order_ok
            and observation_count >= thresholds["minimum_observations"]
            and coalition_score >= thresholds["minimum_coalition_score"]
            and convergent >= thresholds["minimum_convergent_dimensions"]
            and all(dimension_pass.values())
            and not blockers
        )
        status = "RF_COALITION_DETECTED_FUNCTIONALLY" if detected else "NO_RF_COALITION_DETECTED"
        coalition_id = self._safe_id(item.get("coalition_id"), f"AW4-COALITION-{index:04d}")
        record = {
            "coalition_id": coalition_id,
            "member_rf_ids": valid_members,
            "member_count": len(valid_members),
            "missing_member_rf_ids": missing,
            "coalition_status": status,
            "detected": detected,
            **scores,
            "coalition_score": coalition_score,
            "reciprocal_interaction_coverage": graph_coverage,
            "shared_rf_coverage": shared_rf_coverage,
            "member_contributions": contributions,
            "minimum_member_contribution": minimum_contribution,
            "mean_member_contribution": mean_contribution,
            "observation_count": observation_count,
            "valid_from_utc": start,
            "valid_until_utc": end,
            "temporal_order_valid": start_ok and end_ok and temporal_order_ok,
            "dimension_pass": dimension_pass,
            "convergent_dimension_count": convergent,
            "source_refs": self._string_list(item.get("source_refs", [])),
            "false_positive_blockers": sorted(set(blockers)),
            "rival_explanation": rival or None,
            "rival_explanation_sufficient": rival_sufficient,
            "functional_only": True,
            "phenomenology_claim_allowed": False,
        }
        record["coalition_hash"] = self._hash(record)
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
        path = self.output_dir / "latest_coalition_detection.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return None
        return payload if isinstance(payload, dict) and isinstance(payload.get("coalitions"), list) else None

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False, fs_context: Any = None) -> Dict[str, Any]:
        safe_inputs = deepcopy(inputs) if isinstance(inputs, dict) else {}
        load_existing = bool(safe_inputs.get("load_existing", False))
        existing = self._load() if load_existing else None
        if existing is not None:
            safe_inputs = dict(safe_inputs)
            safe_inputs.setdefault("coalition_candidates", deepcopy(existing.get("coalitions", [])))

        registry = self._registry(safe_inputs)
        graph = self._graph(safe_inputs, registry)
        shared = self._shared(safe_inputs, registry, graph)
        valid_rf_ids = {
            str(item.get("rf_id", "")).strip().upper()
            for item in registry.get("registry", [])
            if isinstance(item, Mapping) and item.get("rf_id")
        }
        thresholds = self._thresholds(safe_inputs)
        graph_pairs = self._graph_pair_set(graph)
        shared_pairs = self._shared_pair_set(shared)
        coalitions = [
            self._normalize_candidate(item, index, valid_rf_ids, graph_pairs, shared_pairs, thresholds)
            for index, item in enumerate(self._items(safe_inputs), 1)
        ]
        detected = [item for item in coalitions if item["detected"]]
        blocked = [item for item in coalitions if item["false_positive_blockers"]]
        invalid = [item for item in coalitions if item["missing_member_rf_ids"] or not item["temporal_order_valid"]]
        ready = bool(
            registry.get("multi_rf_registry_ready", False)
            and graph.get("interaction_graph_ready", False)
            and len(valid_rf_ids) >= 2
            and coalitions
            and not invalid
        )
        status = "RF_COALITION_DETECTION_READY" if ready else "RF_COALITION_DETECTION_INCOMPLETE"
        detection_hash = self._hash({"rf_ids": sorted(valid_rf_ids), "thresholds": thresholds, "coalitions": coalitions})
        policy = {
            "minimum_two_distinct_registered_rf_members": True,
            "group_level_convergent_evidence_required": True,
            "durable_coordination_required": True,
            "member_contribution_required": True,
            "coalition_boundary_required": True,
            "rival_explanations_must_be_insufficient": True,
            "interaction_alone_is_insufficient": True,
            "graph_density_alone_is_insufficient": True,
            "shared_rf_alone_is_insufficient": True,
            "alignment_alone_is_insufficient": True,
            "common_controller_is_false_positive_risk": True,
            "external_synchronization_is_false_positive_risk": True,
        }
        guards = {
            "epistemic_scope": "functional_rf_coalition_detection_only",
            "coalition_does_not_prove_collective_consciousness": True,
            "coalition_does_not_prove_collective_subjectivity": True,
            "coalition_does_not_prove_collective_qualia": True,
            "coalition_does_not_prove_collective_phenomenology": True,
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
            "coalition_detection_status": status,
            "coalition_detection_ready": ready,
            "registry_ready": bool(registry.get("multi_rf_registry_ready", False)),
            "interaction_graph_ready": bool(graph.get("interaction_graph_ready", False)),
            "shared_reference_frame_detection_ready": bool(shared.get("shared_reference_frame_detection_ready", False)),
            "rf_ids": sorted(valid_rf_ids),
            "rf_count": len(valid_rf_ids),
            "coalitions": coalitions,
            "coalition_count": len(coalitions),
            "detected_coalitions": detected,
            "detected_coalition_count": len(detected),
            "blocked_coalitions": blocked,
            "blocked_coalition_count": len(blocked),
            "invalid_coalitions": invalid,
            "invalid_coalition_count": len(invalid),
            "thresholds": thresholds,
            "coalition_policy": policy,
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
            path = self.output_dir / "latest_coalition_detection.json"
            payload = deepcopy(result)
            payload.update({"persisted": True, "output_path": str(path)})
            self._atomic_write(path, payload, fs_context)
            result.update({"persisted": True, "output_path": str(path)})
        return result
