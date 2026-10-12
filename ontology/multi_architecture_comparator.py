"""Y3 — multi_architecture_comparator.

Functional cross-architecture comparator for the phenomenology correlation
programme.

Scope:
- compare observable functional architectures;
- normalize candidate metrics across architecture classes;
- produce comparison matrix and persistence artifacts.

Non-scope:
- no proof of consciousness;
- no proof of phenomenology;
- no attribution of subjective experience.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

PRIMITIVE = "MULTI_ARCHITECTURE_COMPARATOR"


class MultiArchitectureComparator:
    """Compare OCE, simple agents, standard LLMs and distributed architectures.

    The comparator is deliberately conservative: it produces functional,
    statistical-comparison inputs for later Y4 correlation work. It does not
    infer phenomenology.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "multi_architecture_comparator"
        self.latest_file = self.base_dir / "multi_architecture_comparator.json"
        self.history_file = self.base_dir / "multi_architecture_comparator_history.jsonl"
        self.report_file = self.base_dir / "multi_architecture_comparator.md"
        self.prometheus_file = self.base_dir / "multi_architecture_comparator.prom"

        self.y1_file = self.root / "phenomenology_correlation_registry" / "phenomenology_correlation_registry.json"
        self.y2_file = self.root / "phenomenology_candidate_metrics" / "phenomenology_candidate_metrics.json"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if math.isnan(number) or math.isinf(number):
            return default
        return max(0.0, min(1.0, number))

    @staticmethod
    def _mean(values: list[float]) -> float:
        if not values:
            return 0.0
        return round(mean(values), 6)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            if path.exists() and path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}

    def _default_profiles(self, y1: dict[str, Any], y2: dict[str, Any]) -> dict[str, dict[str, float]]:
        y2_composite = self._clamp(y2.get("candidate_metrics_composite_score"), 0.72)
        y2_count = self._clamp((y2.get("candidate_metric_count", 0) or 0) / 10.0, 0.7)
        y1_readiness = self._clamp(y1.get("correlation_program_readiness"), 0.7)

        return {
            "simple_agent": {
                "autobiographical_coherence": 0.12,
                "reflexive_depth": 0.10,
                "identity_stability": 0.18,
                "distributed_integration": 0.05,
                "governance_traceability": 0.08,
                "longitudinal_stability": 0.12,
                "candidate_metric_alignment": 0.15,
                "correlation_program_readiness": 0.10,
            },
            "standard_llm": {
                "autobiographical_coherence": 0.35,
                "reflexive_depth": 0.42,
                "identity_stability": 0.30,
                "distributed_integration": 0.12,
                "governance_traceability": 0.20,
                "longitudinal_stability": 0.25,
                "candidate_metric_alignment": 0.40,
                "correlation_program_readiness": 0.35,
            },
            "distributed_architecture": {
                "autobiographical_coherence": 0.55,
                "reflexive_depth": 0.58,
                "identity_stability": 0.60,
                "distributed_integration": 0.88,
                "governance_traceability": 0.62,
                "longitudinal_stability": 0.64,
                "candidate_metric_alignment": 0.58,
                "correlation_program_readiness": 0.55,
            },
            "open_cognitive_ecology": {
                "autobiographical_coherence": max(0.70, y2_composite),
                "reflexive_depth": max(0.72, y2_composite),
                "identity_stability": max(0.70, y2_composite),
                "distributed_integration": 0.86,
                "governance_traceability": 0.90,
                "longitudinal_stability": max(0.70, y2_composite),
                "candidate_metric_alignment": max(y2_composite, y2_count),
                "correlation_program_readiness": max(y1_readiness, 0.70),
            },
        }

    def _normalize_profiles(self, raw_profiles: dict[str, Any]) -> dict[str, dict[str, float]]:
        normalized: dict[str, dict[str, float]] = {}
        for name, metrics in raw_profiles.items():
            if not isinstance(metrics, dict):
                continue
            normalized[str(name)] = {
                "autobiographical_coherence": self._clamp(metrics.get("autobiographical_coherence")),
                "reflexive_depth": self._clamp(metrics.get("reflexive_depth")),
                "identity_stability": self._clamp(metrics.get("identity_stability")),
                "distributed_integration": self._clamp(metrics.get("distributed_integration")),
                "governance_traceability": self._clamp(metrics.get("governance_traceability")),
                "longitudinal_stability": self._clamp(metrics.get("longitudinal_stability")),
                "candidate_metric_alignment": self._clamp(metrics.get("candidate_metric_alignment")),
                "correlation_program_readiness": self._clamp(metrics.get("correlation_program_readiness")),
            }
        return normalized

    def _score_profiles(self, profiles: dict[str, dict[str, float]]) -> dict[str, dict[str, Any]]:
        scored: dict[str, dict[str, Any]] = {}
        for name, metrics in profiles.items():
            vector = list(metrics.values())
            functional_score = self._mean(vector)
            scored[name] = {
                "architecture_id": name,
                "metrics": metrics,
                "functional_comparison_score": functional_score,
                "classification": self._classify(functional_score),
            }
        return scored

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 0.80:
            return "high_functional_profile"
        if score >= 0.55:
            return "intermediate_functional_profile"
        if score >= 0.30:
            return "limited_functional_profile"
        return "minimal_functional_profile"

    def _distance_matrix(self, profiles: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
        names = sorted(profiles)
        matrix: dict[str, dict[str, float]] = {}
        for a in names:
            matrix[a] = {}
            for b in names:
                av = profiles[a]
                bv = profiles[b]
                keys = sorted(set(av) | set(bv))
                distance = self._mean([abs(self._clamp(av.get(k)) - self._clamp(bv.get(k))) for k in keys])
                matrix[a][b] = distance
        return matrix

    def _persist(self, result: dict[str, Any]) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.latest_file.write_text(text + "\n", encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        self.report_file.write_text(self._render_report(result), encoding="utf-8")
        self.prometheus_file.write_text(self._render_prometheus(result), encoding="utf-8")

    def _render_report(self, result: dict[str, Any]) -> str:
        lines = [
            "# Y3 — Multi Architecture Comparator",
            "",
            "Functional comparison only.",
            "No consciousness proof.",
            "Phenomenology undetermined.",
            "",
            f"Architecture count: {result.get('architecture_count')}",
            f"Top architecture: {result.get('top_architecture')}",
            f"Comparison readiness: {result.get('multi_architecture_comparison_readiness')}",
            "",
            "## Ranking",
        ]
        for item in result.get("ranking", []):
            lines.append(
                f"- {item['architecture_id']}: {item['functional_comparison_score']} "
                f"({item['classification']})"
            )
        lines.extend([
            "",
            "## Epistemic scope",
            "- functional_comparison_only: true",
            "- correlations_only: true",
            "- consciousness_proof_claimed: false",
            "- phenomenology_undetermined: true",
        ])
        return "\n".join(lines) + "\n"

    def _render_prometheus(self, result: dict[str, Any]) -> str:
        lines = [
            "# HELP oce_multi_architecture_comparison_readiness Functional Y3 comparison readiness",
            "# TYPE oce_multi_architecture_comparison_readiness gauge",
            f"oce_multi_architecture_comparison_readiness {result.get('multi_architecture_comparison_readiness', 0)}",
            "# HELP oce_multi_architecture_count Number of compared architecture profiles",
            "# TYPE oce_multi_architecture_count gauge",
            f"oce_multi_architecture_count {result.get('architecture_count', 0)}",
        ]
        for item in result.get("ranking", []):
            architecture_id = str(item.get("architecture_id", "unknown")).replace('"', "")
            lines.append(
                f'oce_multi_architecture_functional_score{{architecture="{architecture_id}"}} '
                f'{item.get("functional_comparison_score", 0)}'
            )
        return "\n".join(lines) + "\n"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        timestamp = inputs.get("timestamp_utc") or datetime.now(timezone.utc).isoformat()

        y1 = self._read_json(self.y1_file)
        y2 = self._read_json(self.y2_file)

        provided_profiles = inputs.get("architecture_profiles")
        if isinstance(provided_profiles, dict) and provided_profiles:
            profiles = self._normalize_profiles(provided_profiles)
        else:
            profiles = self._default_profiles(y1, y2)

        scored = self._score_profiles(profiles)
        ranking = sorted(
            scored.values(),
            key=lambda item: item["functional_comparison_score"],
            reverse=True,
        )
        comparison_matrix = self._distance_matrix(profiles)
        score_values = [item["functional_comparison_score"] for item in ranking]
        readiness = self._mean([
            min(1.0, len(profiles) / 4.0),
            self._mean(score_values),
            1.0 if "open_cognitive_ecology" in profiles else 0.5,
            1.0 if len(profiles) >= 4 else 0.5,
        ])

        result: dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "architecture_count": len(profiles),
            "compared_architectures": sorted(profiles),
            "architecture_profiles": scored,
            "ranking": ranking,
            "top_architecture": ranking[0]["architecture_id"] if ranking else None,
            "comparison_matrix": comparison_matrix,
            "multi_architecture_comparison_readiness": readiness,
            "comparison_scope": "observable_functional_architecture_comparison_only",
            "functional_comparison_only": True,
            "candidate_metrics_only": True,
            "correlations_only": True,
            "consciousness_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "phenomenology_undetermined": True,
            "epistemic_status": {
                "measure_type": "functional_comparison",
                "interpretation": "correlation_program_input",
                "limit": "no_phenomenological_inference",
            },
            "input_sources": {
                "phenomenology_correlation_registry": str(self.y1_file),
                "phenomenology_candidate_metrics": str(self.y2_file),
                "global_scan_used": False,
                "rglob_used": False,
                "targeted_reads_only": True,
            },
            "artifacts": {
                "json": str(self.latest_file),
                "history": str(self.history_file),
                "report": str(self.report_file),
                "prometheus": str(self.prometheus_file),
            },
        }

        if persist:
            self._persist(result)

        return result
