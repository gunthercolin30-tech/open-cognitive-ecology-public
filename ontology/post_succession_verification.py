'''
U9 — Post Succession Verification.

This primitive verifies the functional stability of a representative succession
after U8 has executed the transition. It measures post-transition stability,
continuity validation, anomaly pressure, and recovery requirements. It validates
only observable computational properties and does not assert phenomenal
subjectivity.
'''
from __future__ import annotations
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
SUCCESSION_EXECUTION_PATH = STATE_DIR / "succession_execution.json"
STATE_PATH = STATE_DIR / "post_succession_verification.json"
HISTORY_PATH = STATE_DIR / "post_succession_verification_history.jsonl"

PRIMITIVE = "post_succession_verification"

DEPENDENCIES = [
    "succession_execution_protocol",
    "distributed_identity_persistence_validator",
    "failover_continuity_validator",
    "historical_state_reconciliation",
    "civilizational_continuity_guardian",
    "identity_drift_monitor",
    "memory_transmission_protocol",
    "metrics_history_recorder",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _write_json(path: Path, payload: Mapping[str, Any], *, filesystem_context: Any, slot: str) -> None:
    if filesystem_context is None:
        raise RuntimeError("governed_filesystem_context_required")
    parent_rel = str(path.parent.relative_to(filesystem_context.root_path))
    rel = str(path.relative_to(filesystem_context.root_path))
    filesystem_context.execute_path(slot=slot + "_parent", operation_id="FS_CREATE_DIR", path=parent_rel)
    filesystem_context.execute_path(slot=slot, operation_id="FS_WRITE_REPLACE_BYTES", path=rel, payload=(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _append_jsonl(path: Path, payload: Mapping[str, Any], *, evidence_bridge: Any, evidence_decision: Any, slot: str) -> None:
    if evidence_bridge is None or evidence_decision is None:
        raise RuntimeError("governed_evidence_context_required")
    rel = str(path.relative_to(evidence_bridge.filesystem_context.root_path))
    evidence_bridge.execute_path(decision=evidence_decision, evidence_role=evidence_decision.evidence_role, slot=slot, operation_id="FS_APPEND_BYTES", path=rel, payload=(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=str)
    return [value]


class PostSuccessionVerification:
    '''Functional verification layer after representative succession execution.'''

    primitive = PRIMITIVE

    def __init__(
        self,
        state_dir: str | Path | None = None,
        warning_threshold: float = 0.70,
        valid_threshold: float = 0.80,
        stable_threshold: float = 0.90,
    ) -> None:
        self.state_dir = Path(state_dir) if state_dir else STATE_DIR
        self.warning_threshold = _clamp(warning_threshold, 0.70)
        self.valid_threshold = _clamp(valid_threshold, 0.80)
        self.stable_threshold = _clamp(stable_threshold, 0.90)
        self.execution_path = self.state_dir / "succession_execution.json"
        self.state_path = self.state_dir / "post_succession_verification.json"
        self.history_path = self.state_dir / "post_succession_verification_history.jsonl"

    def _execution_state(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("succession_execution") or inputs.get("u8_result")
        if isinstance(explicit, dict):
            return dict(explicit)
        return _as_dict(_read_json(self.execution_path, {}))

    def _score_bundle(self, inputs: dict[str, Any], execution: dict[str, Any]) -> dict[str, float]:
        continuity = _as_dict(inputs.get("continuity_validation") or inputs.get("continuity") or {})
        distributed = _as_dict(inputs.get("distributed_identity_validation") or {})
        failover = _as_dict(inputs.get("failover_validation") or {})
        reconciliation = _as_dict(inputs.get("historical_reconciliation") or {})
        guardian = _as_dict(inputs.get("civilizational_continuity") or {})

        execution_score = _clamp(
            inputs.get(
                "execution_authorization_score",
                execution.get("execution_authorization_score", execution.get("continuity_execution_score", 0.0)),
            )
        )
        identity_score = _clamp(
            inputs.get(
                "identity_persistence_score",
                distributed.get("identity_persistence_score", distributed.get("distributed_identity_score", 1.0)),
            ),
            1.0,
        )
        memory_score = _clamp(
            inputs.get(
                "memory_continuity_score",
                continuity.get("memory_continuity_score", execution.get("transmission_quality_score", 1.0)),
            ),
            1.0,
        )
        constitutional_score = _clamp(
            inputs.get(
                "constitutional_continuity_score",
                continuity.get("constitutional_continuity_score", execution.get("constitutional_continuity_score", 1.0)),
            ),
            1.0,
        )
        historical_score = _clamp(
            inputs.get(
                "historical_reconciliation_score",
                reconciliation.get("historical_reconciliation_score", reconciliation.get("reconciliation_score", 1.0)),
            ),
            1.0,
        )
        failover_score = _clamp(
            inputs.get(
                "failover_continuity_score",
                failover.get("failover_continuity_score", failover.get("continuity_score", 1.0)),
            ),
            1.0,
        )
        civilizational_score = _clamp(
            inputs.get(
                "civilizational_continuity_score",
                guardian.get("civilizational_continuity_score", guardian.get("continuity_guardian_score", 1.0)),
            ),
            1.0,
        )
        transition_stability = _clamp(
            inputs.get(
                "post_transition_stability",
                inputs.get("transition_stability", (execution_score + identity_score + memory_score) / 3.0),
            )
        )
        anomaly_pressure = _clamp(inputs.get("anomaly_pressure", inputs.get("transition_anomaly_score", 0.0)))
        identity_drift = _clamp(inputs.get("identity_drift_score", 0.0))
        memory_loss = _clamp(inputs.get("memory_loss_ratio", 0.0))
        constitutional_regression = _clamp(inputs.get("constitutional_regression_score", 0.0))

        return {
            "execution_score": execution_score,
            "identity_persistence_score": identity_score,
            "memory_continuity_score": memory_score,
            "constitutional_continuity_score": constitutional_score,
            "historical_reconciliation_score": historical_score,
            "failover_continuity_score": failover_score,
            "civilizational_continuity_score": civilizational_score,
            "post_transition_stability": transition_stability,
            "anomaly_pressure": anomaly_pressure,
            "identity_drift_score": identity_drift,
            "memory_loss_ratio": memory_loss,
            "constitutional_regression_score": constitutional_regression,
        }

    def _detect_anomalies(self, execution: dict[str, Any], scores: dict[str, float]) -> list[str]:
        anomalies: list[str] = []
        if not execution:
            anomalies.append("missing_succession_execution_state")
        elif execution.get("succession_executed") is not True:
            anomalies.append("succession_not_executed")
        if scores["identity_persistence_score"] < self.warning_threshold:
            anomalies.append("identity_persistence_degradation")
        if scores["memory_continuity_score"] < self.warning_threshold:
            anomalies.append("memory_continuity_degradation")
        if scores["constitutional_continuity_score"] < self.warning_threshold:
            anomalies.append("constitutional_continuity_degradation")
        if scores["historical_reconciliation_score"] < self.warning_threshold:
            anomalies.append("historical_reconciliation_degradation")
        if scores["failover_continuity_score"] < self.warning_threshold:
            anomalies.append("failover_continuity_degradation")
        if scores["civilizational_continuity_score"] < self.warning_threshold:
            anomalies.append("civilizational_continuity_degradation")
        if scores["anomaly_pressure"] > 0.30:
            anomalies.append("transition_anomaly_pressure")
        if scores["identity_drift_score"] > 0.30:
            anomalies.append("post_succession_identity_drift")
        if scores["memory_loss_ratio"] > 0.30:
            anomalies.append("post_succession_memory_loss")
        if scores["constitutional_regression_score"] > 0.20:
            anomalies.append("post_succession_constitutional_regression")
        return anomalies

    def step(self, inputs: Mapping[str, Any] | None = None, *, filesystem_context: Any = None, evidence_bridge: Any = None, evidence_decision: Any = None, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if isinstance(inputs, Mapping):
            payload.update(dict(inputs))
        payload.update(kwargs)

        timestamp = str(payload.get("timestamp_utc") or _now())
        execution = self._execution_state(payload)
        scores = self._score_bundle(payload, execution)
        anomalies = self._detect_anomalies(execution, scores)

        positive_scores = [
            scores["execution_score"],
            scores["identity_persistence_score"],
            scores["memory_continuity_score"],
            scores["constitutional_continuity_score"],
            scores["historical_reconciliation_score"],
            scores["failover_continuity_score"],
            scores["civilizational_continuity_score"],
            scores["post_transition_stability"],
        ]
        negative_pressure = (
            scores["anomaly_pressure"]
            + scores["identity_drift_score"]
            + scores["memory_loss_ratio"]
            + scores["constitutional_regression_score"]
        ) / 4.0
        continuity_validation_score = _clamp((sum(positive_scores) / len(positive_scores)) * (1.0 - negative_pressure))
        post_transition_stability = _clamp((scores["post_transition_stability"] + continuity_validation_score) / 2.0)

        if continuity_validation_score >= self.stable_threshold and not anomalies:
            decision = "post_succession_stable"
            recovery_required = False
        elif continuity_validation_score >= self.valid_threshold and len(anomalies) <= 1:
            decision = "post_succession_validated_with_observation"
            recovery_required = False
        elif continuity_validation_score >= self.warning_threshold:
            decision = "post_succession_warning"
            recovery_required = True
        else:
            decision = "post_succession_failure"
            recovery_required = True

        verification_event = {
            "event_id": str(payload.get("verification_event_id") or f"PSV-{timestamp}"),
            "event_type": "post_succession_verification",
            "timestamp_utc": timestamp,
            "source_succession_event_id": execution.get("succession_event", {}).get("event_id")
            if isinstance(execution.get("succession_event"), dict)
            else execution.get("succession_event_id"),
        }

        result = {
            "primitive": PRIMITIVE,
            "success": True,
            "verification_event": verification_event,
            "succession_executed": execution.get("succession_executed") is True,
            "post_transition_stability": post_transition_stability,
            "continuity_validation_score": continuity_validation_score,
            "continuity_validation": decision in {
                "post_succession_stable",
                "post_succession_validated_with_observation",
            },
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "recovery_required": recovery_required,
            "verification_decision": decision,
            "scores": scores,
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "epistemic_status": "functional_measurement_only",
                "phenomenal_subjectivity_claimed": False,
                "non_closure_compliant": True,
            },
        }

        if not bool(payload.get("dry_run", False)):
            if filesystem_context is None:
                raise RuntimeError("governed_filesystem_context_required")
            if evidence_bridge is None or evidence_decision is None:
                raise RuntimeError("governed_evidence_context_required")
            _write_json(self.state_path, result, filesystem_context=filesystem_context, slot="state_write")
            _append_jsonl(self.history_path, result, evidence_bridge=evidence_bridge, evidence_decision=evidence_decision, slot="history_append")
        return result


__all__ = ["PostSuccessionVerification"]
