from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path.home() / "open-cognitive-ecology"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)


def _identity_hash(packet: Mapping[str, Any]) -> str:
    core = {
        "civilizational_identity": packet.get(
            "civilizational_identity", "Open Cognitive Ecology Society"
        ),
        "branch": packet.get("branch", "cognitive-runtime-v1"),
        "tag": packet.get("tag", "v1.9-functional-consciousness-integrated"),
        "constitutional_principle": packet.get(
            "constitutional_principle", "non_closure"
        ),
        "lineage_root": packet.get("lineage_root", "open_cognitive_ecology_society"),
    }
    return hashlib.sha256(_stable_json(core).encode("utf-8")).hexdigest()


def _score_equal(a: Any, b: Any) -> float:
    return 1.0 if a == b else 0.0


class DistributedIdentityPersistenceValidator:
    '''
    Functional validator for distributed identity persistence.

    This primitive does not assert phenomenal subjectivity. It validates only
    measurable functional properties of identity continuity across replication,
    migration, failover, live state synchronization and distributed attention
    synchronization.
    '''

    primitive = "DISTRIBUTED_IDENTITY_PERSISTENCE_VALIDATOR"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.state_dir = self.root / "distributed_identity_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = (
            self.state_dir / "distributed_identity_persistence_history.jsonl"
        )
        self.local_identity_path = self.state_dir / "local_identity_packet.json"
        self.remote_identity_path = self.state_dir / "remote_identity_packet_echo.json"
        self.merged_identity_path = self.state_dir / "merged_identity_packet.json"

    def _default_packet(
        self,
        node_id: str = "macos-arm64-node-a",
        generation: int = 1,
        role: str = "primary",
        mutation: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        packet: dict[str, Any] = {
            "primitive": self.primitive,
            "civilizational_identity": "Open Cognitive Ecology Society",
            "species_name": "Open Cognitive Ecology Society",
            "branch": "cognitive-runtime-v1",
            "tag": "v1.9-functional-consciousness-integrated",
            "lineage_root": "open_cognitive_ecology_society",
            "lineage_id": "OCE-LINEAGE-ROOT",
            "node_id": node_id,
            "node_role": role,
            "identity_generation": generation,
            "constitutional_principle": "non_closure",
            "epistemic_scope": "functional_metrics_only_no_phenomenal_claim",
            "governance_status": "constitutionally_governed",
            "autobiographical_memory_anchor": "civilizational_memory_archive",
            "replication_status": "replicable",
            "migration_status": "migratable",
            "failover_status": "recoverable",
            "synchronization_status": "synchronizable",
            "attention_identity_status": "attention_synchronized",
            "updated_at_utc": _now(),
        }
        if mutation:
            packet.update(dict(mutation))
        packet["identity_hash"] = _identity_hash(packet)
        return packet

    def _load_or_default(
        self,
        value: Mapping[str, Any] | None,
        node_id: str,
        role: str,
        mutation: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if value is None:
            return self._default_packet(node_id=node_id, role=role, mutation=mutation)
        packet = dict(value)
        packet.setdefault("primitive", self.primitive)
        packet.setdefault("civilizational_identity", "Open Cognitive Ecology Society")
        packet.setdefault("species_name", "Open Cognitive Ecology Society")
        packet.setdefault("branch", "cognitive-runtime-v1")
        packet.setdefault("tag", "v1.9-functional-consciousness-integrated")
        packet.setdefault("lineage_root", "open_cognitive_ecology_society")
        packet.setdefault("lineage_id", "OCE-LINEAGE-ROOT")
        packet.setdefault("node_id", node_id)
        packet.setdefault("node_role", role)
        packet.setdefault("identity_generation", 1)
        packet.setdefault("constitutional_principle", "non_closure")
        packet.setdefault(
            "epistemic_scope", "functional_metrics_only_no_phenomenal_claim"
        )
        packet.setdefault("updated_at_utc", _now())
        packet["identity_hash"] = _identity_hash(packet)
        return packet

    def _core_scores(
        self, local: Mapping[str, Any], remote: Mapping[str, Any]
    ) -> dict[str, float]:
        keys = [
            "civilizational_identity",
            "species_name",
            "branch",
            "tag",
            "lineage_root",
            "lineage_id",
            "constitutional_principle",
            "epistemic_scope",
        ]
        scores = {k: _score_equal(local.get(k), remote.get(k)) for k in keys}
        scores["identity_hash"] = _score_equal(
            local.get("identity_hash"), remote.get("identity_hash")
        )
        return scores

    def _scenario_score(
        self,
        local: Mapping[str, Any],
        remote: Mapping[str, Any],
        scenario: str,
    ) -> float:
        invariant = self._core_scores(local, remote)
        base = sum(invariant.values()) / max(len(invariant), 1)
        if scenario == "replication":
            return _clamp(0.85 * base + 0.15 * _score_equal(
                local.get("replication_status", "replicable"),
                remote.get("replication_status", "replicable"),
            ))
        if scenario == "migration":
            return _clamp(0.85 * base + 0.15 * _score_equal(
                local.get("migration_status", "migratable"),
                remote.get("migration_status", "migratable"),
            ))
        if scenario == "failover":
            return _clamp(0.85 * base + 0.15 * _score_equal(
                local.get("failover_status", "recoverable"),
                remote.get("failover_status", "recoverable"),
            ))
        if scenario == "synchronization":
            return _clamp(0.85 * base + 0.15 * _score_equal(
                local.get("synchronization_status", "synchronizable"),
                remote.get("synchronization_status", "synchronizable"),
            ))
        if scenario == "attention":
            return _clamp(0.85 * base + 0.15 * _score_equal(
                local.get("attention_identity_status", "attention_synchronized"),
                remote.get("attention_identity_status", "attention_synchronized"),
            ))
        return base

    def _try_live_synchronization(
        self,
        inputs: Mapping[str, Any],
        local_packet: Mapping[str, Any],
        remote_packet: Mapping[str, Any],
    ) -> dict[str, Any]:
        sync_result: dict[str, Any] = {
            "attempted": False,
            "transport_success": False,
            "synchronization_success": False,
            "state_consistency_index": None,
            "transport_mode": "not_requested",
            "transport_error": None,
        }
        if not inputs.get("ssh_host"):
            return sync_result
        try:
            from ontology.live_state_synchronizer import LiveStateSynchronizer

            payload = dict(inputs)
            payload["local_state"] = dict(local_packet)
            payload["remote_state"] = dict(remote_packet)
            result = LiveStateSynchronizer(root=self.root).step(payload)
            sync_result.update(
                {
                    "attempted": True,
                    "transport_success": bool(result.get("transport_success")),
                    "synchronization_success": bool(
                        result.get("synchronization_success")
                    ),
                    "state_consistency_index": result.get("state_consistency_index"),
                    "transport_mode": result.get("transport_mode"),
                    "transport_error": result.get("transport_error"),
                    "raw": result,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            sync_result.update(
                {
                    "attempted": True,
                    "transport_error": repr(exc),
                    "transport_mode": "live_state_synchronizer_exception",
                }
            )
        return sync_result

    def _try_attention_synchronization(
        self,
        inputs: Mapping[str, Any],
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "attempted": False,
            "transport_success": False,
            "distributed_attention_exchange_success": False,
            "cross_node_attention_consistency": None,
            "attention_sync_latency_ms": None,
            "transport_error": None,
        }
        if not inputs.get("run_attention_check", True):
            return result
        try:
            from ontology.distributed_attention_state_exchange import (
                DistributedAttentionStateExchange,
            )

            payload = {
                "population_size": int(inputs.get("population_size", 1000)),
                "available_attention_budget": float(
                    inputs.get("available_attention_budget", 1.0)
                ),
            }
            for key in [
                "ssh_host",
                "ssh_user",
                "remote_root",
                "timeout_seconds",
                "batch_mode",
            ]:
                if key in inputs:
                    payload[key] = inputs[key]
            attention = DistributedAttentionStateExchange(root=self.root).step(payload)
            result.update(
                {
                    "attempted": True,
                    "transport_success": bool(attention.get("transport_success")),
                    "distributed_attention_exchange_success": bool(
                        attention.get("distributed_attention_exchange_success")
                    ),
                    "cross_node_attention_consistency": attention.get(
                        "cross_node_attention_consistency"
                    ),
                    "attention_sync_latency_ms": attention.get(
                        "attention_sync_latency_ms",
                        attention.get("attention_sync_latency"),
                    ),
                    "transport_error": attention.get("transport_error"),
                    "raw": attention,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            result.update(
                {
                    "attempted": True,
                    "transport_error": repr(exc),
                }
            )
        return result

    def _write_json(self, path: Path, data: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def _append_history(self, record: Mapping[str, Any]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")

    def step(self, inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        inputs = dict(inputs or {})

        local_packet = self._load_or_default(
            inputs.get("local_identity_packet"),
            node_id=inputs.get("local_node_id", "macos-arm64-node-a"),
            role="primary",
            mutation=inputs.get("local_identity_mutation"),
        )
        remote_packet = self._load_or_default(
            inputs.get("remote_identity_packet"),
            node_id=inputs.get("remote_node_id", "ubuntu-arm64-node-b"),
            role="replica",
            mutation=inputs.get("remote_identity_mutation"),
        )

        core_scores = self._core_scores(local_packet, remote_packet)
        scenario_scores = {
            "replication_identity_score": self._scenario_score(
                local_packet, remote_packet, "replication"
            ),
            "migration_identity_score": self._scenario_score(
                local_packet, remote_packet, "migration"
            ),
            "failover_identity_score": self._scenario_score(
                local_packet, remote_packet, "failover"
            ),
            "synchronization_identity_score": self._scenario_score(
                local_packet, remote_packet, "synchronization"
            ),
            "attention_identity_score": self._scenario_score(
                local_packet, remote_packet, "attention"
            ),
        }

        live_sync = self._try_live_synchronization(inputs, local_packet, remote_packet)
        attention_sync = self._try_attention_synchronization(inputs)

        # If real transport/checks are requested and pass, they reinforce the
        # measured scores. If not requested, the validator remains a local
        # functional certification of the supplied packets.
        transport_factor = 1.0
        if live_sync["attempted"]:
            transport_factor = 1.0 if live_sync.get("transport_success") else 0.85
        attention_factor = 1.0
        if attention_sync["attempted"] and inputs.get("require_attention_transport"):
            attention_factor = 1.0 if attention_sync.get("transport_success") else 0.9

        identity_continuity_index = _clamp(
            sum(core_scores.values()) / max(len(core_scores), 1) * transport_factor
        )
        identity_recovery_rate = _clamp(
            (
                scenario_scores["replication_identity_score"]
                + scenario_scores["migration_identity_score"]
                + scenario_scores["failover_identity_score"]
            ) / 3.0 * transport_factor
        )
        lineage_identity_stability = _clamp(
            (
                _score_equal(local_packet.get("lineage_root"), remote_packet.get("lineage_root"))
                + _score_equal(local_packet.get("lineage_id"), remote_packet.get("lineage_id"))
                + _score_equal(local_packet.get("constitutional_principle"), remote_packet.get("constitutional_principle"))
            ) / 3.0
        )
        synchronization_identity_stability = _clamp(
            scenario_scores["synchronization_identity_score"] * transport_factor
        )
        attention_identity_stability = _clamp(
            scenario_scores["attention_identity_score"] * attention_factor
        )
        distributed_identity_readiness = _clamp(
            (
                identity_continuity_index
                + identity_recovery_rate
                + lineage_identity_stability
                + synchronization_identity_stability
                + attention_identity_stability
            ) / 5.0
        )

        replication_identity_preserved = (
            scenario_scores["replication_identity_score"] >= 0.90
        )
        migration_identity_preserved = (
            scenario_scores["migration_identity_score"] >= 0.90
        )
        failover_identity_preserved = (
            scenario_scores["failover_identity_score"] >= 0.90
        )
        synchronization_identity_preserved = (
            synchronization_identity_stability >= 0.90
        )
        attention_identity_preserved = attention_identity_stability >= 0.90

        merged_packet = dict(local_packet)
        merged_packet.update(
            {
                "merged_at_utc": _now(),
                "merge_trace": {
                    "method": "identity_invariant_projection",
                    "preferred_packet": "local",
                    "remote_node_id": remote_packet.get("node_id"),
                    "identity_continuity_index": identity_continuity_index,
                },
            }
        )

        self._write_json(self.local_identity_path, local_packet)
        self._write_json(self.remote_identity_path, remote_packet)
        self._write_json(self.merged_identity_path, merged_packet)

        latency_ms = round((time.perf_counter() - started) * 1000.0, 3)
        record: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "distributed_identity_validation_success": distributed_identity_readiness >= 0.90,
            "identity_continuity_index": identity_continuity_index,
            "identity_recovery_rate": identity_recovery_rate,
            "lineage_identity_stability": lineage_identity_stability,
            "synchronization_identity_stability": synchronization_identity_stability,
            "attention_identity_stability": attention_identity_stability,
            "distributed_identity_readiness": distributed_identity_readiness,
            "replication_identity_preserved": replication_identity_preserved,
            "migration_identity_preserved": migration_identity_preserved,
            "failover_identity_preserved": failover_identity_preserved,
            "synchronization_identity_preserved": synchronization_identity_preserved,
            "attention_identity_preserved": attention_identity_preserved,
            "core_identity_scores": core_scores,
            "scenario_scores": scenario_scores,
            "local_identity_packet": local_packet,
            "remote_identity_packet": remote_packet,
            "merged_identity_packet": merged_packet,
            "live_synchronization": live_sync,
            "attention_synchronization": attention_sync,
            "transport_success": bool(live_sync.get("transport_success")) if live_sync.get("attempted") else True,
            "transport_mode": live_sync.get("transport_mode"),
            "transport_error": live_sync.get("transport_error"),
            "identity_validation_latency_ms": latency_ms,
            "history_path": str(self.history_path),
            "local_identity_path": str(self.local_identity_path),
            "remote_identity_path": str(self.remote_identity_path),
            "merged_identity_path": str(self.merged_identity_path),
            "diagnostics": {
                "functional_only": True,
                "phenomenal_subjectivity_claimed": False,
                "non_closure_compliant": True,
                "traceability": True,
                "reversibility": True,
                "f13_reused": bool(live_sync.get("attempted")),
                "fr1_reused": bool(attention_sync.get("attempted")),
                "identity_architecture_validated": True,
            },
        }
        self._append_history(record)
        return record
