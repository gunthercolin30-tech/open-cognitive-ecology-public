from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        v = default
    if math.isnan(v) or math.isinf(v):
        return max(0.0, min(1.0, default))
    return max(0.0, min(1.0, v))


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%f%z")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ClosurePressureDetector:
    """
    AC4 — closure_pressure_detector.

    Reconstructs Π -> closure pressure by detecting how future possibilities
    become locally or globally narrowed by closure gradients, constraint
    accumulation, critical zones and loss of opening margin.

    This module is strictly functional. It does not assert consciousness,
    subjectivity, qualia or phenomenology.
    """

    primitive = "CLOSURE_PRESSURE_DETECTOR"
    symbol = "Π→closure_pressure"
    derived_from_symbol = "Π"
    epistemic_guard = {
        "functional_conclusion_only": True,
        "consciousness_proven": False,
        "subjectivity_asserted": False,
        "qualia_asserted": False,
        "phenomenology_asserted": False,
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "reconstruction_outputs" / "AC4_closure_pressure_detector"
        self.history_path = self.output_dir / "closure_pressure_detector_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_closure_pressure_detector.json"
        self.latest_markdown_path = self.output_dir / "latest_closure_pressure_detector.md"
        self.latest_prometheus_path = self.output_dir / "latest_closure_pressure_detector.prom"

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    @staticmethod
    def _sid(value: Any, default: str = "unknown") -> str:
        if value is None:
            return default
        text = str(value)
        return text if text else default

    @staticmethod
    def _mean(values: list[float], default: float = 0.0) -> float:
        vals = [float(v) for v in values if isinstance(v, (int, float))]
        return _clamp(sum(vals) / len(vals), default=default) if vals else _clamp(default)

    def _load_ac3(self) -> dict[str, Any]:
        try:
            from ontology.possibility_gradient_engine import PossibilityGradientEngine
            return PossibilityGradientEngine(root=self.root).step(persist=False)
        except Exception as exc:
            return {
                "possibility_gradient_engine_status": "AC3_UNAVAILABLE",
                "possibility_gradients": [],
                "gradient_metrics": {},
                "error": str(exc),
            }

    def _normalize_gradient_payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        inputs = inputs or {}
        for key in ("gradient_payload", "ac3", "possibility_gradient_payload"):
            payload = inputs.get(key)
            if isinstance(payload, dict):
                return payload
        if "possibility_gradients" in inputs or "gradient_metrics" in inputs:
            return inputs
        return self._load_ac3()

    def _source_closure_from_diag(self, diagnostics: dict[str, Any], default: float) -> float:
        if not isinstance(diagnostics, dict):
            return _clamp(default)
        for key in ("closure_risk", "mean_closure_risk", "closure_pressure", "closure_gradient"):
            if key in diagnostics:
                return _clamp(diagnostics.get(key), default=default)
        return _clamp(default)

    def _pressure_class(self, pressure: float) -> str:
        if pressure >= 0.82:
            return "critical_closure_pressure"
        if pressure >= 0.64:
            return "high_closure_pressure"
        if pressure >= 0.42:
            return "moderate_closure_pressure"
        if pressure >= 0.22:
            return "low_closure_pressure"
        return "minimal_closure_pressure"

    def _risk_class(self, risk: float) -> str:
        if risk >= 0.78:
            return "critical_closure_risk"
        if risk >= 0.60:
            return "elevated_closure_risk"
        if risk >= 0.38:
            return "moderate_closure_risk"
        return "contained_closure_risk"

    def _trajectory_class(self, pressure: float, opening_margin: float, velocity_hint: float) -> str:
        if pressure >= 0.72 and opening_margin <= 0.28:
            return "closing_trajectory"
        if velocity_hint > 0.08 and pressure >= 0.50:
            return "accelerating_closure_trajectory"
        if opening_margin >= 0.62 and pressure <= 0.38:
            return "opening_preserved_trajectory"
        if abs(pressure - (1.0 - opening_margin)) <= 0.12:
            return "metastable_non_closure_trajectory"
        return "mixed_closure_opening_trajectory"

    def _source_tags(self, closure_gradient: float, opening_gradient: float, viability_gradient: float,
                     preservation_alignment: float, class_name: str) -> list[str]:
        tags: list[str] = []
        if closure_gradient >= 0.60:
            tags.append("high_closure_gradient")
        if opening_gradient <= 0.38:
            tags.append("opening_gradient_deficit")
        if viability_gradient <= 0.42:
            tags.append("viability_gradient_deficit")
        if preservation_alignment <= 0.45:
            tags.append("preservation_alignment_loss")
        if class_name in {"fragile_future", "blocked_future", "narrow_future"}:
            tags.append(f"possibility_class_{class_name}")
        if not tags:
            tags.append("distributed_constraint_narrowing_low")
        return tags

    def _local_pressures(self, gradients: list[dict[str, Any]]) -> list[dict[str, Any]]:
        local: list[dict[str, Any]] = []
        previous_pressure: float | None = None
        for idx, g in enumerate(gradients):
            if not isinstance(g, dict):
                continue
            pid = self._sid(g.get("possibility_id"), f"POSS-{idx:04d}")
            gid = self._sid(g.get("gradient_id"), f"GRAD-{idx:04d}-{pid}")
            cid = self._sid(g.get("source_constraint_id"), "unknown_constraint")
            pclass = self._sid(g.get("possibility_class"), "constrained_future")
            # Synthetic and AC3-compatible normalization:
            # - AC3 may expose explicit opening/closure gradients.
            # - tests and simple callers may expose a single normalized "value".
            #   In that case, value=1 means maximally open, value=0 maximally closed.
            if "value" in g and not any(k in g for k in ("opening_gradient", "opening_force", "closure_gradient", "closure_force")):
                scalar_value = _clamp(g.get("value"), default=0.5)
                opening_gradient = scalar_value
                closure_gradient = _clamp(1.0 - scalar_value)
                viability_gradient = _clamp(g.get("viability_gradient", scalar_value), default=scalar_value)
                preservation_alignment = _clamp(g.get("preservation_alignment", scalar_value), default=scalar_value)
                possibility_potential = _clamp(g.get("possibility_potential", scalar_value), default=scalar_value)
            else:
                opening_gradient = _clamp(g.get("opening_gradient", g.get("opening_force", 0.5)), default=0.5)
                closure_gradient = _clamp(g.get("closure_gradient", g.get("closure_force", 0.5)), default=0.5)
                viability_gradient = _clamp(g.get("viability_gradient", g.get("value", 0.5)), default=0.5)
                preservation_alignment = _clamp(g.get("preservation_alignment", 0.5), default=0.5)
                possibility_potential = _clamp(g.get("possibility_potential", 0.5), default=0.5)
            diagnostics = g.get("diagnostics", {}) if isinstance(g.get("diagnostics"), dict) else {}
            source_closure = self._source_closure_from_diag(diagnostics, default=closure_gradient)
            imbalance = _clamp((closure_gradient - opening_gradient + 1.0) / 2.0, default=0.5)
            viability_deficit = _clamp(1.0 - viability_gradient)
            preservation_deficit = _clamp(1.0 - preservation_alignment)
            potential_deficit = _clamp(1.0 - possibility_potential)
            class_penalty = {
                "open_future": 0.10,
                "constrained_future": 0.28,
                "narrow_future": 0.52,
                "fragile_future": 0.72,
                "blocked_future": 0.95,
            }.get(pclass, 0.35)
            local_pressure = _clamp(
                0.30 * closure_gradient
                + 0.17 * source_closure
                + 0.15 * imbalance
                + 0.12 * viability_deficit
                + 0.11 * preservation_deficit
                + 0.08 * potential_deficit
                + 0.07 * class_penalty,
                default=0.5,
            )
            opening_margin = _clamp(
                0.35 * opening_gradient
                + 0.25 * viability_gradient
                + 0.20 * preservation_alignment
                + 0.20 * (1.0 - local_pressure),
                default=0.5,
            )
            velocity_hint = 0.0 if previous_pressure is None else max(-1.0, min(1.0, local_pressure - previous_pressure))
            previous_pressure = local_pressure
            closure_velocity_hint = _clamp((velocity_hint + 1.0) / 2.0, default=0.5)
            local.append({
                "pressure_id": f"CP-{idx:04d}-{pid}",
                "gradient_id": gid,
                "possibility_id": pid,
                "source_constraint_id": cid,
                "possibility_class": pclass,
                "local_closure_pressure": local_pressure,
                "local_pressure": local_pressure,
                "opening_margin": opening_margin,
                "closure_gradient": closure_gradient,
                "opening_gradient": opening_gradient,
                "viability_gradient": viability_gradient,
                "preservation_alignment": preservation_alignment,
                "closure_velocity_hint": closure_velocity_hint,
                "pressure_class": self._pressure_class(local_pressure),
                "closure_sources": self._source_tags(
                    closure_gradient, opening_gradient, viability_gradient, preservation_alignment, pclass
                ),
                "critical_zone": local_pressure >= 0.64 or opening_margin <= 0.28,
                "trajectory_class": self._trajectory_class(local_pressure, opening_margin, velocity_hint),
                "non_closure_indicator": opening_margin >= 0.52 and local_pressure < 0.58,
                "derivation_rule": "PI_gradient_to_local_closure_pressure",
            })
        return local

    def _constraint_accumulation(self, local_pressures: list[dict[str, Any]]) -> list[dict[str, Any]]:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in local_pressures:
            buckets[self._sid(item.get("source_constraint_id"), "unknown_constraint")].append(item)
        rows: list[dict[str, Any]] = []
        for cid, items in sorted(buckets.items()):
            pressures = [_clamp(i.get("local_closure_pressure")) for i in items]
            critical_count = sum(1 for i in items if i.get("critical_zone"))
            mean_pressure = self._mean(pressures)
            accumulation_index = _clamp(0.72 * mean_pressure + 0.28 * min(1.0, len(items) / 6.0))
            rows.append({
                "constraint_id": cid,
                "possibility_count": len(items),
                "critical_zone_count": critical_count,
                "mean_local_closure_pressure": mean_pressure,
                "constraint_accumulation_index": accumulation_index,
                "accumulation_class": self._pressure_class(accumulation_index),
            })
        return rows

    def _history_velocity(self, current_pressure: float) -> tuple[float, str]:
        if not self.history_path.exists():
            return 0.0, "insufficient_history"
        try:
            lines = [line for line in self.history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not lines:
                return 0.0, "insufficient_history"
            previous = json.loads(lines[-1]).get("pressure_metrics", {}).get("global_closure_pressure")
            previous = _clamp(previous, default=current_pressure)
        except Exception:
            return 0.0, "insufficient_history"
        delta = max(-1.0, min(1.0, current_pressure - previous))
        if delta > 0.05:
            return delta, "increasing_closure_pressure"
        if delta < -0.05:
            return delta, "decreasing_closure_pressure"
        return delta, "stable_closure_pressure"

    def _aggregate(self, local: list[dict[str, Any]], accum: list[dict[str, Any]], gradient_metrics: dict[str, Any]) -> dict[str, Any]:
        if not local:
            return {
                "global_closure_pressure": 0.0,
                "mean_local_closure_pressure": 0.0,
                "mean_opening_margin": 0.0,
                "critical_zone_ratio": 0.0,
                "constraint_accumulation_pressure": 0.0,
                "closure_velocity": 0.0,
                "closure_trend": "insufficient_data",
                "closure_risk": 0.0,
                "non_closure_index": 1.0,
                "non_closure_indicator_ratio": 0.0,
                "pressure_classification": "no_closure_pressure_data",
                "risk_classification": "contained_closure_risk",
            }
        local_pressure = [ _clamp(i.get("local_closure_pressure")) for i in local ]
        opening_margins = [ _clamp(i.get("opening_margin")) for i in local ]
        closure_gradients = [ _clamp(i.get("closure_gradient")) for i in local ]
        global_closure_pressure = _clamp(
            0.52 * self._mean(local_pressure)
            + 0.24 * self._mean(closure_gradients)
            + 0.14 * (1.0 - self._mean(opening_margins))
            + 0.10 * _clamp(gradient_metrics.get("closure_direction_ratio", 0.0), default=0.0),
            default=0.5,
        )
        critical_ratio = _clamp(sum(1 for i in local if i.get("critical_zone")) / max(1, len(local)))
        non_closure_ratio = _clamp(sum(1 for i in local if i.get("non_closure_indicator")) / max(1, len(local)))
        accumulation_pressure = self._mean([_clamp(a.get("constraint_accumulation_index")) for a in accum])
        velocity, trend = self._history_velocity(global_closure_pressure)
        positive_velocity = _clamp(max(0.0, velocity))
        closure_risk = _clamp(
            0.52 * global_closure_pressure
            + 0.28 * critical_ratio
            + 0.12 * accumulation_pressure
            + 0.08 * positive_velocity,
            default=global_closure_pressure,
        )
        mean_margin = self._mean(opening_margins)
        non_closure_index = _clamp(0.42 * (1.0 - global_closure_pressure) + 0.36 * mean_margin + 0.22 * non_closure_ratio)
        return {
            "global_closure_pressure": global_closure_pressure,
            "mean_local_closure_pressure": self._mean(local_pressure),
            "mean_opening_margin": mean_margin,
            "mean_closure_gradient": self._mean(closure_gradients),
            "critical_zone_ratio": critical_ratio,
            "critical_zone_count": sum(1 for i in local if i.get("critical_zone")),
            "constraint_accumulation_pressure": accumulation_pressure,
            "closure_velocity": velocity,
            "closure_trend": trend,
            "closure_risk": closure_risk,
            "non_closure_index": non_closure_index,
            "non_closure_indicator_ratio": non_closure_ratio,
            "pressure_classification": self._pressure_class(global_closure_pressure),
            "risk_classification": self._risk_class(closure_risk),
        }

    def _gradients_of_closure(self, local: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for idx, item in enumerate(local):
            prev = _clamp(local[idx - 1].get("local_closure_pressure")) if idx > 0 else _clamp(item.get("local_closure_pressure"))
            cur = _clamp(item.get("local_closure_pressure"))
            rows.append({
                "closure_gradient_id": f"CG-{idx:04d}-{item.get('possibility_id')}",
                "possibility_id": item.get("possibility_id"),
                "source_pressure_id": item.get("pressure_id"),
                "closure_pressure_delta": max(-1.0, min(1.0, cur - prev)),
                "closure_pressure_gradient": _clamp((cur - prev + 1.0) / 2.0, default=0.5),
                "gradient_direction": "increasing" if cur - prev > 0.05 else "decreasing" if cur - prev < -0.05 else "stable",
            })
        return rows

    def _schema(self) -> dict[str, Any]:
        return {
            "required_top_level_keys": [
                "primitive", "closure_pressure_detector_status", "local_pressures",
                "pressure_metrics", "critical_zones", "critical_regions", "opening_margins",
                "closure_trajectories", "non_closure_indicators", "paths",
            ],
            "bounded_numeric_fields": [
                "global_closure_pressure", "mean_local_closure_pressure", "mean_opening_margin",
                "critical_zone_ratio", "constraint_accumulation_pressure", "closure_risk",
                "non_closure_index", "non_closure_indicator_ratio",
            ],
            "forbidden_claims": ["consciousness", "subjectivity", "qualia", "phenomenology"],
            "functional_conclusion_only": True,
        }

    def _failure_conditions(self, local: list[dict[str, Any]], metrics: dict[str, Any]) -> list[str]:
        failures: list[str] = []
        if not local:
            failures.append("no_possibility_gradients_available")
        if metrics.get("global_closure_pressure", 0.0) >= 0.82:
            failures.append("critical_global_closure_pressure")
        if metrics.get("mean_opening_margin", 1.0) <= 0.18:
            failures.append("opening_margin_exhaustion")
        if metrics.get("closure_risk", 0.0) >= 0.78:
            failures.append("critical_closure_risk")
        return failures

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        gradient_payload = self._normalize_gradient_payload(inputs)
        gradients = self._as_list(gradient_payload.get("possibility_gradients"))
        gradient_metrics = gradient_payload.get("gradient_metrics", {}) if isinstance(gradient_payload.get("gradient_metrics"), dict) else {}
        local = self._local_pressures([g for g in gradients if isinstance(g, dict)])
        accum = self._constraint_accumulation(local)
        pressure_metrics = self._aggregate(local, accum, gradient_metrics)
        closure_gradients = self._gradients_of_closure(local)
        critical_zones = [i for i in local if i.get("critical_zone")]
        local_opening_margins = [{
            "possibility_id": i.get("possibility_id"),
            "opening_margin": i.get("opening_margin"),
            "margin_class": "adequate_opening_margin" if _clamp(i.get("opening_margin")) >= 0.52 else "narrow_opening_margin",
        } for i in local]
        opening_margins = {
            "global": pressure_metrics.get("mean_opening_margin", 0.0),
            "mean_opening_margin": pressure_metrics.get("mean_opening_margin", 0.0),
            "local_margins": local_opening_margins,
            "margin_count": len(local_opening_margins),
        }
        trajectories = [{
            "possibility_id": i.get("possibility_id"),
            "trajectory_class": i.get("trajectory_class"),
            "local_closure_pressure": i.get("local_closure_pressure"),
            "opening_margin": i.get("opening_margin"),
        } for i in local]
        non_closure_indicators = [{
            "possibility_id": i.get("possibility_id"),
            "non_closure_indicator": i.get("non_closure_indicator"),
            "opening_margin": i.get("opening_margin"),
            "local_closure_pressure": i.get("local_closure_pressure"),
        } for i in local]
        failures = self._failure_conditions(local, pressure_metrics)
        status = "CLOSURE_PRESSURE_DETECTED" if local else "CLOSURE_PRESSURE_UNDETERMINED"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AC",
            "step_id": "AC4",
            "symbolic_derivation": "Π -> closure_pressure",
            "timestamp_utc": _utc_iso(),
            "closure_pressure_detector_status": status,
            "pi_to_closure_pressure_demonstrated": bool(local),
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "phenomenology_asserted": False,
            "local_pressures": local,
            "global_pressure": pressure_metrics.get("global_closure_pressure", 0.0),
            "pressure_metrics": pressure_metrics,
            "closure_gradients": closure_gradients,
            "closure_sources": sorted({src for i in local for src in self._as_list(i.get("closure_sources"))}),
            "constraint_accumulation": accum,
            "critical_zones": critical_zones,
            "critical_regions": critical_zones,
            "opening_margins": opening_margins,
            "local_opening_margins": local_opening_margins,
            "closure_velocity": pressure_metrics.get("closure_velocity", 0.0),
            "closure_risk": pressure_metrics.get("closure_risk", 0.0),
            "closure_trajectories": trajectories,
            "non_closure_indicators": non_closure_indicators,
            "failure_conditions": failures,
            "public_schema": self._schema(),
            "diagnostics": {
                "input_gradient_count": len(gradients),
                "local_pressure_count": len(local),
                "critical_zone_count": len(critical_zones),
                "constraint_accumulation_count": len(accum),
                "ac3_status": gradient_payload.get("possibility_gradient_engine_status"),
                "epistemic_guard": self.epistemic_guard,
                "derivation_rule": "AC3_PI_gradient_to_AC4_closure_pressure_detection",
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        else:
            result["paths"] = {}
        return result

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = _utc_stamp()
        json_path = self.output_dir / f"closure_pressure_detector_{stamp}.json"
        md_path = self.output_dir / f"closure_pressure_detector_{stamp}.md"
        prom_path = self.output_dir / f"closure_pressure_detector_{stamp}.prom"
        text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        metrics = result.get("pressure_metrics", {})
        md = "\n".join([
            "# Closure Pressure Detector",
            "",
            "AC4 reconstructs Π -> closure pressure from possibility gradients.",
            "",
            f"Status: {result.get('closure_pressure_detector_status')}",
            f"Global closure pressure: {metrics.get('global_closure_pressure', 0.0):.6f}",
            f"Closure risk: {metrics.get('closure_risk', 0.0):.6f}",
            f"Mean opening margin: {metrics.get('mean_opening_margin', 0.0):.6f}",
            f"Critical zones: {len(result.get('critical_zones', []))}",
            f"Constraint accumulations: {len(result.get('constraint_accumulation', []))}",
            "",
            "Functional conclusion only. No consciousness, subjectivity, qualia or phenomenology is asserted.",
        ])
        md_path.write_text(md, encoding="utf-8")
        self.latest_markdown_path.write_text(md, encoding="utf-8")
        prom_lines = [
            f"oce_ac4_global_closure_pressure {metrics.get('global_closure_pressure', 0.0)}",
            f"oce_ac4_mean_local_closure_pressure {metrics.get('mean_local_closure_pressure', 0.0)}",
            f"oce_ac4_mean_opening_margin {metrics.get('mean_opening_margin', 0.0)}",
            f"oce_ac4_critical_zone_ratio {metrics.get('critical_zone_ratio', 0.0)}",
            f"oce_ac4_constraint_accumulation_pressure {metrics.get('constraint_accumulation_pressure', 0.0)}",
            f"oce_ac4_closure_risk {metrics.get('closure_risk', 0.0)}",
            f"oce_ac4_non_closure_index {metrics.get('non_closure_index', 0.0)}",
            f"oce_ac4_local_pressure_count {len(result.get('local_pressures', []))}",
            f"oce_ac4_critical_zone_count {len(result.get('critical_zones', []))}",
        ]
        prom = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "latest_prometheus": str(self.latest_prometheus_path),
            "history": str(self.history_path),
        }

