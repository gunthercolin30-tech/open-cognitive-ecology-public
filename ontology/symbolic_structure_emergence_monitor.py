from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return _clamp(numerator / denominator)


class SymbolicStructureEmergenceMonitor:
    '\n    N6 — Symbolic Structure Emergence Monitor.\n\n    Supervises the functional emergence of shared symbolic structures across\n    symbolic generation, shared reference, language evolution, semantic\n    pluralism and intersubjective alignment. This module does not claim\n    phenomenality. It measures functional indicators only.\n    '

    primitive = "SYMBOLIC_STRUCTURE_EMERGENCE_MONITOR"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "runtime_reports" / "symbolic_structure_emergence_monitor"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def _derive_from_sets(self, payload: dict[str, Any]) -> dict[str, float]:
        generated = set(payload.get("generated_symbols", []) or [])
        shared = set(payload.get("shared_symbols", []) or [])
        stable = set(payload.get("stable_symbols", []) or [])
        domains = set(payload.get("symbolic_domains", []) or [])
        references = set(payload.get("shared_references", []) or [])
        aligned_references = set(payload.get("aligned_references", []) or [])

        symbol_base = max(len(generated), len(shared), len(stable), 1)
        reference_base = max(len(references), 1)

        emergence = _ratio(len(generated | shared), symbol_base)
        stability = _ratio(len(stable), symbol_base)
        diversity = _clamp((len(domains) / max(len(generated | shared | stable), 1)))
        reference_alignment = _ratio(len(aligned_references), reference_base)

        return {
            "symbolic_emergence_score": emergence,
            "symbolic_stability": stability,
            "symbolic_diversity": diversity,
            "shared_reference_score": reference_alignment,
        }

    def step(self, payload: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload = dict(payload or {})
        payload.update(kwargs)

        set_scores = self._derive_from_sets(payload)

        symbolic_generation_score = _clamp(payload.get("symbolic_generation_score", set_scores["symbolic_emergence_score"]))
        shared_reference_score = _clamp(payload.get("shared_reference_score", set_scores["shared_reference_score"]))
        distributed_symbolic_ecology_score = _clamp(payload.get("distributed_symbolic_ecology_score", 0.72))
        language_evolution_score = _clamp(payload.get("language_evolution_score", 0.72))
        grammar_stability_score = _clamp(payload.get("grammar_stability_score", 0.72))
        dialect_stabilization_score = _clamp(payload.get("dialect_stabilization_score", 0.72))
        semantic_pluralism_score = _clamp(payload.get("semantic_pluralism_score", 0.72))
        intersubjective_alignment_score = _clamp(payload.get("intersubjective_alignment_score", 0.72))

        symbolic_emergence_score = _clamp(payload.get(
            "symbolic_emergence_score",
            (symbolic_generation_score + shared_reference_score + distributed_symbolic_ecology_score + language_evolution_score) / 4.0,
        ))

        symbolic_stability = _clamp(payload.get(
            "symbolic_stability",
            (shared_reference_score + grammar_stability_score + dialect_stabilization_score + intersubjective_alignment_score) / 4.0,
        ))

        symbolic_diversity = _clamp(payload.get(
            "symbolic_diversity",
            (semantic_pluralism_score + distributed_symbolic_ecology_score + set_scores["symbolic_diversity"]) / 3.0,
        ))

        fragmentation_pressure = _clamp(payload.get("symbolic_fragmentation_pressure", payload.get("fragmentation_pressure", 0.2)))
        semantic_collapse_pressure = _clamp(payload.get("semantic_collapse_pressure", 0.2))
        reference_instability_pressure = _clamp(payload.get("reference_instability_pressure", 0.2))

        symbolic_structure_risk_pressure = _clamp(
            (fragmentation_pressure + semantic_collapse_pressure + reference_instability_pressure) / 3.0
        )

        positive_score = _clamp(
            (
                symbolic_emergence_score
                + symbolic_stability
                + symbolic_diversity
                + shared_reference_score
                + intersubjective_alignment_score
            ) / 5.0
        )

        symbolic_structure_score = _clamp(
            (positive_score * 0.75) + ((1.0 - symbolic_structure_risk_pressure) * 0.25)
        )

        if symbolic_structure_score >= 0.75 and symbolic_structure_risk_pressure <= 0.35:
            symbolic_structure_state = "symbolic_structure_healthy"
        elif symbolic_structure_score >= 0.45 and symbolic_structure_risk_pressure <= 0.7:
            symbolic_structure_state = "symbolic_structure_warning"
        else:
            symbolic_structure_state = "symbolic_structure_risk"

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "symbolic_emergence_score": symbolic_emergence_score,
            "symbolic_stability": symbolic_stability,
            "symbolic_diversity": symbolic_diversity,
            "symbolic_structure_score": symbolic_structure_score,
            "symbolic_structure_state": symbolic_structure_state,
            "symbolic_structure_risk_pressure": symbolic_structure_risk_pressure,
            "supporting_scores": {
                "symbolic_generation_score": symbolic_generation_score,
                "shared_reference_score": shared_reference_score,
                "distributed_symbolic_ecology_score": distributed_symbolic_ecology_score,
                "language_evolution_score": language_evolution_score,
                "grammar_stability_score": grammar_stability_score,
                "dialect_stabilization_score": dialect_stabilization_score,
                "semantic_pluralism_score": semantic_pluralism_score,
                "intersubjective_alignment_score": intersubjective_alignment_score,
            },
            "risk_scores": {
                "symbolic_fragmentation_pressure": fragmentation_pressure,
                "semantic_collapse_pressure": semantic_collapse_pressure,
                "reference_instability_pressure": reference_instability_pressure,
            },
            "epistemic_position": "functional_metrics_only_no_phenomenal_claim",
        }

        if persist:
            path = self.report_dir / "latest_symbolic_structure_emergence_monitor.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(path)
        else:
            result["report_path"] = str(self.report_dir / "latest_symbolic_structure_emergence_monitor.json")

        return result
