
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "reconstruction_outputs"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        v = default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(0.0, min(1.0, v))


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%f%z")


class PossibilityGradientEngine:
    """
    AC3 — possibility_gradient_engine.

    Reconstructs possibility gradients over Π from AC1 future possibility
    space and AC2 preservation metrics. This module is functional only: it
    does not assert consciousness, subjectivity, qualia, or phenomenology.
    """

    primitive = "POSSIBILITY_GRADIENT_ENGINE"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.output_dir = self.root / "reconstruction_outputs"

    def _load_ac1(self) -> dict[str, Any]:
        try:
            from ontology.future_possibility_space import FuturePossibilitySpace
            return FuturePossibilitySpace().step(persist=False)
        except Exception as exc:
            return {"future_possibility_space": [], "error": str(exc)}

    def _load_ac2(self, possibility_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            from ontology.possibility_preservation_metric import PossibilityPreservationMetric
            payload = {"possibility_payload": possibility_payload} if possibility_payload else None
            return PossibilityPreservationMetric().step(payload, persist=False)
        except Exception as exc:
            return {"preservation_metrics": {}, "error": str(exc)}

    def _possibilities_from_inputs(self, inputs: dict[str, Any] | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        inputs = inputs or {}
        possibility_payload = inputs.get("possibility_payload") or inputs.get("ac1") or {}
        metric_payload = inputs.get("metric_payload") or inputs.get("ac2") or {}

        possibilities = possibility_payload.get("future_possibility_space")
        if possibilities is None:
            ac1 = self._load_ac1()
            possibilities = ac1.get("future_possibility_space", [])
            possibility_payload = ac1

        if not isinstance(possibilities, list):
            possibilities = []

        metrics = metric_payload.get("preservation_metrics")
        if metrics is None:
            ac2 = self._load_ac2(possibility_payload)
            metrics = ac2.get("preservation_metrics", {})
            metric_payload = ac2

        return possibilities, metrics if isinstance(metrics, dict) else {}

    def _class_weight(self, possibility_class: str) -> float:
        return {
            "open_future": 1.0,
            "constrained_future": 0.75,
            "narrow_future": 0.5,
            "fragile_future": 0.3,
            "blocked_future": 0.05,
        }.get(str(possibility_class), 0.5)

    def _direction_class(self, opening_gradient: float, closure_gradient: float, viability_gradient: float) -> str:
        # Public AC3 taxonomy: opening / stable / narrowing / closing.
        # The old internal labels are intentionally collapsed into this stable API.
        if closure_gradient >= 0.78:
            return "closing"
        if opening_gradient >= 0.72 and viability_gradient >= 0.55:
            return "opening"
        if abs(opening_gradient - closure_gradient) <= 0.12:
            return "stable"
        if closure_gradient > opening_gradient:
            return "narrowing"
        return "opening"

    def _build_gradients(self, possibilities: list[dict[str, Any]], metrics: dict[str, Any]) -> list[dict[str, Any]]:
        mean_openness = _clamp(metrics.get("mean_openness_score"), 0.5)
        mean_viability = _clamp(metrics.get("mean_viability_score"), 0.5)
        mean_closure = _clamp(metrics.get("mean_closure_risk"), 0.5)
        ppi = _clamp(metrics.get("possibility_preservation_index"), 0.5)

        gradients: list[dict[str, Any]] = []
        for idx, p in enumerate(possibilities):
            pid = str(p.get("possibility_id") or f"POSS-{idx:04d}")
            cls = str(p.get("possibility_class") or p.get("class") or "constrained_future")
            openness = _clamp(p.get("openness_score"), mean_openness)
            viability = _clamp(p.get("viability_score"), mean_viability)
            closure = _clamp(p.get("closure_risk"), mean_closure)
            weight = self._class_weight(cls)

            opening_gradient = _clamp((0.50 * openness) + (0.20 * viability) + (0.20 * ppi) + (0.10 * weight))
            closure_gradient = _clamp((0.55 * closure) + (0.20 * (1.0 - openness)) + (0.15 * (1.0 - viability)) + (0.10 * (1.0 - weight)))
            viability_gradient = _clamp((0.45 * viability) + (0.25 * openness) + (0.20 * (1.0 - closure)) + (0.10 * ppi))
            gradient_magnitude = _clamp((abs(opening_gradient - closure_gradient) + viability_gradient) / 2.0)
            preservation_alignment = _clamp(1.0 - abs(ppi - ((openness + viability + (1.0 - closure)) / 3.0)))
            possibility_potential = _clamp((opening_gradient + viability_gradient + preservation_alignment) / 3.0)
            direction_class = self._direction_class(opening_gradient, closure_gradient, viability_gradient)

            gradients.append({
                "gradient_id": f"GRAD-{idx:04d}-{pid}",
                "possibility_id": pid,
                "source_constraint_id": p.get("source_constraint_id"),
                "possibility_class": cls,
                "opening_gradient": opening_gradient,
                "opening_force": opening_gradient,
                "closure_gradient": closure_gradient,
                "closure_force": closure_gradient,
                "viability_gradient": viability_gradient,
                "gradient_magnitude": gradient_magnitude,
                "possibility_potential": possibility_potential,
                "preservation_alignment": preservation_alignment,
                "direction_class": direction_class,
                "gradient_direction": direction_class,
                "opens_possibility": opening_gradient > closure_gradient,
                "closes_possibility": closure_gradient > opening_gradient,
                "diagnostics": {
                    "openness_score": openness,
                    "viability_score": viability,
                    "closure_risk": closure,
                    "class_weight": weight,
                    "possibility_preservation_index": ppi,
                },
            })
        return gradients

    def _summarize(self, gradients: list[dict[str, Any]]) -> dict[str, Any]:
        if not gradients:
            return {
                "mean_opening_gradient": 0.0,
                "mean_closure_gradient": 0.0,
                "mean_viability_gradient": 0.0,
                "mean_gradient_magnitude": 0.0,
                "mean_possibility_potential": 0.0,
                "opening_direction_ratio": 0.0,
                "closure_direction_ratio": 0.0,
            }
        n = len(gradients)
        return {
            "mean_opening_gradient": _clamp(mean(g["opening_gradient"] for g in gradients)),
            "mean_closure_gradient": _clamp(mean(g["closure_gradient"] for g in gradients)),
            "mean_viability_gradient": _clamp(mean(g["viability_gradient"] for g in gradients)),
            "mean_gradient_magnitude": _clamp(mean(g["gradient_magnitude"] for g in gradients)),
            "mean_possibility_potential": _clamp(mean(g["possibility_potential"] for g in gradients)),
            "opening_direction_ratio": _clamp(sum(1 for g in gradients if g.get("gradient_direction", g.get("direction_class")) in {"opening", "opening_direction"}) / n),
            "closure_direction_ratio": _clamp(sum(1 for g in gradients if g.get("gradient_direction", g.get("direction_class")) in {"closing", "closure_direction"}) / n),
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = _utc_stamp()
        base = f"possibility_gradient_engine_{stamp}"
        json_path = self.output_dir / f"{base}.json"
        md_path = self.output_dir / f"{base}.md"
        prom_path = self.output_dir / f"{base}.prom"
        latest_json = self.output_dir / "latest_possibility_gradient_engine.json"
        latest_md = self.output_dir / "latest_possibility_gradient_engine.md"
        latest_prom = self.output_dir / "latest_possibility_gradient_engine.prom"
        history = self.output_dir / "possibility_gradient_engine_history.jsonl"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        gm = result.get("gradient_metrics", {})
        md = "\n".join([
            "# Possibility Gradient Engine",
            "",
            "AC3 reconstructs possibility gradients over Π from the future possibility space and preservation metrics.",
            "",
            f"Status: {result.get('possibility_gradient_engine_status')}",
            f"Π gradient demonstrated: {result.get('pi_gradient_demonstrated')}",
            f"Gradient count: {len(result.get('possibility_gradients', []))}",
            f"Mean opening gradient: {gm.get('mean_opening_gradient', 0.0):.6f}",
            f"Mean closure gradient: {gm.get('mean_closure_gradient', 0.0):.6f}",
            f"Mean possibility potential: {gm.get('mean_possibility_potential', 0.0):.6f}",
            "Gradient directions: opening / stable / narrowing / closing.",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
        ]) + "\n"
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        ready = 1 if result.get("possibility_gradient_engine_status") == "POSSIBILITY_GRADIENT_ENGINE_READY" else 0
        prom = "\n".join([
            f"oce_ac3_possibility_gradient_engine_ready {ready}",
            f"oce_ac3_pi_gradient_demonstrated {1 if result.get('pi_gradient_demonstrated') else 0}",
            f"oce_ac3_mean_opening_gradient {gm.get('mean_opening_gradient', 0.0)}",
            f"oce_ac3_mean_closure_gradient {gm.get('mean_closure_gradient', 0.0)}",
            f"oce_ac3_mean_viability_gradient {gm.get('mean_viability_gradient', 0.0)}",
            f"oce_ac3_mean_gradient_magnitude {gm.get('mean_gradient_magnitude', 0.0)}",
            f"oce_ac3_mean_possibility_potential {gm.get('mean_possibility_potential', 0.0)}",
        ]) + "\n"
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        possibilities, metrics = self._possibilities_from_inputs(inputs)
        failures: list[str] = []
        if not possibilities:
            failures.append("no_future_possibility_space")
        if not metrics:
            failures.append("missing_preservation_metrics")

        gradients = self._build_gradients(possibilities, metrics) if possibilities else []
        gradient_metrics = self._summarize(gradients)
        ready = bool(gradients) and not failures

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "module": "ontology.possibility_gradient_engine",
            "axis": "AC",
            "step_id": "AC3",
            "derivation": "Π → possibility gradients",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "possibility_gradient_engine_status": "POSSIBILITY_GRADIENT_ENGINE_READY" if ready else "POSSIBILITY_GRADIENT_ENGINE_NOT_READY",
            "pi_gradient_demonstrated": ready,
            "possibility_gradients_ready": ready,
            "possibility_gradients": gradients,
            "gradient_metrics": gradient_metrics,
            "failure_conditions": failures,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "no_consciousness_claim": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
