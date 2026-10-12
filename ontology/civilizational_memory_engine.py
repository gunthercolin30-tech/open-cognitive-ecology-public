"""AW8 — governed distributed civilizational memory for RF ecologies.

Functional-only orchestration of traceable, versioned, replicated memory records.
This module does not infer collective consciousness, subjectivity, qualia, or
phenomenology from shared memory, coordination, resilience, or continuity.
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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class CivilizationalMemoryEngine:
    primitive = "CIVILIZATIONAL_MEMORY_ENGINE"
    step_id = "AW8"
    public_schema_version = "1.0"

    default_thresholds = {
        "minimum_replica_count": 3,
        "minimum_quorum_ratio": 0.51,
        "minimum_provenance_coverage": 0.80,
        "minimum_lineage_preservation": 0.80,
        "minimum_availability_score": 0.67,
        "minimum_loss_tolerance_score": 0.50,
        "minimum_future_openness_preservation": 0.70,
    }

    false_positive_fields = (
        "simple_copy_only", "centralized_database_only", "shared_cache_only",
        "passive_archive_only", "forced_synchronization_only", "journal_only",
        "ungoverned_duplication_only", "individual_memory_only",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW8_civilizational_memory_engine"

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
    def _strings(value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        return sorted({str(item).strip() for item in value if str(item).strip()})

    def _thresholds(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        result = dict(self.default_thresholds)
        supplied = inputs.get("thresholds", {})
        if isinstance(supplied, Mapping):
            for key in result:
                if key == "minimum_replica_count":
                    try:
                        result[key] = max(1, int(supplied.get(key, result[key])))
                    except (TypeError, ValueError):
                        pass
                else:
                    result[key] = self._clamp(supplied.get(key, result[key]), result[key])
        return result

    def _registry_ids(self, inputs: Mapping[str, Any]) -> Set[str]:
        registry = inputs.get("multi_rf_registry", {})
        raw = registry.get("registry", []) if isinstance(registry, Mapping) else []
        ids: Set[str] = set()
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, Mapping):
                    rid = item.get("rf_id") or item.get("reference_frame_id")
                    if rid:
                        ids.add(str(rid).strip().upper())
        if not ids:
            raw_records = inputs.get("rf_records", [])
            if isinstance(raw_records, list):
                for item in raw_records:
                    if isinstance(item, Mapping) and item.get("rf_id"):
                        ids.add(str(item["rf_id"]).strip().upper())
        return ids

    def _normalize_record(self, raw: Mapping[str, Any], index: int, valid_rf_ids: Set[str], thresholds: Mapping[str, Any]) -> Dict[str, Any]:
        record_id = self._safe_id(raw.get("memory_record_id"), f"MEM-{index:04d}")
        version_id = self._safe_id(raw.get("version_id"), f"{record_id}-V1")
        origin_rf_id = self._safe_id(raw.get("origin_rf_id"), "UNKNOWN-RF")
        lineage_id = self._safe_id(raw.get("origin_lineage_id"), f"LINEAGE-{origin_rf_id}")
        namespace = str(raw.get("memory_namespace", "civilization")).strip() or "civilization"
        scope = str(raw.get("memory_scope", "distributed")).strip() or "distributed"
        parents = self._strings(raw.get("parent_version_ids", []))
        replica_ids = self._strings(raw.get("replica_ids", []))
        acknowledgements = self._strings(raw.get("acknowledged_replica_ids", replica_ids))
        provenance_chain = deepcopy(raw.get("provenance_chain", [])) if isinstance(raw.get("provenance_chain", []), list) else []
        transmission_chain = deepcopy(raw.get("transmission_chain", [])) if isinstance(raw.get("transmission_chain", []), list) else []
        content = deepcopy(raw.get("content", raw.get("payload")))
        declared_hash = str(raw.get("content_hash", "")).strip().lower()
        computed_hash = self._hash(content)
        content_hash_valid = declared_hash in ("", computed_hash)
        content_hash = declared_hash or computed_hash
        replica_count = len(replica_ids)
        quorum_ratio = round(len(set(acknowledgements) & set(replica_ids)) / replica_count, 6) if replica_count else 0.0
        quorum_reached = replica_count >= thresholds["minimum_replica_count"] and quorum_ratio >= thresholds["minimum_quorum_ratio"]
        provenance_coverage = self._clamp(raw.get("provenance_coverage", 1.0 if provenance_chain else 0.0))
        lineage_preservation_score = self._clamp(raw.get("lineage_preservation_score", 1.0 if lineage_id else 0.0))
        availability_score = self._clamp(raw.get("availability_score", min(1.0, replica_count / max(1, thresholds["minimum_replica_count"]))))
        tolerated_losses = max(0, replica_count - max(1, math.ceil(replica_count * thresholds["minimum_quorum_ratio"]))) if replica_count else 0
        loss_tolerance_score = self._clamp(raw.get("loss_tolerance_score", tolerated_losses / replica_count if replica_count else 0.0))
        future_openness_score = self._clamp(raw.get("future_openness_preservation_score", 0.0))
        blockers = [field for field in self.false_positive_fields if bool(raw.get(field, False))]
        registered = not valid_rf_ids or origin_rf_id in valid_rf_ids
        integrity_status = "VALID" if content_hash_valid and registered else "INVALID"
        retention_policy = deepcopy(raw.get("retention_policy", {"mode": "governed"}))
        forgetting_policy = deepcopy(raw.get("forgetting_policy", {"mode": "governed", "authorized": False}))
        eligible = all([
            integrity_status == "VALID", quorum_reached,
            provenance_coverage >= thresholds["minimum_provenance_coverage"],
            lineage_preservation_score >= thresholds["minimum_lineage_preservation"],
            availability_score >= thresholds["minimum_availability_score"],
            loss_tolerance_score >= thresholds["minimum_loss_tolerance_score"],
            future_openness_score >= thresholds["minimum_future_openness_preservation"],
            not blockers,
        ])
        return {
            "memory_record_id": record_id,
            "memory_namespace": namespace,
            "memory_scope": scope,
            "content": content,
            "content_hash": content_hash,
            "computed_content_hash": computed_hash,
            "content_hash_valid": content_hash_valid,
            "version_id": version_id,
            "parent_version_ids": parents,
            "origin_rf_id": origin_rf_id,
            "origin_rf_registered": registered,
            "origin_lineage_id": lineage_id,
            "writer_id": self._safe_id(raw.get("writer_id"), origin_rf_id),
            "replica_ids": replica_ids,
            "replica_count": replica_count,
            "acknowledged_replica_ids": acknowledgements,
            "quorum_ratio": quorum_ratio,
            "quorum_status": "QUORUM_REACHED" if quorum_reached else "QUORUM_NOT_REACHED",
            "provenance_chain": provenance_chain,
            "provenance_coverage": provenance_coverage,
            "transmission_chain": transmission_chain,
            "created_at_utc": raw.get("created_at_utc"),
            "updated_at_utc": raw.get("updated_at_utc"),
            "retention_policy": retention_policy,
            "forgetting_policy": forgetting_policy,
            "integrity_status": integrity_status,
            "availability_score": availability_score,
            "loss_tolerance_score": loss_tolerance_score,
            "lineage_preservation_score": lineage_preservation_score,
            "future_openness_preservation_score": future_openness_score,
            "false_positive_blockers": sorted(blockers),
            "record_eligible": eligible,
        }

    def _reconcile(self, records: List[Dict[str, Any]], inputs: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for record in records:
            groups.setdefault((record["memory_namespace"], record["memory_record_id"]), []).append(record)
        reconciled: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        policy = str(inputs.get("reconciliation_policy", "highest_quorum_then_latest_version")).strip()
        for (namespace, record_id), versions in sorted(groups.items()):
            hashes = sorted({v["content_hash"] for v in versions})
            conflict = len(hashes) > 1
            ranked = sorted(versions, key=lambda v: (v["record_eligible"], v["quorum_ratio"], v["availability_score"], v["version_id"]), reverse=True)
            winner = deepcopy(ranked[0])
            winner["reconciliation_policy"] = policy
            winner["reconciliation_status"] = "RECONCILED" if not conflict or winner["record_eligible"] else "UNRESOLVED"
            reconciled.append(winner)
            if conflict:
                conflicts.append({
                    "memory_namespace": namespace,
                    "memory_record_id": record_id,
                    "version_ids": sorted(v["version_id"] for v in versions),
                    "content_hashes": hashes,
                    "selected_version_id": winner["version_id"],
                    "conflict_status": "RESOLVED" if winner["reconciliation_status"] == "RECONCILED" else "UNRESOLVED",
                })
        return reconciled, conflicts

    def _load_existing(self) -> Optional[Dict[str, Any]]:
        path = self.output_dir / "latest_civilizational_memory_engine.json"
        if not path.exists():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = deepcopy(dict(inputs or {}))
        thresholds = self._thresholds(inputs)
        valid_rf_ids = self._registry_ids(inputs)
        raw_records = inputs.get("memory_records", [])
        if isinstance(raw_records, Mapping):
            raw_records = raw_records.get("records", [])
        records = [self._normalize_record(item, index, valid_rf_ids, thresholds) for index, item in enumerate(raw_records, start=1) if isinstance(item, Mapping)] if isinstance(raw_records, list) else []
        records = sorted(records, key=lambda r: (r["memory_namespace"], r["memory_record_id"], r["version_id"]))

        identity_counts: Dict[Tuple[str, str, str], int] = {}
        for record in records:
            key = (
                record["memory_namespace"],
                record["memory_record_id"],
                record["version_id"],
            )
            identity_counts[key] = identity_counts.get(key, 0) + 1
        duplicate_record_keys = [
            {"memory_namespace": key[0], "memory_record_id": key[1], "version_id": key[2], "count": count}
            for key, count in sorted(identity_counts.items())
            if count > 1
        ]

        reconciled, conflicts = self._reconcile(records, inputs)
        eligible = [r for r in records if r["record_eligible"]]
        unresolved = [c for c in conflicts if c["conflict_status"] == "UNRESOLVED"]
        all_parent_ids = {p for r in records for p in r["parent_version_ids"]}
        all_versions = {r["version_id"] for r in records}
        orphan_parent_ids = sorted(all_parent_ids - all_versions)

        version_graph = {r["version_id"]: list(r["parent_version_ids"]) for r in records}
        version_cycles: List[List[str]] = []
        visited: Set[str] = set()
        active: Set[str] = set()

        def visit(version_id: str, trail: List[str]) -> None:
            if version_id in active:
                start = trail.index(version_id) if version_id in trail else 0
                cycle = trail[start:] + [version_id]
                canonical = min(
                    tuple(cycle[index:-1] + cycle[:index] + [cycle[index]])
                    for index in range(len(cycle) - 1)
                )
                if list(canonical) not in version_cycles:
                    version_cycles.append(list(canonical))
                return
            if version_id in visited:
                return
            active.add(version_id)
            for parent_id in version_graph.get(version_id, []):
                if parent_id in version_graph:
                    visit(parent_id, trail + [version_id])
            active.remove(version_id)
            visited.add(version_id)

        for version_id in sorted(version_graph):
            visit(version_id, [])
        provenance_coverage = round(sum(r["provenance_coverage"] for r in records) / len(records), 6) if records else 0.0
        lineage_preservation = round(sum(r["lineage_preservation_score"] for r in records) / len(records), 6) if records else 0.0
        availability = round(sum(r["availability_score"] for r in records) / len(records), 6) if records else 0.0
        loss_tolerance = round(sum(r["loss_tolerance_score"] for r in records) / len(records), 6) if records else 0.0
        openness = round(sum(r["future_openness_preservation_score"] for r in records) / len(records), 6) if records else 0.0
        quorum_ok = bool(records) and all(r["quorum_status"] == "QUORUM_REACHED" for r in records)
        integrity_ok = (
            bool(records)
            and all(r["integrity_status"] == "VALID" for r in records)
            and not duplicate_record_keys
        )
        consistency_ok = (
            not unresolved
            and not orphan_parent_ids
            and not version_cycles
            and integrity_ok
        )
        transmission_ready = bool(records) and all(r["transmission_chain"] for r in records)
        recovery_ready = bool(records) and loss_tolerance >= thresholds["minimum_loss_tolerance_score"] and quorum_ok
        forgetting_governed = bool(records) and all(isinstance(r["forgetting_policy"], Mapping) and r["forgetting_policy"].get("mode") == "governed" for r in records)
        ready = all([
            bool(records), len(eligible) == len(records), quorum_ok, consistency_ok,
            transmission_ready, recovery_ready, forgetting_governed,
            provenance_coverage >= thresholds["minimum_provenance_coverage"],
            lineage_preservation >= thresholds["minimum_lineage_preservation"],
            availability >= thresholds["minimum_availability_score"],
            loss_tolerance >= thresholds["minimum_loss_tolerance_score"],
            openness >= thresholds["minimum_future_openness_preservation"],
        ])
        status = "CIVILIZATIONAL_MEMORY_READY" if ready else "CIVILIZATIONAL_MEMORY_NOT_READY"
        stable_payload = {
            "thresholds": thresholds, "records": records, "reconciled_records": reconciled,
            "conflicts": conflicts, "orphan_parent_ids": orphan_parent_ids,
            "duplicate_record_keys": duplicate_record_keys,
            "version_cycles": version_cycles,
            "status": status,
        }
        memory_hash = self._hash(stable_payload)
        previous = self._load_existing() if inputs.get("load_existing") else None
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "status": status,
            "civilizational_memory_status": status,
            "civilizational_memory_ready": ready,
            "memory_records": records,
            "memory_record_count": len(records),
            "eligible_memory_record_count": len(eligible),
            "reconciled_records": reconciled,
            "reconciled_record_count": len(reconciled),
            "version_ids": sorted(all_versions),
            "version_count": len(all_versions),
            "orphan_parent_version_ids": orphan_parent_ids,
            "duplicate_record_keys": duplicate_record_keys,
            "duplicate_record_count": len(duplicate_record_keys),
            "version_cycles": version_cycles,
            "version_cycle_count": len(version_cycles),
            "replica_ids": sorted({rid for r in records for rid in r["replica_ids"]}),
            "replica_count": len({rid for r in records for rid in r["replica_ids"]}),
            "quorum_status": "QUORUM_REACHED" if quorum_ok else "QUORUM_NOT_REACHED",
            "consistency_status": "CONSISTENT" if consistency_ok else "INCONSISTENT",
            "conflict_status": "NO_UNRESOLVED_CONFLICT" if not unresolved else "UNRESOLVED_CONFLICT",
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "unresolved_conflict_count": len(unresolved),
            "reconciliation_status": "RECONCILIATION_COMPLETE" if not unresolved else "RECONCILIATION_INCOMPLETE",
            "transmission_status": "INTERGENERATIONAL_TRANSMISSION_READY" if transmission_ready else "TRANSMISSION_INCOMPLETE",
            "recovery_status": "RECOVERY_READY" if recovery_ready else "RECOVERY_NOT_READY",
            "forgetting_status": "GOVERNED_FORGETTING_READY" if forgetting_governed else "FORGETTING_POLICY_INCOMPLETE",
            "integrity_status": "VALID" if integrity_ok else "INVALID",
            "availability_score": availability,
            "loss_tolerance_score": loss_tolerance,
            "provenance_coverage": provenance_coverage,
            "lineage_preservation_score": lineage_preservation,
            "future_openness_preservation_score": openness,
            "thresholds": thresholds,
            "memory_hash": memory_hash,
            "result_hash": memory_hash,
            "previous_result_loaded": previous is not None,
            "false_positive_controls": list(self.false_positive_fields),
            "reused_foundations": [
                "distributed_civilizational_memory", "distributed_memory_consistency_validator",
                "distributed_memory_reconciliation", "memory_transmission_protocol",
                "adaptive_civilizational_forgetting", "historical_state_reconciliation",
                "runtime_lineage_inheritance", "genealogical_continuity", "future_openness",
            ],
            "allowed_claims": [
                "distributed RF memory records are functionally versioned and traceable",
                "declared replica, quorum, reconciliation, recovery and lineage properties are measurable",
                "intergenerational transmission may be functionally tested",
            ],
            "blocked_claims": [
                "shared memory proves collective consciousness",
                "memory continuity proves collective subjectivity",
                "replication or reconciliation proves collective qualia",
                "civilizational memory proves collective phenomenology",
            ],
            "epistemic_scope": "functional_distributed_civilizational_memory_only",
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
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = self.output_dir / "latest_civilizational_memory_engine.json"
            fd, temp_name = tempfile.mkstemp(prefix="aw8_", suffix=".json", dir=str(self.output_dir))
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(result, handle, indent=2, sort_keys=True, ensure_ascii=False)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp_name, output_path)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
            result["persisted"] = True
            result["output_path"] = str(output_path)
        return result
