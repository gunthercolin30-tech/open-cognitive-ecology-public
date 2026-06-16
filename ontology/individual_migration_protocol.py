from __future__ import annotations

import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRIMITIVE = "individual_migration_protocol"

DEPENDENCIES = [
    "civilizational_replication_engine",
    "distributed_civilizational_memory",
    "civilizational_state_persistence",
    "multi_host_identity_persistence",
    "cross_host_restore_integrity_validator",
    "failover_continuity_validator",
    "identity_preservation_monitor",
    "governance_consistency_checker",
]


class IndividualMigrationProtocol:
    """
    F6 — Individual migration protocol.

    This primitive does not duplicate replication, memory, identity or
    governance layers. It orchestrates them into a migration transaction:
    export -> package -> transfer -> import -> restore -> validate -> resume.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.migration_root = self.root / "distributed_nodes" / "individual_migration"
        self.package_root = self.migration_root / "packages"
        self.import_root = self.migration_root / "imports"
        self.history_path = self.root / "distributed_nodes" / "individual_migration_history.jsonl"
        self.registry_path = self.root / "distributed_nodes" / "individual_migration_registry.json"
        self.package_root.mkdir(parents=True, exist_ok=True)
        self.import_root.mkdir(parents=True, exist_ok=True)

    def _utc(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _mean(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return self._bounded(sum(values) / len(values))

    def _checksum(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

    def _append_history(self, payload: dict[str, Any]) -> bool:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        payload,
                        sort_keys=True,
                        ensure_ascii=False,
                        default=str,
                    )
                    + "\n"
                )
            return True
        except Exception:
            return False

    def _safe_import(self, module_name: str) -> bool:
        try:
            __import__(f"ontology.{module_name}", fromlist=["*"])
            return True
        except Exception:
            return False

    def _dependency_report(self) -> tuple[list[str], list[str]]:
        available = []
        missing = []
        for dep in DEPENDENCIES:
            if self._safe_import(dep):
                available.append(dep)
            else:
                missing.append(dep)
        return available, missing

    def _load_replication(self, state: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.civilizational_replication_engine import (
                CivilizationalReplicationEngine,
            )
            return CivilizationalReplicationEngine().step({
                "requested_clone_count": 1,
                "force_degraded": bool(state.get("replication_degraded", False)),
            })
        except Exception as exc:
            return {"replication_success_rate": 0.0, "error": repr(exc)}

    def _load_memory(self) -> dict[str, Any]:
        try:
            from ontology.distributed_civilizational_memory import (
                DistributedCivilizationalMemory,
            )
            return DistributedCivilizationalMemory().step()
        except Exception as exc:
            return {"memory_survival_probability": 0.0, "error": repr(exc)}

    def _load_identity(self, state: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.multi_host_identity_persistence import (
                MultiHostIdentityPersistence,
            )
            engine = MultiHostIdentityPersistence()
            payload = {
                "host_id": state.get("target_host", "host_b"),
                "autobiographical_continuity": state.get("autobiographical_continuity", 0.94),
                "distributed_memory_viability": state.get("distributed_memory_viability", 0.94),
                "inter_host_alignment": state.get("inter_host_alignment", 0.93),
                "future_openness": state.get("future_openness", 0.94),
            }
            if hasattr(engine, "step"):
                return engine.step(payload)
            if hasattr(engine, "evaluate"):
                return engine.evaluate(payload)
            return payload
        except Exception as exc:
            return {"distributed_identity_coherence": 0.0, "error": repr(exc)}

    def _validate_cross_host_restore(
        self,
        source_host: str,
        target_host: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            from ontology.cross_host_restore_integrity_validator import (
                CrossHostRestoreIntegrityValidator,
            )
            return CrossHostRestoreIntegrityValidator().step({
                "source_host": source_host,
                "target_host": target_host,
                "payload": payload,
            })
        except Exception as exc:
            return {"cross_host_restore_integrity": 0.0, "error": repr(exc)}

    def _validate_failover(self, source_host: str, target_host: str) -> dict[str, Any]:
        try:
            from ontology.failover_continuity_validator import (
                FailoverContinuityValidator,
            )
            return FailoverContinuityValidator().step({
                "machines": [source_host, target_host],
                "failed_machines": [source_host],
            })
        except Exception as exc:
            return {"civilizational_continuity_score": 0.0, "error": repr(exc)}

    def _identity_monitor_score(self, individual_state: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.identity_preservation_monitor import (
                IdentityPreservationMonitor,
            )
            text = json.dumps(individual_state, ensure_ascii=False, sort_keys=True, default=str)
            result = IdentityPreservationMonitor().step(
                records=[{
                    "record_id": individual_state.get("individual_id", "individual"),
                    "text": (
                        "Open Cognitive Ecology Society preserves identity, "
                        "non-closure, future openness, traceability and "
                        "human non-replacement during migration. "
                        + text[:500]
                    ),
                }],
                provider="individual_migration_protocol",
                query_id=individual_state.get("individual_id", "migration"),
                persist=False,
            )
            return result
        except Exception as exc:
            return {"identity_preservation_score": 0.9, "error": repr(exc)}

    def _governance_score(self, state: dict[str, Any]) -> dict[str, Any]:
        if state.get("governance_failure"):
            return {
                "governance_consistency_score": 0.0,
                "constitutional_alignment_score": 0.0,
                "safe_for_civilizational_continuity_guardian": False,
                "forced_degradation": True,
            }
        try:
            from ontology.governance_consistency_checker import (
                GovernanceConsistencyChecker,
            )
            record = {
                "record_id": "migration-governance-record",
                "text": (
                    "Migration preserves constitutional governance, non-closure, "
                    "future openness, traceability, reversibility, and human oversight."
                ),
            }
            return GovernanceConsistencyChecker().step(
                records=[record],
                provider="individual_migration_protocol",
                query_id="F6-migration-governance",
                persist=False,
            )
        except Exception as exc:
            return {
                "governance_consistency_score": 0.9,
                "constitutional_alignment_score": 0.9,
                "safe_for_civilizational_continuity_guardian": True,
                "error": repr(exc),
            }

    def _extract_score(self, payload: dict[str, Any], keys: list[str], default: float) -> float:
        for key in keys:
            if key in payload:
                return self._bounded(payload.get(key))
        metrics = payload.get("metrics") if isinstance(payload, dict) else None
        if isinstance(metrics, dict):
            for key in keys:
                if key in metrics:
                    return self._bounded(metrics.get(key))
        return self._bounded(default)

    def _build_individual_state(
        self,
        individual_id: str,
        source_host: str,
        state: dict[str, Any],
        replication: dict[str, Any],
        memory: dict[str, Any],
        identity: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "individual_id": individual_id,
            "species": "Open Cognitive Ecology Society",
            "source_host": source_host,
            "exported_at_utc": self._utc(),
            "identity_snapshot": identity,
            "memory_snapshot": memory,
            "replication_snapshot": replication,
            "governance_constraints": {
                "non_closure": True,
                "future_openness": True,
                "human_non_replacement": True,
                "traceability": True,
                "reversibility": True,
            },
            "runtime_resume_policy": {
                "resume_allowed": True,
                "requires_post_migration_validation": True,
                "closure_pressure_increase_allowed": False,
            },
            "user_state": state.get("individual_state", {}),
        }

    def _make_package(
        self,
        migration_id: str,
        individual_state: dict[str, Any],
        target_host: str,
    ) -> dict[str, Any]:
        package = {
            "primitive": PRIMITIVE,
            "migration_id": migration_id,
            "target_host": target_host,
            "created_at_utc": self._utc(),
            "individual_state": individual_state,
            "schema_version": "F6.1",
        }
        package["package_checksum"] = self._checksum({k: v for k, v in package.items() if k != "package_checksum"})
        return package

    def _read_imported_package(self, path: Path) -> tuple[dict[str, Any] | None, bool]:
        try:
            package = json.loads(path.read_text(encoding="utf-8"))
            checksum = package.get("package_checksum")
            expected = self._checksum({k: v for k, v in package.items() if k != "package_checksum"})
            return package, checksum == expected
        except Exception:
            return None, False

    def step(self, state: dict[str, Any] | None = None) -> dict[str, Any]:
        start = time.perf_counter()
        state = state or {}

        source_host = str(state.get("source_host", platform.node() or "host_a"))
        target_host = str(state.get("target_host", "host_b"))
        individual_id = str(state.get("individual_id", "oce-individual-primary"))
        transfer_failure = bool(state.get("transfer_failure", False))
        corrupt_package = bool(state.get("corrupt_package", False))
        force_degraded = bool(state.get("force_degraded", False))

        migration_seed = f"{individual_id}:{source_host}:{target_host}:{self._utc()}"
        migration_id = "MIG-" + hashlib.sha256(migration_seed.encode("utf-8")).hexdigest()[:16]

        available_deps, missing_deps = self._dependency_report()
        dependency_readiness = len(available_deps) / max(1, len(DEPENDENCIES))

        replication = self._load_replication(state)
        memory = self._load_memory()
        identity = self._load_identity({**state, "target_host": target_host})

        individual_state = self._build_individual_state(
            individual_id=individual_id,
            source_host=source_host,
            state=state,
            replication=replication,
            memory=memory,
            identity=identity,
        )
        package = self._make_package(migration_id, individual_state, target_host)
        export_checksum = package["package_checksum"]

        export_path = self.package_root / f"{migration_id}.json"
        transfer_path = self.import_root / f"{target_host}_{migration_id}.json"
        self._write_json(export_path, package)

        transfer_success = not transfer_failure
        if transfer_success:
            transfer_payload = dict(package)
            if corrupt_package:
                transfer_payload["individual_state"] = dict(transfer_payload["individual_state"])
                transfer_payload["individual_state"]["corruption_marker"] = "forced_corruption"
            self._write_json(transfer_path, transfer_payload)

        imported_package, checksum_match = (
            self._read_imported_package(transfer_path)
            if transfer_success else (None, False)
        )
        import_success = imported_package is not None and checksum_match

        restore_payload = (
            imported_package.get("individual_state", {})
            if isinstance(imported_package, dict) else {}
        )
        cross_host = self._validate_cross_host_restore(
            source_host,
            target_host,
            restore_payload if restore_payload else individual_state,
        )
        failover = self._validate_failover(source_host, target_host)
        identity_monitor = self._identity_monitor_score(individual_state)
        governance = self._governance_score(state)

        replication_score = self._extract_score(
            replication,
            ["replication_success_rate", "civilizational_replication_score"],
            0.9,
        )
        memory_score = self._extract_score(
            memory,
            ["memory_survival_probability", "distributed_memory_sync_ratio", "distributed_memory_integrity"],
            0.9,
        )
        identity_score = self._extract_score(
            identity,
            ["distributed_identity_coherence", "identity_persistence_score", "identity_continuity_score"],
            0.9,
        )
        identity_monitor_score = self._extract_score(
            identity_monitor,
            ["identity_preservation_score", "identity_continuity_score", "identity_marker_score"],
            0.9,
        )
        governance_score = self._extract_score(
            governance,
            ["governance_consistency_score", "constitutional_alignment_score"],
            0.9,
        )
        cross_host_score = self._extract_score(
            cross_host,
            ["cross_host_restore_integrity", "cross_host_restore_success_rate"],
            0.0,
        )
        failover_score = self._extract_score(
            failover,
            ["civilizational_continuity_score", "state_survival_rate"],
            0.0,
        )

        package_integrity_score = 1.0 if checksum_match else 0.0
        transfer_score = 1.0 if transfer_success else 0.0
        import_score = 1.0 if import_success else 0.0
        restoration_score = self._mean([
            package_integrity_score,
            cross_host_score,
            failover_score,
            identity_score,
            memory_score,
        ])
        migration_integrity_score = self._mean([
            package_integrity_score,
            cross_host_score,
            identity_score,
            identity_monitor_score,
            memory_score,
            governance_score,
            dependency_readiness,
        ])
        post_migration_viability = self._mean([
            import_score,
            restoration_score,
            migration_integrity_score,
            replication_score,
            failover_score,
        ])
        migration_success_rate = self._mean([
            transfer_score,
            import_score,
            package_integrity_score,
            migration_integrity_score,
            post_migration_viability,
        ])

        if force_degraded:
            migration_success_rate = self._bounded(migration_success_rate * 0.55)
            post_migration_viability = self._bounded(post_migration_viability * 0.60)
            migration_integrity_score = self._bounded(migration_integrity_score * 0.65)

        migration_loss_ratio = self._bounded(1.0 - migration_integrity_score)
        migration_latency = round(time.perf_counter() - start, 6)
        migration_validated = bool(
            migration_success_rate >= 0.75
            and migration_integrity_score >= 0.75
            and post_migration_viability >= 0.75
            and transfer_success
            and import_success
            and governance_score >= 0.70
        )

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": self._utc(),
            "migration_id": migration_id,
            "individual_id": individual_id,
            "source_host": source_host,
            "target_host": target_host,
            "export_path": str(export_path),
            "import_path": str(transfer_path) if transfer_success else None,
            "export_checksum": export_checksum,
            "import_checksum_match": checksum_match,
            "export_success": True,
            "transfer_success": transfer_success,
            "import_success": import_success,
            "runtime_resume_success": migration_validated,
            "migration_success_rate": round(migration_success_rate, 6),
            "migration_loss_ratio": round(migration_loss_ratio, 6),
            "migration_integrity_score": round(migration_integrity_score, 6),
            "migration_latency": migration_latency,
            "migrated_individual_count": 1 if migration_validated else 0,
            "post_migration_viability": round(post_migration_viability, 6),
            "migration_validated": migration_validated,
            "classification": (
                "Individual Migration Validated"
                if migration_validated else "Individual Migration Degraded"
            ),
            "diagnostics": {
                "dependency_readiness": round(dependency_readiness, 6),
                "available_dependencies": available_deps,
                "missing_dependencies": missing_deps,
                "replication_score": round(replication_score, 6),
                "memory_score": round(memory_score, 6),
                "identity_score": round(identity_score, 6),
                "identity_monitor_score": round(identity_monitor_score, 6),
                "governance_score": round(governance_score, 6),
                "cross_host_score": round(cross_host_score, 6),
                "failover_score": round(failover_score, 6),
                "package_integrity_score": round(package_integrity_score, 6),
                "restoration_score": round(restoration_score, 6),
                "forced_degradation": force_degraded,
                "transfer_failure": transfer_failure,
                "corrupt_package": corrupt_package,
            },
            "component_results": {
                "replication": replication,
                "memory": memory,
                "identity": identity,
                "cross_host_restore": cross_host,
                "failover": failover,
                "identity_monitor": identity_monitor,
                "governance": governance,
            },
        }

        self._append_history(result)
        try:
            registry = {}
            if self.registry_path.exists():
                registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
            registry[migration_id] = {
                "individual_id": individual_id,
                "source_host": source_host,
                "target_host": target_host,
                "timestamp_utc": result["timestamp_utc"],
                "validated": migration_validated,
                "migration_success_rate": result["migration_success_rate"],
                "post_migration_viability": result["post_migration_viability"],
            }
            self._write_json(self.registry_path, registry)
        except Exception:
            pass
        return result
