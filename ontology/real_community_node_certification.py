from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ontology.governed_network_effector import GovernedTcpProbeEffector, TrustedTcpConnectProbeTransport


ROOT = Path.home() / "open-cognitive-ecology"


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(value)))
    except Exception:
        return 0.0


def _mean(values):
    vals = [float(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals)) if vals else 0.0


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


P162_G63B6_TCP_PROBE_MEDIATED = True

class RealCommunityNodeCertification:
    # F16.2 real community-node certification.
    primitive = "REAL_COMMUNITY_NODE_CERTIFICATION"

    def __init__(self, root: Optional[Path] = None, filesystem_effect_context_provider=None) -> None:
        self.root = Path(root) if root else ROOT
        self.filesystem_effect_context_provider = filesystem_effect_context_provider
        self.history_path = self._history_path()
        self.governed_tcp_probe_context = None
        self._last_reachability_diagnostic = "not_checked"

    def set_governed_tcp_probe_context(self, context: Optional[Dict[str, Any]]) -> None:
        self.governed_tcp_probe_context = context

    def _history_path(self) -> Path:
        ssd_root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
        ssd_continuity = Path(
            os.environ.get(
                "OCE_CONTINUITY",
                str(ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY"),
            )
        )
        if ssd_continuity.exists():
            path = ssd_continuity / "certifications" / "real_community_node_certification_history.jsonl"
        else:
            path = self.root / "real_community_node_certification_history.jsonl"
        parent = path.parent
        if not parent.exists():
            provider = self.filesystem_effect_context_provider
            if provider is None or not callable(provider):
                raise RuntimeError("filesystem_effect_context_provider_required")
            context = provider("FS_CREATE_DIRS", parent)
            if context is None:
                raise RuntimeError("preissued_filesystem_effect_context_required")
            context.begin()
            context.execute_path("history_parent", "FS_CREATE_DIRS", parent)
        return path

    def _dependency_available(self, name: str) -> bool:
        return (self.root / "ontology" / f"{name}.py").exists()

    def _probe_reachability(self, host: str, port: int, timeout: float) -> bool:
        if not host:
            self._last_reachability_diagnostic = "missing_host"
            return False
        context = self.governed_tcp_probe_context
        if not isinstance(context, dict) or context.get("handle") is None:
            self._last_reachability_diagnostic = "governed_tcp_probe_context_required"
            return False
        effector = context.get("effector") or GovernedTcpProbeEffector(transport=TrustedTcpConnectProbeTransport())
        result = effector.execute(host=host, port=int(port), timeout_seconds=float(timeout),
                                  handle=context.get("handle"), adapter_id=context.get("adapter_id"),
                                  effector_id=context.get("effector_id"))
        self._last_reachability_diagnostic = str(result.get("reason") or result.get("status"))
        return bool(result.get("status") == "EFFECT_CONFIRMED" and result.get("reachable") is True)

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = dict(inputs or {})

        node_id = str(inputs.get("community_node_id") or inputs.get("node_id") or "").strip()
        host = str(inputs.get("host") or inputs.get("hostname") or "").strip()
        provider = str(inputs.get("provider") or "external-community").strip()
        operator = str(inputs.get("operator") or inputs.get("operator_id") or "").strip()

        operator_consent = bool(inputs.get("operator_consent", False))
        governance_acknowledged = bool(inputs.get("governance_acknowledged", False))
        external_operator_confirmed = bool(inputs.get("external_operator_confirmed", False))
        external_site_confirmed = bool(inputs.get("external_site_confirmed", False))
        non_founder_device_confirmed = bool(inputs.get("non_founder_device_confirmed", False))

        require_reachability = bool(inputs.get("require_reachability", False))
        simulate_unreachable = bool(inputs.get("simulate_unreachable", False))
        port = int(inputs.get("port", 22))
        timeout_seconds = float(inputs.get("timeout_seconds", 5))

        if simulate_unreachable:
            reachable = False
        elif require_reachability:
            reachable = self._probe_reachability(host, port, timeout_seconds)
        else:
            reachable = bool(node_id and host)

        declared = bool(node_id and host and provider)
        consent_score = 1.0 if operator_consent and operator else 0.0
        governance_score = _clamp(inputs.get("governance_alignment_score", inputs.get("non_closure_score", 0.92)))
        identity_score = _clamp(inputs.get("identity_alignment_score", 0.90))
        continuity_score = _clamp(inputs.get("continuity_alignment_score", 0.90))
        traceability_score = _clamp(inputs.get("traceability_score", 0.90))
        reversibility_score = _clamp(inputs.get("reversibility_score", 0.90))
        non_closure_score = _clamp(inputs.get("non_closure_score", 0.92))

        external_operator_score = 1.0 if external_operator_confirmed and operator else 0.0
        external_site_score = 1.0 if external_site_confirmed else 0.0
        non_founder_device_score = 1.0 if non_founder_device_confirmed else 0.0
        external_independence_index = _mean([
            external_operator_score,
            external_site_score,
            non_founder_device_score,
        ])

        dependency_names = [
            "community_node_onboarding",
            "distributed_civilizational_node",
            "node_capability_registry",
            "civilizational_replication_engine",
            "distributed_civilizational_memory",
            "distributed_governance_layer",
            "distributed_identity_persistence_validator",
            "civilizational_state_persistence",
            "failure_recovery_orchestrator",
            "real_cloud_node_deployment_validator",
        ]
        available_dependencies = [name for name in dependency_names if self._dependency_available(name)]
        missing_dependencies = [name for name in dependency_names if name not in available_dependencies]
        dependency_readiness = len(available_dependencies) / len(dependency_names)

        reachability_score = 1.0 if reachable else 0.0
        declaration_score = 1.0 if declared else 0.0

        community_resilience_index = _mean([
            reachability_score,
            external_independence_index,
            continuity_score,
            dependency_readiness,
            governance_score,
        ])

        community_node_certification_index = _mean([
            declaration_score,
            consent_score,
            reachability_score,
            governance_score,
            identity_score,
            continuity_score,
            traceability_score,
            reversibility_score,
            non_closure_score,
            external_independence_index,
            dependency_readiness,
        ])

        community_node_count = 1 if (
            declared
            and consent_score >= 1.0
            and governance_acknowledged
            and (reachable or not require_reachability)
            and external_independence_index >= 0.99
        ) else 0

        community_validation_passed = bool(
            community_node_count >= 1
            and community_node_certification_index >= 0.86
            and community_resilience_index >= 0.84
            and governance_score >= 0.85
            and non_closure_score >= 0.85
        )

        payload = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "community_node_id": node_id,
            "host": host,
            "provider": provider,
            "operator": operator,
            "community_node_declared": declared,
            "operator_consent": operator_consent,
            "governance_acknowledged": governance_acknowledged,
            "community_node_reachable": reachable,
            "require_reachability": require_reachability,
            "community_node_count": community_node_count,
            "community_node_certified": community_validation_passed,
            "community_validation_passed": community_validation_passed,
            "community_node_certification_index": round(community_node_certification_index, 6),
            "community_resilience_index": round(community_resilience_index, 6),
            "external_independence_index": round(external_independence_index, 6),
            "community_node_governance_alignment": round(governance_score, 6),
            "community_node_identity_alignment": round(identity_score, 6),
            "community_node_continuity_alignment": round(continuity_score, 6),
            "traceability_score": round(traceability_score, 6),
            "reversibility_score": round(reversibility_score, 6),
            "non_closure_score": round(non_closure_score, 6),
            "dependency_readiness": round(dependency_readiness, 6),
            "available_dependencies": available_dependencies,
            "missing_dependencies": missing_dependencies,
            "classification": (
                "Real Community Node Certified"
                if community_validation_passed
                else "Real Community Node Not Certified"
            ),
            "history_path": str(self.history_path),
            "epistemic_boundary": "functional infrastructure validation only; no phenomenal subjectivity claim",
            "diagnostics": {
                "non_redundant_role": "real_external_community_node_certification",
                "simulated_unreachable": simulate_unreachable,
                "port": port,
                "timeout_seconds": timeout_seconds,
                "reachability_probe_governance": self._last_reachability_diagnostic if require_reachability else "not_required",
                "network_dimension_mediated": True,
                "closure_pressure_added": 0.0,
            },
        }

        payload["record_checksum"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        self._persist(payload)
        return payload

    def _persist(self, payload: Dict[str, Any]) -> None:
        try:
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        except Exception:
            pass


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return RealCommunityNodeCertification().step(inputs)
