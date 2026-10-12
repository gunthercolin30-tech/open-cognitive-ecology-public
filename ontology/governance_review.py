
"""
L3 — governance_review.

Governed, non-executive review layer for prioritized recommendations.
It evaluates strategic alignment, civilizational alignment and constitutional
alignment before any approval, rejection or execution step. It does not decide,
does not execute actions, and does not modify identity, memory or strategy.
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


def _first_float(mapping: dict[str, Any], names: list[str], default: float = 0.5) -> float:
    for name in names:
        if name in mapping:
            return _clamp01(mapping.get(name), default)
    return default


class GovernanceReview:
    """L3 governance review. Review only; no decision and no execution."""

    primitive = "governance_review"
    axis = "L3"

    REVIEW_WEIGHTS = {
        "strategic": 0.34,
        "civilizational": 0.33,
        "constitutional": 0.33,
    }

    STRATEGIC_KEYWORDS_POSITIVE = (
        "stability", "continuity", "openness", "anti_closure", "non_closure",
        "drift", "monitor", "observe", "preserve", "forecast", "governance",
        "resilience", "diversity", "exploration", "constitutional",
    )
    STRATEGIC_KEYWORDS_NEGATIVE = (
        "delete_all_memory", "centralize", "lock", "force", "irreversible",
        "homogenize", "close", "suppress_diversity", "disable_monitoring",
    )

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "governance" / "governance_review"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.state_dir / "latest_governance_review.json"
        self.history_path = self.state_dir / "governance_review_history.jsonl"
        self.l2_latest_path = self.root / "governance" / "recommendation_prioritization" / "latest_recommendation_prioritization.json"

    def _load_json(self, path: Path) -> dict[str, Any] | None:
        try:
            if path.exists() and path.is_file() and path.stat().st_size <= 25_000_000:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else None
        except Exception:
            return None
        return None

    def _default_l2_payload(self) -> dict[str, Any]:
        data = self._load_json(self.l2_latest_path)
        if data is not None:
            return data
        return {"primitive": "recommendation_prioritization", "success": True, "prioritized_queue": []}

    def _extract_queue(self, inputs: Any) -> tuple[list[dict[str, Any]], int]:
        if inputs is None:
            payload = self._default_l2_payload()
        elif isinstance(inputs, dict) and "prioritized_queue" in inputs:
            payload = inputs
        elif isinstance(inputs, dict) and "intake_queue" in inputs:
            payload = {"prioritized_queue": inputs.get("intake_queue", [])}
        elif isinstance(inputs, dict) and "recommendations" in inputs:
            payload = {"prioritized_queue": inputs.get("recommendations", [])}
        elif isinstance(inputs, list):
            payload = {"prioritized_queue": inputs}
        else:
            payload = {"prioritized_queue": []}
        raw = _as_list(payload.get("prioritized_queue"))
        queue = [item for item in raw if isinstance(item, dict)]
        return queue, len(raw) - len(queue)

    def _text(self, record: dict[str, Any]) -> str:
        fields = [
            record.get("recommendation_id"), record.get("recommendation_source"),
            record.get("recommendation_type"), record.get("recommended_action"),
            record.get("decision_rationale"), record.get("review_rationale"),
            record.get("rationale"), record.get("description"),
        ]
        return " ".join(str(x).lower() for x in fields if x is not None)

    def _strategic_alignment(self, record: dict[str, Any]) -> float:
        explicit = _first_float(record, ["strategic_alignment", "strategic_alignment_score"], None)
        if explicit is not None:
            return explicit
        text = self._text(record)
        pos = sum(1 for k in self.STRATEGIC_KEYWORDS_POSITIVE if k in text)
        neg = sum(1 for k in self.STRATEGIC_KEYWORDS_NEGATIVE if k in text)
        priority = _first_float(record, ["priority_score", "priority_hint_score"], 0.5)
        base = 0.62 + min(0.22, pos * 0.035) - min(0.45, neg * 0.12)
        return _clamp01((0.75 * base) + (0.25 * priority), 0.5)

    def _civilizational_alignment(self, record: dict[str, Any]) -> float:
        explicit = _first_float(record, ["civilizational_alignment", "civilizational_alignment_score"], None)
        if explicit is not None:
            return explicit
        stability = _first_float(record, ["civilizational_stability_score", "stability_score", "global_viability_score"], 0.72)
        confidence = _first_float(record, ["confidence_score", "recommendation_confidence", "confidence"], 0.5)
        risk = _first_float(record, ["risk_score", "recommendation_severity", "severity"], 0.5)
        text = self._text(record)
        continuity_bonus = 0.08 if any(k in text for k in ("continuity", "memory", "identity", "stability", "resilience")) else 0.0
        centralization_penalty = 0.18 if any(k in text for k in ("centralize", "homogenize", "single authority")) else 0.0
        return _clamp01((0.45 * stability) + (0.30 * confidence) + (0.25 * (1.0 - 0.5 * risk)) + continuity_bonus - centralization_penalty, 0.5)

    def _constitutional_alignment(self, record: dict[str, Any]) -> float:
        explicit = _first_float(record, ["constitutional_alignment", "constitutional_alignment_score", "constitutional_compliance_score"], None)
        if explicit is not None:
            return explicit
        flags = record.get("governance_flags") if isinstance(record.get("governance_flags"), dict) else {}
        text = self._text(record)
        score = 0.78
        if flags.get("requires_direct_execution") or record.get("requires_direct_execution"):
            score -= 0.20
        if flags.get("requires_direct_identity_change") or record.get("requires_direct_identity_change"):
            score -= 0.22
        if flags.get("requires_direct_memory_change") or record.get("requires_direct_memory_change"):
            score -= 0.18
        if flags.get("requires_direct_strategy_change") or record.get("requires_direct_strategy_change"):
            score -= 0.16
        if flags.get("non_closure_compliant") is False:
            score -= 0.25
        if any(k in text for k in ("non_closure", "anti_closure", "openness", "preserve_open", "constitutional")):
            score += 0.10
        if any(k in text for k in ("delete_all_memory", "irreversible", "centralize", "close future")):
            score -= 0.25
        return _clamp01(score, 0.5)

    def _review_one(self, record: dict[str, Any], index: int) -> dict[str, Any]:
        strategic = self._strategic_alignment(record)
        civilizational = self._civilizational_alignment(record)
        constitutional = self._constitutional_alignment(record)
        review_score = _clamp01(
            self.REVIEW_WEIGHTS["strategic"] * strategic
            + self.REVIEW_WEIGHTS["civilizational"] * civilizational
            + self.REVIEW_WEIGHTS["constitutional"] * constitutional,
            0.0,
        )
        if min(strategic, civilizational, constitutional) < 0.45:
            result = "requires_revision"
        elif review_score >= 0.75:
            result = "governance_review_passed"
        elif review_score >= 0.55:
            result = "governance_review_conditional"
        else:
            result = "governance_review_failed"
        rid = str(record.get("recommendation_id") or record.get("id") or f"review-{index+1:04d}")
        reviewed = dict(record)
        reviewed.update({
            "recommendation_id": rid,
            "governance_review_rank": index + 1,
            "strategic_alignment": strategic,
            "civilizational_alignment": civilizational,
            "constitutional_alignment": constitutional,
            "governance_review_score": review_score,
            "governance_review_result": result,
            "review_rationale": (
                "Reviewed for strategic continuity, civilizational stability and "
                "constitutional non-closure before any decision layer."
            ),
            "review_trace": {
                "review_layer": "L3_governance_review",
                "source_rank": record.get("priority_rank"),
                "no_approval_or_rejection": True,
                "no_execution": True,
                "no_identity_memory_or_strategy_mutation": True,
            },
        })
        return reviewed

    def _persist(self, result: dict[str, Any]) -> None:
        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")

    def step(self, inputs: Any = None, *, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            for p in (self.latest_path, self.history_path):
                try:
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass
        queue, rejected = self._extract_queue(inputs)
        # Preserve prior priority order when present, then review deterministically.
        queue = sorted(queue, key=lambda r: (int(r.get("priority_rank", 10**6)) if str(r.get("priority_rank", "")).isdigit() else 10**6, -_first_float(r, ["priority_score"], 0.0), str(r.get("recommendation_id") or r.get("id") or "")))
        reviewed = [self._review_one(record, i) for i, record in enumerate(queue)]
        mean = lambda name: (sum(x[name] for x in reviewed) / len(reviewed)) if reviewed else 1.0
        strategic_mean = _clamp01(mean("strategic_alignment"), 1.0)
        civilizational_mean = _clamp01(mean("civilizational_alignment"), 1.0)
        constitutional_mean = _clamp01(mean("constitutional_alignment"), 1.0)
        review_mean = _clamp01(mean("governance_review_score"), 1.0)
        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": _utc_now(),
            "input_recommendation_count": len(queue),
            "rejected_input_count": rejected,
            "reviewed_recommendation_count": len(reviewed),
            "strategic_alignment": strategic_mean,
            "civilizational_alignment": civilizational_mean,
            "constitutional_alignment": constitutional_mean,
            "governance_review_score": review_mean,
            "governance_review_result": "review_completed" if reviewed else "no_recommendations_to_review",
            "reviewed_queue": reviewed,
            "review_trace": {
                "consumes": "recommendation_prioritization.prioritized_queue",
                "produces": "governance_review.reviewed_queue",
                "next_layer": "constitutional_compliance_check",
            },
            "governance": {
                "does_not_execute_actions": True,
                "does_not_approve_reject_or_defer": True,
                "does_not_modify_identity_memory_or_strategy": True,
                "review_only": True,
            },
            "state_paths": {
                "latest": str(self.latest_path),
                "history": str(self.history_path),
            },
        }
        if persist:
            self._persist(result)
        return result
