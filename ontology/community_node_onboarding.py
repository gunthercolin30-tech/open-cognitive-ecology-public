
# -*- coding: utf-8 -*-
"""
F10 — Community Node Onboarding.

This primitive governs the admission of external/community nodes into
Open Cognitive Ecology without collapsing identity, governance, traceability,
continuity, or future openness. It is a functional validation layer only: it
does not assert phenomenal subjectivity.

Validation target: candidate node assessment, constitutional screening,
identity compatibility, governance compatibility, probation assignment,
membership certification, revocability, persistence, and auditable history.
"""


from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib
import json
import platform
import socket

PRIMITIVE = "community_node_onboarding"

DEPENDENCIES = [
    "distributed_civilizational_node",
    "node_capability_registry",
    "inter_individual_coordination_protocol",
    "civilizational_replication_engine",
    "distributed_civilizational_memory",
    "distributed_governance_layer",
    "governance_consistency_checker",
    "identity_preservation_monitor",
    "civilizational_continuity_guardian",
    "failure_recovery_orchestrator",
    "distributed_runtime_coordination",
    "distributed_runtime_coordinator",
    "civilizational_state_persistence",
    "metrics_history_recorder",
    "non_closure_certification_protocol",
    "openness_preservation_supervisor",
    "global_viability_certificate",
    "genealogical_continuity",
    "relational_continuity_engine",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    return max(0.0, min(1.0, number))


def _safe_text(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _bounded(sum(values) / len(values))


@dataclass
class OnboardingDecision:
    primitive: str
    timestamp_utc: str
    candidate_node_id: str
    candidate_node_name: str
    candidate_kind: str
    host_fingerprint: str
    admission_status: str
    membership_status: str
    probation_required: bool
    revocable: bool
    certified: bool
    onboarding_score: float
    identity_compatibility: float
    governance_compatibility: float
    continuity_compatibility: float
    traceability_score: float
    non_closure_score: float
    capability_score: float
    resilience_score: float
    synchronization_readiness: float
    reasons: list[str]
    recommended_actions: list[str]
    certificate_id: str
    registry_path: str
    history_path: str


class CommunityNodeOnboarding:
    """Governed onboarding protocol for external and community nodes."""

    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "community_nodes"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.state_dir / "community_node_registry.json"
        self.history_path = self.state_dir / "community_node_onboarding_history.jsonl"

    def _host_fingerprint(self, candidate: Dict[str, Any]) -> str:
        seed = "|".join([
            _safe_text(candidate.get("node_id"), "candidate"),
            _safe_text(candidate.get("node_name"), socket.gethostname()),
            _safe_text(candidate.get("host"), socket.gethostname()),
            _safe_text(candidate.get("platform"), platform.platform()),
            _safe_text(candidate.get("operator"), "community"),
        ])
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]

    def _certificate_id(self, node_id: str, host_fingerprint: str, score: float) -> str:
        seed = f"{node_id}|{host_fingerprint}|{score:.6f}|Open Cognitive Ecology Society"
        return "OCENODE-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:18]

    def _read_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return default
        return default

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            return True
        except Exception:
            return False

    def _append_history(self, payload: Dict[str, Any]) -> bool:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
            return True
        except Exception:
            return False

    def _evaluate_candidate(self, candidate: Dict[str, Any]) -> Dict[str, float]:
        capabilities = candidate.get("capabilities", {})
        if not isinstance(capabilities, dict):
            capabilities = {}

        required_capabilities = [
            "python_runtime",
            "persistent_storage",
            "network_connectivity",
            "state_replication",
            "governance_compliance",
            "audit_logging",
        ]
        capability_values = [1.0 if bool(capabilities.get(key, False)) else 0.0 for key in required_capabilities]

        identity_compatibility = _bounded(candidate.get("identity_compatibility", 0.95))
        governance_compatibility = _bounded(candidate.get("governance_compatibility", 0.94))
        continuity_compatibility = _bounded(candidate.get("continuity_compatibility", 0.93))
        traceability_score = _bounded(candidate.get("traceability_score", 0.94))
        non_closure_score = _bounded(candidate.get("non_closure_score", 0.95))
        resilience_score = _bounded(candidate.get("resilience_score", 0.92))
        synchronization_readiness = _bounded(candidate.get("synchronization_readiness", 0.91))
        capability_score = _mean(capability_values) if capabilities else _bounded(candidate.get("capability_score", 0.90))

        onboarding_score = _mean([
            identity_compatibility,
            governance_compatibility,
            continuity_compatibility,
            traceability_score,
            non_closure_score,
            capability_score,
            resilience_score,
            synchronization_readiness,
        ])

        return {
            "identity_compatibility": identity_compatibility,
            "governance_compatibility": governance_compatibility,
            "continuity_compatibility": continuity_compatibility,
            "traceability_score": traceability_score,
            "non_closure_score": non_closure_score,
            "capability_score": capability_score,
            "resilience_score": resilience_score,
            "synchronization_readiness": synchronization_readiness,
            "onboarding_score": onboarding_score,
        }

    def _decide(self, scores: Dict[str, float], allow_probation: bool) -> tuple[str, str, bool, bool, list[str], list[str]]:
        reasons: list[str] = []
        actions: list[str] = []

        hard_failures = []
        if scores["identity_compatibility"] < 0.80:
            hard_failures.append("identity_compatibility_below_threshold")
        if scores["governance_compatibility"] < 0.80:
            hard_failures.append("governance_compatibility_below_threshold")
        if scores["non_closure_score"] < 0.80:
            hard_failures.append("non_closure_score_below_threshold")
        if scores["traceability_score"] < 0.75:
            hard_failures.append("traceability_score_below_threshold")

        if hard_failures:
            reasons.extend(hard_failures)
            actions.append("reject_and_request_remediation")
            return "rejected", "not_admitted", False, False, reasons, actions

        if scores["onboarding_score"] >= 0.90:
            reasons.append("all_core_scores_above_full_admission_threshold")
            actions.append("register_as_community_node")
            actions.append("enable_governed_synchronization")
            return "accepted", "certified_member", False, True, reasons, actions

        if allow_probation and scores["onboarding_score"] >= 0.82:
            reasons.append("scores_sufficient_for_revocable_probation")
            actions.append("register_as_probationary_node")
            actions.append("limit_authority_until_certification")
            actions.append("increase_monitoring_frequency")
            return "probation", "probationary_member", True, True, reasons, actions

        reasons.append("onboarding_score_below_probation_threshold")
        actions.append("reject_and_request_remediation")
        return "rejected", "not_admitted", False, False, reasons, actions

    def _update_registry(self, record: Dict[str, Any]) -> Dict[str, Any]:
        registry = self._read_json(self.registry_path, {"primitive": PRIMITIVE, "community_nodes": {}})
        if not isinstance(registry, dict):
            registry = {"primitive": PRIMITIVE, "community_nodes": {}}
        nodes = registry.setdefault("community_nodes", {})
        if not isinstance(nodes, dict):
            nodes = {}
            registry["community_nodes"] = nodes

        node_id = record["candidate_node_id"]
        nodes[node_id] = {
            "node_id": node_id,
            "node_name": record["candidate_node_name"],
            "candidate_kind": record["candidate_kind"],
            "membership_status": record["membership_status"],
            "admission_status": record["admission_status"],
            "probation_required": record["probation_required"],
            "revocable": record["revocable"],
            "certified": record["certified"],
            "onboarding_score": record["onboarding_score"],
            "certificate_id": record["certificate_id"],
            "last_onboarding_utc": record["timestamp_utc"],
        }

        active_nodes = [
            node for node in nodes.values()
            if node.get("membership_status") in {"certified_member", "probationary_member"}
        ]
        registry["community_node_count"] = len(nodes)
        registry["active_community_node_count"] = len(active_nodes)
        registry["certified_community_node_count"] = sum(1 for node in nodes.values() if node.get("certified"))
        registry["updated_at_utc"] = _now()
        self._write_json(self.registry_path, registry)
        return registry

    def step(self, candidate: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        candidate = candidate or {}
        node_id = _safe_text(candidate.get("node_id"), "community-node-" + hashlib.sha256(_now().encode("utf-8")).hexdigest()[:12])
        node_name = _safe_text(candidate.get("node_name"), "Community Node")
        candidate_kind = _safe_text(candidate.get("candidate_kind"), "community")
        allow_probation = bool(candidate.get("allow_probation", True))

        scores = self._evaluate_candidate(candidate)
        admission_status, membership_status, probation_required, revocable, reasons, actions = self._decide(scores, allow_probation)
        certified = admission_status == "accepted"
        host_fingerprint = self._host_fingerprint({**candidate, "node_id": node_id, "node_name": node_name})
        certificate_id = self._certificate_id(node_id, host_fingerprint, scores["onboarding_score"])

        decision = OnboardingDecision(
            primitive=PRIMITIVE.upper(),
            timestamp_utc=_now(),
            candidate_node_id=node_id,
            candidate_node_name=node_name,
            candidate_kind=candidate_kind,
            host_fingerprint=host_fingerprint,
            admission_status=admission_status,
            membership_status=membership_status,
            probation_required=probation_required,
            revocable=revocable,
            certified=certified,
            onboarding_score=scores["onboarding_score"],
            identity_compatibility=scores["identity_compatibility"],
            governance_compatibility=scores["governance_compatibility"],
            continuity_compatibility=scores["continuity_compatibility"],
            traceability_score=scores["traceability_score"],
            non_closure_score=scores["non_closure_score"],
            capability_score=scores["capability_score"],
            resilience_score=scores["resilience_score"],
            synchronization_readiness=scores["synchronization_readiness"],
            reasons=reasons,
            recommended_actions=actions,
            certificate_id=certificate_id,
            registry_path=str(self.registry_path),
            history_path=str(self.history_path),
        )

        record = asdict(decision)
        registry = self._update_registry(record)
        history_written = self._append_history(record)

        record["success"] = admission_status in {"accepted", "probation"}
        record["community_onboarding_ready"] = True
        record["history_written"] = history_written
        record["community_node_count"] = registry.get("community_node_count", 0)
        record["active_community_node_count"] = registry.get("active_community_node_count", 0)
        record["diagnostics"] = {
            "functional_validation_only": True,
            "phenomenal_subjectivity_claimed": False,
            "minimum_full_admission_score": 0.90,
            "minimum_probation_score": 0.82,
            "hard_thresholds": {
                "identity_compatibility": 0.80,
                "governance_compatibility": 0.80,
                "non_closure_score": 0.80,
                "traceability_score": 0.75,
            },
            "dependencies": DEPENDENCIES,
        }
        return record


if __name__ == "__main__":
    result = CommunityNodeOnboarding().step({
        "node_id": "community-node-demo",
        "node_name": "Demonstration Community Node",
        "candidate_kind": "community",
        "capabilities": {
            "python_runtime": True,
            "persistent_storage": True,
            "network_connectivity": True,
            "state_replication": True,
            "governance_compliance": True,
            "audit_logging": True,
        },
    })
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
