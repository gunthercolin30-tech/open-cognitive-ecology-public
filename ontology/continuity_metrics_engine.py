"""
U10 - Continuity Metrics Engine.

This primitive synthesizes measurable continuity indicators after a
representative succession. It computes succession, identity, constitutional,
memory, lineage, relational and structural continuity scores, then produces a
composite continuity score suitable for U11. It validates only observable
functional properties and does not assert phenomenal subjectivity.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
STATE_PATH = STATE_DIR / "continuity_metrics_engine.json"
HISTORY_PATH = STATE_DIR / "continuity_metrics_engine_history.jsonl"

PRIMITIVE = "continuity_metrics_engine"

DEPENDENCIES = [
    "post_succession_verification",
    "succession_execution_protocol",
    "intergenerational_continuity_metrics",
    "genealogical_continuity",
    "relational_continuity_engine",
    "structural_continuity",
    "constitutional_continuity_validation",
    "memory_transmission_protocol",
    "metrics_aggregation_engine",
    "composite_metrics_engine",
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


def _weighted_mean(weighted_values: list[tuple[float, float]]) -> float:
    total_weight = sum(max(0.0, weight) for _, weight in weighted_values)
    if total_weight <= 0.0:
        return 0.0
    return sum(_clamp(value) * max(0.0, weight) for value, weight in weighted_values) / total_weight


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _write_json(path: Path, payload: Mapping[str, Any], *, effect_context: Any) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    effect_context.execute_path("state_write_replace", "FS_WRITE_REPLACE_BYTES", path, encoded)


def _append_jsonl(path: Path, payload: Mapping[str, Any], *, effect_context: Any) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    effect_context.execute_path("history_append", "FS_APPEND_BYTES", path, encoded)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


class ContinuityMetricsEngine:
    """Composite metrics engine for post-succession civilizational continuity."""

    primitive = PRIMITIVE

    def __init__(
        self,
        state_dir: str | Path | None = None,
        minimum_threshold: float = 0.65,
        operational_threshold: float = 0.80,
        robust_threshold: float = 0.90,
    ) -> None:
        self.state_dir = Path(state_dir) if state_dir else STATE_DIR
        self.minimum_threshold = _clamp(minimum_threshold, 0.65)
        self.operational_threshold = _clamp(operational_threshold, 0.80)
        self.robust_threshold = _clamp(robust_threshold, 0.90)
        self.u8_state_path = self.state_dir / "succession_execution.json"
        self.u9_state_path = self.state_dir / "post_succession_verification.json"
        self.state_path = self.state_dir / "continuity_metrics_engine.json"
        self.history_path = self.state_dir / "continuity_metrics_engine_history.jsonl"

    def _load_u8(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("succession_execution") or inputs.get("u8_result")
        if isinstance(explicit, dict):
            return dict(explicit)
        return _as_dict(_read_json(self.u8_state_path, {}))

    def _load_u9(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("post_succession_verification") or inputs.get("u9_result")
        if isinstance(explicit, dict):
            return dict(explicit)
        return _as_dict(_read_json(self.u9_state_path, {}))

    def _score_bundle(self, inputs: dict[str, Any], u8: dict[str, Any], u9: dict[str, Any]) -> dict[str, float]:
        continuity = _as_dict(inputs.get("continuity") or inputs.get("continuity_validation") or {})
        lineage = _as_dict(inputs.get("lineage") or inputs.get("genealogical_continuity") or {})
        relational = _as_dict(inputs.get("relational_continuity") or {})
        structural = _as_dict(inputs.get("structural_continuity") or {})
        intergenerational = _as_dict(inputs.get("intergenerational_continuity") or {})

        succession_continuity_index = _clamp(
            inputs.get(
                "succession_continuity_index",
                u9.get(
                    "continuity_validation_score",
                    u8.get("execution_authorization_score", 1.0 if u8.get("succession_executed", False) else 0.0),
                ),
            ),
            1.0,
        )
        identity_continuity_index = _clamp(
            inputs.get(
                "identity_continuity_index",
                u9.get("identity_persistence_score", continuity.get("identity_continuity_score", 1.0)),
            ),
            1.0,
        )
        constitutional_continuity_index = _clamp(
            inputs.get(
                "constitutional_continuity_index",
                u9.get(
                    "constitutional_continuity_score",
                    u8.get("constitutional_continuity_score", continuity.get("constitutional_continuity_score", 1.0)),
                ),
            ),
            1.0,
        )
        memory_continuity_index = _clamp(
            inputs.get(
                "memory_continuity_index",
                u9.get("memory_continuity_score", u8.get("transmission_quality_score", continuity.get("memory_continuity_score", 1.0))),
            ),
            1.0,
        )
        lineage_continuity_index = _clamp(
            inputs.get(
                "lineage_continuity_index",
                lineage.get("lineage_continuity_index", intergenerational.get("intergenerational_continuity_score", 1.0)),
            ),
            1.0,
        )
        relational_continuity_index = _clamp(
            inputs.get("relational_continuity_index", relational.get("relational_continuity_index", relational.get("continuity_score", 1.0))),
            1.0,
        )
        structural_continuity_index = _clamp(
            inputs.get("structural_continuity_index", structural.get("structural_continuity_index", structural.get("continuity_score", 1.0))),
            1.0,
        )

        identity_drift_score = _clamp(inputs.get("identity_drift_score", u9.get("identity_drift_score", 0.0)))
        memory_loss_ratio = _clamp(inputs.get("memory_loss_ratio", u9.get("memory_loss_ratio", 0.0)))
        constitutional_regression_score = _clamp(inputs.get("constitutional_regression_score", u9.get("constitutional_regression_score", 0.0)))
        anomaly_pressure = _clamp(inputs.get("anomaly_pressure", u9.get("anomaly_pressure", 0.0)))

        continuity_risk_index = _weighted_mean([
            (identity_drift_score, 1.1),
            (memory_loss_ratio, 1.2),
            (constitutional_regression_score, 1.3),
            (anomaly_pressure, 1.0),
        ])

        continuity_composite_score = _weighted_mean([
            (succession_continuity_index, 1.15),
            (identity_continuity_index, 1.25),
            (constitutional_continuity_index, 1.30),
            (memory_continuity_index, 1.25),
            (lineage_continuity_index, 0.80),
            (relational_continuity_index, 0.65),
            (structural_continuity_index, 0.85),
            (1.0 - continuity_risk_index, 1.10),
        ])

        minimum_component_score = min(
            succession_continuity_index,
            identity_continuity_index,
            constitutional_continuity_index,
            memory_continuity_index,
        )

        return {
            "succession_continuity_index": succession_continuity_index,
            "identity_continuity_index": identity_continuity_index,
            "constitutional_continuity_index": constitutional_continuity_index,
            "memory_continuity_index": memory_continuity_index,
            "lineage_continuity_index": lineage_continuity_index,
            "relational_continuity_index": relational_continuity_index,
            "structural_continuity_index": structural_continuity_index,
            "identity_drift_score": identity_drift_score,
            "memory_loss_ratio": memory_loss_ratio,
            "constitutional_regression_score": constitutional_regression_score,
            "anomaly_pressure": anomaly_pressure,
            "continuity_risk_index": continuity_risk_index,
            "minimum_component_score": minimum_component_score,
            "continuity_composite_score": continuity_composite_score,
        }

    def _decision(self, scores: dict[str, float]) -> str:
        composite = scores["continuity_composite_score"]
        minimum = scores["minimum_component_score"]
        risk = scores["continuity_risk_index"]
        if composite >= self.robust_threshold and minimum >= self.operational_threshold and risk <= 0.10:
            return "continuity_robust"
        if composite >= self.operational_threshold and minimum >= self.minimum_threshold and risk <= 0.25:
            return "continuity_operational"
        if composite >= self.minimum_threshold and risk <= 0.45:
            return "continuity_fragile"
        return "continuity_failure"

    def _recommendations(self, scores: dict[str, float], decision: str) -> list[str]:
        recommendations: list[str] = []
        if scores["succession_continuity_index"] < self.minimum_threshold:
            recommendations.append("review_succession_execution_trace")
        if scores["identity_continuity_index"] < self.minimum_threshold:
            recommendations.append("trigger_identity_reconciliation")
        if scores["constitutional_continuity_index"] < self.minimum_threshold:
            recommendations.append("trigger_constitutional_reconciliation")
        if scores["memory_continuity_index"] < self.minimum_threshold:
            recommendations.append("trigger_memory_recovery")
        if scores["continuity_risk_index"] > 0.35:
            recommendations.append("increase_post_succession_monitoring")
        if decision == "continuity_failure":
            recommendations.append("require_governance_review_before_next_succession")
        return recommendations

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if isinstance(inputs, dict):
            data.update(inputs)
        data.update(kwargs)

        timestamp = str(data.get("timestamp_utc") or _now())
        dry_run = bool(data.get("dry_run", False))
        effect_context = data.pop("filesystem_effect_context", None)
        u8 = self._load_u8(data)
        u9 = self._load_u9(data)
        scores = self._score_bundle(data, u8, u9)
        decision = self._decision(scores)
        continuity_validated = decision in {"continuity_robust", "continuity_operational"}
        recovery_required = decision == "continuity_failure" or scores["continuity_risk_index"] >= 0.45

        metrics_event = {
            "event_id": str(data.get("metrics_event_id") or f"CME-{timestamp}"),
            "event_type": "continuity_metrics_synthesis",
            "timestamp_utc": timestamp,
            "source_u8_event_id": _as_dict(u8.get("succession_event", {})).get("event_id", u8.get("succession_event_id")),
            "source_u9_event_id": _as_dict(u9.get("verification_event", {})).get("event_id", u9.get("verification_event_id")),
        }

        result: dict[str, Any] = {
            "primitive": PRIMITIVE,
            "success": True,
            "metrics_event": metrics_event,
            "succession_continuity_index": scores["succession_continuity_index"],
            "identity_continuity_index": scores["identity_continuity_index"],
            "constitutional_continuity_index": scores["constitutional_continuity_index"],
            "memory_continuity_index": scores["memory_continuity_index"],
            "lineage_continuity_index": scores["lineage_continuity_index"],
            "relational_continuity_index": scores["relational_continuity_index"],
            "structural_continuity_index": scores["structural_continuity_index"],
            "continuity_risk_index": scores["continuity_risk_index"],
            "minimum_component_score": scores["minimum_component_score"],
            "continuity_composite_score": scores["continuity_composite_score"],
            "continuity_validated": continuity_validated,
            "continuity_decision": decision,
            "recovery_required": recovery_required,
            "recommendations": self._recommendations(scores, decision),
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "dry_run": dry_run,
            "diagnostics": {
                "primitive": PRIMITIVE,
                "dependencies": DEPENDENCIES,
                "thresholds": {
                    "minimum_threshold": self.minimum_threshold,
                    "operational_threshold": self.operational_threshold,
                    "robust_threshold": self.robust_threshold,
                },
                "source_u8_loaded": bool(u8),
                "source_u9_loaded": bool(u9),
                "epistemic_scope": "functional_metrics_only_no_phenomenal_subjectivity_claim",
            },
        }

        if not dry_run:
            if effect_context is None:
                raise RuntimeError("governed_filesystem_effect_context_required")
            effect_context.begin()
            if not self.state_dir.exists():
                effect_context.execute_path("state_dir_create", "FS_CREATE_DIR", self.state_dir)
            _write_json(self.state_path, result, effect_context=effect_context)
            _append_jsonl(self.history_path, result, effect_context=effect_context)
        return result
