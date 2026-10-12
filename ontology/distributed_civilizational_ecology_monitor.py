
"""
Distributed Civilizational Ecology Monitor — N9.

Longitudinal monitor for the distributed civilizational ecology axis.
It historizes diversity, culture, memory and cooperation signals and derives
functional metrics for ecological stability, growth and resilience.

This module validates only measurable functional properties. It does not make
claims about phenomenal subjectivity.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
REPORT_DIR = ROOT / "runtime_reports" / "distributed_civilizational_ecology_monitor"
LATEST_REPORT = REPORT_DIR / "latest_distributed_civilizational_ecology_monitor.json"
HISTORY_PATH = REPORT_DIR / "distributed_civilizational_ecology_history.jsonl"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return float(default)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _round(value: float) -> float:
    return round(_clamp(value), 6)


def _safe_read_history(limit: int = 25) -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines()[-limit:]:
            if line.strip():
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
    except Exception:
        return []
    return rows


@dataclass
class DistributedCivilizationalEcologyMonitor:
    """Monitor longitudinal N9 for distributed civilizational ecology."""

    primitive: str = "DISTRIBUTED_CIVILIZATIONAL_ECOLOGY_MONITOR"

    def _extract_inputs(self, inputs: Mapping[str, Any] | None) -> dict[str, float]:
        data = dict(inputs or {})

        diversity = _mean([
            _clamp(data.get("diversity_score", data.get("cognitive_diversity_score", 0.0))),
            _clamp(data.get("distributed_pluralism_score", data.get("semantic_pluralism_score", 0.0))),
            _clamp(data.get("lineage_diversity_score", data.get("individual_diversity_score", 0.0))),
        ])

        culture = _mean([
            _clamp(data.get("culture_score", data.get("cultural_memory_score", 0.0))),
            _clamp(data.get("cultural_continuity_score", 0.0)),
            _clamp(data.get("symbolic_structure_score", data.get("symbolic_emergence_score", 0.0))),
        ])

        memory = _mean([
            _clamp(data.get("memory_score", data.get("civilizational_memory_score", 0.0))),
            _clamp(data.get("historical_archive_score", data.get("historical_continuity_score", 0.0))),
            _clamp(data.get("intergenerational_transfer_score", data.get("knowledge_transfer_score", 0.0))),
        ])

        cooperation = _mean([
            _clamp(data.get("cooperation_score", data.get("social_learning_score", 0.0))),
            _clamp(data.get("cooperative_specialization_score", 0.0)),
            _clamp(data.get("collective_coordination_score", data.get("collective_intelligence_score", 0.0))),
        ])

        supervisor_score = _clamp(data.get("distributed_ecology_score", 0.0))
        ecological_continuity = _clamp(data.get("ecological_continuity_score", 0.0))
        closure_pressure = _clamp(data.get("closure_pressure_index", data.get("closure_pressure", 0.0)))
        drift_pressure = _clamp(data.get("civilizational_drift_score", data.get("drift_pressure", 0.0)))

        # When N8 output is provided, it should inform but not erase category signals.
        distributed_ecology_observation = _mean([
            diversity,
            culture,
            memory,
            cooperation,
            supervisor_score if supervisor_score else _mean([diversity, culture, memory, cooperation]),
        ])

        return {
            "diversity_signal": _round(diversity),
            "culture_signal": _round(culture),
            "memory_signal": _round(memory),
            "cooperation_signal": _round(cooperation),
            "distributed_ecology_observation": _round(distributed_ecology_observation),
            "supervisor_score": _round(supervisor_score),
            "ecological_continuity_input": _round(ecological_continuity),
            "closure_pressure_index": _round(closure_pressure),
            "drift_pressure": _round(drift_pressure),
        }

    def _derive_metrics(self, signals: dict[str, float], history: list[dict[str, Any]]) -> dict[str, float]:
        ecological_level = _mean([
            signals["diversity_signal"],
            signals["culture_signal"],
            signals["memory_signal"],
            signals["cooperation_signal"],
            signals["distributed_ecology_observation"],
        ])

        pressures = _mean([
            signals["closure_pressure_index"],
            signals["drift_pressure"],
        ])

        current_score = _clamp(ecological_level * (1.0 - 0.35 * pressures))

        historical_scores = [
            _clamp(row.get("distributed_ecology_score"))
            for row in history
            if "distributed_ecology_score" in row
        ]

        if historical_scores:
            previous = historical_scores[-1]
            growth_rate = max(-1.0, min(1.0, current_score - previous))
            volatility = _mean([abs(current_score - s) for s in historical_scores[-10:]])
            historical_mean = _mean(historical_scores[-10:])
        else:
            growth_rate = 0.0
            volatility = 0.0
            historical_mean = current_score

        ecological_stability = _clamp(1.0 - volatility - 0.35 * pressures)
        ecological_growth_rate = round(growth_rate, 6)
        ecological_resilience = _clamp(_mean([
            current_score,
            ecological_stability,
            1.0 - pressures,
            signals["ecological_continuity_input"] or historical_mean,
        ]))

        return {
            "distributed_ecology_score": _round(current_score),
            "ecological_stability": _round(ecological_stability),
            "ecological_growth_rate": ecological_growth_rate,
            "ecological_resilience": _round(ecological_resilience),
            "historical_mean_ecology_score": _round(historical_mean),
            "ecological_volatility": _round(volatility),
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        signals = self._extract_inputs(inputs)
        history = _safe_read_history() if persist else []
        metrics = self._derive_metrics(signals, history)

        stability = metrics["ecological_stability"]
        score = metrics["distributed_ecology_score"]
        resilience = metrics["ecological_resilience"]

        monitor_health_score = _round(_mean([score, stability, resilience]))

        ecology_monitor_stable = monitor_health_score >= 0.74 and signals["closure_pressure_index"] <= 0.35
        ecology_monitor_warning = (0.48 <= monitor_health_score < 0.74) or (0.35 < signals["closure_pressure_index"] <= 0.70)
        ecology_monitor_risk = monitor_health_score < 0.48 or signals["closure_pressure_index"] > 0.70

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "diversity_history_signal": signals["diversity_signal"],
            "culture_history_signal": signals["culture_signal"],
            "memory_history_signal": signals["memory_signal"],
            "cooperation_history_signal": signals["cooperation_signal"],
            "distributed_ecology_score": metrics["distributed_ecology_score"],
            "ecological_stability": metrics["ecological_stability"],
            "ecological_growth_rate": metrics["ecological_growth_rate"],
            "ecological_resilience": metrics["ecological_resilience"],
            "ecological_volatility": metrics["ecological_volatility"],
            "historical_mean_ecology_score": metrics["historical_mean_ecology_score"],
            "monitor_health_score": monitor_health_score,
            "ecology_monitor_stable": ecology_monitor_stable,
            "ecology_monitor_warning": ecology_monitor_warning,
            "ecology_monitor_risk": ecology_monitor_risk,
            "ecological_monitoring_decision": (
                "ecological_monitoring_stable" if ecology_monitor_stable else
                "ecological_monitoring_warning" if ecology_monitor_warning else
                "ecological_monitoring_risk"
            ),
            "historized_dimensions": ["diversity", "culture", "memory", "cooperation"],
            "diagnostics": {
                "epistemic_scope": "functional_metrics_only",
                "subjectivity_claim": False,
                "closure_pressure_index": signals["closure_pressure_index"],
                "drift_pressure": signals["drift_pressure"],
                "history_used": bool(history),
                "history_sample_count": len(history),
            },
        }

        if persist:
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            event = dict(result)
            event["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            LATEST_REPORT.write_text(json.dumps(event, indent=2, sort_keys=True), encoding="utf-8")
            with HISTORY_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, sort_keys=True) + "\n")
            result["report_path"] = str(LATEST_REPORT)
            result["history_path"] = str(HISTORY_PATH)

        return result
