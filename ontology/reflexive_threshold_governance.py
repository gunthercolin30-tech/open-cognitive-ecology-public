
from __future__ import annotations
import json
from pathlib import Path

PRIMITIVE = "reflexive_threshold_governance"
ROOT = Path.home() / "open-cognitive-ecology"
HISTORY_FILE = ROOT / "reflexive_governance_history.jsonl"

def _clamp(v):
    return max(0.0, min(1.0, float(v)))

class ReflexiveThresholdGovernance:
    def __init__(self, activation_threshold=0.90):
        self.base_activation_threshold = activation_threshold
        self.meta_policy_gain = 1.0
        self.last_effectiveness_score = None

    def _load_history(self):
        if not HISTORY_FILE.exists():
            return []
        rows = []
        with HISTORY_FILE.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
        return rows

    def _append(self, record):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\\n")

    def step(self,
             reflexive_threshold_result=None,
             constitutional_governance_score=0.90,
             longitudinal_result=None,
             inter_run_result=None):

        reflexive_threshold_result = reflexive_threshold_result or {}
        longitudinal_result = longitudinal_result or {}
        inter_run_result = inter_run_result or {}

        score = _clamp((
            reflexive_threshold_result.get("reflexive_coherence_score", 0.0)
            + float(constitutional_governance_score)
            + longitudinal_result.get("stability_index", 1.0)
            + inter_run_result.get("inter_run_stability_index", 1.0)
        ) / 4.0)

        history = self._load_history()

        scores_before = [r.get("governance_activation_score", score) for r in history[-20:]]
        stability_before = _clamp(1.0 - (max(scores_before) - min(scores_before))) if scores_before else 1.0

        scores_after = scores_before + [score]
        stability_after = _clamp(1.0 - (max(scores_after) - min(scores_after)))

        stability_gain = stability_after - stability_before

        prev_eff = self.last_effectiveness_score
        if prev_eff is None:
            prev_eff = history[-1].get("effectiveness_score", 0.5) if history else 0.5

        effectiveness_score = _clamp(
            0.5 + stability_gain + (0.3 * prev_eff)
        )

        effectiveness_delta = effectiveness_score - prev_eff

        if effectiveness_delta > 0.01:
            self.meta_policy_gain = min(2.0, self.meta_policy_gain + 0.05)
        elif effectiveness_delta < -0.01:
            self.meta_policy_gain = max(0.5, self.meta_policy_gain - 0.05)

        self.last_effectiveness_score = effectiveness_score

        trend = "stable"
        if history:
            prev_score = history[-1].get("governance_activation_score", score)
            d = score - prev_score
            if d > 0.01:
                trend = "improving"
            elif d < -0.01:
                trend = "declining"

        base_bias = {
            "improving": 0.05,
            "stable": 0.0,
            "declining": -0.05
        }.get(trend, 0.0)

        policy_bias = base_bias * self.meta_policy_gain * (0.5 + effectiveness_score)
        activation_threshold = _clamp(self.base_activation_threshold - policy_bias)
        enabled = score >= activation_threshold

        self._append({
            "governance_activation_score": score,
            "effectiveness_score": effectiveness_score,
            "effectiveness_delta": effectiveness_delta,
            "meta_policy_gain": self.meta_policy_gain,
            "governance_enabled": enabled
        })

        return {
            "primitive": PRIMITIVE,
            "governance_activation_score": score,
            "governance_enabled": enabled,
            "activation_threshold": activation_threshold,
            "policy_bias": policy_bias,
            "effectiveness_score": effectiveness_score,
            "effectiveness_delta": effectiveness_delta,
            "meta_policy_gain": self.meta_policy_gain,
            "stability_gain": stability_gain,
            "history_length": len(history) + 1
        }

