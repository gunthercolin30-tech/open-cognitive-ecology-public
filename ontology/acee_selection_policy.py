"""ACEE10 — governed selection policy over ACEE8/ACEE9 evidence.

This module selects a next action but does not execute installation, validation,
causal analysis, or rollback. It consumes normalized evidence produced upstream
and preserves constitutional, governance, reversibility, and non-closure gates.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_SELECTION_POLICY"
STATUS_READY = "ACEE_SELECTION_DECISION_READY"
STATUS_DEGRADED = "ACEE_SELECTION_DECISION_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_DECISIONS = {"accept", "reject", "rollback", "repeat", "sandbox_longer"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _finite(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _score(value: Any) -> Optional[float]:
    number = _finite(value)
    if number is None or number < 0.0 or number > 1.0:
        return None
    return number


def _decision_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, Mapping):
        for key in (
            "compliant", "approved", "authorized", "accepted",
            "governance_approved", "constitutional_compliant",
        ):
            if isinstance(value.get(key), bool):
                return value[key]
        text = str(value.get("status") or value.get("decision") or value.get("result") or "").lower()
    else:
        text = str(value or "").lower()
    if any(token in text for token in ("reject", "block", "fail", "non_compliant", "declin", "veto")):
        return False
    if any(token in text for token in ("approv", "authoriz", "accept", "pass", "compliant", "valid")):
        return True
    return None


def _first_score(*sources: Mapping[str, Any], keys: Tuple[str, ...]) -> Optional[float]:
    for source in sources:
        for key in keys:
            if key in source:
                value = _score(source.get(key))
                if value is not None:
                    return value
    return None


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass
class AceeSelectionPolicy:
    root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root = (
            Path(self.root) if self.root is not None
            else Path.home() / "open-cognitive-ecology"
        ).expanduser().resolve()

    def _paths(self) -> Tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE10_acee_selection_policy"
        return (
            directory / "latest_selection_decision.json",
            directory / "selection_decision_history.jsonl",
            directory / ".selection_decision.lock",
        )

    def _previous(self, history: Path) -> Tuple[Optional[Dict[str, Any]], bool]:
        if not history.is_file():
            return None, False
        try:
            lines = [line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError, TypeError):
            return None, True

    def _build(
        self,
        supplied: Mapping[str, Any],
        previous_hash: Optional[str],
        corrupted: bool,
    ) -> Dict[str, Any]:
        impact = _mapping(supplied.get("impact_evaluation"))
        causal = _mapping(supplied.get("causal_analysis"))
        stability = _mapping(supplied.get("stability_evidence"))
        simplicity = _mapping(supplied.get("simplicity_evidence"))
        reversibility = _mapping(supplied.get("reversibility_evidence"))
        non_closure = _mapping(supplied.get("non_closure_evidence"))
        constitutional = _mapping(supplied.get("constitutional_evidence"))
        governance = _mapping(supplied.get("governance_evidence"))

        impact_score = _finite(impact.get("impact_score"))
        causal_confidence = _score(causal.get("causal_confidence"))
        causal_probability = _score(causal.get("causal_probability"))
        effect_size = _finite(causal.get("effect_size"))
        effect_direction = str(causal.get("effect_direction") or "").lower()

        stability_score = _first_score(
            stability, impact,
            keys=("stability_score", "overall_stability_score", "mean_stability_score", "stability_index"),
        )
        simplicity_score = _first_score(
            simplicity,
            keys=("simplicity_score", "minimality_score", "complexity_reduction_score", "maintainability_score"),
        )
        reversibility_score = _first_score(
            reversibility,
            keys=("mean_reversibility_score", "reversibility_score", "rollback_capability_score"),
        )
        closure_pressure = _first_score(
            non_closure, impact,
            keys=("closure_pressure", "closure_pressure_index", "post_closure_pressure"),
        )
        non_closure_score = _first_score(
            non_closure, constitutional,
            keys=("non_closure_score", "anti_closure_compliance", "architectural_non_closure_index", "openness_preservation_score"),
        )
        constitutional_score = _first_score(
            constitutional, governance,
            keys=("constitutional_compliance_score", "constitutional_integrity_score", "constitutional_integrity_index", "constitutional_alignment_score"),
        )
        governance_score = _first_score(
            governance, impact,
            keys=("governance_score", "governance_consistency_score", "governance_review_score"),
        )

        constitutional_ok = _decision_bool(constitutional)
        governance_ok = _decision_bool(governance)
        if constitutional_ok is None and constitutional_score is not None:
            constitutional_ok = constitutional_score >= 0.70
        if governance_ok is None and governance_score is not None:
            governance_ok = governance_score >= 0.70

        reversibility_assured = reversibility.get("reversibility_assured")
        if not isinstance(reversibility_assured, bool):
            reversibility_assured = reversibility_score is not None and reversibility_score >= 0.80

        closure_increased = (
            impact.get("metric_classifications", {}).get("closure_pressure") == "regressed"
            if isinstance(impact.get("metric_classifications"), Mapping)
            else False
        ) or bool(non_closure.get("closure_pressure_increased", False))

        thresholds = _mapping(supplied.get("thresholds"))
        min_causal = _score(thresholds.get("minimum_causal_confidence"))
        min_causal = 0.60 if min_causal is None else min_causal
        min_stability = _score(thresholds.get("minimum_stability_score"))
        min_stability = 0.70 if min_stability is None else min_stability
        min_simplicity = _score(thresholds.get("minimum_simplicity_score"))
        min_simplicity = 0.50 if min_simplicity is None else min_simplicity
        max_closure = _score(thresholds.get("maximum_closure_pressure"))
        max_closure = 0.30 if max_closure is None else max_closure

        blocking = []
        if impact.get("comparison_valid") is not True:
            blocking.append("valid_impact_evaluation_required")
        if causal.get("ready_for_selection") is not True or causal.get("causal_effect_resolved") is not True:
            blocking.append("resolved_causal_analysis_required")
        if impact_score is None:
            blocking.append("finite_impact_score_required")
        if causal_confidence is None:
            blocking.append("causal_confidence_required")
        if stability_score is None:
            blocking.append("stability_evidence_required")
        if simplicity_score is None:
            blocking.append("simplicity_evidence_required")
        if reversibility_score is None:
            blocking.append("reversibility_evidence_required")
        if closure_pressure is None:
            blocking.append("closure_pressure_evidence_required")
        if constitutional_ok is None:
            blocking.append("constitutional_evidence_required")
        if governance_ok is None:
            blocking.append("governance_evidence_required")
        if corrupted:
            blocking.append("history_corrupted")

        decision = "repeat"
        reasons = []
        vetoes = []

        if constitutional_ok is False:
            decision = "reject"
            vetoes.append("constitutional_veto")
        elif governance_ok is False:
            decision = "reject"
            vetoes.append("governance_veto")
        elif closure_increased or (closure_pressure is not None and closure_pressure > max_closure):
            if effect_direction == "harmful" and reversibility_assured:
                decision = "rollback"
                reasons.append("closure_pressure_increase_with_reversible_harm")
            else:
                decision = "reject"
                vetoes.append("non_closure_veto")
        elif blocking:
            decision = "repeat"
            reasons.append("insufficient_or_invalid_evidence")
        elif causal_confidence < min_causal or (causal_probability is not None and causal_probability < min_causal):
            decision = "sandbox_longer" if impact_score is not None and impact_score > 0 else "repeat"
            reasons.append("causal_confidence_below_threshold")
        elif effect_direction == "harmful" or (effect_size is not None and effect_size < 0) or (impact_score is not None and impact_score < 0):
            if reversibility_assured:
                decision = "rollback"
                reasons.append("causally_attributed_harm_is_reversible")
            else:
                decision = "reject"
                reasons.append("harm_detected_but_rollback_not_assured")
        elif stability_score < min_stability:
            decision = "sandbox_longer"
            reasons.append("stability_below_threshold")
        elif simplicity_score < min_simplicity:
            decision = "reject"
            reasons.append("simplicity_below_threshold")
        else:
            decision = "accept"
            reasons.append("beneficial_causal_stable_simple_reversible_compliant")

        decision_ready = not blocking and decision in ALLOWED_DECISIONS
        rollback_requested = decision == "rollback"
        acceptance_authorized = decision == "accept"

        result = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "selection_id": str(supplied.get("selection_id") or "selection-unspecified"),
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "selection_status": STATUS_READY if decision_ready else STATUS_DEGRADED,
            "selection_decision_ready": decision_ready,
            "decision": decision,
            "allowed_decisions": sorted(ALLOWED_DECISIONS),
            "decision_reasons": sorted(set(reasons)),
            "vetoes": sorted(set(vetoes)),
            "blocking_reasons": sorted(set(blocking)),
            "impact_score": impact_score,
            "causal_probability": causal_probability,
            "causal_confidence": causal_confidence,
            "effect_size": effect_size,
            "effect_direction": effect_direction or "undetermined",
            "stability_score": stability_score,
            "simplicity_score": simplicity_score,
            "reversibility_score": reversibility_score,
            "reversibility_assured": bool(reversibility_assured),
            "closure_pressure": closure_pressure,
            "closure_pressure_increased": closure_increased,
            "non_closure_score": non_closure_score,
            "constitutional_compliant": constitutional_ok is True,
            "governance_approved": governance_ok is True,
            "acceptance_authorized": acceptance_authorized,
            "rollback_requested": rollback_requested,
            "rollback_request": {
                "requested": rollback_requested,
                "reason": "closure_pressure_increase" if closure_increased else "stability_regression" if effect_direction == "harmful" else "explicit_governed_request",
                "requires_acee11": rollback_requested,
                "requires_governance_authorization": True,
                "requires_constitutional_authorization": True,
            },
            "rollback_executed": False,
            "acee11_called": False,
            "installation_executed": False,
            "validation_executed_by_policy": False,
            "causal_analysis_executed_by_policy": False,
            "previous_selection_hash": previous_hash,
            "history_corrupted": corrupted,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
        }
        result["selection_hash"] = _sha({k: v for k, v in result.items() if k != "selection_hash"})
        return result

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        latest, history, lock = self._paths()
        previous, corrupted = self._previous(history)
        result = self._build(supplied, previous.get("selection_hash") if previous else None, corrupted)
        result.update({"persisted": False, "latest_path": str(latest), "history_path": str(history)})
        if not persist:
            return result
        latest.parent.mkdir(parents=True, exist_ok=True)
        with lock.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            previous, corrupted = self._previous(history)
            record = self._build(supplied, previous.get("selection_hash") if previous else None, corrupted)
            record.update({"persisted": True, "latest_path": str(latest), "history_path": str(history)})
            tmp = latest.with_suffix(".tmp")
            tmp.write_text(json.dumps(record, sort_keys=True, indent=2), encoding="utf-8")
            tmp.replace(latest)
            with history.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            return record
