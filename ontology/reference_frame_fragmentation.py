"""AW7 — functional reference-frame fragmentation."""
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


class ReferenceFrameFragmentation:
    primitive = "REFERENCE_FRAME_FRAGMENTATION"
    step_id = "AW7"
    public_schema_version = "1.0"

    default_thresholds = {
        "minimum_lineage_traceability": 0.80,
        "minimum_partial_continuity": 0.50,
        "maximum_partial_continuity": 0.95,
        "minimum_descendant_divergence": 0.60,
        "minimum_source_unity_reduction": 0.60,
        "minimum_information_redistribution": 0.55,
        "minimum_functional_impact": 0.55,
        "minimum_temporal_stability": 0.60,
        "minimum_evidence_quality": 0.65,
        "maximum_information_loss": 0.40,
        "minimum_descendant_contribution": 0.35,
        "minimum_observations": 3,
        "minimum_convergent_dimensions": 14,
        "minimum_fragmentation_score": 0.65,
    }

    false_positive_fields = (
        "exact_duplication", "clone_only", "replication_only", "backup_only",
        "logical_partition_only", "technical_sharding_only", "migration_only",
        "multi_host_deployment_only", "degradation_only",
        "progressive_diversification_only", "succession_only", "temporary_fork",
        "test_branch_only", "renamed_copy", "load_balancing_only",
        "modularization_without_rupture",
    )

    score_fields = (
        "lineage_traceability_score", "descendant_divergence_score",
        "source_unity_reduction_score", "information_redistribution_score",
        "functional_impact_score", "temporal_stability_score",
        "evidence_quality", "reversibility_score",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW7_reference_frame_fragmentation"

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
        raw = inputs.get("fragmentation_candidates", inputs.get("reference_frame_fragmentations", []))
        if isinstance(raw, Mapping):
            raw = raw.get("fragmentations", raw.get("candidates", []))
        return [item for item in raw if isinstance(item, Mapping)] if isinstance(raw, list) else []

    def _normalize_candidate(self, item: Mapping[str, Any], index: int, valid_rf_ids: Set[str], thresholds: Dict[str, Any]) -> Dict[str, Any]:
        source_id = self._safe_id(item.get("source_rf_id"), f"AW7-SOURCE-{index:04d}")
        source_registered = source_id in valid_rf_ids
        raw_descendants = item.get("descendant_rf_ids", item.get("child_rf_ids", []))
        descendant_ids = sorted({str(v).strip().upper() for v in raw_descendants if str(v).strip()}) if isinstance(raw_descendants, list) else []
        missing_descendants = sorted(set(descendant_ids) - valid_rf_ids)
        valid_descendants = sorted(set(descendant_ids) & valid_rf_ids)
        descendants_distinct = len(valid_descendants) >= 2 and source_id not in valid_descendants

        start, start_ok = self._time(item.get("valid_from_utc"))
        end, end_ok = self._time(item.get("valid_until_utc"))
        temporal_order_ok = True
        if start and end and start_ok and end_ok:
            temporal_order_ok = datetime.fromisoformat(end.replace("Z", "+00:00")) >= datetime.fromisoformat(start.replace("Z", "+00:00"))

        scores = {name: self._clamp(item.get(name, 0.0)) for name in self.score_fields}
        information_loss_score = self._clamp(item.get("information_loss_score", 1.0), 1.0)
        information_preservation_score = round(1.0 - information_loss_score, 6)

        raw_continuity = item.get("descendant_continuity_scores", {})
        continuity = {d: self._clamp(raw_continuity.get(d, 0.0)) for d in valid_descendants} if isinstance(raw_continuity, Mapping) else {d: 0.0 for d in valid_descendants}
        minimum_partial_continuity = min(continuity.values()) if continuity else 0.0
        maximum_partial_continuity = max(continuity.values()) if continuity else 0.0
        mean_partial_continuity = round(sum(continuity.values()) / len(continuity), 6) if continuity else 0.0

        raw_contrib = item.get("descendant_contributions", {})
        contributions = {d: self._clamp(raw_contrib.get(d, 0.0)) for d in valid_descendants} if isinstance(raw_contrib, Mapping) else {d: 0.0 for d in valid_descendants}
        minimum_descendant_contribution = min(contributions.values()) if contributions else 0.0
        mean_descendant_contribution = round(sum(contributions.values()) / len(contributions), 6) if contributions else 0.0

        try:
            observation_count = max(0, int(item.get("observation_count", 0)))
        except (TypeError, ValueError):
            observation_count = 0

        blockers = [name for name in self.false_positive_fields if bool(item.get(name, False))]
        rival = str(item.get("rival_explanation", "") or "").strip()
        rival_sufficient = bool(item.get("rival_explanation_sufficient", False))
        if rival_sufficient:
            blockers.append("sufficient_rival_explanation")

        continuity_band_valid = (
            minimum_partial_continuity >= thresholds["minimum_partial_continuity"]
            and maximum_partial_continuity <= thresholds["maximum_partial_continuity"]
        )
        dimension_pass = {
            "source_registered": source_registered,
            "descendants_registered": not missing_descendants and len(valid_descendants) >= 2,
            "descendants_distinct": descendants_distinct,
            "lineage_traceability": scores["lineage_traceability_score"] >= thresholds["minimum_lineage_traceability"],
            "partial_continuity": continuity_band_valid,
            "descendant_divergence": scores["descendant_divergence_score"] >= thresholds["minimum_descendant_divergence"],
            "source_unity_reduction": scores["source_unity_reduction_score"] >= thresholds["minimum_source_unity_reduction"],
            "information_redistribution": scores["information_redistribution_score"] >= thresholds["minimum_information_redistribution"],
            "functional_impact": scores["functional_impact_score"] >= thresholds["minimum_functional_impact"],
            "temporal_stability": scores["temporal_stability_score"] >= thresholds["minimum_temporal_stability"],
            "evidence_quality": scores["evidence_quality"] >= thresholds["minimum_evidence_quality"],
            "information_loss": information_loss_score <= thresholds["maximum_information_loss"],
            "descendant_contribution": minimum_descendant_contribution >= thresholds["minimum_descendant_contribution"],
            "observations": observation_count >= thresholds["minimum_observations"],
        }
        convergent_dimension_count = sum(bool(v) for v in dimension_pass.values())
        fragmentation_score = round((
            scores["lineage_traceability_score"] + mean_partial_continuity
            + scores["descendant_divergence_score"] + scores["source_unity_reduction_score"]
            + scores["information_redistribution_score"] + scores["functional_impact_score"]
            + scores["temporal_stability_score"] + scores["evidence_quality"]
            + information_preservation_score + minimum_descendant_contribution
        ) / 10.0, 6)

        detected = bool(
            all(dimension_pass.values())
            and start_ok and end_ok and temporal_order_ok
            and convergent_dimension_count >= thresholds["minimum_convergent_dimensions"]
            and fragmentation_score >= thresholds["minimum_fragmentation_score"]
            and not blockers
        )

        record = {
            "fragmentation_id": self._safe_id(item.get("fragmentation_id"), f"AW7-FRAGMENTATION-{index:04d}"),
            "source_rf_id": source_id,
            "source_registered": source_registered,
            "descendant_rf_ids": valid_descendants,
            "descendant_count": len(valid_descendants),
            "missing_descendant_rf_ids": missing_descendants,
            "descendants_distinct": descendants_distinct,
            "fragmentation_status": "REFERENCE_FRAME_FRAGMENTATION_DETECTED_FUNCTIONALLY" if detected else "NO_REFERENCE_FRAME_FRAGMENTATION_DETECTED",
            "detected": detected,
            **scores,
            "information_loss_score": information_loss_score,
            "information_preservation_score": information_preservation_score,
            "descendant_continuity_scores": continuity,
            "minimum_partial_continuity": minimum_partial_continuity,
            "maximum_partial_continuity": maximum_partial_continuity,
            "mean_partial_continuity": mean_partial_continuity,
            "descendant_contributions": contributions,
            "minimum_descendant_contribution": minimum_descendant_contribution,
            "mean_descendant_contribution": mean_descendant_contribution,
            "dimension_pass": dimension_pass,
            "convergent_dimension_count": convergent_dimension_count,
            "fragmentation_score": fragmentation_score,
            "observation_count": observation_count,
            "valid_from_utc": start,
            "valid_until_utc": end,
            "temporal_order_valid": start_ok and end_ok and temporal_order_ok,
            "lineage_edges": [{"source_rf_id": source_id, "descendant_rf_id": d} for d in valid_descendants],
            "redistributed_information_ids": self._string_list(item.get("redistributed_information_ids", [])),
            "lost_information_ids": self._string_list(item.get("lost_information_ids", [])),
            "source_status_after_fragmentation": str(item.get("source_status_after_fragmentation", "FUNCTIONALLY_FRAGMENTED")).strip().upper(),
            "reversible": bool(item.get("reversible", scores["reversibility_score"] >= 0.60)),
            "recombination_reference": str(item.get("recombination_reference", "")).strip() or None,
            "source_refs": self._string_list(item.get("source_refs", [])),
            "false_positive_blockers": sorted(set(blockers)),
            "rival_explanation": rival or None,
            "rival_explanation_sufficient": rival_sufficient,
            "functional_only": True,
            "phenomenology_claim_allowed": False,
        }
        record["fragmentation_hash"] = self._hash(record)
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
        path = self.output_dir / "latest_reference_frame_fragmentation.json"
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
        fragmentations = [
            self._normalize_candidate(item, index, valid_rf_ids, thresholds)
            for index, item in enumerate(self._items(inputs), start=1)
        ]
        detected = [item for item in fragmentations if item["detected"]]
        ready = bool(registry.get("registry_ready", registry.get("multi_rf_registry_ready", False)) and fragmentations)
        status = "REFERENCE_FRAME_FRAGMENTATION_READY" if ready else "REFERENCE_FRAME_FRAGMENTATION_INCOMPLETE"
        previous = self._load() if bool(inputs.get("load_existing", False)) else None
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": status,
            "reference_frame_fragmentation_status": status,
            "reference_frame_fragmentation_ready": ready,
            "fragmentation_count": len(fragmentations),
            "detected_fragmentation_count": len(detected),
            "fragmentations": fragmentations,
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
            "epistemic_scope": "FUNCTIONAL_REFERENCE_FRAME_FRAGMENTATION_ONLY",
        }
        stable = deepcopy(result)
        stable.pop("generated_at_utc", None)
        result["result_hash"] = self._hash(stable)
        if persist:
            path = self.output_dir / "latest_reference_frame_fragmentation.json"
            self._atomic_write(path, result, fs_context)
            result["persisted"] = True
            result["output_path"] = str(path)
        else:
            result["persisted"] = False
            result["output_path"] = None
        return result
