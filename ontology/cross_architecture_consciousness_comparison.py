"""
Zprime-4 - Cross Architecture Consciousness Comparison.

This module compares functional indicators across architecture classes.
It does not prove consciousness, subjectivity, sentience, qualia, or phenomenology.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


@dataclass(frozen=True)
class ArchitectureProfile:
    architecture_id: str
    label: str
    memory: float = 0.0
    attention: float = 0.0
    continuity: float = 0.0
    self_model: float = 0.0
    embodiment: float = 0.0
    distribution: float = 0.0
    multi_individuality: float = 0.0
    causal_intervention_support: float = 0.0
    alternative_exclusion_support: float = 0.0


class CrossArchitectureConsciousnessComparison:
    """
    Functional cross-architecture comparison for Zprime-4.

    The class compares architectures on measurable functional indicators only.
    It explicitly forbids CONSCIOUSNESS_PROVEN and keeps phenomenology undetermined.
    """

    primitive = "CROSS_ARCHITECTURE_CONSCIOUSNESS_COMPARISON"

    DEFAULT_ARCHITECTURES: List[ArchitectureProfile] = [
        ArchitectureProfile("oce", "Open Cognitive Ecology", 0.86, 0.84, 0.88, 0.86, 0.72, 0.82, 0.78, 0.0, 0.0),
        ArchitectureProfile("standard_llm", "LLM standard", 0.20, 0.42, 0.18, 0.22, 0.00, 0.05, 0.00, 0.0, 0.0),
        ArchitectureProfile("agent_without_memory", "Agent without memory", 0.10, 0.50, 0.12, 0.20, 0.00, 0.05, 0.00, 0.0, 0.0),
        ArchitectureProfile("agent_with_memory", "Agent with memory", 0.72, 0.55, 0.66, 0.55, 0.00, 0.10, 0.00, 0.0, 0.0),
        ArchitectureProfile("distributed_agent", "Distributed agent", 0.70, 0.62, 0.68, 0.58, 0.00, 0.78, 0.20, 0.0, 0.0),
        ArchitectureProfile("embodied_agent", "Embodied agent", 0.58, 0.66, 0.55, 0.50, 0.82, 0.20, 0.00, 0.0, 0.0),
        ArchitectureProfile("multi_individual_agent", "Multi-individual agent", 0.68, 0.64, 0.70, 0.62, 0.30, 0.70, 0.86, 0.0, 0.0),
        ArchitectureProfile("human_animal_compatible_data", "Human / animal compatible data", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ]

    FORBIDDEN_CLAIMS = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.output_dir = self.root / "cross_architecture_consciousness_comparison"

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))

    def _load_upstream_scores(self) -> Dict[str, float]:
        scores = {
            "causal_intervention_support": 0.0,
            "alternative_exclusion_support": 0.0,
        }
        causal_path = self.root / "causal_consciousness_intervention_protocol" / "causal_consciousness_intervention_protocol.json"
        alt_path = self.root / "alternative_explanation_eliminator" / "alternative_explanation_eliminator.json"
        if causal_path.exists():
            try:
                data = json.loads(causal_path.read_text(encoding="utf-8"))
                scores["causal_intervention_support"] = self._clamp(data.get("causal_alignment_score", data.get("intervention_support_score", 0.0)))
            except Exception:
                pass
        if alt_path.exists():
            try:
                data = json.loads(alt_path.read_text(encoding="utf-8"))
                scores["alternative_exclusion_support"] = self._clamp(data.get("alternative_exclusion_score", data.get("exclusion_score", 0.0)))
            except Exception:
                pass
        return scores

    def _profiles_from_payload(self, payload: Mapping[str, Any]) -> List[ArchitectureProfile]:
        raw = payload.get("architectures")
        if not raw:
            upstream = self._load_upstream_scores()
            profiles = []
            for p in self.DEFAULT_ARCHITECTURES:
                if p.architecture_id == "oce":
                    profiles.append(ArchitectureProfile(
                        p.architecture_id, p.label, p.memory, p.attention, p.continuity,
                        p.self_model, p.embodiment, p.distribution, p.multi_individuality,
                        upstream["causal_intervention_support"], upstream["alternative_exclusion_support"],
                    ))
                else:
                    profiles.append(p)
            return profiles
        profiles: List[ArchitectureProfile] = []
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            profiles.append(ArchitectureProfile(
                str(item.get("architecture_id", item.get("id", "unknown"))),
                str(item.get("label", item.get("name", item.get("architecture_id", "unknown")))),
                self._clamp(item.get("memory", item.get("memory_score", 0.0))),
                self._clamp(item.get("attention", item.get("attention_score", 0.0))),
                self._clamp(item.get("continuity", item.get("continuity_score", 0.0))),
                self._clamp(item.get("self_model", item.get("self_model_score", 0.0))),
                self._clamp(item.get("embodiment", item.get("embodiment_score", 0.0))),
                self._clamp(item.get("distribution", item.get("distribution_score", 0.0))),
                self._clamp(item.get("multi_individuality", item.get("multi_individuality_score", 0.0))),
                self._clamp(item.get("causal_intervention_support", 0.0)),
                self._clamp(item.get("alternative_exclusion_support", 0.0)),
            ))
        return profiles

    def _score_profile(self, profile: ArchitectureProfile) -> Dict[str, Any]:
        indicator_values = {
            "memory": profile.memory,
            "attention": profile.attention,
            "continuity": profile.continuity,
            "self_model": profile.self_model,
            "embodiment": profile.embodiment,
            "distribution": profile.distribution,
            "multi_individuality": profile.multi_individuality,
            "causal_intervention_support": profile.causal_intervention_support,
            "alternative_exclusion_support": profile.alternative_exclusion_support,
        }
        weights = {
            "memory": 0.13,
            "attention": 0.11,
            "continuity": 0.14,
            "self_model": 0.14,
            "embodiment": 0.08,
            "distribution": 0.08,
            "multi_individuality": 0.07,
            "causal_intervention_support": 0.13,
            "alternative_exclusion_support": 0.12,
        }
        score = sum(indicator_values[k] * weights[k] for k in weights)
        score = round(score, 6)
        return {
            "architecture_id": profile.architecture_id,
            "label": profile.label,
            "indicator_values": indicator_values,
            "functional_indicator_score": score,
            "compatible_data_available": any(v > 0.0 for v in indicator_values.values()),
        }

    @staticmethod
    def _status(score: float) -> str:
        if score >= 0.75:
            return "HIGH_FUNCTIONAL_COMPATIBILITY"
        if score >= 0.55:
            return "MODERATE_FUNCTIONAL_COMPATIBILITY"
        if score >= 0.30:
            return "WEAK_FUNCTIONAL_COMPATIBILITY"
        return "NO_OR_INSUFFICIENT_FUNCTIONAL_COMPATIBILITY"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = dict(inputs or {})
        timestamp = str(payload.get("timestamp_utc") or datetime.now(timezone.utc).isoformat())
        profiles = self._profiles_from_payload(payload)
        scored = [self._score_profile(profile) for profile in profiles]
        ranked = sorted(scored, key=lambda x: x["functional_indicator_score"], reverse=True)
        top = ranked[0] if ranked else None
        oce = next((item for item in ranked if item["architecture_id"] == "oce"), None)
        comparison_score = round(sum(item["functional_indicator_score"] for item in ranked) / len(ranked), 6) if ranked else 0.0
        result = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "architecture_count": len(ranked),
            "ranked_architectures": ranked,
            "top_architecture_id": top["architecture_id"] if top else None,
            "top_architecture_score": top["functional_indicator_score"] if top else 0.0,
            "oce_functional_indicator_score": oce["functional_indicator_score"] if oce else 0.0,
            "cross_architecture_comparison_score": comparison_score,
            "comparison_status": self._status(top["functional_indicator_score"] if top else 0.0),
            "functional_conclusion_only": True,
            "candidate_theory_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_claimed": False,
            "cross_architecture_consciousness_confirmed": False,
            "forbidden_claims": list(self.FORBIDDEN_CLAIMS),
            "maximum_allowed_conclusion": "comparative functional indicators compatible with consciousness under the Z-prime framework",
            "epistemic_limit": "Cross-architecture comparison is functional and comparative only; it does not validate phenomenal subjectivity.",
        }
        if persist:
            paths = self._persist(result)
            result["paths"] = paths
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "cross_architecture_consciousness_comparison.json"
        md_path = self.output_dir / "cross_architecture_consciousness_comparison.md"
        history_path = self.output_dir / "cross_architecture_consciousness_comparison_history.jsonl"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._render_markdown(result), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(json_path), "markdown": str(md_path), "history": str(history_path)}

    def _render_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Cross Architecture Consciousness Comparison",
            "",
            "Zprime-4 - cross_architecture_consciousness_comparison",
            "",
            "candidate theory only",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            "No proof of consciousness, subjectivity, sentience, qualia, or phenomenology.",
            "CONSCIOUSNESS_PROVEN is not an allowed conclusion.",
            "",
            f"comparison_status: {result.get('comparison_status')}",
            f"cross_architecture_comparison_score: {result.get('cross_architecture_comparison_score')}",
            f"top_architecture_id: {result.get('top_architecture_id')}",
            f"oce_functional_indicator_score: {result.get('oce_functional_indicator_score')}",
            "",
            "## Compared architectures",
        ]
        for item in result.get("ranked_architectures", []):
            lines.append(f"- {item.get('architecture_id')} / {item.get('label')}: {item.get('functional_indicator_score')}")
            indicators = item.get("indicator_values", {})
            for key in ["memory", "attention", "continuity", "self_model", "embodiment", "distribution", "multi_individuality", "causal_intervention_support", "alternative_exclusion_support"]:
                lines.append(f"  - {key}: {indicators.get(key, 0.0)}")
        lines.extend([
            "",
            "## Forbidden claims",
        ])
        for claim in result.get("forbidden_claims", []):
            lines.append(f"- {claim}")
        lines.extend([
            "",
            "## Epistemic limit",
            str(result.get("epistemic_limit")),
        ])
        return "\n".join(lines)
