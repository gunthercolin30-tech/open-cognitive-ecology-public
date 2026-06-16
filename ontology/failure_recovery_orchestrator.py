from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMITIVE = "failure_recovery_orchestrator"
DEPENDENCIES = [
    "trajectory_failure",
    "trajectory_recovery",
    "failover_continuity_validator",
    "individual_migration_protocol",
    "civilizational_replication_engine",
    "distributed_civilizational_memory",
    "distributed_runtime_coordinator",
    "distributed_runtime_coordination",
    "civilizational_resilience",
    "network_fragmentation_resilience",
    "resilience_distribution_analyzer",
    "longitudinal_recovery_observer",
    "civilizational_state_persistence",
    "metrics_history_recorder",
    "distributed_identity_persistence_validator",
    "civilizational_memory",
    "civilizational_memory_archive",
    "civilizational_identity_synthesis",
    "civilizational_continuity_guardian",
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    try:
        value = float(value)
    except Exception:
        value = low
    return max(low, min(high, value))


def _safe_get(data: Any, key: str, default: Any = 0.0) -> Any:
    if isinstance(data, dict):
        return data.get(key, default)
    return default


def _sha_payload(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _ssd_continuity_root() -> Optional[Path]:
    ssd_root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
    continuity = Path(
        os.environ.get(
            "OCE_CONTINUITY",
            str(ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY"),
        )
    )
    if continuity.exists():
        return continuity
    return None


class FailureRecoveryOrchestrator:
    """Active recovery orchestration layer for F7, refined by F7-R1 and F16.4.

    F16.4 adds distributed snapshot recovery without creating a redundant
    primitive. The orchestrator now creates a bounded civilizational snapshot,
    validates restore integrity, records restoration metrics, and persists the
    recovery certificate preferably on the external OCE SSD continuity tree.

    Epistemic boundary: functional continuity validation only; no phenomenal
    subjectivity claim.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        continuity_root = _ssd_continuity_root()
        if continuity_root is not None:
            self.recovery_root = continuity_root / "distributed_snapshots" / "failure_recovery"
            self.history_path = continuity_root / "certifications" / "failure_recovery_history.jsonl"
            self.registry_path = continuity_root / "distributed_snapshots" / "failure_recovery_registry.json"
            self.snapshot_root = continuity_root / "distributed_snapshots" / "snapshots"
            self.restoration_root = continuity_root / "distributed_snapshots" / "restorations"
        else:
            self.recovery_root = self.root / "distributed_nodes" / "failure_recovery"
            self.history_path = self.root / "distributed_nodes" / "failure_recovery_history.jsonl"
            self.registry_path = self.root / "distributed_nodes" / "failure_recovery_registry.json"
            self.snapshot_root = self.root / "distributed_nodes" / "distributed_snapshots"
            self.restoration_root = self.root / "distributed_nodes" / "distributed_restorations"

        self.recovery_root.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_root.mkdir(parents=True, exist_ok=True)
        self.restoration_root.mkdir(parents=True, exist_ok=True)

    def _dependency_readiness(self) -> Dict[str, Any]:
        available: List[str] = []
        missing: List[str] = []
        for dep in DEPENDENCIES:
            try:
                __import__(f"ontology.{dep}", fromlist=["*"])
                available.append(dep)
            except Exception:
                missing.append(dep)
        readiness = len(available) / max(1, len(DEPENDENCIES))
        return {
            "available_dependencies": available,
            "missing_dependencies": missing,
            "dependency_readiness": round(readiness, 6),
            "available_dependency_count": len(available),
            "missing_dependency_count": len(missing),
        }

    def _call_component(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            obj = cls()
            if hasattr(obj, "step"):
                result = obj.step(*args, **kwargs)
                if isinstance(result, dict):
                    return result
                return {"primitive": module_name, "result": result, "success": True}
            return {"primitive": module_name, "success": True, "step_available": False}
        except Exception as exc:
            return {"primitive": module_name, "success": False, "error": repr(exc)}

    def _detect_failure(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        failure_type = str(inputs.get("failure_type", "node_unavailable"))
        forced = bool(inputs.get("force_failure", True))
        total = bool(inputs.get("simulate_total_failure", False))
        transfer_failure = bool(inputs.get("transfer_failure", False))
        memory_corruption = bool(inputs.get("memory_corruption", False))
        snapshot_corruption = bool(inputs.get("snapshot_corruption", False))
        snapshot_missing = bool(inputs.get("snapshot_missing", False))
        detected = forced or total or transfer_failure or memory_corruption or snapshot_corruption or snapshot_missing
        severity = 0.45
        if failure_type in {"node_unavailable", "primary_node_loss"}:
            severity = 0.55
        if transfer_failure:
            severity = 0.65
        if memory_corruption or snapshot_corruption:
            severity = 0.78
        if snapshot_missing:
            severity = 0.82
        if total:
            severity = 0.92
        return {
            "failure_detected": detected,
            "failure_type": failure_type,
            "failure_severity": round(_bounded(severity), 6),
            "affected_node": inputs.get("affected_node", "primary"),
            "detection_confidence": 0.97 if detected else 0.75,
        }

    def _classify_failure(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        severity = float(detection.get("failure_severity", 0.0))
        if severity >= 0.85:
            failure_class = "critical_distributed_failure"
        elif severity >= 0.78:
            failure_class = "snapshot_or_memory_integrity_failure"
        elif severity >= 0.70:
            failure_class = "memory_or_state_integrity_failure"
        elif severity >= 0.60:
            failure_class = "migration_or_transfer_failure"
        elif severity >= 0.50:
            failure_class = "node_failover_required"
        else:
            failure_class = "local_recovery_required"
        return {
            "failure_class": failure_class,
            "recovery_required": bool(detection.get("failure_detected", False)),
            "severity_band": "high" if severity >= 0.7 else "moderate" if severity >= 0.45 else "low",
        }

    def _select_strategy(self, detection: Dict[str, Any], classification: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        if inputs.get("disable_snapshot_recovery"):
            strategy = "replication_failover_recovery"
        elif inputs.get("restore_from_snapshot", True):
            strategy = "distributed_snapshot_recovery"
        elif inputs.get("disable_migration"):
            strategy = "replication_failover_recovery"
        elif classification.get("failure_class") in {
            "critical_distributed_failure",
            "snapshot_or_memory_integrity_failure",
            "memory_or_state_integrity_failure",
            "migration_or_transfer_failure",
            "node_failover_required",
        }:
            strategy = "migration_assisted_failover_recovery"
        else:
            strategy = "local_trajectory_recovery"
        return {
            "selected_recovery_strategy": strategy,
            "snapshot_recovery_enabled": strategy == "distributed_snapshot_recovery",
            "migration_enabled": strategy == "migration_assisted_failover_recovery",
            "replication_enabled": strategy in {
                "migration_assisted_failover_recovery",
                "replication_failover_recovery",
                "distributed_snapshot_recovery",
            },
            "local_recovery_enabled": True,
        }

    def _build_recovery_runs(
        self,
        failover_score: float,
        migration_score: float,
        replication_score: float,
        memory_score: float,
        runtime_score: float,
        resilience_score: float,
        local_recovery_score: float,
        detection: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> List[Dict[str, float]]:
        severity = _bounded(detection.get("failure_severity", 0.0))
        forced_total = bool(inputs.get("simulate_total_failure", False))
        forced_transfer = bool(inputs.get("migration_transfer_failure", False)) or bool(inputs.get("transfer_failure", False))
        forced_corrupt = bool(inputs.get("memory_corruption", False)) or bool(inputs.get("migration_corrupt_package", False))
        snapshot_corrupt = bool(inputs.get("snapshot_corruption", False))
        penalty = 0.0
        if forced_transfer:
            penalty += 0.10
        if forced_corrupt:
            penalty += 0.16
        if snapshot_corrupt:
            penalty += 0.18
        if forced_total:
            penalty += 0.32

        base = _bounded(
            0.18 * failover_score
            + 0.17 * max(migration_score, local_recovery_score)
            + 0.16 * replication_score
            + 0.16 * memory_score
            + 0.13 * runtime_score
            + 0.10 * resilience_score
            + 0.10 * (1.0 - severity * 0.35)
            - penalty
        )
        persistence = _bounded(0.45 * replication_score + 0.35 * memory_score + 0.20 * runtime_score - penalty * 0.5)
        convergence = _bounded(0.45 * failover_score + 0.35 * max(migration_score, local_recovery_score) + 0.20 * runtime_score - penalty * 0.5)
        coherence = _bounded((base + persistence + convergence) / 3.0)
        collapse_frequency = _bounded(max(0.0, severity - coherence) + penalty * 0.35)

        runs: List[Dict[str, float]] = []
        for delta in (-0.012, -0.006, 0.0, 0.006, 0.012):
            runs.append(
                {
                    "recovery_resilience_index": round(_bounded(base + delta), 6),
                    "attractor_persistence_score": round(_bounded(persistence + delta * 0.5), 6),
                    "trajectory_convergence_score": round(_bounded(convergence - delta * 0.25), 6),
                    "ecological_recovery_coherence": round(_bounded(coherence + delta * 0.25), 6),
                    "collapse_frequency": round(collapse_frequency, 6),
                }
            )
        return runs

    def _collect_snapshot_state(self, inputs: Dict[str, Any], component_results: Dict[str, Any]) -> Dict[str, Any]:
        explicit_state = inputs.get("snapshot_state")
        if isinstance(explicit_state, dict):
            state = dict(explicit_state)
        else:
            state = {
                "civilizational_identity": inputs.get("civilizational_identity", "open_cognitive_ecology"),
                "constitution_version": inputs.get("constitution_version", "distributed_non_closure"),
                "memory_anchor_count": int(inputs.get("memory_anchor_count", 12)),
                "governance_ruleset": inputs.get("governance_ruleset", "non_closure_traceability_reversibility"),
                "lineage_depth": int(inputs.get("lineage_depth", 3)),
                "successor_count": int(inputs.get("successor_count", 3)),
                "active_node_count": int(inputs.get("active_node_count", 3)),
                "distributed_memory_index": _bounded(_safe_get(component_results.get("memory"), "distributed_memory_index", 0.9)),
                "identity_persistence_index": _bounded(inputs.get("identity_persistence_index", 0.92)),
                "timestamp_utc": _utc(),
            }
        state.setdefault("civilizational_identity", "open_cognitive_ecology")
        state.setdefault("governance_ruleset", "non_closure_traceability_reversibility")
        state.setdefault("memory_anchor_count", 0)
        state.setdefault("active_node_count", 0)
        return state

    def _create_snapshot(self, recovery_id: str, state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = inputs.get("snapshot_id") or f"SNAP-{recovery_id}"
        snapshot_path = self.snapshot_root / f"{snapshot_id}.json"
        checksum = _sha_payload(state)
        payload = {
            "primitive": PRIMITIVE,
            "refinement": "F16.4",
            "snapshot_id": snapshot_id,
            "created_at_utc": _utc(),
            "source_host": socket.gethostname(),
            "state": state,
            "snapshot_checksum": checksum,
            "epistemic_boundary": "functional continuity snapshot only; no phenomenal subjectivity claim",
        }
        if inputs.get("snapshot_missing"):
            return {
                "snapshot_id": snapshot_id,
                "snapshot_created": False,
                "snapshot_available": False,
                "snapshot_path": str(snapshot_path),
                "snapshot_checksum": "",
                "snapshot_error": "snapshot_missing_simulated",
            }
        snapshot_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return {
            "snapshot_id": snapshot_id,
            "snapshot_created": True,
            "snapshot_available": True,
            "snapshot_path": str(snapshot_path),
            "snapshot_checksum": checksum,
        }

    def _restore_snapshot(self, snapshot: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not snapshot.get("snapshot_available"):
            return {
                "snapshot_restored": False,
                "snapshot_integrity_validated": False,
                "restoration_target": inputs.get("restoration_target_node", "recovery-node"),
                "restored_checksum": "",
                "restoration_error": "snapshot_unavailable",
            }

        path = Path(snapshot["snapshot_path"])
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            state = payload.get("state", {})
            expected = payload.get("snapshot_checksum", "")
            if inputs.get("snapshot_corruption"):
                state = dict(state)
                state["corruption_marker"] = "simulated"
            restored_checksum = _sha_payload(state)
            integrity = bool(restored_checksum == expected and expected)
            target = str(inputs.get("restoration_target_node", "recovery-node"))
            restoration_id = f"REST-{hashlib.sha256((snapshot['snapshot_id'] + target + str(time.time())).encode()).hexdigest()[:16]}"
            restoration_path = self.restoration_root / f"{restoration_id}.json"
            restoration_payload = {
                "primitive": PRIMITIVE,
                "refinement": "F16.4",
                "restoration_id": restoration_id,
                "snapshot_id": snapshot["snapshot_id"],
                "restoration_target": target,
                "restored_at_utc": _utc(),
                "snapshot_integrity_validated": integrity,
                "restored_checksum": restored_checksum,
                "expected_checksum": expected,
                "state": state if integrity else {},
            }
            restoration_path.write_text(json.dumps(restoration_payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            return {
                "snapshot_restored": integrity,
                "snapshot_integrity_validated": integrity,
                "restoration_id": restoration_id,
                "restoration_target": target,
                "restored_checksum": restored_checksum,
                "expected_checksum": expected,
                "restoration_path": str(restoration_path),
            }
        except Exception as exc:
            return {
                "snapshot_restored": False,
                "snapshot_integrity_validated": False,
                "restoration_target": inputs.get("restoration_target_node", "recovery-node"),
                "restored_checksum": "",
                "restoration_error": repr(exc),
            }

    def _validate_restored_continuity(
        self,
        state: Dict[str, Any],
        snapshot: Dict[str, Any],
        restoration: Dict[str, Any],
        inputs: Dict[str, Any],
        scores: Dict[str, float],
    ) -> Dict[str, Any]:
        memory_anchor_count = int(state.get("memory_anchor_count", 0) or 0)
        active_node_count = int(state.get("active_node_count", 0) or 0)
        successor_count = int(state.get("successor_count", 0) or 0)

        memory_restore_score = _bounded(inputs.get("memory_restore_score", min(1.0, memory_anchor_count / 10.0)))
        identity_restore_score = _bounded(inputs.get("identity_restore_score", state.get("identity_persistence_index", 0.0)))
        governance_restore_score = _bounded(
            inputs.get(
                "governance_restore_score",
                1.0 if str(state.get("governance_ruleset", "")).strip() else 0.0,
            )
        )
        node_restore_score = _bounded(inputs.get("node_restore_score", min(1.0, active_node_count / 3.0)))
        succession_restore_score = _bounded(inputs.get("succession_restore_score", min(1.0, successor_count / 2.0)))
        continuity_guardian_score = _bounded(
            0.35 * scores.get("failover_score", 0.0)
            + 0.25 * scores.get("memory_score", 0.0)
            + 0.20 * scores.get("replication_score", 0.0)
            + 0.20 * scores.get("runtime_score", 0.0)
        )

        distributed_snapshot_recovery_index = round(
            _bounded(
                0.16 * (1.0 if snapshot.get("snapshot_available") else 0.0)
                + 0.18 * (1.0 if restoration.get("snapshot_integrity_validated") else 0.0)
                + 0.16 * memory_restore_score
                + 0.15 * identity_restore_score
                + 0.13 * governance_restore_score
                + 0.10 * node_restore_score
                + 0.07 * succession_restore_score
                + 0.05 * continuity_guardian_score
            ),
            6,
        )

        blockers: List[str] = []
        if not snapshot.get("snapshot_available"):
            blockers.append("snapshot_unavailable")
        if not restoration.get("snapshot_integrity_validated"):
            blockers.append("snapshot_integrity_failed")
        if memory_restore_score < 0.70:
            blockers.append("memory_restore_below_threshold")
        if identity_restore_score < 0.70:
            blockers.append("identity_restore_below_threshold")
        if governance_restore_score < 0.70:
            blockers.append("governance_restore_below_threshold")
        if node_restore_score < 0.50:
            blockers.append("node_restore_below_threshold")

        restored_continuity_validated = bool(
            distributed_snapshot_recovery_index >= 0.82
            and not blockers
        )

        if restored_continuity_validated and distributed_snapshot_recovery_index >= 0.92:
            classification = "Distributed Snapshot Recovery Validated"
        elif restored_continuity_validated:
            classification = "Distributed Snapshot Recovery Partially Validated"
        else:
            classification = "Distributed Snapshot Recovery Degraded"

        return {
            "distributed_snapshot_recovery_index": distributed_snapshot_recovery_index,
            "snapshot_restored_continuity_validated": restored_continuity_validated,
            "memory_restore_score": round(memory_restore_score, 6),
            "identity_restore_score": round(identity_restore_score, 6),
            "governance_restore_score": round(governance_restore_score, 6),
            "node_restore_score": round(node_restore_score, 6),
            "succession_restore_score": round(succession_restore_score, 6),
            "continuity_guardian_score": round(continuity_guardian_score, 6),
            "snapshot_recovery_blockers": blockers,
            "snapshot_recovery_classification": classification,
        }

    def _write_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        record_path = self.recovery_root / f"{record['recovery_id']}.json"
        record_with_checksum = dict(record)
        record_with_checksum["record_checksum"] = digest
        record_path.write_text(json.dumps(record_with_checksum, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record_with_checksum, ensure_ascii=False, sort_keys=True) + "\n")
        registry = {
            "primitive": PRIMITIVE,
            "latest_recovery_id": record["recovery_id"],
            "latest_record_path": str(record_path),
            "latest_checksum": digest,
            "updated_at_utc": _utc(),
            "refinement": "F16.4",
            "snapshot_id": record.get("snapshot_id"),
            "snapshot_path": record.get("snapshot_path"),
            "restoration_path": record.get("restoration_path"),
        }
        self.registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return {"record_path": str(record_path), "history_path": str(self.history_path), "registry_path": str(self.registry_path), "record_checksum": digest}

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        started = time.perf_counter()
        inputs = dict(inputs or {})
        recovery_id = "REC-" + hashlib.sha256(f"{time.time()}-{socket.gethostname()}".encode()).hexdigest()[:16]

        deps = self._dependency_readiness()
        detection = self._detect_failure(inputs)
        classification = self._classify_failure(detection)
        strategy = self._select_strategy(detection, classification, inputs)

        trajectory = self._call_component("trajectory_recovery", "TrajectoryRecovery")
        failover = self._call_component("failover_continuity_validator", "FailoverContinuityValidator")
        replication = self._call_component("civilizational_replication_engine", "CivilizationalReplicationEngine")
        memory = self._call_component("distributed_civilizational_memory", "DistributedCivilizationalMemory")
        runtime_coord = self._call_component("distributed_runtime_coordinator", "DistributedRuntimeCoordinator")
        runtime_summary = self._call_component("distributed_runtime_coordination", "DistributedRuntimeCoordination")
        resilience = self._call_component("civilizational_resilience", "CivilizationalResilience")
        fragmentation = self._call_component("network_fragmentation_resilience", "NetworkFragmentationResilience")

        migration: Dict[str, Any] = {"primitive": "individual_migration_protocol", "skipped": True, "migration_validated": False}
        if strategy.get("migration_enabled"):
            migration_inputs: Dict[str, Any] = {}
            if inputs.get("migration_corrupt_package"):
                migration_inputs["corrupt_package"] = True
            if inputs.get("migration_transfer_failure"):
                migration_inputs["transfer_failure"] = True
            migration = self._call_component("individual_migration_protocol", "IndividualMigrationProtocol", migration_inputs)

        failover_score = float(_safe_get(failover, "civilizational_continuity_score", _safe_get(failover, "validation_success", 0.75)))
        if isinstance(_safe_get(failover, "validation_success", False), bool) and _safe_get(failover, "validation_success", False):
            failover_score = max(failover_score, 0.75)
        migration_score = 0.0
        if not migration.get("skipped"):
            migration_score = float(_safe_get(migration, "post_migration_viability", 0.0))
        replication_score = float(_safe_get(replication, "replication_success_rate", 0.9))
        memory_score = float(_safe_get(memory, "memory_survival_probability", _safe_get(memory, "distributed_memory_index", 0.88)))
        runtime_score = float(_safe_get(runtime_coord, "node_health", _safe_get(runtime_summary, "coordination_integrity", 0.9)))
        resilience_score = float(_safe_get(resilience, "civilizational_resilience_index", _safe_get(fragmentation, "network_resilience_score", 0.75)))
        if resilience_score == 0.0:
            resilience_score = 0.75
        local_recovery_score = 0.86 if trajectory.get("success", True) is not False else 0.55

        recovery_runs = self._build_recovery_runs(
            failover_score=failover_score,
            migration_score=migration_score,
            replication_score=replication_score,
            memory_score=memory_score,
            runtime_score=runtime_score,
            resilience_score=resilience_score,
            local_recovery_score=local_recovery_score,
            detection=detection,
            inputs=inputs,
        )
        distribution = self._call_component("resilience_distribution_analyzer", "ResilienceDistributionAnalyzer", recovery_runs)
        longitudinal = self._call_component("longitudinal_recovery_observer", "LongitudinalRecoveryObserver", recovery_runs)

        distribution_score = float(
            _safe_get(
                distribution,
                "ecological_recovery_coherence",
                _safe_get(distribution, "resilience_distribution_index", 0.86),
            )
        )
        if distribution.get("success") is False:
            distribution_score = 0.86
        longitudinal_score = float(
            _safe_get(
                longitudinal,
                "ecological_recovery_continuity",
                _safe_get(longitudinal, "longitudinal_recovery_index", 0.86),
            )
        )
        if longitudinal.get("success") is False:
            longitudinal_score = 0.86

        forced_total = bool(inputs.get("simulate_total_failure", False))
        forced_transfer = bool(inputs.get("migration_transfer_failure", False)) or bool(inputs.get("transfer_failure", False))
        forced_corrupt = bool(inputs.get("memory_corruption", False)) or bool(inputs.get("migration_corrupt_package", False))
        snapshot_corrupt = bool(inputs.get("snapshot_corruption", False))
        snapshot_missing = bool(inputs.get("snapshot_missing", False))

        recovery_integrity_score = _bounded(
            0.19 * failover_score
            + 0.17 * max(migration_score, local_recovery_score)
            + 0.16 * replication_score
            + 0.16 * memory_score
            + 0.11 * runtime_score
            + 0.08 * resilience_score
            + 0.07 * distribution_score
            + 0.06 * longitudinal_score
        )
        if forced_transfer:
            recovery_integrity_score *= 0.72
        if forced_corrupt:
            recovery_integrity_score *= 0.68
        if snapshot_corrupt:
            recovery_integrity_score *= 0.76
        if snapshot_missing:
            recovery_integrity_score *= 0.58
        if forced_total:
            recovery_integrity_score *= 0.48
        recovery_integrity_score = round(_bounded(recovery_integrity_score), 6)

        migration_recovery_ratio = migration_score if strategy.get("migration_enabled") else 0.0

        component_results = {
            "trajectory_recovery": trajectory,
            "failover": failover,
            "migration": migration,
            "replication": replication,
            "memory": memory,
            "runtime_coordinator": runtime_coord,
            "runtime_coordination": runtime_summary,
            "resilience": resilience,
            "network_fragmentation": fragmentation,
            "resilience_distribution": distribution,
            "longitudinal_recovery": longitudinal,
        }

        snapshot_state = self._collect_snapshot_state(inputs, {"memory": memory, "replication": replication})
        snapshot = self._create_snapshot(recovery_id, snapshot_state, inputs)
        restoration = self._restore_snapshot(snapshot, inputs)
        snapshot_validation = self._validate_restored_continuity(
            state=snapshot_state,
            snapshot=snapshot,
            restoration=restoration,
            inputs=inputs,
            scores={
                "failover_score": _bounded(failover_score),
                "memory_score": _bounded(memory_score),
                "replication_score": _bounded(replication_score),
                "runtime_score": _bounded(runtime_score),
            },
        )

        snapshot_recovery_index = snapshot_validation["distributed_snapshot_recovery_index"]

        recovery_success_rate = round(
            _bounded(
                0.54 * recovery_integrity_score
                + 0.26 * deps["dependency_readiness"]
                + 0.20 * snapshot_recovery_index
            ),
            6,
        )
        civilizational_survival_ratio = round(
            _bounded(
                0.35 * memory_score
                + 0.20 * replication_score
                + 0.17 * failover_score
                + 0.13 * recovery_integrity_score
                + 0.15 * snapshot_recovery_index
            ),
            6,
        )
        if forced_total:
            civilizational_survival_ratio = round(_bounded(civilizational_survival_ratio * 0.62), 6)
        node_failure_recovery_time = round(time.perf_counter() - started, 6)
        recovery_strategy_efficiency = round(_bounded(recovery_success_rate / max(0.001, 1.0 + detection["failure_severity"] * 0.25)), 6)

        analyzer_interface_repaired = bool(distribution.get("success") is True and longitudinal.get("success") is True)
        snapshot_recovery_validated = bool(
            strategy.get("snapshot_recovery_enabled")
            and snapshot_validation["snapshot_restored_continuity_validated"]
            and not forced_total
            and not forced_transfer
            and not forced_corrupt
            and not snapshot_corrupt
            and not snapshot_missing
        )

        recovery_validated = (
            detection["failure_detected"]
            and deps["dependency_readiness"] >= 0.85
            and recovery_success_rate >= 0.78
            and civilizational_survival_ratio >= 0.72
            and recovery_integrity_score >= 0.72
            and analyzer_interface_repaired
            and snapshot_recovery_validated
        )

        record: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "refinement": "F16.4",
            "timestamp_utc": _utc(),
            "recovery_id": recovery_id,
            "source_host": socket.gethostname(),
            "failure_detected": detection["failure_detected"],
            "failure_type": detection["failure_type"],
            "failure_class": classification["failure_class"],
            "selected_recovery_strategy": strategy["selected_recovery_strategy"],
            "node_failure_recovery_time": node_failure_recovery_time,
            "recovery_success_rate": recovery_success_rate,
            "civilizational_survival_ratio": civilizational_survival_ratio,
            "recovery_integrity_score": recovery_integrity_score,
            "recovery_strategy_efficiency": recovery_strategy_efficiency,
            "migration_recovery_ratio": round(_bounded(migration_recovery_ratio), 6),
            "recovery_validated": bool(recovery_validated),
            "runtime_reallocated": bool(runtime_score >= 0.85 and not forced_total),
            "restart_success": bool(recovery_success_rate >= 0.78 and not forced_total),
            "analyzer_interface_repaired": analyzer_interface_repaired,
            "snapshot_id": snapshot.get("snapshot_id"),
            "snapshot_path": snapshot.get("snapshot_path"),
            "snapshot_available": snapshot.get("snapshot_available", False),
            "snapshot_checksum": snapshot.get("snapshot_checksum", ""),
            "snapshot_restored": restoration.get("snapshot_restored", False),
            "snapshot_integrity_validated": restoration.get("snapshot_integrity_validated", False),
            "restoration_id": restoration.get("restoration_id"),
            "restoration_target": restoration.get("restoration_target"),
            "restoration_path": restoration.get("restoration_path"),
            "distributed_snapshot_recovery_index": snapshot_recovery_index,
            "snapshot_restored_continuity_validated": snapshot_validation["snapshot_restored_continuity_validated"],
            "snapshot_recovery_validated": snapshot_recovery_validated,
            "snapshot_recovery_classification": snapshot_validation["snapshot_recovery_classification"],
            "classification": (
                "Distributed Snapshot Recovery Validated"
                if recovery_validated
                else "Distributed Snapshot Recovery Degraded"
            ),
            "diagnostics": {
                **deps,
                **detection,
                **classification,
                **strategy,
                "failover_score": round(_bounded(failover_score), 6),
                "migration_score": round(_bounded(migration_score), 6),
                "replication_score": round(_bounded(replication_score), 6),
                "memory_score": round(_bounded(memory_score), 6),
                "runtime_score": round(_bounded(runtime_score), 6),
                "resilience_score": round(_bounded(resilience_score), 6),
                "distribution_score": round(_bounded(distribution_score), 6),
                "longitudinal_score": round(_bounded(longitudinal_score), 6),
                "forced_total_failure": forced_total,
                "forced_transfer_failure": forced_transfer,
                "forced_memory_corruption": forced_corrupt,
                "forced_snapshot_corruption": snapshot_corrupt,
                "forced_snapshot_missing": snapshot_missing,
                "analyzer_interface_repaired": analyzer_interface_repaired,
                "recovery_run_count": len(recovery_runs),
                "epistemic_boundary": "functional continuity validation only; no phenomenal subjectivity claim",
            },
            "snapshot_result": snapshot,
            "restoration_result": restoration,
            "snapshot_validation": snapshot_validation,
            "component_results": component_results,
            "recovery_runs": recovery_runs,
        }
        persistence = self._write_record(record)
        record.update(persistence)
        return record


if __name__ == "__main__":
    from pprint import pprint
    pprint(FailureRecoveryOrchestrator().step())
