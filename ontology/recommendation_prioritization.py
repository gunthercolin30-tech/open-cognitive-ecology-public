
"""
L2 — recommendation_prioritization.

Governed prioritization layer for recommendations emitted by L1
recommendation_intake. This module evaluates and ranks recommendations by
urgency, impact, risk and confidence. It does not approve, reject, defer or
execute recommendations, and it does not modify identity, memory or strategy.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        n = float(value)
        if math.isnan(n) or math.isinf(n):
            return default
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, n))


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _safe_float_from_mapping(mapping: dict[str, Any], names: list[str], default: float = 0.0) -> float:
    for name in names:
        if name in mapping:
            return _clamp01(mapping.get(name), default)
    return default


class RecommendationPrioritization:
    """L2 governed recommendation ranking. Scoring only; no decision or execution."""

    primitive = "recommendation_prioritization"
    axis = "L2"

    DEFAULT_WEIGHTS = {
        "urgency": 0.30,
        "impact": 0.30,
        "risk": 0.25,
        "confidence": 0.15,
    }

    SOURCE_CRITICALITY = {
        "anti_closure_recommendation_engine": 0.92,
        "preventive_stability_recommendation_engine": 0.86,
        "paradigm_shift_detection_engine": 0.88,
        "drift_forecasting_engine": 0.84,
        "closure_pressure_forecasting_engine": 0.90,
        "civilizational_stability_index": 0.82,
        "recommendation_intake": 0.70,
        "unknown": 0.50,
    }

    TYPE_IMPACT = {
        "anti_closure": 0.95,
        "closure": 0.92,
        "drift": 0.88,
        "stability": 0.84,
        "paradigm": 0.87,
        "constitutional": 0.93,
        "governance": 0.80,
        "observational": 0.65,
        "unspecified": 0.50,
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "governance" / "recommendation_prioritization"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.state_dir / "latest_recommendation_prioritization.json"
        self.history_path = self.state_dir / "recommendation_prioritization_history.jsonl"
        self.l1_latest_path = self.root / "governance" / "recommendation_intake" / "latest_recommendation_intake.json"

    def _load_json(self, path: Path) -> dict[str, Any] | None:
        try:
            if path.exists() and path.is_file() and path.stat().st_size <= 20_000_000:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else None
        except Exception:
            return None
        return None

    def _default_l1_payload(self) -> dict[str, Any]:
        data = self._load_json(self.l1_latest_path)
        if data is not None:
            return data
        return {
            "primitive": "recommendation_intake",
            "success": True,
            "intake_queue": [],
            "recommendation_count": 0,
        }

    def _extract_queue(self, inputs: Any) -> tuple[list[dict[str, Any]], int]:
        if inputs is None:
            payload = self._default_l1_payload()
        elif isinstance(inputs, dict) and "intake_queue" in inputs:
            payload = inputs
        elif isinstance(inputs, dict) and "recommendations" in inputs:
            payload = {"intake_queue": inputs.get("recommendations", [])}
        elif isinstance(inputs, dict) and "prioritization_inputs" in inputs:
            payload = {"intake_queue": inputs.get("prioritization_inputs", [])}
        elif isinstance(inputs, list):
            payload = {"intake_queue": inputs}
        else:
            payload = {"intake_queue": []}

        raw_items = _as_list(payload.get("intake_queue"))
        queue = [item for item in raw_items if isinstance(item, dict)]
        rejected = len(raw_items) - len(queue)
        return queue, rejected

    def _source_criticality(self, record: dict[str, Any]) -> float:
        source = str(record.get("recommendation_source") or record.get("source") or "unknown")
        if source in self.SOURCE_CRITICALITY:
            return self.SOURCE_CRITICALITY[source]
        lowered = source.lower()
        for key, value in self.SOURCE_CRITICALITY.items():
            if key != "unknown" and key in lowered:
                return value
        return self.SOURCE_CRITICALITY["unknown"]

    def _type_impact(self, record: dict[str, Any]) -> float:
        rtype = str(record.get("recommendation_type") or "unspecified").lower()
        action = str(record.get("recommended_action") or "").lower()
        text = f"{rtype} {action}"
        for key, value in self.TYPE_IMPACT.items():
            if key in text:
                return value
        return self.TYPE_IMPACT["unspecified"]

    def _governance_risk(self, record: dict[str, Any]) -> float:
        flags = record.get("governance_flags")
        if not isinstance(flags, dict):
            flags = {}
        risk = 0.0
        if flags.get("requires_direct_execution") or record.get("requires_direct_execution"):
            risk += 0.30
        if flags.get("requires_direct_identity_change") or record.get("requires_direct_identity_change"):
            risk += 0.25
        if flags.get("requires_direct_memory_change") or record.get("requires_direct_memory_change"):
            risk += 0.20
        if flags.get("requires_direct_strategy_change") or record.get("requires_direct_strategy_change"):
            risk += 0.20
        if flags.get("non_closure_compliant") is False:
            risk += 0.30
        return _clamp01(risk, 0.0)

    def _compute_scores(self, record: dict[str, Any]) -> dict[str, float]:
        severity = _safe_float_from_mapping(record, ["recommendation_severity", "severity", "recommendation_priority_score", "priority_hint_score"], 0.0)
        priority_hint = _safe_float_from_mapping(record, ["priority_hint_score", "recommendation_priority_score", "priority_score"], severity)
        confidence = _safe_float_from_mapping(record, ["recommendation_confidence", "confidence", "confidence_score"], 0.5)
        source_criticality = self._source_criticality(record)
        type_impact = self._type_impact(record)
        governance_risk = self._governance_risk(record)

        urgency = _clamp01((0.65 * severity) + (0.25 * priority_hint) + (0.10 * source_criticality), 0.0)
        impact = _clamp01((0.55 * type_impact) + (0.25 * source_criticality) + (0.20 * priority_hint), 0.0)
        risk = _clamp01((0.60 * severity) + (0.40 * governance_risk), 0.0)
        priority = _clamp01(
            self.DEFAULT_WEIGHTS["urgency"] * urgency
            + self.DEFAULT_WEIGHTS["impact"] * impact
            + self.DEFAULT_WEIGHTS["risk"] * risk
            + self.DEFAULT_WEIGHTS["confidence"] * confidence,
            0.0,
        )
        return {
            "urgency_score": urgency,
            "impact_score": impact,
            "risk_score": risk,
            "confidence_score": confidence,
            "priority_score": priority,
            "source_criticality_score": source_criticality,
            "governance_risk_score": governance_risk,
        }

    def _prioritize_record(self, record: dict[str, Any], index: int) -> dict[str, Any]:
        scores = self._compute_scores(record)
        recommendation_id = str(record.get("recommendation_id") or record.get("id") or record.get("recommendation_code") or f"REC-IN-{index:04d}")
        source = str(record.get("recommendation_source") or record.get("source") or "unknown")
        rtype = str(record.get("recommendation_type") or "unspecified_recommendation")
        rationale = str(record.get("rationale") or "Prioritized from L1 intake queue using governed urgency-impact-risk-confidence scoring.")
        action = str(record.get("recommended_action") or record.get("action") or "Route to governance review.")
        return {
            "recommendation_id": recommendation_id,
            "recommendation_source": source,
            "recommendation_type": rtype,
            "recommended_action": action,
            "rationale": rationale,
            "original_intake_rank": record.get("rank"),
            "priority_rank": None,
            "priority_score": scores["priority_score"],
            "urgency_score": scores["urgency_score"],
            "impact_score": scores["impact_score"],
            "risk_score": scores["risk_score"],
            "confidence_score": scores["confidence_score"],
            "source_criticality_score": scores["source_criticality_score"],
            "governance_risk_score": scores["governance_risk_score"],
            "priority_class": self._priority_class(scores["priority_score"]),
            "ranking_rationale": self._ranking_rationale(scores),
            "governance_flags": {
                "prioritization_only": True,
                "does_not_execute_actions": True,
                "does_not_approve_or_reject": True,
                "routes_to": "governance_review",
                "non_closure_compliant": True,
                "traceable": True,
            },
            "raw_intake_record": record,
        }

    def _priority_class(self, score: float) -> str:
        if score >= 0.80:
            return "critical"
        if score >= 0.65:
            return "high"
        if score >= 0.45:
            return "medium"
        if score > 0.0:
            return "low"
        return "minimal"

    def _ranking_rationale(self, scores: dict[str, float]) -> str:
        return (
            "priority_score combines urgency="
            f"{scores['urgency_score']:.3f}, impact={scores['impact_score']:.3f}, "
            f"risk={scores['risk_score']:.3f}, confidence={scores['confidence_score']:.3f}."
        )

    def _rank(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked = sorted(
            records,
            key=lambda item: (
                -float(item.get("priority_score", 0.0)),
                -float(item.get("risk_score", 0.0)),
                -float(item.get("confidence_score", 0.0)),
                str(item.get("recommendation_id", "")),
            ),
        )
        for rank, item in enumerate(ranked, start=1):
            item["priority_rank"] = rank
        return ranked

    def _metrics(self, ranked: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(ranked)
        if count == 0:
            return {
                "prioritized_recommendation_count": 0,
                "max_priority_score": 0.0,
                "mean_priority_score": 0.0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "minimal_count": 0,
            }
        scores = [float(x.get("priority_score", 0.0)) for x in ranked]
        classes = [str(x.get("priority_class", "minimal")) for x in ranked]
        return {
            "prioritized_recommendation_count": count,
            "max_priority_score": max(scores),
            "mean_priority_score": sum(scores) / count,
            "critical_count": classes.count("critical"),
            "high_count": classes.count("high"),
            "medium_count": classes.count("medium"),
            "low_count": classes.count("low"),
            "minimal_count": classes.count("minimal"),
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    def step(self, inputs: Any = None, *, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            for path in (self.latest_path, self.history_path):
                if path.exists():
                    path.unlink()

        queue, rejected = self._extract_queue(inputs)
        prioritized = [self._prioritize_record(record, index) for index, record in enumerate(queue, start=1)]
        ranked = self._rank(prioritized)
        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": _utc_now(),
            "input_recommendation_count": len(queue),
            "rejected_input_count": rejected,
            "prioritized_queue": ranked,
            "priority_metrics": self._metrics(ranked),
            "scoring_policy": {
                "weights": dict(self.DEFAULT_WEIGHTS),
                "deterministic_ranking": True,
                "tie_breakers": ["priority_score", "risk_score", "confidence_score", "recommendation_id"],
            },
            "governance": {
                "prioritization_only": True,
                "does_not_execute_actions": True,
                "does_not_approve_or_reject": True,
                "does_not_modify_identity": True,
                "does_not_modify_memory": True,
                "does_not_modify_strategy": True,
                "routes_to": "governance_review",
                "non_closure_compliant": True,
                "traceability": True,
                "reversibility": True,
            },
            "state_paths": {
                "latest": str(self.latest_path),
                "history": str(self.history_path),
            },
        }
        if persist:
            self._persist(result)
        return result


if __name__ == "__main__":
    print(json.dumps(RecommendationPrioritization().step(), indent=2, ensure_ascii=False))
