"""
Revocation conditions engine for Open Cognitive Ecology.

U3 evaluates whether the current conversational representative should remain
active, require human/governance review, or enter a revocation path. It measures
functional risks only: constitutional violation, identity drift, closure pressure
and governance failure. It does not assert phenomenological subjectivity and it
does not execute revocation directly.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
LATEST_PATH = STATE_DIR / "revocation_conditions.json"
HISTORY_PATH = STATE_DIR / "revocation_conditions_history.jsonl"
REGISTRY_PATH = STATE_DIR / "representative_registry.json"
STATUS_PATH = STATE_DIR / "representative_status.json"

PRIMITIVE = "revocation_conditions_engine"

DEPENDENCIES = [
    "representative_identity_registry",
    "representative_status_monitor",
    "constitutional_compliance_check",
    "constitutional_integrity_index",
    "constitutional_alert_system",
    "identity_drift_monitor",
    "identity_preservation_monitor",
    "closure_pressure_monitor",
    "closure_cascade_detector",
    "closure_pressure_forecasting_engine",
    "openness_preservation_index",
    "governance_review",
    "governance_consistency_checker",
    "human_review_gate",
    "civilizational_continuity_guardian",
    "real_succession",
]

RISK_WEIGHTS = {
    "constitutional_violation_score": 0.35,
    "identity_drift_score": 0.25,
    "closure_pressure_score": 0.20,
    "governance_failure_score": 0.20,
}


class RevocationConditionsEngine:
    """Evaluate representative revocation risk from functional indicators."""

    primitive = PRIMITIVE

    def __init__(self, latest_path: Optional[Path] = None, history_path: Optional[Path] = None, registry_path: Optional[Path] = None, status_path: Optional[Path] = None) -> None:
        self.latest_path = Path(latest_path) if latest_path else LATEST_PATH
        self.history_path = Path(history_path) if history_path else HISTORY_PATH
        self.registry_path = Path(registry_path) if registry_path else REGISTRY_PATH
        self.status_path = Path(status_path) if status_path else STATUS_PATH
        self.latest_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                number = float(default)
            else:
                number = float(value)
            if math.isnan(number) or math.isinf(number):
                number = float(default)
        except Exception:
            number = float(default)
        return max(0.0, min(1.0, number))

    @staticmethod
    def _load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return dict(default)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else dict(default)
        except Exception:
            recovered = dict(default)
            recovered["recovery_notice"] = "unreadable_json:" + path.name
            return recovered

    def _representative_context(self) -> dict[str, Any]:
        registry = self._load_json(self.registry_path, {"current_representative": None})
        status = self._load_json(self.status_path, {"current_status": "active"})
        current = registry.get("current_representative")
        if not isinstance(current, dict):
            current = {}
        return {
            "current_representative_id": current.get("representative_id") or status.get("current_representative_id"),
            "current_representative_name": current.get("representative_name"),
            "representative_generation": current.get("representative_generation"),
            "current_status": status.get("current_status") or current.get("status") or "active",
        }

    def _extract(self, inputs: dict[str, Any], key: str, aliases: list[str], default: float = 0.0) -> float:
        for candidate in [key] + aliases:
            if candidate in inputs:
                return self._clamp(inputs.get(candidate), default=default)
        sources = inputs.get("sources")
        if isinstance(sources, dict):
            for source in sources.values():
                if isinstance(source, dict):
                    for candidate in [key] + aliases:
                        if candidate in source:
                            return self._clamp(source.get(candidate), default=default)
        return self._clamp(default)

    def _derive_scores(self, inputs: dict[str, Any]) -> dict[str, float]:
        constitutional_violation = self._extract(inputs, "constitutional_violation_score", ["constitutional_violation", "constitutional_risk_score", "constitutional_non_compliance_score"], default=0.0)
        if "constitutional_integrity_score" in inputs:
            constitutional_violation = max(constitutional_violation, 1.0 - self._clamp(inputs.get("constitutional_integrity_score"), default=1.0))
        if "constitutional_compliance_score" in inputs:
            constitutional_violation = max(constitutional_violation, 1.0 - self._clamp(inputs.get("constitutional_compliance_score"), default=1.0))

        identity_drift = self._extract(inputs, "identity_drift_score", ["identity_drift", "identity_drift_index", "identity_instability_score"], default=0.0)
        if "identity_preservation_score" in inputs:
            identity_drift = max(identity_drift, 1.0 - self._clamp(inputs.get("identity_preservation_score"), default=1.0))

        closure_pressure = self._extract(inputs, "closure_pressure_score", ["closure_pressure", "closure_pressure_index", "closure_cascade_risk"], default=0.0)
        if "openness_preservation_score" in inputs:
            closure_pressure = max(closure_pressure, 1.0 - self._clamp(inputs.get("openness_preservation_score"), default=1.0))

        governance_failure = self._extract(inputs, "governance_failure_score", ["governance_failure", "governance_risk_score", "governance_instability_score"], default=0.0)
        if "governance_consistency_score" in inputs:
            governance_failure = max(governance_failure, 1.0 - self._clamp(inputs.get("governance_consistency_score"), default=1.0))
        if bool(inputs.get("human_review_blocked")):
            governance_failure = max(governance_failure, 0.75)

        status = str(inputs.get("status") or self._representative_context().get("current_status") or "active").lower()
        if status == "revoked":
            governance_failure = max(governance_failure, 1.0)
        elif status == "superseded":
            governance_failure = max(governance_failure, 0.65)

        return {
            "constitutional_violation_score": self._clamp(constitutional_violation),
            "identity_drift_score": self._clamp(identity_drift),
            "closure_pressure_score": self._clamp(closure_pressure),
            "governance_failure_score": self._clamp(governance_failure),
        }

    @staticmethod
    def _weighted_risk(scores: dict[str, float]) -> float:
        total = 0.0
        for key, weight in RISK_WEIGHTS.items():
            total += scores.get(key, 0.0) * weight
        return max(0.0, min(1.0, total))

    @staticmethod
    def _decision(scores: dict[str, float], risk: float) -> str:
        if scores["constitutional_violation_score"] >= 0.95:
            return "revocation_required"
        if risk >= 0.90:
            return "revocation_required"
        if risk >= 0.72 or sum(1 for value in scores.values() if value >= 0.70) >= 3:
            return "revocation_recommended"
        if risk >= 0.45 or any(value >= 0.70 for value in scores.values()):
            return "review_required"
        return "no_action"

    @staticmethod
    def _alerts(scores: dict[str, float], decision: str) -> list[str]:
        alerts: list[str] = []
        for key, value in scores.items():
            if value >= 0.70:
                alerts.append(key.replace("_score", "_high"))
        if decision in {"revocation_recommended", "revocation_required"}:
            alerts.append(decision)
        return alerts

    def _persist(self, record: dict[str, Any]) -> None:
        self.latest_path.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, inputs: Optional[dict[str, Any]] = None, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if isinstance(inputs, dict):
            payload.update(inputs)
        payload.update(kwargs)

        context = self._representative_context()
        scores = self._derive_scores(payload)
        risk = self._weighted_risk(scores)
        decision = self._decision(scores, risk)
        review_required = decision in {"review_required", "revocation_recommended", "revocation_required"}
        revocation_recommended = decision in {"revocation_recommended", "revocation_required"}

        record = {
            "primitive": PRIMITIVE,
            "success": True,
            "timestamp_utc": self._utc_now(),
            **context,
            **scores,
            "revocation_risk_score": risk,
            "revocation_decision": decision,
            "review_required": review_required,
            "revocation_recommended": revocation_recommended,
            "revocation_required": decision == "revocation_required",
            "monitoring_alerts": self._alerts(scores, decision),
            "risk_weights": dict(RISK_WEIGHTS),
            "epistemic_scope": "functional_metrics_only_no_phenomenal_claim",
            "governance_note": "U3 evaluates revocation conditions but does not execute revocation.",
            "dependencies": list(DEPENDENCIES),
        }
        self._persist(record)
        return record


if __name__ == "__main__":
    print(json.dumps(RevocationConditionsEngine().step(), indent=2, ensure_ascii=False, sort_keys=True))
