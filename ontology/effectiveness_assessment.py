from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EffectivenessAssessment:
    '\n    L11 — Effectiveness Assessment.\n\n    Convert L10 outcome monitoring records into governed effectiveness metrics.\n    This module does not modify policy directly. It measures goal achievement,\n    side effects, and overall effectiveness, then prepares structured evidence\n    for L12 adaptive_policy_update.\n    '

    primitive = "effectiveness_assessment"
    axis = "L11"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "governance" / "effectiveness_assessment"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.state_dir / "effectiveness_assessment_history.jsonl"
        self.latest_path = self.state_dir / "latest_effectiveness_assessment.json"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            f = float(value)
        except (TypeError, ValueError):
            f = default
        if f < 0.0:
            return 0.0
        if f > 1.0:
            return 1.0
        return f

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return sorted(value)
        return [value]

    @staticmethod
    def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
        basis = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
        return f"{prefix}-{digest}"

    def _goal_achievement_score(self, data: dict[str, Any]) -> float:
        if "goal_progress" in data:
            return self._clamp(data.get("goal_progress"))

        expected = self._as_list(data.get("expected_outcomes"))
        observed = self._as_list(data.get("observed_outcomes"))
        if expected:
            observed_set = set(map(str, observed))
            matched = sum(1 for x in expected if str(x) in observed_set)
            return self._clamp(matched / len(expected))

        status = str(data.get("monitoring_status") or data.get("execution_status") or "").lower()
        if status in {"matched", "completed", "completed_without_expected_outcomes"}:
            return 1.0
        if "rolled_back" in status:
            return 0.2
        if "failed" in status or "aborted" in status:
            return 0.0
        return 0.0

    def _side_effect_score(self, data: dict[str, Any]) -> float:
        if "side_effect_score" in data:
            return self._clamp(data.get("side_effect_score"))

        unexpected = self._as_list(data.get("unexpected_effects"))
        adverse = self._as_list(data.get("adverse_effects"))
        side_effects = unexpected + adverse

        if not side_effects:
            return 0.0

        explicit_severity = data.get("side_effect_severity")
        if explicit_severity is not None:
            return self._clamp(explicit_severity)

        # Bounded monotone penalty: 1 effect => 0.25, 2 => 0.5, 3 => 0.75, 4+ => 1.0.
        return self._clamp(len(side_effects) / 4.0)

    def _execution_quality_modifier(self, data: dict[str, Any]) -> float:
        status = str(data.get("execution_status") or data.get("monitoring_status") or "").lower()
        rollback_status = str(data.get("rollback_status") or "").lower()

        if "rolled_back" in status or rollback_status == "completed":
            return 0.35
        if "failed" in status:
            return 0.15
        if "aborted" in status:
            return 0.0
        if "pending" in status:
            return 0.0
        return 1.0

    @staticmethod
    def _classify(effectiveness_score: float, side_effect_score: float) -> str:
        if effectiveness_score >= 0.85 and side_effect_score <= 0.10:
            return "highly_effective"
        if effectiveness_score >= 0.60 and side_effect_score <= 0.35:
            return "effective"
        if effectiveness_score >= 0.30:
            return "partially_effective"
        if side_effect_score >= 0.60:
            return "harmful_or_unstable"
        return "ineffective"

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if isinstance(inputs, dict):
            data.update(inputs)
        data.update(kwargs)

        goal_achievement_score = self._goal_achievement_score(data)
        side_effect_score = self._side_effect_score(data)
        execution_modifier = self._execution_quality_modifier(data)
        effectiveness_score = self._clamp(goal_achievement_score * (1.0 - side_effect_score) * execution_modifier)
        classification = self._classify(effectiveness_score, side_effect_score)

        assessment_payload = {
            "execution_request_id": data.get("execution_request_id"),
            "outcome_monitoring_id": data.get("outcome_monitoring_id"),
            "execution_id": data.get("execution_id"),
            "goal_achievement_score": goal_achievement_score,
            "side_effect_score": side_effect_score,
            "execution_quality_modifier": execution_modifier,
            "effectiveness_score": effectiveness_score,
            "effectiveness_classification": classification,
        }

        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": self._now(),
            "effectiveness_assessment_id": self._stable_id("EA", assessment_payload),
            "execution_request_id": data.get("execution_request_id"),
            "outcome_monitoring_id": data.get("outcome_monitoring_id"),
            "execution_id": data.get("execution_id"),
            "execution_status": data.get("execution_status"),
            "monitoring_status": data.get("monitoring_status"),
            "goal_achievement_score": goal_achievement_score,
            "side_effect_score": side_effect_score,
            "execution_quality_modifier": execution_modifier,
            "effectiveness_score": effectiveness_score,
            "effectiveness_classification": classification,
            "unexpected_effects": self._as_list(data.get("unexpected_effects")),
            "observed_effects": self._as_list(data.get("observed_effects", data.get("observed_outcomes"))),
            "expected_effects": self._as_list(data.get("expected_effects", data.get("expected_outcomes"))),
            "requires_policy_update_assessment": True,
            "l12_ready": True,
            "policy_update_signal": classification in {"partially_effective", "ineffective", "harmful_or_unstable"},
            "diagnostics": {
                "non_direct_policy_modification": True,
                "governed_measurement_only": True,
                "side_effect_score_semantics": "0=no_side_effect, 1=severe_side_effects",
            },
        }

        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return result
