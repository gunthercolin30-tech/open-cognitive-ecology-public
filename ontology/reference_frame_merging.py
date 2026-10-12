"""AW6 — functional reference-frame merging.

A merge is inferred only when distinct registered source RFs give rise to a
registered successor RF with explicit lineage, measurable structural
conservation, bounded information loss, functional continuity, reduced source
independence, and sufficient evidence. Aggregation, coordination, alignment,
copying, migration, replacement, and partial integration are not merges.
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


class ReferenceFrameMerging:
    primitive = "REFERENCE_FRAME_MERGING"
    step_id = "AW6"
    public_schema_version = "1.0"

    default_thresholds = {
        "minimum_compatibility": 0.65,
        "minimum_structural_conservation": 0.70,
        "minimum_functional_continuity": 0.70,
        "minimum_lineage_traceability": 0.80,
        "minimum_source_contribution": 0.45,
        "minimum_source_independence_reduction": 0.60,
        "minimum_temporal_stability": 0.60,
        "minimum_evidence_quality": 0.65,
        "maximum_information_loss": 0.30,
        "minimum_observations": 3,
        "minimum_convergent_dimensions": 8,
        "minimum_merge_score": 0.68,
    }

    false_positive_fields = (
        "aggregation_only",
        "coordination_only",
        "alignment_only",
        "shared_rf_only",
        "coalition_only",
        "copy_or_clone",
        "migration_only",
        "replacement_only",
        "synchronization_only",
        "replication_only",
        "superposition_only",
        "partial_integration_only",
        "encapsulation_only",
        "common_controller",
        "information_exchange_only",
        "succession_without_merge",
    )

    score_fields = (
        "compatibility_score",
        "structural_conservation_score",
        "functional_continuity_score",
        "lineage_traceability_score",
        "source_independence_reduction_score",
        "temporal_stability_score",
        "evidence_quality",
        "reversibility_score",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW6_reference_frame_merging"

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
        raw = inputs.get("merge_candidates", inputs.get("reference_frame_merges", []))
        if isinstance(raw, Mapping):
            raw = raw.get("merges", raw.get("candidates", []))
        return [x for x in raw if isinstance(x, Mapping)] if isinstance(raw, list) else []

    def _normalize_candidate(
        self,
        item: Mapping[str, Any],
        index: int,
        valid_rf_ids: Set[str],
        thresholds: Dict[str, Any],
    ) -> Dict[str, Any]:
        raw_sources = item.get("source_rf_ids", item.get("rf_ids", []))
        source_ids = sorted({str(x).strip().upper() for x in raw_sources if str(x).strip()}) if isinstance(raw_sources, list) else []
        missing_sources = sorted(set(source_ids) - valid_rf_ids)
        valid_sources = sorted(set(source_ids) & valid_rf_ids)
        successor_id = self._safe_id(item.get("successor_rf_id", item.get("resulting_rf_id")), f"AW6-SUCCESSOR-{index:04d}")
        successor_registered = successor_id in valid_rf_ids
        successor_distinct = bool(successor_id and successor_id not in valid_sources)

        start, start_ok = self._time(item.get("valid_from_utc"))
        end, end_ok = self._time(item.get("valid_until_utc"))
        temporal_order_ok = True
        if start and end and start_ok and end_ok:
            temporal_order_ok = datetime.fromisoformat(end.replace("Z", "+00:00")) >= datetime.fromisoformat(start.replace("Z", "+00:00"))

        scores = {name: self._clamp(item.get(name, 0.0)) for name in self.score_fields}
        information_loss_score = self._clamp(item.get("information_loss_score", 1.0), 1.0)

        raw_contrib = item.get("source_contributions", {})
        contributions = {
            source: self._clamp(raw_contrib.get(source, 0.0))
            for source in valid_sources
        } if isinstance(raw_contrib, Mapping) else {source: 0.0 for source in valid_sources}
        minimum_source_contribution = min(contributions.values()) if contributions else 0.0
        mean_source_contribution = round(sum(contributions.values()) / len(contributions), 6) if contributions else 0.0

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

        dimension_pass = {
            "compatibility": scores["compatibility_score"] >= thresholds["minimum_compatibility"],
            "structural_conservation": scores["structural_conservation_score"] >= thresholds["minimum_structural_conservation"],
            "functional_continuity": scores["functional_continuity_score"] >= thresholds["minimum_functional_continuity"],
            "lineage_traceability": scores["lineage_traceability_score"] >= thresholds["minimum_lineage_traceability"],
            "source_contribution": minimum_source_contribution >= thresholds["minimum_source_contribution"],
            "source_independence_reduction": scores["source_independence_reduction_score"] >= thresholds["minimum_source_independence_reduction"],
            "temporal_stability": scores["temporal_stability_score"] >= thresholds["minimum_temporal_stability"],
            "evidence_quality": scores["evidence_quality"] >= thresholds["minimum_evidence_quality"],
            "information_loss": information_loss_score <= thresholds["maximum_information_loss"],
            "observations": observation_count >= thresholds["minimum_observations"],
        }
        convergent_dimension_count = sum(dimension_pass.values())
        information_preservation_score = round(1.0 - information_loss_score, 6)
        merge_score = round((
            scores["compatibility_score"]
            + scores["structural_conservation_score"]
            + scores["functional_continuity_score"]
            + scores["lineage_traceability_score"]
            + minimum_source_contribution
            + scores["source_independence_reduction_score"]
            + scores["temporal_stability_score"]
            + scores["evidence_quality"]
            + information_preservation_score
        ) / 9.0, 6)

        detected = bool(
            len(valid_sources) >= 2
            and not missing_sources
            and successor_registered
            and successor_distinct
            and start_ok and end_ok and temporal_order_ok
            and convergent_dimension_count >= thresholds["minimum_convergent_dimensions"]
            and merge_score >= thresholds["minimum_merge_score"]
            and all(dimension_pass[name] for name in (
                "compatibility", "structural_conservation", "functional_continuity",
                "lineage_traceability", "source_contribution",
                "source_independence_reduction", "temporal_stability",
                "evidence_quality", "information_loss", "observations",
            ))
            and not blockers
        )

        merge_id = self._safe_id(item.get("merge_id"), f"AW6-MERGE-{index:04d}")
        reversible = bool(item.get("reversible", scores["reversibility_score"] >= 0.60))
        record = {
            "merge_id": merge_id,
            "source_rf_ids": valid_sources,
            "source_count": len(valid_sources),
            "missing_source_rf_ids": missing_sources,
            "successor_rf_id": successor_id,
            "successor_registered": successor_registered,
            "successor_distinct": successor_distinct,
            "merge_status": "REFERENCE_FRAME_MERGE_DETECTED_FUNCTIONALLY" if detected else "NO_REFERENCE_FRAME_MERGE_DETECTED",
            "detected": detected,
            **scores,
            "information_loss_score": information_loss_score,
            "information_preservation_score": information_preservation_score,
            "source_contributions": contributions,
            "minimum_source_contribution": minimum_source_contribution,
            "mean_source_contribution": mean_source_contribution,
            "dimension_pass": dimension_pass,
            "convergent_dimension_count": convergent_dimension_count,
            "merge_score": merge_score,
            "observation_count": observation_count,
            "valid_from_utc": start,
            "valid_until_utc": end,
            "temporal_order_valid": start_ok and end_ok and temporal_order_ok,
            "lineage_edges": [{"source_rf_id": source, "successor_rf_id": successor_id} for source in valid_sources],
            "preserved_invariant_ids": self._string_list(item.get("preserved_invariant_ids", [])),
            "lost_information_ids": self._string_list(item.get("lost_information_ids", [])),
            "source_status_after_merge": str(item.get("source_status_after_merge", "TRANSFORMED_INTO_SUCCESSOR")).strip().upper(),
            "reversible": reversible,
            "rollback_reference": str(item.get("rollback_reference", "")).strip() or None,
            "source_refs": self._string_list(item.get("source_refs", [])),
            "false_positive_blockers": sorted(set(blockers)),
            "rival_explanation": rival or None,
            "rival_explanation_sufficient": rival_sufficient,
            "functional_only": True,
            "phenomenology_claim_allowed": False,
        }
        record["merge_hash"] = self._hash(record)
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
        path = self.output_dir / "latest_reference_frame_merging.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False, fs_context: Any = None) -> Dict[str, Any]:
        inputs = deepcopy(inputs) if isinstance(inputs, dict) else {}
        registry = self._registry(inputs)
        valid_rf_ids = {
            str(item.get("rf_id", "")).strip().upper()
            for item in registry.get("registry", [])
            if isinstance(item, Mapping) and str(item.get("rf_id", "")).strip()
        }
        thresholds = self._thresholds(inputs)
        merges = [
            self._normalize_candidate(item, index, valid_rf_ids, thresholds)
            for index, item in enumerate(self._items(inputs), start=1)
        ]
        detected_merges = [item for item in merges if item["detected"]]
        ready = bool(registry.get("registry_ready", registry.get("multi_rf_registry_ready", False)) and merges)
        status = "REFERENCE_FRAME_MERGING_READY" if ready else "REFERENCE_FRAME_MERGING_INCOMPLETE"

        previous = self._load() if bool(inputs.get("load_existing", False)) else None
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": status,
            "reference_frame_merging_status": status,
            "reference_frame_merging_ready": ready,
            "merge_count": len(merges),
            "detected_merge_count": len(detected_merges),
            "merges": merges,
            "thresholds": thresholds,
            "registry_hash": registry.get("registry_hash"),
            "previous_result_loaded": previous is not None,
            "generated_at_utc": self._now(),
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
            "epistemic_scope": "FUNCTIONAL_REFERENCE_FRAME_MERGING_ONLY",
        }
        stable_payload = deepcopy(result)
        stable_payload.pop("generated_at_utc", None)
        result["result_hash"] = self._hash(stable_payload)
        if persist:
            path = self.output_dir / "latest_reference_frame_merging.json"
            self._atomic_write(path, result, fs_context)
            result["persisted"] = True
            result["output_path"] = str(path)
        else:
            result["persisted"] = False
            result["output_path"] = None
        return result
