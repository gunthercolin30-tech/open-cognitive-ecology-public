from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PossibilityPreservationMetric:
    """
    AC2 — possibility_preservation_metric.

    Quantifies preservation of Π from AC1 future possibilities. This module is
    a metric layer, not a possible-world generator, closure regulator, or final
    AC certifier. It measures how much of the reconstructed possibility space
    remains open, viable, diverse and non-closed under constraints.

    It does not assert consciousness, subjectivity, qualia, or phenomenology.
    """

    primitive = "POSSIBILITY_PRESERVATION_METRIC"
    derived_from_symbol = "Π"
    metric_target = "possibility_preservation"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AC2_possibility_preservation_metric"
        self.history_path = self.output_dir / "possibility_preservation_metric_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_possibility_preservation_metric.json"
        self.latest_markdown_path = self.output_dir / "latest_possibility_preservation_metric.md"
        self.latest_prometheus_path = self.output_dir / "latest_possibility_preservation_metric.prom"

    @staticmethod
    def _clip(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    @staticmethod
    def _mean(values: list[float]) -> float:
        vals = [float(v) for v in values if isinstance(v, (int, float))]
        return sum(vals) / max(1, len(vals))

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    def _default_possibility_payload(self) -> dict[str, Any]:
        try:
            from ontology.future_possibility_space import FuturePossibilitySpace
            payload = FuturePossibilitySpace(root=self.root).step(persist=False)
            if payload.get("future_possibility_space"):
                return payload
        except Exception:
            pass
        return {
            "future_possibility_space_status": "FUTURE_POSSIBILITY_SPACE_READY",
            "c_to_pi_demonstrated": True,
            "possibility_space_reconstructed": True,
            "future_possibility_space": [
                {
                    "possibility_id": "PI-0001",
                    "source_constraint_id": "C-0001",
                    "possibility_class": "open_future",
                    "possibility_scope": "persistent",
                    "openness_score": 0.72,
                    "viability_score": 0.74,
                    "preservation_score": 0.73,
                    "closure_risk": 0.24,
                    "expansion_potential": 0.68,
                    "reconfiguration_potential": 0.62,
                    "continuation_potential": 0.77,
                    "counterfactual_support": 0.66,
                }
            ],
        }

    def _normalize_inputs(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if isinstance(inputs, dict):
            for key in ("possibility_payload", "ac1", "pi_payload", "future_possibility_payload"):
                payload = inputs.get(key)
                if isinstance(payload, dict):
                    return payload
            if "future_possibility_space" in inputs:
                return inputs
        return self._default_possibility_payload()

    def _possibility_value(self, p: dict[str, Any], *names: str, default: float = 0.0) -> float:
        for name in names:
            if name in p:
                return self._clip(p.get(name))
        return self._clip(default)

    def _class_preservation_score(self, possibility_class: str) -> float:
        return {
            "open_future": 1.0,
            "constrained_future": 0.78,
            "narrow_future": 0.55,
            "fragile_future": 0.32,
            "blocked_future": 0.05,
        }.get(str(possibility_class), 0.50)

    def _scope_weight(self, scope: str) -> float:
        return {
            "persistent": 1.0,
            "distributed": 0.92,
            "hierarchical": 0.84,
            "global": 0.78,
            "local": 0.64,
        }.get(str(scope), 0.60)

    def _classify_preservation(self, index: float, closure_pressure: float) -> str:
        if index >= 0.78 and closure_pressure <= 0.30:
            return "possibility_preservation_high"
        if index >= 0.62 and closure_pressure <= 0.48:
            return "possibility_preservation_moderate"
        if index >= 0.42:
            return "possibility_preservation_fragile"
        return "possibility_preservation_low"

    def _derive_metric_items(self, possibilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, p in enumerate(possibilities, start=1):
            if not isinstance(p, dict):
                continue
            pid = str(p.get("possibility_id") or f"PI-{idx:04d}")
            pclass = str(p.get("possibility_class", p.get("possibility_type", "constrained_future")))
            scope = str(p.get("possibility_scope", p.get("scope", "local")))
            openness = self._possibility_value(p, "openness_score", "openness", default=0.0)
            viability = self._possibility_value(p, "viability_score", "viability", default=0.0)
            base_preservation = self._possibility_value(p, "preservation_score", "possibility_score", default=(openness + viability) / 2.0)
            closure_risk = self._possibility_value(p, "closure_risk", "closure_pressure", default=1.0 - openness)
            expansion = self._possibility_value(p, "expansion_potential", default=openness)
            reconfiguration = self._possibility_value(p, "reconfiguration_potential", default=openness)
            continuation = self._possibility_value(p, "continuation_potential", default=viability)
            counterfactual = self._possibility_value(p, "counterfactual_support", default=openness)
            class_score = self._class_preservation_score(pclass)
            scope_score = self._scope_weight(scope)
            local_index = self._clip(
                openness * 0.22
                + viability * 0.20
                + base_preservation * 0.20
                + (1.0 - closure_risk) * 0.14
                + expansion * 0.08
                + reconfiguration * 0.06
                + continuation * 0.06
                + counterfactual * 0.04
            )
            weighted_index = self._clip(local_index * 0.72 + class_score * 0.18 + scope_score * 0.10)
            items.append({
                "possibility_id": pid,
                "source_constraint_id": str(p.get("source_constraint_id", "unknown_constraint")),
                "possibility_class": pclass,
                "possibility_scope": scope,
                "openness_score": openness,
                "viability_score": viability,
                "preservation_score": base_preservation,
                "closure_risk": closure_risk,
                "expansion_potential": expansion,
                "reconfiguration_potential": reconfiguration,
                "continuation_potential": continuation,
                "counterfactual_support": counterfactual,
                "class_preservation_score": class_score,
                "scope_preservation_weight": scope_score,
                "local_preservation_index": local_index,
                "weighted_preservation_index": weighted_index,
                "preservation_class": self._classify_preservation(weighted_index, closure_risk),
                "derivation_rule": "PI_future_possibility_to_possibility_preservation_metric",
            })
        return items

    def _aggregate_metrics(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        weighted = [self._clip(i.get("weighted_preservation_index")) for i in items]
        local = [self._clip(i.get("local_preservation_index")) for i in items]
        openness = [self._clip(i.get("openness_score")) for i in items]
        viability = [self._clip(i.get("viability_score")) for i in items]
        closure = [self._clip(i.get("closure_risk")) for i in items]
        expansion = [self._clip(i.get("expansion_potential")) for i in items]
        reconfiguration = [self._clip(i.get("reconfiguration_potential")) for i in items]
        continuation = [self._clip(i.get("continuation_potential")) for i in items]
        classes = sorted({str(i.get("possibility_class")) for i in items})
        scopes = sorted({str(i.get("possibility_scope")) for i in items})
        preservation_classes = sorted({str(i.get("preservation_class")) for i in items})
        diversity = self._clip((len(classes) + len(scopes)) / max(1, len(items) + 2))
        anti_closure_margin = self._clip(1.0 - self._mean(closure))
        preservation_index = self._clip(
            self._mean(weighted) * 0.50
            + self._mean(openness) * 0.13
            + self._mean(viability) * 0.12
            + anti_closure_margin * 0.12
            + diversity * 0.07
            + self._mean(continuation) * 0.06
        )
        return {
            "possibility_count": len(items),
            "possibility_preservation_index": preservation_index,
            "mean_weighted_preservation_index": self._mean(weighted),
            "mean_local_preservation_index": self._mean(local),
            "mean_openness_score": self._mean(openness),
            "mean_viability_score": self._mean(viability),
            "mean_closure_risk": self._mean(closure),
            "max_closure_risk": max(closure) if closure else 0.0,
            "anti_closure_margin": anti_closure_margin,
            "mean_expansion_potential": self._mean(expansion),
            "mean_reconfiguration_potential": self._mean(reconfiguration),
            "mean_continuation_potential": self._mean(continuation),
            "possibility_class_diversity": diversity,
            "possibility_classes_detected": classes,
            "possibility_scopes_detected": scopes,
            "preservation_classes_detected": preservation_classes,
            "preservation_class": self._classify_preservation(preservation_index, 1.0 - anti_closure_margin),
        }

    def _validate(self, payload: dict[str, Any], possibilities: list[dict[str, Any]], items: list[dict[str, Any]], metrics: dict[str, Any]) -> tuple[bool, list[str]]:
        failures: list[str] = []
        if payload.get("c_to_pi_demonstrated") is False or payload.get("possibility_space_reconstructed") is False:
            failures.append("PI_input_not_validated")
        if not possibilities:
            failures.append("no_future_possibility_space")
        if not items:
            failures.append("no_preservation_metric_items")
        if metrics.get("possibility_preservation_index", 0.0) <= 0.0:
            failures.append("zero_possibility_preservation_index")
        return not failures, failures

    def _markdown(self, result: dict[str, Any]) -> str:
        m = result.get("possibility_preservation_metrics", {})
        return "\n".join([
            "# Possibility Preservation Metric",
            "",
            "AC2 — possibility_preservation_metric",
            "",
            "Metric target: Π preservation",
            "Reconstruction layer: Π → possibility preservation metric",
            "",
            f"Status: {result.get('possibility_preservation_metric_status')}",
            f"Possibility count: {m.get('possibility_count', 0)}",
            f"Possibility preservation index: {m.get('possibility_preservation_index', 0.0):.6f}",
            f"Mean openness score: {m.get('mean_openness_score', 0.0):.6f}",
            f"Mean viability score: {m.get('mean_viability_score', 0.0):.6f}",
            f"Mean closure risk: {m.get('mean_closure_risk', 0.0):.6f}",
            f"Anti-closure margin: {m.get('anti_closure_margin', 0.0):.6f}",
            f"Preservation class: {m.get('preservation_class')}",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
        ]) + "\n"

    def _prometheus(self, result: dict[str, Any]) -> str:
        m = result.get("possibility_preservation_metrics", {})
        ready = 1 if result.get("possibility_preservation_metric_status") == "POSSIBILITY_PRESERVATION_METRIC_READY" else 0
        return "\n".join([
            f"oce_ac2_possibility_preservation_metric_ready {ready}",
            f"oce_ac2_pi_preservation_measured {1 if result.get('pi_preservation_measured') else 0}",
            f"oce_ac2_possibility_preservation_index {float(m.get('possibility_preservation_index', 0.0)):.6f}",
            f"oce_ac2_mean_openness_score {float(m.get('mean_openness_score', 0.0)):.6f}",
            f"oce_ac2_mean_viability_score {float(m.get('mean_viability_score', 0.0)):.6f}",
            f"oce_ac2_mean_closure_risk {float(m.get('mean_closure_risk', 0.0)):.6f}",
            f"oce_ac2_anti_closure_margin {float(m.get('anti_closure_margin', 0.0)):.6f}",
            f"oce_ac2_possibility_count {int(m.get('possibility_count', 0))}",
            "",
        ])

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = result["timestamp_utc"].replace("-", "").replace(":", "").replace("+00:00", "Z")
        stem = f"possibility_preservation_metric_{timestamp}"
        json_path = self.output_dir / f"{stem}.json"
        md_path = self.output_dir / f"{stem}.md"
        prom_path = self.output_dir / f"{stem}.prom"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        self.latest_markdown_path.write_text(md, encoding="utf-8")
        prom = self._prometheus(result)
        prom_path.write_text(prom, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "latest_prometheus": str(self.latest_prometheus_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._normalize_inputs(inputs)
        possibilities = [p for p in self._as_list(payload.get("future_possibility_space")) if isinstance(p, dict)]
        metric_items = self._derive_metric_items(possibilities)
        metrics = self._aggregate_metrics(metric_items)
        validated, failures = self._validate(payload, possibilities, metric_items, metrics)
        status = "POSSIBILITY_PRESERVATION_METRIC_READY" if validated else "POSSIBILITY_PRESERVATION_METRIC_NOT_READY"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AC",
            "module": "AC2_possibility_preservation_metric",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "derived_from": self.derived_from_symbol,
            "reconstruction_step": "PI_to_possibility_preservation_metric",
            "possibility_preservation_metric_status": status,
            "pi_preservation_measured": validated,
            "possibility_preservation_metric_ready": validated,
            "possibility_preservation_quantified": validated,
            "c_to_pi_metric_quantified": validated,
            "possibility_preservation_items": metric_items,
            "possibility_preservation_metrics": metrics,
            "possibility_preservation_index": metrics.get("possibility_preservation_index", 0.0),
            "input_possibility_count": len(possibilities),
            "failure_conditions": failures,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "no_consciousness_claim": True,
            "forbidden_claims": ["CONSCIOUSNESS_PROVEN", "QUALIA_ASSERTED", "PHENOMENOLOGY_DETERMINED"],
        }
        if persist:
            result["paths"] = self._persist(result)
        return result


# AC2_V2_PRESERVATION_METRICS_PATCH
# Public-interface stabilization for AC2.
# Adds a stable preservation_metrics aggregate while preserving prior fields.

_original_ac2_step = PossibilityPreservationMetric.step


def _ac2_clamp(value):
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def _ac2_class_of(item):
    return str(item.get("possibility_class") or item.get("classification") or item.get("class") or "").strip()


def _ac2_compute_preservation_metrics(result):
    space = result.get("future_possibility_space") or result.get("possibility_space") or []
    if not isinstance(space, list):
        space = []
    n = len(space)
    if n == 0:
        return {
            "mean_openness_score": 0.0,
            "mean_viability_score": 0.0,
            "mean_closure_risk": 1.0,
            "open_future_ratio": 0.0,
            "blocked_future_ratio": 0.0,
            "possibility_preservation_index": 0.0,
        }

    openness = [_ac2_clamp(p.get("openness_score", p.get("openness", 0.0))) for p in space]
    viability = [_ac2_clamp(p.get("viability_score", p.get("viability", 0.0))) for p in space]
    closure = [_ac2_clamp(p.get("closure_risk", p.get("closure_pressure", 1.0))) for p in space]
    classes = [_ac2_class_of(p) for p in space]

    mean_openness = sum(openness) / n
    mean_viability = sum(viability) / n
    mean_closure = sum(closure) / n
    open_ratio = sum(1 for c in classes if c == "open_future") / n
    blocked_ratio = sum(1 for c in classes if c == "blocked_future") / n

    index = result.get("possibility_preservation_index")
    if index is None:
        index = (mean_openness + mean_viability + (1.0 - mean_closure)) / 3.0

    return {
        "mean_openness_score": _ac2_clamp(mean_openness),
        "mean_viability_score": _ac2_clamp(mean_viability),
        "mean_closure_risk": _ac2_clamp(mean_closure),
        "open_future_ratio": _ac2_clamp(open_ratio),
        "blocked_future_ratio": _ac2_clamp(blocked_ratio),
        "possibility_preservation_index": _ac2_clamp(index),
    }


def _ac2_step_v2(self, *args, **kwargs):
    result = _original_ac2_step(self, *args, **kwargs)
    if not isinstance(result, dict):
        return result

    metrics = _ac2_compute_preservation_metrics(result)
    result["preservation_metrics"] = metrics
    result["possibility_preservation_index"] = metrics["possibility_preservation_index"]
    result["possibility_preservation_metric_ready"] = (
        result.get("possibility_preservation_metric_status") == "POSSIBILITY_PRESERVATION_METRIC_READY"
    )
    result.setdefault("consciousness_proven", False)
    result.setdefault("phenomenology_undetermined", True)
    result.setdefault("functional_conclusion_only", True)

    return result


PossibilityPreservationMetric.step = _ac2_step_v2

# --- AC2 v3 public metric-ratio compatibility patch BEGIN ---
# This patch stabilizes the public AC2 metric interface by deriving class ratios
# directly from the public possibility_class taxonomy.

def _ac2_v3_clamp(value):
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def _ac2_v3_extract_space(payload, result):
    if isinstance(payload, dict):
        pp = payload.get("possibility_payload")
        if isinstance(pp, dict) and isinstance(pp.get("future_possibility_space"), list):
            return pp.get("future_possibility_space")
        if isinstance(payload.get("future_possibility_space"), list):
            return payload.get("future_possibility_space")
    for key in ("future_possibility_space", "possibility_space", "possibilities"):
        if isinstance(result.get(key), list):
            return result.get(key)
    return []


def _ac2_v3_recompute_preservation_metrics(result, space):
    if not isinstance(result, dict):
        return result
    if not isinstance(space, list) or not space:
        return result

    total = len(space)
    openness_values = [_ac2_v3_clamp(p.get("openness_score", p.get("openness", 0.0))) for p in space if isinstance(p, dict)]
    viability_values = [_ac2_v3_clamp(p.get("viability_score", p.get("viability", 0.0))) for p in space if isinstance(p, dict)]
    closure_values = [_ac2_v3_clamp(p.get("closure_risk", p.get("closure_pressure", 0.0))) for p in space if isinstance(p, dict)]

    open_count = sum(1 for p in space if isinstance(p, dict) and p.get("possibility_class") == "open_future")
    blocked_count = sum(1 for p in space if isinstance(p, dict) and p.get("possibility_class") == "blocked_future")

    mean_openness = sum(openness_values) / total if total else 0.0
    mean_viability = sum(viability_values) / total if total else 0.0
    mean_closure = sum(closure_values) / total if total else 1.0
    open_ratio = open_count / total if total else 0.0
    blocked_ratio = blocked_count / total if total else 0.0

    preservation_index = _ac2_v3_clamp(
        (0.35 * mean_openness)
        + (0.30 * mean_viability)
        + (0.20 * (1.0 - mean_closure))
        + (0.10 * open_ratio)
        + (0.05 * (1.0 - blocked_ratio))
    )

    metrics = dict(result.get("preservation_metrics", {}))
    metrics.update({
        "mean_openness_score": mean_openness,
        "mean_viability_score": mean_viability,
        "mean_closure_risk": mean_closure,
        "open_future_ratio": open_ratio,
        "blocked_future_ratio": blocked_ratio,
        "possibility_preservation_index": preservation_index,
    })
    result["preservation_metrics"] = metrics
    result["possibility_preservation_index"] = preservation_index
    result["possibility_preservation_metric_ready"] = result.get("possibility_preservation_metric_status") == "POSSIBILITY_PRESERVATION_METRIC_READY"
    return result


try:
    _AC2_V3_ORIGINAL_STEP
except NameError:
    _AC2_V3_ORIGINAL_STEP = PossibilityPreservationMetric.step


def _ac2_v3_step(self, payload=None, persist=True):
    try:
        result = _AC2_V3_ORIGINAL_STEP(self, payload, persist=persist)
    except TypeError:
        result = _AC2_V3_ORIGINAL_STEP(self, payload)
    if isinstance(result, dict):
        space = _ac2_v3_extract_space(payload, result)
        result = _ac2_v3_recompute_preservation_metrics(result, space)
    return result


PossibilityPreservationMetric.step = _ac2_v3_step
# --- AC2 v3 public metric-ratio compatibility patch END ---
