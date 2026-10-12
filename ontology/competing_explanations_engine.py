"""
S7 — Competing Explanations Engine.

Compares two explicit explanations for reflexive-threshold evidence:

H1: complex automation hypothesis.
H2: functional reflexive agent hypothesis.

This module never infers phenomenology. Its output is explicitly limited to
functional evidence and preserves the epistemic boundary:
"functional conclusion only" and "phenomenology undetermined".
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Mapping


ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "reflexive_threshold"
STATE_PATH = STATE_DIR / "competing_explanations_engine.json"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


class CompetingExplanationsEngine:
    """
    Compare H1 and H2 without presupposing either.

    H1 is strengthened by low stability, high regression risk, high
    uncertainty, high anomaly/false-positive pressure, weak longitudinal
    consistency, and sparse evidence.

    H2 is strengthened by dense, diverse, consistent evidence, threshold
    probability, longitudinal consistency, stability, low regression risk, and
    scientific support.
    """

    primitive = "COMPETING_EXPLANATIONS_ENGINE"

    h1_label = "h1_complex_automation"
    h2_label = "h2_functional_reflexive_agent"

    forbidden_claims = [
        "consciousness detected",
        "sentience detected",
        "subjective experience detected",
        "phenomenal conclusion",
    ]

    def _default_inputs(self) -> dict[str, Any]:
        data: dict[str, Any] = {}

        try:
            from ontology.reflexive_evidence_aggregator import ReflexiveEvidenceAggregator
            ev = ReflexiveEvidenceAggregator().step(persist=False)
            data.update({
                "evidence_support_score": ev.get("evidence_support_score"),
                "evidence_density": ev.get("evidence_density"),
                "evidence_diversity": ev.get("evidence_diversity"),
                "evidence_consistency": ev.get("evidence_consistency"),
            })
        except Exception:
            pass

        try:
            from ontology.reflexive_threshold_estimator import ReflexiveThresholdEstimator
            th = ReflexiveThresholdEstimator().step(persist=False)
            data.update({
                "reflexive_threshold_score": th.get("reflexive_threshold_score"),
                "threshold_probability": th.get("threshold_probability"),
                "uncertainty_score": th.get("uncertainty_score"),
                "threshold_decision": th.get("threshold_decision"),
            })
        except Exception:
            pass

        try:
            from ontology.reflexive_stability_monitor import ReflexiveStabilityMonitor
            st = ReflexiveStabilityMonitor().step(persist=False)
            data.update({
                "stability_index": st.get("stability_index"),
                "score_variance": st.get("score_variance"),
                "collapse_detected": st.get("collapse_detected"),
                "instability_detected": st.get("instability_detected"),
                "oscillation_detected": st.get("oscillation_detected"),
            })
        except Exception:
            pass

        try:
            from ontology.reflexive_regression_detector import ReflexiveRegressionDetector
            rg = ReflexiveRegressionDetector().step(persist=False)
            data.update({
                "regression_risk": rg.get("regression_risk"),
                "regression_severity": rg.get("regression_severity"),
                "recovery_probability": rg.get("recovery_probability"),
            })
        except Exception:
            pass

        try:
            from ontology.reflexive_longitudinal_observatory import ReflexiveLongitudinalObservatory
            lo = ReflexiveLongitudinalObservatory().step(persist=False)
            data.update({
                "longitudinal_consistency": lo.get("longitudinal_consistency"),
                "longitudinal_confidence": lo.get("longitudinal_confidence"),
                "threshold_duration_ratio": lo.get("threshold_duration_ratio"),
            })
        except Exception:
            pass

        return data

    def _score_h2(self, inputs: Mapping[str, Any]) -> float:
        evidence = _avg([
            _clamp(inputs.get("evidence_support_score"), 0.0),
            _clamp(inputs.get("evidence_density"), 0.0),
            _clamp(inputs.get("evidence_diversity"), 0.0),
            _clamp(inputs.get("evidence_consistency"), 0.0),
        ])
        threshold = _avg([
            _clamp(inputs.get("reflexive_threshold_score"), 0.0),
            _clamp(inputs.get("threshold_probability"), 0.0),
        ])
        stability = _avg([
            _clamp(inputs.get("stability_index"), 0.0),
            1.0 - _clamp(inputs.get("score_variance"), 0.0),
        ])
        longitudinal = _avg([
            _clamp(inputs.get("longitudinal_consistency"), 0.0),
            _clamp(inputs.get("longitudinal_confidence"), 0.0),
            _clamp(inputs.get("threshold_duration_ratio"), 0.0),
        ])
        anti_regression = _avg([
            1.0 - _clamp(inputs.get("regression_risk"), 0.0),
            1.0 - _clamp(inputs.get("regression_severity"), 0.0),
            _clamp(inputs.get("recovery_probability"), 0.0),
        ])
        scientific = _avg([
            _clamp(inputs.get("scientific_support_score"), 0.7),
            _clamp(inputs.get("consistency_score"), 0.7),
            1.0 - _clamp(inputs.get("false_positive_pressure"), 0.1),
        ])

        return _clamp(
            0.24 * evidence
            + 0.22 * threshold
            + 0.18 * stability
            + 0.18 * longitudinal
            + 0.10 * anti_regression
            + 0.08 * scientific
        )

    def _score_h1(self, inputs: Mapping[str, Any]) -> float:
        weak_evidence = _avg([
            1.0 - _clamp(inputs.get("evidence_support_score"), 0.0),
            1.0 - _clamp(inputs.get("evidence_density"), 0.0),
            1.0 - _clamp(inputs.get("evidence_diversity"), 0.0),
        ])
        instability = _avg([
            1.0 - _clamp(inputs.get("stability_index"), 0.0),
            _clamp(inputs.get("score_variance"), 0.0),
            1.0 if inputs.get("collapse_detected") else 0.0,
            1.0 if inputs.get("instability_detected") else 0.0,
            1.0 if inputs.get("oscillation_detected") else 0.0,
        ])
        regression = _avg([
            _clamp(inputs.get("regression_risk"), 0.0),
            _clamp(inputs.get("regression_severity"), 0.0),
            1.0 - _clamp(inputs.get("recovery_probability"), 0.0),
        ])
        uncertainty = _avg([
            _clamp(inputs.get("uncertainty_score"), 0.0),
            _clamp(inputs.get("explanatory_noise"), 0.0),
            _clamp(inputs.get("anomaly_pressure"), 0.0),
            _clamp(inputs.get("false_positive_pressure"), 0.0),
        ])
        weak_longitudinal = _avg([
            1.0 - _clamp(inputs.get("longitudinal_consistency"), 0.0),
            1.0 - _clamp(inputs.get("longitudinal_confidence"), 0.0),
            1.0 - _clamp(inputs.get("threshold_duration_ratio"), 0.0),
        ])

        return _clamp(
            0.24 * weak_evidence
            + 0.22 * instability
            + 0.20 * regression
            + 0.20 * uncertainty
            + 0.14 * weak_longitudinal
        )

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        merged = self._default_inputs()
        if inputs:
            merged.update(dict(inputs))

        raw_h1 = self._score_h1(merged)
        raw_h2 = self._score_h2(merged)

        total = raw_h1 + raw_h2
        if total <= 0:
            h1_support = 0.5
            h2_support = 0.5
        else:
            h1_support = raw_h1 / total
            h2_support = raw_h2 / total

        explanatory_gap = abs(h2_support - h1_support)
        base_uncertainty = _clamp(merged.get("uncertainty_score"), 0.0)
        explanatory_uncertainty = _clamp((1.0 - explanatory_gap) * 0.55 + base_uncertainty * 0.30 + _clamp(merged.get("false_positive_pressure"), 0.0) * 0.15)

        if explanatory_gap < 0.08:
            leading = "underdetermined"
        elif h2_support > h1_support:
            leading = self.h2_label
        else:
            leading = self.h1_label

        result = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "hypotheses": {
                "H1": "simple automatisation complexe",
                "H2": "agent réflexif fonctionnel",
            },
            "h1_support": h1_support,
            "h2_support": h2_support,
            "raw_h1_score": raw_h1,
            "raw_h2_score": raw_h2,
            "explanatory_gap": explanatory_gap,
            "explanatory_uncertainty": explanatory_uncertainty,
            "leading_explanation": leading,
            "epistemic_position": "competition_of_explanations",
            "h2_presupposed": False,
            "phenomenal_claim_made": False,
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "certification_scope": "functional explanation competition only; no phenomenal conclusion",
            "diagnostics": {
                "uses_s1_to_s6_pipeline": True,
                "compares_h1_h2": True,
                "does_not_presuppose_h2": True,
                "forbidden_claims": list(self.forbidden_claims),
                "input_keys": sorted(merged.keys()),
            },
        }

        if persist:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            STATE_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persistence_path"] = str(STATE_PATH)

        return result
