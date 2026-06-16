from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import textwrap
from typing import Any


PRIMITIVE = "autonomous_prompt_generator"

DEPENDENCIES = [
    "cognitive_gap_detector",
    "external_assistance_trigger",
    "interaction_queue_manager",
    "contextual_goal_decomposition",
    "conversational_context_manager",
    "civilizational_dialogue_memory",
    "conversation_memory_archive",
    "dialogue_memory_persistence",
    "autonomous_dialogue_orchestrator",
    "civilizational_strategy_orchestrator",
    "civilizational_strategic_planner",
]


class AutonomousPromptGenerator:
    # O3 transforms an authorized external-assistance decision into a structured prompt.
    # It does not detect gaps, authorize requests, or manage the queue.

    DEFAULT_CONSTRAINTS = [
        "preserve_identity",
        "preserve_governance",
        "preserve_historicity",
        "preserve_non_closure",
        "avoid_uncontrolled_self_modification",
        "maintain_traceability",
    ]

    def __init__(
        self,
        root: Path | None = None,
        history_file: Path | None = None,
        max_context_chars: int = 2400,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.history_file = (
            Path(history_file)
            if history_file is not None
            else self.root / "autonomous_prompt_history.jsonl"
        )
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_context_chars = max(400, int(max_context_chars))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _safe_text(self, value: Any, fallback: str = "") -> str:
        if value is None:
            return fallback
        if isinstance(value, str):
            return value.strip()
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            return str(value)

    def _compact(self, value: Any, max_chars: int | None = None) -> str:
        text = self._safe_text(value)
        text = " ".join(text.split())
        limit = max_chars or self.max_context_chars
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 120)].rstrip() + " … [context_truncated]"

    def _extract_gap(self, inputs: dict[str, Any]) -> dict[str, Any]:
        gap = inputs.get("gap_result")
        if isinstance(gap, dict):
            return gap
        if "knowledge_gap_index" in inputs:
            return inputs
        return {}

    def _extract_decision(self, inputs: dict[str, Any]) -> dict[str, Any]:
        decision = inputs.get("trigger_decision")
        if isinstance(decision, dict):
            return decision
        if "assistance_required" in inputs:
            return inputs
        return {}

    def _build_objective(self, inputs: dict[str, Any], gap: dict[str, Any], decision: dict[str, Any]) -> str:
        explicit = self._safe_text(inputs.get("objective"))
        if explicit:
            return explicit

        dominant = self._safe_text(gap.get("dominant_gap_signal"), "cognitive_gap")
        index = self._bounded(gap.get("knowledge_gap_index", decision.get("knowledge_gap_index", 0.0)))

        return (
            "Obtenir une assistance cognitive externe afin de résoudre une lacune "
            f"opérationnelle détectée ({dominant}, knowledge_gap_index={index:.3f}) "
            "tout en préservant l'identité, la gouvernance et la continuité historique "
            "d'Open Cognitive Ecology."
        )

    def _build_context(self, inputs: dict[str, Any], gap: dict[str, Any], decision: dict[str, Any]) -> str:
        supplied_context = self._safe_text(inputs.get("context"))
        components = []

        if supplied_context:
            components.append("Contexte fourni : " + supplied_context)

        components.append(
            "État OCE : phase O — collaboration cognitive externe autonome. "
            "O1 a détecté une lacune cognitive ; O2 a évalué l'opportunité "
            "d'une assistance externe ; O3 doit formuler une requête structurée."
        )

        if gap:
            components.append("Diagnostic O1 : " + self._compact(gap, 900))
        if decision:
            components.append("Décision O2 : " + self._compact(decision, 900))

        historical = inputs.get("history") or inputs.get("historical_context") or inputs.get("memory_excerpt")
        if historical:
            components.append("Historique pertinent : " + self._compact(historical, 700))

        return self._compact("\n".join(components), self.max_context_chars)

    def _build_constraints(self, inputs: dict[str, Any]) -> list[str]:
        constraints: list[str] = []
        raw = inputs.get("constraints", [])

        if isinstance(raw, str):
            constraints.extend([part.strip() for part in raw.split(";") if part.strip()])
        elif isinstance(raw, list):
            constraints.extend([self._safe_text(item) for item in raw if self._safe_text(item)])

        for item in self.DEFAULT_CONSTRAINTS:
            if item not in constraints:
                constraints.append(item)

        return constraints

    def _build_question(self, inputs: dict[str, Any], gap: dict[str, Any], decision: dict[str, Any]) -> str:
        explicit = self._safe_text(inputs.get("question"))
        if explicit:
            return explicit

        dominant = self._safe_text(gap.get("dominant_gap_signal"), "cognitive gap")
        reason = self._safe_text(decision.get("trigger_reason"), "external assistance authorized")

        return (
            "Au regard du contexte, du diagnostic et des contraintes ci-dessus, "
            f"propose une réponse structurée pour traiter la lacune dominante '{dominant}'. "
            f"La décision de consultation externe est motivée par : {reason}. "
            "Réponds en distinguant : analyse, hypothèses, risques, recommandations, "
            "conditions d'intégration et tests de validation."
        )

    def _render_prompt(
        self,
        objective: str,
        context: str,
        constraints: list[str],
        question: str,
        expected_output: str,
    ) -> str:
        constraints_text = "\n".join(f"- {item}" for item in constraints)
        return textwrap.dedent(f'''
        Projet : Open Cognitive Ecology — Collaboration cognitive externe autonome

        Objectif :
        {objective}

        Contexte :
        {context}

        Contraintes impératives :
        {constraints_text}

        Question :
        {question}

        Format de réponse attendu :
        {expected_output}
        ''').strip()

    def _score_prompt(
        self,
        objective: str,
        context: str,
        constraints: list[str],
        question: str,
        external_prompt: str,
    ) -> dict[str, float | bool]:
        objective_present = bool(objective.strip())
        context_present = bool(context.strip())
        question_present = bool(question.strip())
        constraints_present = bool(constraints)
        governance_constraints_included = any("governance" in c or "gouvernance" in c for c in constraints)
        identity_constraints_included = any("identity" in c or "identité" in c for c in constraints)
        historical_context_included = "histor" in context.lower() or any("histor" in c.lower() for c in constraints)
        compactness = self._bounded(1.0 - max(0, len(context) - self.max_context_chars) / max(self.max_context_chars, 1))

        score = self._bounded(
            0.18 * objective_present
            + 0.20 * context_present
            + 0.17 * question_present
            + 0.13 * constraints_present
            + 0.10 * governance_constraints_included
            + 0.10 * identity_constraints_included
            + 0.07 * historical_context_included
            + 0.05 * min(len(external_prompt) / 900.0, 1.0)
        )

        return {
            "prompt_quality_score": score,
            "context_compactness_score": compactness,
            "governance_constraints_included": bool(governance_constraints_included),
            "identity_constraints_included": bool(identity_constraints_included),
            "historical_context_included": bool(historical_context_included),
        }

    def generate(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        gap = self._extract_gap(inputs)
        decision = self._extract_decision(inputs)

        assistance_required = bool(decision.get("assistance_required", inputs.get("assistance_required", False)))

        strategic_prompt_diversification = None
        if not inputs.get("disable_strategic_prompt_diversification", False):
            try:
                from ontology.strategic_prompt_diversification_engine import StrategicPromptDiversificationEngine

                strategic_prompt_diversification = StrategicPromptDiversificationEngine(root=self.root).step({
                    "inputs": inputs,
                    "gap_result": gap,
                    "trigger_decision": decision,
                })
                if strategic_prompt_diversification.get("strategic_prompt_diversification_success"):
                    inputs.setdefault("objective", strategic_prompt_diversification.get("diversified_objective", ""))
                    inputs.setdefault("question", strategic_prompt_diversification.get("diversified_question", ""))
                    inputs.setdefault("expected_output", strategic_prompt_diversification.get("diversified_expected_output", ""))
                    constraints = list(inputs.get("constraints", [])) if isinstance(inputs.get("constraints"), list) else []
                    for item in strategic_prompt_diversification.get("strategic_constraints", []):
                        if item not in constraints:
                            constraints.append(item)
                    if constraints:
                        inputs["constraints"] = constraints
            except Exception as exc:
                strategic_prompt_diversification = {
                    "strategic_prompt_diversification_success": False,
                    "error": repr(exc),
                }

        objective = self._build_objective(inputs, gap, decision)
        context = self._build_context(inputs, gap, decision)
        constraints = self._build_constraints(inputs)
        question = self._build_question(inputs, gap, decision)
        expected_output = self._safe_text(
            inputs.get("expected_output"),
            (
                "1. Analyse structurée. 2. Hypothèses explicites. "
                "3. Risques et contradictions possibles. 4. Recommandations opérationnelles. "
                "5. Conditions d'intégration gouvernée. 6. Tests fonctionnels."
            ),
        )

        external_prompt = self._render_prompt(objective, context, constraints, question, expected_output)
        scores = self._score_prompt(objective, context, constraints, question, external_prompt)

        payload = {
            "objective": objective,
            "context": context,
            "constraints": constraints,
            "question": question,
            "expected_output": expected_output,
            "external_prompt": external_prompt,
            "metadata": {
                "source_primitive": PRIMITIVE,
                "gap_result": gap,
                "trigger_decision": decision,
                "generated_at_utc": self._utc_now(),
            },
        }

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": self._utc_now(),
            "prompt_generated": True,
            "assistance_required": assistance_required,
            "external_prompt": external_prompt,
            "external_query_payload": payload,
            **scores,
            "recommended_next_step": (
                "enqueue_external_query"
                if assistance_required and scores["prompt_quality_score"] >= 0.80
                else "review_or_enrich_prompt"
            ),
            "diagnostics": {
                "specialization": "external_prompt_generation",
                "non_redundancy": (
                    "Generates structured external prompts from O1/O2 outputs; "
                    "does not detect gaps, authorize assistance, or manage queues."
                ),
                "prompt_length": len(external_prompt),
                "context_length": len(context),
                "constraint_count": len(constraints),
            },
        }

        self._append_jsonl(self.history_file, result)
        return result

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        if isinstance(inputs, dict):
            merged.update(inputs)
        merged.update(kwargs)
        return self.generate(merged)


if __name__ == "__main__":
    generator = AutonomousPromptGenerator()
    print(json.dumps(generator.step({
        "trigger_decision": {
            "assistance_required": True,
            "trigger_reason": "test",
            "knowledge_gap_index": 0.7,
        },
        "gap_result": {
            "dominant_gap_signal": "uncertainty",
            "knowledge_gap_index": 0.7,
        },
    }), ensure_ascii=False, indent=2))
