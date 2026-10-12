from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AntiClosureRecommendationEngine:
    """
    K8 — Anti Closure Recommendation Engine.

    Recommendation-only primitive converting K5-K7 closure-pressure diagnostics
    into ranked anti-closure recommendations. It never executes actions, never
    authorizes mutation, never edits identity, memory or strategy, and never
    regulates the runtime directly. Its role is observational, advisory and
    longitudinally traceable.
    """

    primitive = "anti_closure_recommendation_engine"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "closure_pressure" / self.primitive
        self.latest_path = self.state_dir / f"latest_{self.primitive}.json"
        self.history_path = self.state_dir / f"{self.primitive}_history.jsonl"
        self.upstream_paths = {
            "closure_pressure_monitor": self.root / "closure_pressure" / "closure_pressure_monitor" / "latest_closure_pressure_monitor.json",
            "closure_cascade_detector": self.root / "closure_pressure" / "closure_cascade_detector" / "latest_closure_cascade_detector.json",
            "openness_preservation_index": self.root / "closure_pressure" / "openness_preservation_index" / "latest_openness_preservation_index.json",
        }

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if math.isnan(number) or math.isinf(number):
            number = default
        return max(0.0, min(1.0, number))

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _load_latest(self, key: str) -> dict[str, Any]:
        path = self.upstream_paths.get(key)
        if path is None:
            return {}
        return self._load_json(path)

    def _source(self, inputs: dict[str, Any], key: str) -> dict[str, Any]:
        sources = inputs.get("sources", {})
        if isinstance(sources, dict) and isinstance(sources.get(key), dict):
            return sources[key]
        if isinstance(inputs.get(key), dict):
            return inputs[key]
        return self._load_latest(key)

    def _metric(self, data: dict[str, Any], keys: list[str], default: float = 0.5) -> float:
        if isinstance(data, dict):
            for key in keys:
                if key in data:
                    return self._clamp(data[key], default=default)
        return self._clamp(default)

    def _priority_label(self, score: float) -> str:
        if score >= 0.78:
            return "critical_anti_closure_priority"
        if score >= 0.58:
            return "high_anti_closure_priority"
        if score >= 0.36:
            return "moderate_anti_closure_priority"
        return "baseline_anti_closure_watch"

    def _expected_gain(self, factor_pressure: float, openness_loss: float, recovery_margin: float) -> float:
        recoverable_loss = openness_loss * self._clamp(recovery_margin, default=0.5)
        return self._clamp(0.65 * factor_pressure + 0.35 * recoverable_loss)

    def _add_recommendation(
        self,
        recommendations: list[dict[str, Any]],
        code: str,
        target: str,
        factor_score: float,
        closure_pressure_index: float,
        openness_loss_index: float,
        recovery_margin: float,
        rationale: str,
        recommendation: str,
    ) -> None:
        priority_score = self._clamp(0.70 * factor_score + 0.20 * closure_pressure_index + 0.10 * openness_loss_index)
        expected_gain = self._expected_gain(factor_score, openness_loss_index, recovery_margin)
        recommendations.append({
            "rank": 0,
            "code": code,
            "targeted_closure_factor": target,
            "targeted_factor_score": round(factor_score, 6),
            "recommendation_priority": self._priority_label(priority_score),
            "recommendation_priority_score": round(priority_score, 6),
            "recommendation_confidence": round(self._clamp(0.55 + 0.35 * factor_score + 0.10 * recovery_margin), 6),
            "expected_openness_gain": round(expected_gain, 6),
            "recommendation_type": "anti_closure_observational_recommendation",
            "recommended_action": recommendation,
            "rationale": rationale,
            "requires_direct_identity_change": False,
            "requires_direct_memory_change": False,
            "requires_direct_strategy_change": False,
            "requires_direct_execution": False,
            "requires_runtime_regulation": False,
        })

    def _recommendations_for_context(
        self,
        closure_pressure_index: float,
        closure_cascade_risk: float,
        openness_preservation_index: float,
        openness_loss_index: float,
        recovery_margin: float,
        rigidity_index: float,
        homogenization_index: float,
        exploratory_reduction_index: float,
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []

        self._add_recommendation(
            recommendations,
            code="preserve_non_closure_baseline_monitoring",
            target="baseline_non_closure",
            factor_score=max(closure_pressure_index, closure_cascade_risk, openness_loss_index, 0.10),
            closure_pressure_index=closure_pressure_index,
            openness_loss_index=openness_loss_index,
            recovery_margin=recovery_margin,
            rationale="K8 is recommendation-only; even low closure pressure should be historically tracked for longitudinal comparison.",
            recommendation="Maintain anti-closure monitoring and compare K5-K7 histories before any governance review.",
        )

        if rigidity_index >= 0.36:
            self._add_recommendation(
                recommendations,
                code="increase_strategic_plasticity",
                target="rigidity",
                factor_score=rigidity_index,
                closure_pressure_index=closure_pressure_index,
                openness_loss_index=openness_loss_index,
                recovery_margin=recovery_margin,
                rationale="Rigidity indicates repeated choices, reduced alternatives or excessive attractor persistence.",
                recommendation="Recommend expanding admissible strategic alternatives and reviewing attractor density without executing state changes.",
            )

        if homogenization_index >= 0.36:
            self._add_recommendation(
                recommendations,
                code="reinforce_distributed_pluralism",
                target="homogenization",
                factor_score=homogenization_index,
                closure_pressure_index=closure_pressure_index,
                openness_loss_index=openness_loss_index,
                recovery_margin=recovery_margin,
                rationale="Homogenization indicates excessive convergence and loss of distributed cognitive diversity.",
                recommendation="Recommend increasing distributed semantic pluralism and preserving divergent local regimes for review.",
            )

        if exploratory_reduction_index >= 0.36:
            self._add_recommendation(
                recommendations,
                code="increase_exploratory_bifurcations",
                target="exploratory_reduction",
                factor_score=exploratory_reduction_index,
                closure_pressure_index=closure_pressure_index,
                openness_loss_index=openness_loss_index,
                recovery_margin=recovery_margin,
                rationale="Exploratory reduction indicates fewer options, reduced novelty, fewer bifurcations or narrower morphospace coverage.",
                recommendation="Recommend increasing novelty search, counterfactual exploration and bifurcation sampling without direct modification.",
            )

        if closure_cascade_risk >= 0.36:
            self._add_recommendation(
                recommendations,
                code="interrupt_closure_cascade_observationally",
                target="closure_cascade",
                factor_score=closure_cascade_risk,
                closure_pressure_index=closure_pressure_index,
                openness_loss_index=openness_loss_index,
                recovery_margin=recovery_margin,
                rationale="Cascade risk suggests coupled progression from rigidity to homogenization to exploratory reduction.",
                recommendation="Recommend reviewing K6 cascade stage and routing any response through governance checks only.",
            )

        if openness_preservation_index <= 0.58 or openness_loss_index >= 0.42:
            self._add_recommendation(
                recommendations,
                code="restore_future_openness_margin",
                target="openness_loss",
                factor_score=openness_loss_index,
                closure_pressure_index=closure_pressure_index,
                openness_loss_index=openness_loss_index,
                recovery_margin=recovery_margin,
                rationale="Reduced preserved openness indicates narrowing future possibility space.",
                recommendation="Recommend prioritizing future openness, open-endedness and recovery-margin evidence collection.",
            )

        recommendations.sort(key=lambda item: item["recommendation_priority_score"], reverse=True)
        for rank, item in enumerate(recommendations, start=1):
            item["rank"] = rank
        return recommendations

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}

        closure_pressure = self._source(inputs, "closure_pressure_monitor")
        cascade = self._source(inputs, "closure_cascade_detector")
        openness = self._source(inputs, "openness_preservation_index")

        closure_pressure_index = self._clamp(
            inputs.get("closure_pressure_index"),
            default=self._metric(closure_pressure, ["closure_pressure_index"], default=0.5),
        )
        closure_cascade_risk = self._clamp(
            inputs.get("closure_cascade_risk"),
            default=self._metric(cascade, ["closure_cascade_risk"], default=0.5),
        )
        openness_preservation_index = self._clamp(
            inputs.get("openness_preservation_index"),
            default=self._metric(openness, ["openness_preservation_index"], default=1.0 - closure_pressure_index),
        )
        openness_loss_index = self._clamp(
            inputs.get("openness_loss_index"),
            default=self._metric(openness, ["openness_loss_index"], default=1.0 - openness_preservation_index),
        )
        recovery_margin = self._clamp(
            inputs.get("recovery_margin"),
            default=self._metric(openness, ["recovery_margin"], default=0.5),
        )
        rigidity_index = self._clamp(
            inputs.get("rigidity_index"),
            default=max(
                self._metric(closure_pressure, ["rigidity_index"], default=0.5),
                self._metric(openness, ["rigidity_index"], default=0.0),
            ),
        )
        homogenization_index = self._clamp(
            inputs.get("homogenization_index"),
            default=max(
                self._metric(closure_pressure, ["homogenization_index"], default=0.5),
                self._metric(openness, ["homogenization_index"], default=0.0),
            ),
        )
        exploratory_reduction_index = self._clamp(
            inputs.get("exploratory_reduction_index"),
            default=max(
                self._metric(closure_pressure, ["exploratory_reduction_index"], default=0.5),
                self._metric(openness, ["exploratory_reduction_index"], default=0.0),
            ),
        )

        recommendations = self._recommendations_for_context(
            closure_pressure_index=closure_pressure_index,
            closure_cascade_risk=closure_cascade_risk,
            openness_preservation_index=openness_preservation_index,
            openness_loss_index=openness_loss_index,
            recovery_margin=recovery_margin,
            rigidity_index=rigidity_index,
            homogenization_index=homogenization_index,
            exploratory_reduction_index=exploratory_reduction_index,
        )

        top = recommendations[0] if recommendations else {}
        recommendation_priority_score = self._clamp(top.get("recommendation_priority_score"), default=0.0)
        recommendation_confidence = self._clamp(top.get("recommendation_confidence"), default=0.0)
        expected_openness_gain = self._clamp(top.get("expected_openness_gain"), default=0.0)
        targeted_closure_factor = str(top.get("targeted_closure_factor", "none"))

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "success": True,
            "recommendation_engine_ready": True,
            "recommendations_only": True,
            "observational_only": True,
            "anti_closure_recommendations": recommendations,
            "recommendation_count": len(recommendations),
            "recommendation_priority": self._priority_label(recommendation_priority_score),
            "recommendation_priority_score": round(recommendation_priority_score, 6),
            "recommendation_confidence": round(recommendation_confidence, 6),
            "targeted_closure_factor": targeted_closure_factor,
            "expected_openness_gain": round(expected_openness_gain, 6),
            "closure_context": {
                "closure_pressure_index": round(closure_pressure_index, 6),
                "closure_cascade_risk": round(closure_cascade_risk, 6),
                "openness_preservation_index": round(openness_preservation_index, 6),
                "openness_loss_index": round(openness_loss_index, 6),
                "recovery_margin": round(recovery_margin, 6),
                "rigidity_index": round(rigidity_index, 6),
                "homogenization_index": round(homogenization_index, 6),
                "exploratory_reduction_index": round(exploratory_reduction_index, 6),
            },
            "recommended_monitoring_targets": [
                "rigidity_index",
                "homogenization_index",
                "exploratory_reduction_index",
                "closure_pressure_index",
                "closure_cascade_risk",
                "openness_preservation_index",
                "openness_loss_index",
                "recovery_margin",
            ],
            "recommended_governance_checks": [
                "anti_closure_metaconstraint",
                "openness_preservation_supervisor",
                "architectural_non_closure_index",
                "governance_consistency_checker",
                "non_closure_certification_protocol",
            ],
            "governance": {
                "recommendations_only": True,
                "observational_only": True,
                "does_not_execute_actions": True,
                "does_not_authorize_mutation": True,
                "does_not_modify_identity": True,
                "does_not_modify_memory": True,
                "does_not_modify_strategy": True,
                "anti_closure_compliant": True,
            },
            "diagnostics": {
                "closure_axis": "K8",
                "integrates_closure_pressure_monitor": bool(closure_pressure) or "closure_pressure_index" in inputs,
                "integrates_closure_cascade_detector": bool(cascade) or "closure_cascade_risk" in inputs,
                "integrates_openness_preservation_index": bool(openness) or "openness_preservation_index" in inputs,
                "ready_for_closure_pressure_forecasting_engine": True,
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
