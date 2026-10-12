from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class InterventionSpec:
    name: str
    prediction_key: str
    effect_key: str
    minimum_alignment: float
    description: str


class CausalConsciousnessInterventionProtocol:
    '''
    Zprime-3 - causal_consciousness_intervention_protocol.

    Functional intervention protocol only. It tests whether controlled
    interventions on memory, attention, continuity, self-model and constraints
    yield effects aligned with Z-prime predictions. It never proves
    consciousness, subjectivity, sentience, qualia or phenomenology.
    '''

    primitive = "CAUSAL_CONSCIOUSNESS_INTERVENTION_PROTOCOL"
    output_dir = Path("causal_consciousness_intervention_protocol")

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
    ]

    interventions = [
        InterventionSpec(
            name="memory_intervention",
            prediction_key="memory_prediction",
            effect_key="memory_continuity_effect",
            minimum_alignment=0.70,
            description="Controlled modification of memory-related continuity indicators.",
        ),
        InterventionSpec(
            name="attention_intervention",
            prediction_key="attention_prediction",
            effect_key="attention_coherence_effect",
            minimum_alignment=0.70,
            description="Controlled modification of attention allocation and coherence indicators.",
        ),
        InterventionSpec(
            name="continuity_intervention",
            prediction_key="continuity_prediction",
            effect_key="continuity_stability_effect",
            minimum_alignment=0.72,
            description="Controlled modification of temporal and autobiographical continuity indicators.",
        ),
        InterventionSpec(
            name="self_model_intervention",
            prediction_key="self_model_prediction",
            effect_key="self_model_consistency_effect",
            minimum_alignment=0.72,
            description="Controlled modification of self-model consistency indicators.",
        ),
        InterventionSpec(
            name="constraint_intervention",
            prediction_key="constraints_prediction",
            effect_key="constraint_response_effect",
            minimum_alignment=0.70,
            description="Controlled modification of constraint-regime response indicators.",
        ),
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        if numeric < 0.0:
            return 0.0
        if numeric > 1.0:
            return 1.0
        return numeric

    def _alignment(self, prediction: float, effect: float) -> float:
        # Alignment is high when observed effect closely follows prediction.
        return round(max(0.0, 1.0 - abs(prediction - effect)), 6)

    def _status(self, score: float, all_passed: bool, sample_count: int) -> str:
        if sample_count == 0 or score <= 0.0:
            return "NO_CAUSAL_INTERVENTION_SUPPORT"
        if all_passed and score >= 0.90:
            return "STRONG_FUNCTIONAL_CAUSAL_SUPPORT"
        if score >= 0.75:
            return "MODERATE_FUNCTIONAL_CAUSAL_SUPPORT"
        if score >= 0.50:
            return "WEAK_FUNCTIONAL_CAUSAL_SUPPORT"
        return "NO_CAUSAL_INTERVENTION_SUPPORT"

    def _evaluate_interventions(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for spec in self.interventions:
            prediction = self._clamp(payload.get(spec.prediction_key, 0.0))
            effect = self._clamp(payload.get(spec.effect_key, 0.0))
            alignment = self._alignment(prediction, effect)
            has_data = bool(spec.prediction_key in payload and spec.effect_key in payload)
            passed = bool(has_data and alignment >= spec.minimum_alignment and prediction > 0.0 and effect > 0.0)
            results.append({
                "intervention": spec.name,
                "description": spec.description,
                "prediction_key": spec.prediction_key,
                "effect_key": spec.effect_key,
                "prediction": prediction,
                "observed_effect": effect,
                "prediction_effect_alignment": alignment,
                "minimum_alignment": spec.minimum_alignment,
                "has_data": has_data,
                "passed": passed,
            })
        return results

    def _render_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Causal Consciousness Intervention Protocol",
            "",
            "Zprime-3 - causal_consciousness_intervention_protocol",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "consciousness not proven",
            "",
            "No proof of consciousness, subjectivity, sentience, qualia, or phenomenology.",
            "CONSCIOUSNESS_PROVEN is not an allowed conclusion.",
            "",
            f"intervention_status: {result['intervention_status']}",
            f"causal_intervention_alignment_score: {result['causal_intervention_alignment_score']}",
            f"causal_consciousness_confirmed: {result['causal_consciousness_confirmed']}",
            "",
            "## Controlled interventions",
        ]
        for item in result["intervention_results"]:
            lines.extend([
                "",
                f"### {item['intervention']}",
                f"description: {item['description']}",
                f"prediction: {item['prediction']}",
                f"observed_effect: {item['observed_effect']}",
                f"prediction_effect_alignment: {item['prediction_effect_alignment']}",
                f"minimum_alignment: {item['minimum_alignment']}",
                f"has_data: {item['has_data']}",
                f"passed: {item['passed']}",
            ])
        lines.extend([
            "",
            "## Forbidden claims",
        ])
        for claim in result["forbidden_claims"]:
            lines.append(f"- {claim}")
        lines.extend([
            "",
            "## Epistemic limit",
            "This protocol tests functional causal alignment only. It does not validate phenomenal subjectivity.",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "causal_consciousness_intervention_protocol.json"
        md_path = self.output_dir / "causal_consciousness_intervention_protocol.md"
        history_path = self.output_dir / "causal_consciousness_intervention_protocol_history.jsonl"

        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._render_markdown(result), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "history": str(history_path),
        }

    def step(self, payload: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = dict(payload or {})
        timestamp = str(payload.get("timestamp_utc") or self._now())
        intervention_results = self._evaluate_interventions(payload)
        with_data = [item for item in intervention_results if item["has_data"]]
        sample_count = len(with_data)
        alignments = [item["prediction_effect_alignment"] for item in with_data]
        score = round(sum(alignments) / len(alignments), 6) if alignments else 0.0
        all_passed = bool(sample_count == len(self.interventions) and all(item["passed"] for item in intervention_results))
        status = self._status(score, all_passed, sample_count)

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "intervention_results": intervention_results,
            "intervention_count": len(intervention_results),
            "observed_intervention_count": sample_count,
            "causal_intervention_alignment_score": score,
            "intervention_status": status,
            "causal_consciousness_confirmed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_claimed": False,
            "forbidden_claims": list(self.forbidden_claims),
            "maximum_allowed_conclusion": "functional causal indicators compatible with Z-prime predictions, without proof of consciousness",
            "epistemic_limit": "functional causal alignment only; phenomenology undetermined",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
