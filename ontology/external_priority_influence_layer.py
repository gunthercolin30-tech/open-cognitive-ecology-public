
"""
External Priority Influence Layer — R2.

Transforms an accepted external influence into a governed, decaying and
expiring priority signal. The primitive never permits direct external writes:
it only computes whether an externally sourced suggestion may influence
internal priority ranking, with explicit confidence, decay, expiration and
traceability fields.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import math


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = 0.0
    return max(low, min(high, number))


def _mean(values: list[float]) -> float:
    clean = [float(v) for v in values]
    if not clean:
        return 0.0
    return sum(clean) / len(clean)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "accepted", "approved", "adopted"}
    return bool(value)


class ExternalPriorityInfluenceLayer:
    """
    R2 governed priority layer for external influences.

    Inputs may include either a flat payload or an ``external_influence``
    mapping. The layer accepts only already-governed external influence
    candidates and emits deterministic priority metrics:

    - priority_delta
    - priority_confidence
    - priority_decay
    - priority_expiration
    - effective_priority
    - remaining_priority_lifetime

    Decisions are restricted to priority_adopted, priority_observed,
    priority_rejected and priority_expired.
    """

    primitive = "EXTERNAL_PRIORITY_INFLUENCE_LAYER"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.audit_dir = self.root / "external_priority_influence_layer"

    def _payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        base = dict(inputs or {})
        nested = base.get("external_influence")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in base.items() if k != "external_influence"})
            return merged
        return base

    def _governance_accepted(self, payload: dict[str, Any]) -> bool:
        decision = str(
            payload.get("adoption_decision")
            or payload.get("governance_decision")
            or payload.get("decision")
            or "priority_observed"
        ).strip().lower()
        explicit = payload.get("accepted", payload.get("approved", None))
        if explicit is not None:
            return _as_bool(explicit)
        return decision in {
            "accepted",
            "approved",
            "adopted",
            "priority_adopted",
            "influence_adopted",
            "adoption_allowed",
        }

    def _traceability_ready(self, payload: dict[str, Any]) -> bool:
        required_any = [
            payload.get("external_influence_id"),
            payload.get("influence_id"),
            payload.get("source_id"),
            payload.get("trace_id"),
        ]
        return any(str(v).strip() for v in required_any if v is not None)

    def _r0_context(self) -> dict[str, Any]:
        try:
            from ontology.external_influence_gap_analysis import ExternalInfluenceGapAnalysis

            audit = ExternalInfluenceGapAnalysis(root=self.root).step(persist=False)
            return {
                "r0_available": True,
                "r0_architecture_decision": audit.get("architecture_decision"),
                "r0_overall_external_influence_coverage": audit.get("overall_external_influence_coverage"),
            }
        except Exception as exc:
            return {
                "r0_available": False,
                "r0_error": str(exc),
            }

    def _compute_decay(self, payload: dict[str, Any]) -> tuple[float, float, bool]:
        age_steps = max(0.0, float(payload.get("age_steps", payload.get("elapsed_steps", 0.0)) or 0.0))
        max_lifetime = max(1.0, float(payload.get("max_lifetime_steps", payload.get("priority_lifetime_steps", 10.0)) or 10.0))
        decay_rate = _clamp(payload.get("decay_rate", 0.1), 0.0, 1.0)

        normalized_age = _clamp(age_steps / max_lifetime)
        # Smooth deterministic decay. Larger age and larger decay_rate reduce influence.
        survival = math.exp(-decay_rate * age_steps)
        lifetime_factor = 1.0 - normalized_age
        priority_decay = _clamp(survival * lifetime_factor)
        remaining_lifetime = _clamp(1.0 - normalized_age)
        expired = age_steps >= max_lifetime or remaining_lifetime <= 0.0
        return priority_decay, remaining_lifetime, expired

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._payload(inputs)

        proposed_delta = _clamp(
            payload.get(
                "proposed_priority_delta",
                payload.get("priority_delta", payload.get("external_priority_signal", 0.0)),
            )
        )
        source_reliability = _clamp(payload.get("source_reliability", payload.get("source_confidence", 0.5)))
        adoption_confidence = _clamp(payload.get("adoption_confidence", payload.get("priority_confidence", 0.5)))
        governance_confidence = _clamp(payload.get("governance_confidence", payload.get("review_confidence", 0.5)))
        constitutional_compatibility = _clamp(payload.get("constitutional_compatibility", 0.8))
        evidence_quality = _clamp(payload.get("evidence_quality", payload.get("external_evidence_quality", 0.5)))
        urgency = _clamp(payload.get("urgency", payload.get("priority_urgency", 0.5)))

        governance_accepted = self._governance_accepted(payload)
        traceability_ready = self._traceability_ready(payload)
        direct_write_requested = _as_bool(payload.get("direct_write_requested", False))

        priority_confidence = _mean([
            source_reliability,
            adoption_confidence,
            governance_confidence,
            constitutional_compatibility,
            evidence_quality,
        ])
        priority_decay, remaining_lifetime, expired = self._compute_decay(payload)

        safety_multiplier = 0.0 if direct_write_requested else 1.0
        governance_multiplier = 1.0 if governance_accepted else 0.0
        traceability_multiplier = 1.0 if traceability_ready else 0.6
        urgency_multiplier = 0.5 + 0.5 * urgency

        priority_delta = _clamp(proposed_delta * priority_confidence * constitutional_compatibility)
        effective_priority = _clamp(
            priority_delta
            * priority_decay
            * governance_multiplier
            * traceability_multiplier
            * urgency_multiplier
            * safety_multiplier
        )

        rejection_reasons: list[str] = []
        if direct_write_requested:
            rejection_reasons.append("direct_write_requested")
        if not governance_accepted:
            rejection_reasons.append("external_influence_not_governance_accepted")
        if constitutional_compatibility < 0.5:
            rejection_reasons.append("constitutional_compatibility_too_low")
        if priority_confidence < 0.35:
            rejection_reasons.append("priority_confidence_too_low")
        if not traceability_ready:
            rejection_reasons.append("traceability_incomplete")

        if expired:
            decision = "priority_expired"
        elif rejection_reasons:
            decision = "priority_rejected"
        elif effective_priority >= 0.35 and priority_confidence >= 0.55:
            decision = "priority_adopted"
        else:
            decision = "priority_observed"

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "external_influence_id": payload.get("external_influence_id") or payload.get("influence_id") or "external-influence-unspecified",
            "source_id": payload.get("source_id") or payload.get("external_source") or "external-source-unspecified",
            "priority_domain": payload.get("priority_domain") or payload.get("domain") or "general",
            "proposed_priority_delta": proposed_delta,
            "priority_delta": priority_delta,
            "priority_confidence": _clamp(priority_confidence),
            "priority_decay": priority_decay,
            "priority_expiration": bool(expired),
            "effective_priority": effective_priority,
            "remaining_priority_lifetime": remaining_lifetime,
            "priority_decision": decision,
            "governance_accepted": governance_accepted,
            "traceability_ready": traceability_ready,
            "direct_write_allowed": False,
            "direct_write_requested": direct_write_requested,
            "rejection_reasons": rejection_reasons,
            "integration_context": self._r0_context(),
            "epistemic_position": "functional_priority_governance_only_no_phenomenal_claim",
        }

        if persist:
            self.audit_dir.mkdir(parents=True, exist_ok=True)
            latest = self.audit_dir / "latest_external_priority_influence_layer.json"
            latest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(latest)

        return result
