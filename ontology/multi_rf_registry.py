\
"""
AW1 — multi_rf_registry.

Canonical registry for multiple functional reference frames (RF) in the
Open Cognitive Ecology axis. RF identity is explicitly distinct from
individual, representative, architecture, lineage, host, and node identity.

Registration, interaction, persistence, similarity, or continuity never prove
phenomenology, qualia, subjectivity, individual consciousness, or collective
consciousness.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class MultiRFRegistry:
    """Maintain a canonical, auditable population registry of RF records."""

    primitive = "MULTI_RF_REGISTRY"
    step_id = "AW1"
    public_schema_version = "1.0"
    output_dir = ROOT / "rf_ecology" / "AW1_multi_rf_registry"

    allowed_statuses = {
        "ACTIVE",
        "INACTIVE",
        "REVOKED",
        "MERGED",
        "FRAGMENTED",
        "ARCHIVED",
    }

    allowed_origins = {
        "observed",
        "declared",
        "synthetic",
        "reconstructed",
        "inherited",
        "unknown",
    }

    default_records: List[Dict[str, Any]] = [
        {
            "rf_id": "RF-AW1-ALPHA",
            "display_name": "AW1 Alpha RF",
            "status": "ACTIVE",
            "origin": "synthetic",
            "synthetic": True,
            "lineage_id": "LINEAGE-AW1-ALPHA",
            "architecture_id": "OCE_RF_STAR",
            "individual_id": "INDIVIDUAL-AW1-ALPHA",
            "representative_id": None,
            "node_ids": ["NODE-AW1-LOCAL"],
            "aliases": ["alpha"],
            "parent_rf_ids": [],
            "successor_rf_ids": [],
            "evidence_refs": ["ecology_blueprint"],
            "metadata": {"functional_only": True},
        },
        {
            "rf_id": "RF-AW1-BETA",
            "display_name": "AW1 Beta RF",
            "status": "ACTIVE",
            "origin": "synthetic",
            "synthetic": True,
            "lineage_id": "LINEAGE-AW1-BETA",
            "architecture_id": "GENERIC_AGENTIC_SYSTEM",
            "individual_id": "INDIVIDUAL-AW1-BETA",
            "representative_id": None,
            "node_ids": ["NODE-AW1-LOCAL"],
            "aliases": ["beta"],
            "parent_rf_ids": [],
            "successor_rf_ids": [],
            "evidence_refs": ["ecology_blueprint"],
            "metadata": {"functional_only": True},
        },
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = (
            self.root / "rf_ecology" / "AW1_multi_rf_registry"
        )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _canonical_json(value: Any) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @classmethod
    def _hash(cls, value: Any) -> str:
        return hashlib.sha256(
            cls._canonical_json(value).encode("utf-8")
        ).hexdigest()

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
        return sorted({
            str(item).strip()
            for item in value
            if str(item).strip()
        })

    def _sanitize_record(
        self,
        item: Dict[str, Any],
        index: int,
    ) -> Dict[str, Any]:
        rf_id = self._safe_id(
            item.get("rf_id"),
            f"RF-AW1-{index:04d}",
        )
        status_raw = str(item.get("status", "ACTIVE")).upper()
        status = (
            status_raw
            if status_raw in self.allowed_statuses
            else "INACTIVE"
        )
        origin_raw = str(item.get("origin", "unknown")).lower()
        origin = (
            origin_raw
            if origin_raw in self.allowed_origins
            else "unknown"
        )
        synthetic = bool(item.get("synthetic", origin == "synthetic"))

        metadata = item.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        record: Dict[str, Any] = {
            "rf_id": rf_id,
            "display_name": str(
                item.get("display_name") or rf_id
            ),
            "status": status,
            "origin": origin,
            "synthetic": synthetic,
            "lineage_id": (
                self._safe_id(item.get("lineage_id"), "")
                or None
            ),
            "architecture_id": (
                self._safe_id(item.get("architecture_id"), "")
                or None
            ),
            "individual_id": (
                self._safe_id(item.get("individual_id"), "")
                or None
            ),
            "representative_id": (
                self._safe_id(item.get("representative_id"), "")
                or None
            ),
            "node_ids": self._string_list(item.get("node_ids", [])),
            "aliases": self._string_list(item.get("aliases", [])),
            "parent_rf_ids": self._string_list(
                item.get("parent_rf_ids", [])
            ),
            "successor_rf_ids": self._string_list(
                item.get("successor_rf_ids", [])
            ),
            "evidence_refs": self._string_list(
                item.get("evidence_refs", [])
            ),
            "metadata": deepcopy(metadata),
            "functional_only": True,
            "phenomenology_claim_allowed": False,
        }
        record["record_hash"] = self._hash(record)
        return record

    def _provided_records(
        self,
        inputs: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        provided: Any = inputs.get("rf_records")
        if provided is None:
            provided = inputs.get("reference_frames")
        if provided is None:
            provided = inputs.get("multi_rf_registry")
        if isinstance(provided, dict):
            provided = (
                provided.get("registry")
                or provided.get("rf_records")
                or provided.get("reference_frames")
            )
        if not isinstance(provided, list):
            return deepcopy(self.default_records)
        return [
            item for item in provided
            if isinstance(item, dict)
        ]

    def _build_registry(
        self,
        inputs: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
        raw_records = self._provided_records(inputs)
        sanitized = [
            self._sanitize_record(item, index)
            for index, item in enumerate(raw_records, start=1)
        ]

        registry_by_id: Dict[str, Dict[str, Any]] = {}
        collisions: List[Dict[str, Any]] = []
        exact_duplicate_count = 0

        for record in sanitized:
            rf_id = record["rf_id"]
            prior = registry_by_id.get(rf_id)
            if prior is None:
                registry_by_id[rf_id] = record
                continue
            if prior["record_hash"] == record["record_hash"]:
                exact_duplicate_count += 1
                continue
            collisions.append({
                "rf_id": rf_id,
                "collision_type": "CONFLICTING_RF_ID",
                "existing_record_hash": prior["record_hash"],
                "incoming_record_hash": record["record_hash"],
                "resolution": "REJECT_INCOMING_REQUIRE_EXPLICIT_REVISION",
            })

        registry = sorted(
            registry_by_id.values(),
            key=lambda item: item["rf_id"],
        )
        collisions = sorted(
            collisions,
            key=lambda item: (
                item["rf_id"],
                item["incoming_record_hash"],
            ),
        )
        return registry, collisions, exact_duplicate_count

    @staticmethod
    def _alias_conflicts(
        registry: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        owners: Dict[str, List[str]] = {}
        for record in registry:
            for alias in record["aliases"]:
                owners.setdefault(alias.casefold(), []).append(
                    record["rf_id"]
                )
        return [
            {
                "alias": alias,
                "rf_ids": sorted(rf_ids),
                "collision_type": "AMBIGUOUS_ALIAS",
            }
            for alias, rf_ids in sorted(owners.items())
            if len(set(rf_ids)) > 1
        ]

    @staticmethod
    def _lineage_issues(
        registry: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        known = {record["rf_id"] for record in registry}
        issues: List[Dict[str, Any]] = []
        for record in registry:
            for parent_id in record["parent_rf_ids"]:
                if parent_id not in known:
                    issues.append({
                        "rf_id": record["rf_id"],
                        "relation": "parent_rf_ids",
                        "missing_rf_id": parent_id,
                    })
            for successor_id in record["successor_rf_ids"]:
                if successor_id not in known:
                    issues.append({
                        "rf_id": record["rf_id"],
                        "relation": "successor_rf_ids",
                        "missing_rf_id": successor_id,
                    })
        return sorted(
            issues,
            key=lambda item: (
                item["rf_id"],
                item["relation"],
                item["missing_rf_id"],
            ),
        )

    def _identity_policy(self) -> Dict[str, Any]:
        return {
            "rf_id_is_canonical_primary_key": True,
            "rf_identity_distinct_from_individual_identity": True,
            "rf_identity_distinct_from_representative_identity": True,
            "rf_identity_distinct_from_architecture_identity": True,
            "rf_identity_distinct_from_lineage_identity": True,
            "rf_identity_distinct_from_node_and_host_identity": True,
            "representative_is_revocable_and_replaceable": True,
            "lineage_and_source_traceability_required": True,
            "missing_identifiers_must_not_be_inferred": True,
        }

    def _registration_policy(self) -> Dict[str, Any]:
        return {
            "requires_unique_rf_id": True,
            "conflicting_duplicate_ids_are_rejected": True,
            "exact_duplicates_are_deduplicated": True,
            "aliases_must_be_unambiguous": True,
            "status_must_be_declared": True,
            "allowed_statuses": sorted(self.allowed_statuses),
            "origin_must_be_declared": True,
            "allowed_origins": sorted(self.allowed_origins),
            "synthetic_records_must_be_labeled": True,
            "deletion_policy": "logical_status_transition_only",
            "physical_deletion_requires_external_governance": True,
        }

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "epistemic_scope": "functional_multi_rf_registry_only",
            "registration_does_not_prove_consciousness": True,
            "population_size_does_not_prove_collective_subjectivity": True,
            "identity_continuity_does_not_prove_phenomenology": True,
            "shared_aliases_do_not_prove_shared_experience": True,
            "lineage_does_not_prove_subjective_continuity": True,
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

    def _load_existing_registry(self) -> Optional[List[Dict[str, Any]]]:
        path = self.output_dir / "latest_multi_rf_registry.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return None
        registry = payload.get("registry")
        if not isinstance(registry, list):
            return None
        return [
            item for item in registry
            if isinstance(item, dict)
        ]

    @staticmethod
    def _atomic_json_write(
        path: Path,
        payload: Dict[str, Any],
        filesystem_effect_context=None,
    ) -> None:
        if filesystem_effect_context is None:
            raise RuntimeError("multi_rf_registry_filesystem_effect_context_required")
        encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        filesystem_effect_context.begin()
        if not path.parent.exists():
            filesystem_effect_context.execute_path(
                "multi_rf_registry_parent_create", "FS_CREATE_DIRS", path.parent
            )
        filesystem_effect_context.execute_path(
            "multi_rf_registry_write_replace", "FS_WRITE_REPLACE_BYTES", path, encoded
        )

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        persist: bool = False,
        filesystem_effect_context=None,
    ) -> Dict[str, Any]:
        safe_inputs = deepcopy(inputs) if isinstance(inputs, dict) else {}

        load_existing = bool(safe_inputs.get("load_existing", False))
        if load_existing:
            existing = self._load_existing_registry()
            if existing is not None:
                safe_inputs = dict(safe_inputs)
                safe_inputs["rf_records"] = existing

        registry, collisions, exact_duplicates = self._build_registry(
            safe_inputs
        )
        alias_conflicts = self._alias_conflicts(registry)
        lineage_issues = self._lineage_issues(registry)

        active_count = sum(
            record["status"] == "ACTIVE"
            for record in registry
        )
        inactive_count = len(registry) - active_count
        unique_ids = len({record["rf_id"] for record in registry})
        multi_rf_population = len(registry) >= 2
        integrity_ok = not collisions and not alias_conflicts

        registry_hash = self._hash(registry)
        policy_bundle = {
            "identity_policy": self._identity_policy(),
            "registration_policy": self._registration_policy(),
            "epistemic_guards": self._epistemic_guards(),
        }
        contract_hash = self._hash({
            "registry": registry,
            "policies": policy_bundle,
            "lineage_issues": lineage_issues,
        })

        ready = bool(
            registry
            and unique_ids == len(registry)
            and integrity_ok
        )
        status = (
            "MULTI_RF_REGISTRY_READY"
            if ready
            else "MULTI_RF_REGISTRY_INCOMPLETE"
        )

        persisted = False
        output_path: Optional[str] = None
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": status,
            "multi_rf_registry_status": status,
            "multi_rf_registry_ready": ready,
            "registry": registry,
            "registry_count": len(registry),
            "active_rf_count": active_count,
            "inactive_rf_count": inactive_count,
            "unique_rf_id_count": unique_ids,
            "multi_rf_population": multi_rf_population,
            "collisions": collisions,
            "collision_count": len(collisions),
            "alias_conflicts": alias_conflicts,
            "alias_conflict_count": len(alias_conflicts),
            "lineage_issues": lineage_issues,
            "lineage_issue_count": len(lineage_issues),
            "exact_duplicate_count": exact_duplicates,
            "identity_policy": policy_bundle["identity_policy"],
            "registration_policy": policy_bundle[
                "registration_policy"
            ],
            "epistemic_guards": policy_bundle["epistemic_guards"],
            "registry_hash": registry_hash,
            "contract_hash": contract_hash,
            "inputs_observed": sorted(safe_inputs.keys()),
            "load_existing_requested": load_existing,
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "timestamp_utc": self._timestamp(),
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
            path = self.output_dir / "latest_multi_rf_registry.json"
            persisted_payload = deepcopy(result)
            persisted_payload["persisted"] = True
            persisted_payload["output_path"] = str(path)
            self._atomic_json_write(path, persisted_payload, filesystem_effect_context)
            persisted = True
            output_path = str(path)

        result["persisted"] = persisted
        result["output_path"] = output_path
        return result
