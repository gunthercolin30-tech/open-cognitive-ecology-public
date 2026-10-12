
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


class AdaptivePolicyUpdate:
    primitive = "adaptive_policy_update"
    axis = "L12"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "governance" / "adaptive_policy_update"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.state_dir / "latest_adaptive_policy_update.json"
        self.history_path = self.state_dir / "adaptive_policy_update_history.jsonl"

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
    def _stable_id(payload: dict[str, Any]) -> str:
        basis = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
        return "APU-" + digest

    @staticmethod
    def _classify_need(
        effectiveness_score: float,
        side_effect_score: float,
        goal_achievement_score: float,
        policy_update_signal: bool,
    ) -> str:
        if side_effect_score >= 0.75:
            return "urgent_corrective_review"
        if effectiveness_score < 0.35:
            return "major_policy_review"
        if effectiveness_score < 0.70 or policy_update_signal:
            return "moderate_policy_adjustment_recommended"
        if goal_achievement_score < 0.85:
            return "minor_goal_alignment_review"
        return "no_policy_update_required"

    @staticmethod
    def _build_rationale(
        need_classification: str,
        effectiveness_score: float,
        side_effect_score: float,
        goal_achievement_score: float,
        unexpected_effects: list[Any],
    ) -> str:
        return (
            "Adaptive policy update classified as "
            + need_classification
            + ": effectiveness="
            + format(effectiveness_score, ".3f")
            + ", goal_achievement="
            + format(goal_achievement_score, ".3f")
            + ", side_effect="
            + format(side_effect_score, ".3f")
            + ", unexpected_effect_count="
            + str(len(unexpected_effects))
            + ". No direct policy modification is performed."
        )

    def _recommendations(
        self,
        need_classification: str,
        effectiveness_score: float,
        side_effect_score: float,
        goal_achievement_score: float,
        unexpected_effects: list[Any],
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []

        if need_classification == "no_policy_update_required":
            return recommendations

        if goal_achievement_score < 0.85:
            recommendations.append({
                "recommendation_id": "APU-GOAL-ALIGNMENT",
                "type": "goal_alignment_review",
                "priority": round(1.0 - goal_achievement_score, 6),
                "rationale": "Goal achievement is below the preferred governance threshold.",
                "direct_policy_modification": False,
            })

        if effectiveness_score < 0.70:
            recommendations.append({
                "recommendation_id": "APU-EFFECTIVENESS-IMPROVEMENT",
                "type": "effectiveness_improvement_review",
                "priority": round(1.0 - effectiveness_score, 6),
                "rationale": "Empirical effectiveness is insufficient for stable governance.",
                "direct_policy_modification": False,
            })

        if side_effect_score > 0.0 or unexpected_effects:
            recommendations.append({
                "recommendation_id": "APU-SIDE-EFFECT-MITIGATION",
                "type": "side_effect_mitigation_review",
                "priority": round(max(side_effect_score, min(1.0, 0.2 * len(unexpected_effects))), 6),
                "rationale": "Unexpected effects or side effects were detected.",
                "unexpected_effect_count": len(unexpected_effects),
                "direct_policy_modification": False,
            })

        if need_classification == "urgent_corrective_review":
            recommendations.append({
                "recommendation_id": "APU-HUMAN-GOVERNANCE-ESCALATION",
                "type": "human_governance_review",
                "priority": 1.0,
                "rationale": "High side-effect pressure requires explicit governed review.",
                "direct_policy_modification": False,
            })

        return recommendations

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if isinstance(inputs, dict):
            data.update(inputs)
        data.update(kwargs)

        timestamp = datetime.now(timezone.utc).isoformat()

        effectiveness_score = _clamp01(
            data.get("effectiveness_score"),
            default=_clamp01(data.get("goal_progress"), 0.0),
        )
        side_effect_score = _clamp01(data.get("side_effect_score"), default=0.0)
        goal_achievement_score = _clamp01(
            data.get("goal_achievement_score"),
            default=_clamp01(data.get("goal_progress"), 0.0),
        )
        policy_update_signal = bool(data.get("policy_update_signal", False))
        unexpected_effects = self._as_list(data.get("unexpected_effects"))

        need_classification = self._classify_need(
            effectiveness_score,
            side_effect_score,
            goal_achievement_score,
            policy_update_signal,
        )

        recommendations = self._recommendations(
            need_classification,
            effectiveness_score,
            side_effect_score,
            goal_achievement_score,
            unexpected_effects,
        )

        recommendation_pressure = 0.0
        if recommendations:
            recommendation_pressure = max(float(r.get("priority", 0.0)) for r in recommendations)

        governance_learning_score = _clamp01(
            (1.0 - effectiveness_score) * 0.40
            + side_effect_score * 0.35
            + (1.0 - goal_achievement_score) * 0.25
        )

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": timestamp,
            "adaptive_policy_update_id": self._stable_id(data),
            "execution_request_id": data.get("execution_request_id"),
            "effectiveness_assessment_id": data.get("effectiveness_assessment_id"),
            "outcome_monitoring_id": data.get("outcome_monitoring_id"),
            "effectiveness_score": effectiveness_score,
            "side_effect_score": side_effect_score,
            "goal_achievement_score": goal_achievement_score,
            "policy_update_signal": policy_update_signal,
            "need_classification": need_classification,
            "policy_update_recommendations": recommendations,
            "policy_update_recommendation_count": len(recommendations),
            "recommendation_pressure": round(recommendation_pressure, 6),
            "governance_learning_score": round(governance_learning_score, 6),
            "adaptation_rationale": self._build_rationale(
                need_classification,
                effectiveness_score,
                side_effect_score,
                goal_achievement_score,
                unexpected_effects,
            ),
            "requires_governance_review": len(recommendations) > 0,
            "requires_human_review": need_classification == "urgent_corrective_review",
            "direct_policy_modification_performed": False,
            "non_direct_policy_modification": True,
            "l13_ready": True,
            "diagnostics": {
                "governed_recommendation_only": True,
                "no_policy_state_mutation": True,
                "input_from_l11_expected": True,
                "dashboard_export_ready": True,
            },
        }

        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

        return result
