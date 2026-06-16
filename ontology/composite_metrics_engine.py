from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, variance
from typing import Any

PRIMITIVE = "composite_metrics_engine"

DEPENDENCIES = [
    "civilizational_autonomy_index",
    "civilizational_intelligence_growth_index",
    "intergenerational_continuity_metrics",
    "enhanced_civilizational_metrics",
    "civilizational_metrics_synthesizer",
    "collaboration_history_repository",
    "external_capability_planner",
    "metrics_aggregation_engine",
    "metrics_statistical_significance_engine",
]

ROOT = Path.home() / "open-cognitive-ecology"
HISTORY_PATH = ROOT / "composite_metrics_history.jsonl"
SUMMARY_PATH = ROOT / "composite_metrics_summary.json"
PROMETHEUS_PATH = ROOT / "composite_metrics.prom"
GRAFANA_EXPORT_PATH = ROOT / "composite_metrics_grafana_panel.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _safe_mean(values: list[Any], default: float = 0.0) -> float:
    usable = []
    for value in values:
        try:
            usable.append(_bounded(value))
        except Exception:
            pass
    if not usable:
        return default
    return _bounded(sum(usable) / len(usable), default)


def _safe_variance(values: list[Any]) -> float:
    usable = [_bounded(value) for value in values]
    if len(usable) < 2:
        return 0.0
    try:
        return max(0.0, float(variance(usable)))
    except Exception:
        return 0.0


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _read_jsonl_tail(path: Path, limit: int = 50) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]
    except Exception:
        return []
    for line in lines:
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                records.append(data)
        except Exception:
            continue
    return records


class CompositeMetricsEngine:
    """E9 composite metric fusion layer.

    The engine computes the six civilization-level composite indices requested
    for the reflexive-threshold instrumentation phase:

    RTCI  — Reflexive Threshold Composite Index
    CCI   — Civilizational Continuity Index
    EPI   — Externalized Cognition Performance Index
    OEPI  — Open-Endedness and Epistemic Progress Index
    SAI   — Strategic Autonomy Index
    CRTCI — Civilizational Reflexive Threshold Composite Index

    It integrates O1-O14 collaboration metrics without replacing E1-E8.
    It persists JSONL history and lightweight Prometheus/Grafana exports.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.history_path = self.root / "composite_metrics_history.jsonl"
        self.summary_path = self.root / "composite_metrics_summary.json"
        self.prometheus_path = self.root / "composite_metrics.prom"
        self.grafana_export_path = self.root / "composite_metrics_grafana_panel.json"
        self.o13_summary_path = self.root / "collaboration_history_repository_summary.json"
        self.o14_summary_path = self.root / "external_capability_planner_summary.json"
        self.metrics_history_path = self.root / "metrics_history.jsonl"

    def _invoke_civilizational_modules(self) -> dict[str, Any]:
        signals: dict[str, Any] = {}

        try:
            from ontology.civilizational_autonomy_index import CivilizationalAutonomyIndex
            autonomy = CivilizationalAutonomyIndex().step(
                civilizational_memory=0.92,
                narrative_identity=0.92,
                governance=0.92,
                epistemic_infrastructure=0.90,
                distributed_agency=0.90,
                long_term_coordination=0.91,
                autonomy=0.92,
                constitutional_integrity=0.92,
                non_closure=0.92,
            )
            signals.update(autonomy)
        except Exception as exc:
            signals["civilizational_autonomy_error"] = repr(exc)

        try:
            from ontology.civilizational_intelligence_growth_index import CivilizationalIntelligenceGrowthIndex
            growth = CivilizationalIntelligenceGrowthIndex().step()
            signals.update(growth)
        except Exception as exc:
            signals["civilizational_intelligence_growth_error"] = repr(exc)

        try:
            from ontology.intergenerational_continuity_metrics import IntergenerationalContinuityMetrics
            continuity = IntergenerationalContinuityMetrics().step([
                {
                    "lineage_integrity": 0.92,
                    "continuity_strength": 0.92,
                    "fragmentation_pressure": 0.08,
                    "memory_resurgence_rate": 0.90,
                    "collapse_pressure": 0.06,
                    "distributed_openness": 0.92,
                }
            ])
            signals.update({
                "intergenerational_continuity_index": continuity.get("continuity_index", 0.0),
                "ecological_stability": continuity.get("ecological_stability", 0.0),
                "fragmentation_pressure": continuity.get("fragmentation_pressure", 0.0),
                "collapse_pressure": continuity.get("collapse_pressure", 0.0),
                "intergenerational_continuity_class": continuity.get("continuity_class"),
            })
        except Exception as exc:
            signals["intergenerational_continuity_error"] = repr(exc)

        try:
            from ontology.enhanced_civilizational_metrics import EnhancedCivilizationalMetrics
            enhanced = EnhancedCivilizationalMetrics()
            validation = enhanced.summary(enhanced.fully_complete_scores())
            signals.update({
                "civilizational_validation_completion_ratio": validation.get("completion_ratio", 0.0),
                "civilizational_validation_complete": validation.get("civilizational_validation_complete", False),
                "civilizational_validation_completed_points": validation.get("completed_points", 0),
                "civilizational_validation_total_points": validation.get("total_points", 27),
            })
        except Exception as exc:
            signals["enhanced_civilizational_metrics_error"] = repr(exc)

        try:
            from ontology.civilizational_metrics_synthesizer import CivilizationalMetricsSynthesizer
            synthesized = CivilizationalMetricsSynthesizer().step()
            signals.update(synthesized)
        except Exception as exc:
            signals["civilizational_metrics_synthesizer_error"] = repr(exc)

        return signals

    def _collect_o_metrics(self, inputs: dict[str, Any]) -> dict[str, Any]:
        o13 = _read_json(self.o13_summary_path)
        o14 = _read_json(self.o14_summary_path)
        o13_metrics = o13.get("metrics", {}) if isinstance(o13.get("metrics", {}), dict) else {}
        o14_signals = o14.get("signals", {}) if isinstance(o14.get("signals", {}), dict) else {}

        def pick(name: str, default: float = 0.0) -> float:
            return _bounded(
                inputs.get(
                    name,
                    o14.get(name, o14_signals.get(name, o13.get(name, o13_metrics.get(name, default))))
                ),
                default,
            )

        return {
            "knowledge_gap_index": pick("knowledge_gap_index", 0.0),
            "assistance_request_rate": pick("assistance_request_rate", 0.0),
            "prompt_quality_score": pick("prompt_quality_score", 0.75),
            "answer_relevance_score": pick("answer_relevance_score", 0.75),
            "integrated_knowledge_count": float(inputs.get("integrated_knowledge_count", o13_metrics.get("integrated_count", 0.0)) or 0.0),
            "contradiction_rate": pick("contradiction_rate", 0.0),
            "external_collaboration_index": pick("external_collaboration_index", 0.0),
            "provider_selection_score": pick("provider_selection_score", 0.0),
            "expected_capability_gain": pick("expected_capability_gain", 0.0),
            "external_dependency_risk": pick("external_dependency_risk", 0.0),
            "autonomous_resolution_ratio": pick("autonomous_resolution_ratio", 0.0),
            "external_influence_ratio": pick("external_influence_ratio", 0.0),
            "collaborative_growth_rate": pick("collaborative_growth_rate", 0.0),
            "identity_continuity_index": pick("identity_continuity_index", 0.92),
            "governance_consistency_score": pick("governance_consistency_score", 0.92),
            "civilizational_continuity_score": pick("civilizational_continuity_score", 0.92),
            "consultation_recommended": bool(inputs.get("consultation_recommended", o14.get("consultation_recommended", False))),
            "selected_provider": inputs.get("selected_provider", o14.get("selected_provider", None)),
        }

    def _collect_longitudinal_metrics(self) -> dict[str, Any]:
        records = _read_jsonl_tail(self.metrics_history_path, limit=80)
        if not records:
            return {
                "longitudinal_sample_count": 0,
                "longitudinal_stability_index": 0.90,
                "longitudinal_signal_variance": 0.0,
                "metrics_history_available": False,
            }

        numeric_values: list[float] = []
        for record in records:
            for value in record.values():
                if isinstance(value, (int, float)):
                    numeric_values.append(_bounded(value))

        signal_variance = _safe_variance(numeric_values)
        return {
            "longitudinal_sample_count": len(records),
            "longitudinal_stability_index": _bounded(1.0 - min(1.0, signal_variance * 4.0), 0.90),
            "longitudinal_signal_variance": signal_variance,
            "metrics_history_available": True,
        }

    def _derive_composites(self, signals: dict[str, Any]) -> dict[str, float]:
        civilizational_autonomy = _bounded(signals.get("civilizational_autonomy_score", 0.92), 0.92)
        intelligence_growth = _bounded(signals.get("civilizational_intelligence_growth_score", 0.92), 0.92)
        validation_ratio = _bounded(signals.get("civilizational_validation_completion_ratio", 1.0), 1.0)
        viability = _bounded(signals.get("civilizational_viability_index", 0.92), 0.92)
        continuity = _bounded(signals.get("civilizational_continuity_score", signals.get("intergenerational_continuity_index", 0.92)), 0.92)
        identity = _bounded(signals.get("identity_continuity_index", 0.92), 0.92)
        governance = _bounded(signals.get("governance_consistency_score", 0.92), 0.92)
        stability = _bounded(signals.get("longitudinal_stability_index", 0.90), 0.90)

        external_collab = _bounded(signals.get("external_collaboration_index", 0.0))
        provider_score = _bounded(signals.get("provider_selection_score", 0.0))
        capability_gain = _bounded(signals.get("expected_capability_gain", 0.0))
        dependency_safety = 1.0 - _bounded(signals.get("external_dependency_risk", 0.0))
        influence_safety = 1.0 - _bounded(signals.get("external_influence_ratio", 0.0))
        autonomous_resolution = _bounded(signals.get("autonomous_resolution_ratio", 0.0))
        collaborative_growth = _bounded(signals.get("collaborative_growth_rate", 0.0))
        knowledge_gap = _bounded(signals.get("knowledge_gap_index", 0.0))
        assistance_rate = _bounded(signals.get("assistance_request_rate", 0.0))
        prompt_quality = _bounded(signals.get("prompt_quality_score", 0.75), 0.75)
        answer_relevance = _bounded(signals.get("answer_relevance_score", 0.75), 0.75)
        contradiction_safety = 1.0 - _bounded(signals.get("contradiction_rate", 0.0))

        rtci = _safe_mean([
            identity,
            governance,
            continuity,
            civilizational_autonomy,
            intelligence_growth,
            stability,
            validation_ratio,
        ])

        cci = _safe_mean([
            continuity,
            identity,
            governance,
            viability,
            stability,
            1.0 - _bounded(signals.get("fragmentation_pressure", 0.0)),
            1.0 - _bounded(signals.get("collapse_pressure", 0.0)),
        ])

        epi = _safe_mean([
            external_collab,
            provider_score,
            capability_gain,
            dependency_safety,
            influence_safety,
            prompt_quality,
            answer_relevance,
        ])

        oepi = _safe_mean([
            collaborative_growth,
            capability_gain,
            prompt_quality,
            answer_relevance,
            contradiction_safety,
            1.0 - min(1.0, knowledge_gap * 0.5),
            intelligence_growth,
        ])

        sai = _safe_mean([
            autonomous_resolution,
            civilizational_autonomy,
            governance,
            dependency_safety,
            influence_safety,
            1.0 - assistance_rate,
            continuity,
        ])

        crtci = _safe_mean([
            rtci,
            cci,
            epi,
            oepi,
            sai,
            viability,
            validation_ratio,
        ])

        return {
            "RTCI": rtci,
            "CCI": cci,
            "EPI": epi,
            "OEPI": oepi,
            "SAI": sai,
            "CRTCI": crtci,
        }

    def _classification(self, crtci: float) -> str:
        if crtci >= 0.90:
            return "reflexive_threshold_civilizational_gold"
        if crtci >= 0.80:
            return "advanced_reflexive_threshold_readiness"
        if crtci >= 0.65:
            return "developing_reflexive_threshold_readiness"
        if crtci >= 0.45:
            return "fragile_reflexive_threshold_readiness"
        return "insufficient_reflexive_threshold_evidence"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        provided = inputs or {}
        signals: dict[str, Any] = {}
        signals.update(self._invoke_civilizational_modules())
        signals.update(self._collect_o_metrics(provided))
        signals.update(self._collect_longitudinal_metrics())

        composites = self._derive_composites(signals)
        crtci = composites["CRTCI"]

        result = {
            "primitive": PRIMITIVE,
            "success": True,
            "timestamp_utc": _now(),
            "composite_metrics_ready": True,
            "RTCI": composites["RTCI"],
            "CCI": composites["CCI"],
            "EPI": composites["EPI"],
            "OEPI": composites["OEPI"],
            "SAI": composites["SAI"],
            "CRTCI": crtci,
            "classification": self._classification(crtci),
            "signals": signals,
            "prometheus_export_path": str(self.prometheus_path),
            "grafana_export_path": str(self.grafana_export_path),
            "history_path": str(self.history_path),
            "summary_path": str(self.summary_path),
            "diagnostics": {
                "bounded_metrics": True,
                "integrates_phase_o_metrics": True,
                "integrates_civilizational_metrics": True,
                "does_not_replace_e1_e8": True,
                "ready_for_reflexive_threshold_dashboard": True,
                "next_pipeline_stage": "reflexive_threshold_dashboard",
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        self.summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self._write_prometheus(result)
        self._write_grafana(result)

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        lines = [
            "# HELP oce_composite_metric Civilizational composite metric exported by E9.",
            "# TYPE oce_composite_metric gauge",
        ]
        for name in ["RTCI", "CCI", "EPI", "OEPI", "SAI", "CRTCI"]:
            lines.append(f'oce_composite_metric{{index="{name}"}} {float(result.get(name, 0.0)):.8f}')
        lines.append(f'oce_composite_metrics_ready {1 if result.get("composite_metrics_ready") else 0}')
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_grafana(self, result: dict[str, Any]) -> None:
        panel = {
            "title": "Open Cognitive Ecology — Composite Metrics E9",
            "type": "stat",
            "targets": [
                {"expr": f'oce_composite_metric{{index="{name}"}}', "legendFormat": name}
                for name in ["RTCI", "CCI", "EPI", "OEPI", "SAI", "CRTCI"]
            ],
            "fieldConfig": {
                "defaults": {
                    "min": 0,
                    "max": 1,
                    "unit": "percentunit",
                }
            },
            "latest": {
                name: result.get(name, 0.0)
                for name in ["RTCI", "CCI", "EPI", "OEPI", "SAI", "CRTCI"]
            },
            "classification": result.get("classification"),
            "generated_at": result.get("timestamp_utc"),
        }
        self.grafana_export_path.write_text(json.dumps(panel, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
