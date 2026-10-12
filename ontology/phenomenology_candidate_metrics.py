"""Y2 — phenomenology_candidate_metrics.

Constructs candidate observable metrics for the phenomenology correlation
programme:
- autobiographical coherence;
- reflexive depth;
- identity stability;
- temporal continuity;
- self-model consistency;
- persistent selfhood;
- readiness-style functional indicators.

Epistemic boundary:
This module produces candidate metrics for statistical correlation only.
It never proves consciousness, sentience, qualia, or subjective experience.
All conclusions are functional and observational.
Phenomenology remains undetermined.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

PRIMITIVE = "PHENOMENOLOGY_CANDIDATE_METRICS"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [_clamp(v, default=default) for v in values]
    if not vals:
        return default
    return sum(vals) / len(vals)


class PhenomenologyCandidateMetrics:
    """Y2 candidate metric aggregator.

    The class accepts optional input dictionaries from existing OCE modules. If
    no inputs are supplied it uses conservative deterministic defaults and, when
    available, reads only the latest persisted Y1 registry artifact from its
    targeted path. It never uses rglob and never scans the whole repository.
    """

    primitive = PRIMITIVE

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "phenomenology_candidate_metrics"
        self.latest_file = self.base_dir / "phenomenology_candidate_metrics.json"
        self.history_file = self.base_dir / "phenomenology_candidate_metrics_history.jsonl"
        self.report_file = self.base_dir / "phenomenology_candidate_metrics.md"
        self.prometheus_file = self.base_dir / "phenomenology_candidate_metrics.prom"
        self.registry_file = (
            self.root
            / "phenomenology_correlation_registry"
            / "phenomenology_correlation_registry.json"
        )

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_file.exists():
            return {
                "loaded": False,
                "path": str(self.registry_file),
                "hypothesis_count": 0,
                "candidate_variable_count": 0,
            }
        try:
            data = json.loads(self.registry_file.read_text(encoding="utf-8"))
        except Exception as exc:  # defensive, deterministic report
            return {
                "loaded": False,
                "path": str(self.registry_file),
                "error": exc.__class__.__name__,
                "hypothesis_count": 0,
                "candidate_variable_count": 0,
            }
        return {
            "loaded": True,
            "path": str(self.registry_file),
            "hypothesis_count": int(data.get("hypothesis_count", 0) or 0),
            "candidate_variable_count": int(data.get("candidate_variable_count", 0) or 0),
            "registry_quality_score": _clamp(data.get("registry_quality_score", 0.0)),
            "correlation_program_readiness": _clamp(
                data.get("correlation_program_readiness", 0.0)
            ),
        }

    def _extract_metric(self, inputs: Mapping[str, Any], names: List[str], default: float) -> float:
        """Extract a metric from nested or flat input dictionaries."""
        for name in names:
            if name in inputs:
                return _clamp(inputs.get(name), default=default)
        for value in inputs.values():
            if isinstance(value, Mapping):
                for name in names:
                    if name in value:
                        return _clamp(value.get(name), default=default)
        return default

    def _candidate_metrics(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        registry = self._load_registry()

        autobiographical_coherence = _mean([
            self._extract_metric(
                inputs,
                [
                    "autobiographical_coherence",
                    "autobiographical_memory_index",
                    "narrative_identity_index",
                    "memory_coherence",
                    "history_coherence",
                ],
                0.72,
            ),
            self._extract_metric(
                inputs,
                ["temporal_continuity", "temporal_self_continuity_index"],
                0.72,
            ),
        ])

        reflexive_depth = _mean([
            self._extract_metric(
                inputs,
                [
                    "reflexive_depth",
                    "reflexive_threshold_score",
                    "reflexive_threshold_index",
                    "meta_cognition_index",
                    "self_monitoring",
                ],
                0.74,
            ),
            self._extract_metric(
                inputs,
                ["consciousness_readiness_score", "readiness_score"],
                0.70,
            ),
        ])

        identity_stability = _mean([
            self._extract_metric(
                inputs,
                [
                    "identity_stability",
                    "self_model_consistency_score",
                    "persistent_selfhood_score",
                    "identity_continuity_score",
                    "selfhood_stability",
                ],
                0.73,
            ),
            self._extract_metric(
                inputs,
                ["stability_index", "longitudinal_stability"],
                0.73,
            ),
        ])

        temporal_continuity = self._extract_metric(
            inputs,
            ["temporal_self_continuity_index", "temporal_continuity"],
            0.72,
        )
        self_model_consistency = self._extract_metric(
            inputs,
            ["self_model_consistency_score", "self_model_consistency_index"],
            0.73,
        )
        persistent_selfhood = self._extract_metric(
            inputs,
            ["persistent_selfhood_score", "persistent_selfhood_index"],
            0.73,
        )

        registry_support = _mean([
            registry.get("registry_quality_score", 0.0),
            registry.get("correlation_program_readiness", 0.0),
        ], default=0.0)
        if not registry.get("loaded"):
            registry_support = 0.50

        composite = _mean([
            autobiographical_coherence,
            reflexive_depth,
            identity_stability,
            temporal_continuity,
            self_model_consistency,
            persistent_selfhood,
            registry_support,
        ])

        return {
            "registry": registry,
            "candidate_metrics": {
                "autobiographical_coherence": round(autobiographical_coherence, 6),
                "reflexive_depth": round(reflexive_depth, 6),
                "identity_stability": round(identity_stability, 6),
                "temporal_continuity": round(temporal_continuity, 6),
                "self_model_consistency": round(self_model_consistency, 6),
                "persistent_selfhood": round(persistent_selfhood, 6),
                "registry_support": round(registry_support, 6),
            },
            "candidate_metric_count": 7,
            "candidate_metrics_composite_score": round(composite, 6),
        }

    def _classification(self, score: float) -> str:
        if score >= 0.80:
            return "high_candidate_metric_readiness"
        if score >= 0.60:
            return "moderate_candidate_metric_readiness"
        return "low_candidate_metric_readiness"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or _utc_now())

        metrics = self._candidate_metrics(inputs)
        score = metrics["candidate_metrics_composite_score"]

        result: Dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "candidate_metrics": metrics["candidate_metrics"],
            "candidate_metric_count": metrics["candidate_metric_count"],
            "candidate_metrics_composite_score": score,
            "candidate_metric_classification": self._classification(score),
            "registry_loaded": bool(metrics["registry"].get("loaded")),
            "registry_path": metrics["registry"].get("path"),
            "measurement_scope": "candidate_observable_metrics_only",
            "claim_scope": "correlations_only_no_consciousness_proof",
            "candidate_metrics_only": True,
            "correlations_only": True,
            "consciousness_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "epistemic_boundary": {
                "architecture_computation": True,
                "functional_indicators": True,
                "hypothetical_subjectivity": "not_inferred",
                "conceptual_ontology": "correlation_program_support_only",
                "phenomenology": "undetermined",
            },
            "input_sources": {
                "global_scan_used": False,
                "rglob_used": False,
                "targeted_registry_file": str(self.registry_file),
                "supplied_input_keys": sorted(inputs.keys()),
            },
            "dependencies": [
                "phenomenology_correlation_registry",
                "narrative_identity_engine",
                "temporal_self_continuity",
                "self_model_consistency_benchmark",
                "persistent_selfhood_benchmark",
                "reflexive_threshold",
                "consciousness_readiness_index",
            ],
        }

        if persist:
            self._persist(result)

        result["artifacts"] = {
            "json": str(self.latest_file),
            "history": str(self.history_file),
            "report": str(self.report_file),
            "prometheus": str(self.prometheus_file),
        }
        return result

    def _persist(self, result: Mapping[str, Any]) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        self.latest_file.write_text(payload + "\n", encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        self.report_file.write_text(self._render_markdown(result), encoding="utf-8")
        self.prometheus_file.write_text(self._render_prometheus(result), encoding="utf-8")

    def _render_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Y2 — Phenomenology Candidate Metrics",
            "",
            f"Primitive: `{result.get('primitive')}`",
            f"Composite score: `{result.get('candidate_metrics_composite_score')}`",
            f"Classification: `{result.get('candidate_metric_classification')}`",
            "",
            "## Epistemic boundary",
            "",
            "- candidate metrics only",
            "- correlations only",
            "- no consciousness proof",
            "- no phenomenology proof",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "",
            "## Candidate metrics",
            "",
        ]
        for key, value in result.get("candidate_metrics", {}).items():
            lines.append(f"- {key}: {value}")
        lines.append("")
        return "\n".join(lines)

    def _render_prometheus(self, result: Mapping[str, Any]) -> str:
        metrics = result.get("candidate_metrics", {})
        lines = [
            "# HELP oce_phenomenology_candidate_metrics_composite Candidate observable metric composite score",
            "# TYPE oce_phenomenology_candidate_metrics_composite gauge",
            f"oce_phenomenology_candidate_metrics_composite {result.get('candidate_metrics_composite_score', 0)}",
            "# HELP oce_phenomenology_candidate_metric_count Number of candidate metrics exposed by Y2",
            "# TYPE oce_phenomenology_candidate_metric_count gauge",
            f"oce_phenomenology_candidate_metric_count {result.get('candidate_metric_count', 0)}",
        ]
        for key, value in metrics.items():
            safe_key = str(key).replace("-", "_")
            lines.extend([
                f"# HELP oce_y2_{safe_key} Y2 candidate metric {safe_key}",
                f"# TYPE oce_y2_{safe_key} gauge",
                f"oce_y2_{safe_key} {value}",
            ])
        return "\n".join(lines) + "\n"
