"""AW3 — shared_reference_frame_detector.

Functional detector for candidate shared reference-frame structures across
multiple registered RFs. Detection requires convergent evidence and explicit
false-positive controls. Similarity, interaction, alignment, translation, or a
common controller are never sufficient on their own.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class SharedReferenceFrameDetector:
    primitive = "SHARED_REFERENCE_FRAME_DETECTOR"
    step_id = "AW3"
    public_schema_version = "1.0"
    output_dir = ROOT / "rf_ecology" / "AW3_shared_reference_frame_detector"

    default_thresholds = {
        "minimum_similarity": 0.65,
        "minimum_alignment": 0.65,
        "minimum_symbolic_reference": 0.60,
        "minimum_structural_invariance": 0.60,
        "minimum_reproducibility": 0.60,
        "minimum_evidence_quality": 0.50,
        "minimum_shared_score": 0.65,
        "minimum_convergent_dimensions": 4,
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW3_shared_reference_frame_detector"

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
    def _string_list(value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        return sorted({str(item).strip() for item in value if str(item).strip()})

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

    def _profiles(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        raw = inputs.get("rf_profiles", {})
        if isinstance(raw, list):
            raw = {
                str(item.get("rf_id", "")): item
                for item in raw
                if isinstance(item, Mapping) and item.get("rf_id")
            }
        if not isinstance(raw, Mapping):
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        for key, value in raw.items():
            if isinstance(value, Mapping):
                out[str(key).strip().upper()] = deepcopy(dict(value))
        return out

    def _pair_evidence(self, a: str, b: str, profiles: Dict[str, Dict[str, Any]], inputs: Dict[str, Any]) -> Dict[str, Any]:
        pair_key = "|".join(sorted((a, b)))
        explicit = inputs.get("pair_evidence", {})
        canonical_explicit: Dict[str, Any] = {}
        if isinstance(explicit, Mapping):
            for raw_key, raw_value in explicit.items():
                parts = [
                    str(part).strip().upper()
                    for part in str(raw_key).split("|")
                    if str(part).strip()
                ]
                if len(parts) == 2 and all(parts):
                    canonical_key = "|".join(sorted(parts))
                    canonical_explicit[canonical_key] = raw_value
        item = canonical_explicit.get(pair_key, {})
        if not isinstance(item, Mapping):
            item = {}
        pa, pb = profiles.get(a, {}), profiles.get(b, {})

        features_a = set(self._string_list(pa.get("features", [])))
        features_b = set(self._string_list(pb.get("features", [])))
        symbols_a = set(self._string_list(pa.get("symbols", [])))
        symbols_b = set(self._string_list(pb.get("symbols", [])))
        invariants_a = set(self._string_list(pa.get("invariants", [])))
        invariants_b = set(self._string_list(pb.get("invariants", [])))

        feature_union = features_a | features_b
        symbol_union = symbols_a | symbols_b
        invariant_union = invariants_a | invariants_b

        similarity_default = len(features_a & features_b) / len(feature_union) if feature_union else 0.0
        symbolic_default = len(symbols_a & symbols_b) / len(symbol_union) if symbol_union else 0.0
        invariant_default = len(invariants_a & invariants_b) / len(invariant_union) if invariant_union else 0.0

        evidence = {
            "pair_id": pair_key,
            "rf_ids": [a, b],
            "similarity": self._clamp(item.get("similarity", similarity_default)),
            "alignment": self._clamp(item.get("alignment", 0.0)),
            "symbolic_reference": self._clamp(item.get("symbolic_reference", symbolic_default)),
            "structural_invariance": self._clamp(item.get("structural_invariance", invariant_default)),
            "reproducibility": self._clamp(item.get("reproducibility", 0.0)),
            "evidence_quality": self._clamp(item.get("evidence_quality", 0.0)),
            "translation_only": bool(item.get("translation_only", False)),
            "common_controller": bool(item.get("common_controller", False)),
            "copy_or_clone_explanation": bool(item.get("copy_or_clone_explanation", False)),
            "lexical_overlap_only": bool(item.get("lexical_overlap_only", False)),
            "single_observation_only": bool(item.get("single_observation_only", False)),
            "source_refs": self._string_list(item.get("source_refs", [])),
        }
        evidence["evidence_hash"] = self._hash(evidence)
        return evidence

    def _thresholds(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(self.default_thresholds)
        supplied = inputs.get("thresholds", {})
        if isinstance(supplied, Mapping):
            for key in result:
                if key == "minimum_convergent_dimensions":
                    try:
                        result[key] = max(1, min(6, int(supplied.get(key, result[key]))))
                    except (TypeError, ValueError):
                        pass
                else:
                    result[key] = self._clamp(supplied.get(key, result[key]), result[key])
        return result

    def _evaluate_pair(self, evidence: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
        dimensions = {
            "similarity": evidence["similarity"] >= thresholds["minimum_similarity"],
            "alignment": evidence["alignment"] >= thresholds["minimum_alignment"],
            "symbolic_reference": evidence["symbolic_reference"] >= thresholds["minimum_symbolic_reference"],
            "structural_invariance": evidence["structural_invariance"] >= thresholds["minimum_structural_invariance"],
            "reproducibility": evidence["reproducibility"] >= thresholds["minimum_reproducibility"],
            "evidence_quality": evidence["evidence_quality"] >= thresholds["minimum_evidence_quality"],
        }
        convergent = sum(dimensions.values())
        scores = [
            evidence["similarity"], evidence["alignment"], evidence["symbolic_reference"],
            evidence["structural_invariance"], evidence["reproducibility"], evidence["evidence_quality"],
        ]
        shared_score = round(sum(scores) / len(scores), 6)
        blockers = [
            name for name in (
                "translation_only", "common_controller", "copy_or_clone_explanation",
                "lexical_overlap_only", "single_observation_only",
            ) if evidence[name]
        ]
        detected = bool(
            shared_score >= thresholds["minimum_shared_score"]
            and convergent >= thresholds["minimum_convergent_dimensions"]
            and not blockers
        )
        status = "SHARED_REFERENCE_FRAME_DETECTED_FUNCTIONALLY" if detected else "NO_SHARED_REFERENCE_FRAME_DETECTED"
        return {
            "pair_id": evidence["pair_id"],
            "rf_ids": evidence["rf_ids"],
            "status": status,
            "detected": detected,
            "shared_score": shared_score,
            "convergent_dimension_count": convergent,
            "dimension_pass": dimensions,
            "false_positive_blockers": blockers,
            "evidence": evidence,
        }

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
        path = self.output_dir / "latest_shared_reference_frame_detection.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return None
        return payload if isinstance(payload, dict) and isinstance(payload.get("pair_results"), list) else None

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False, fs_context: Any = None) -> Dict[str, Any]:
        safe_inputs = deepcopy(inputs) if isinstance(inputs, dict) else {}
        load_existing = bool(safe_inputs.get("load_existing", False))
        existing = self._load() if load_existing else None
        if existing is not None:
            safe_inputs = dict(safe_inputs)
            safe_inputs.setdefault("pair_evidence", {
                item["pair_id"]: item["evidence"] for item in existing.get("pair_results", [])
                if isinstance(item, Mapping) and isinstance(item.get("evidence"), Mapping)
            })

        registry = self._registry(safe_inputs)
        graph = self._graph(safe_inputs, registry)
        rf_ids = sorted({
            str(item.get("rf_id", "")).strip().upper()
            for item in registry.get("registry", [])
            if isinstance(item, Mapping) and item.get("rf_id")
        })
        profiles = self._profiles(safe_inputs)
        thresholds = self._thresholds(safe_inputs)

        pair_results = [
            self._evaluate_pair(self._pair_evidence(a, b, profiles, safe_inputs), thresholds)
            for a, b in combinations(rf_ids, 2)
        ]
        detected_pairs = [item for item in pair_results if item["detected"]]
        blocked_pairs = [item for item in pair_results if item["false_positive_blockers"]]
        evidence_complete = bool(pair_results) and all(
            item["evidence"]["evidence_quality"] > 0.0 for item in pair_results
        )
        ready = bool(
            registry.get("multi_rf_registry_ready", False)
            and graph.get("interaction_graph_ready", False)
            and len(rf_ids) >= 2
            and evidence_complete
        )
        status = "SHARED_REFERENCE_FRAME_DETECTION_READY" if ready else "SHARED_REFERENCE_FRAME_DETECTION_INCOMPLETE"

        detection_hash = self._hash({
            "rf_ids": rf_ids,
            "thresholds": thresholds,
            "pair_results": pair_results,
        })
        guards = {
            "epistemic_scope": "functional_shared_reference_frame_detection_only",
            "similarity_alone_is_insufficient": True,
            "alignment_alone_is_insufficient": True,
            "interaction_alone_is_insufficient": True,
            "translation_alone_is_insufficient": True,
            "common_controller_is_false_positive_risk": True,
            "shared_rf_does_not_prove_shared_experience": True,
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
            "shared_reference_frame_detection_status": status,
            "shared_reference_frame_detection_ready": ready,
            "registry_ready": bool(registry.get("multi_rf_registry_ready", False)),
            "interaction_graph_ready": bool(graph.get("interaction_graph_ready", False)),
            "rf_ids": rf_ids,
            "rf_count": len(rf_ids),
            "pair_results": pair_results,
            "pair_count": len(pair_results),
            "detected_pairs": detected_pairs,
            "detected_pair_count": len(detected_pairs),
            "blocked_pairs": blocked_pairs,
            "blocked_pair_count": len(blocked_pairs),
            "evidence_complete": evidence_complete,
            "thresholds": thresholds,
            "detection_hash": detection_hash,
            "epistemic_guards": guards,
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
            path = self.output_dir / "latest_shared_reference_frame_detection.json"
            payload = deepcopy(result)
            payload["persisted"] = True
            payload["output_path"] = str(path)
            self._atomic_write(path, payload, fs_context)
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
