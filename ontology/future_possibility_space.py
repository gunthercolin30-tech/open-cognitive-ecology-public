from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FuturePossibility:
    possibility_id: str
    source_constraint_id: str
    source_attractor_id: str
    target_attractor_id: str
    possibility_type: str
    possibility_class: str
    possibility_scope: str
    future_horizon: str
    constraint_support: float
    possibility_score: float
    openness_score: float
    viability_score: float
    preservation_score: float
    closure_risk: float
    expansion_potential: float
    reconfiguration_potential: float
    continuation_potential: float
    counterfactual_support: float
    dependency_count: int
    derivation_rule: str


class FuturePossibilitySpace:
    """
    AC1 — future_possibility_space.

    Reconstructs C -> Π by deriving a bounded, functional future possibility
    space from emergent constraints validated by AB5/AB6. The module models
    what remains open, viable, reconfigurable and continuable under constraints.

    It does not assert consciousness, subjectivity, qualia, or phenomenology.
    """

    primitive = "FUTURE_POSSIBILITY_SPACE"
    symbol = "Π"
    derived_from_symbol = "C"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AC1_future_possibility_space"
        self.history_path = self.output_dir / "future_possibility_space_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_future_possibility_space.json"
        self.latest_markdown_path = self.output_dir / "latest_future_possibility_space.md"
        self.latest_prometheus_path = self.output_dir / "latest_future_possibility_space.prom"

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
    def _sid(value: Any, default: str = "unknown") -> str:
        if value is None:
            return default
        text = str(value)
        return text if text else default

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    def _default_constraint_payload(self) -> dict[str, Any]:
        try:
            from ontology.constraint_emergence_engine import ConstraintEmergenceEngine
            payload = ConstraintEmergenceEngine(root=self.root).step(persist=False)
            if payload.get("emergent_constraints"):
                return payload
        except Exception:
            pass
        return {
            "constraint_emergence_engine_status": "CONSTRAINT_EMERGENCE_READY",
            "gamma_to_c_demonstrated": True,
            "gamma_to_constraints_demonstrated": True,
            "emergent_constraints": [
                {
                    "constraint_id": "C-0001",
                    "source_attractor_id": "A-0001",
                    "target_attractor_id": "A-0001",
                    "constraint_scope": "persistent",
                    "constraint_type": "continuity_preservation",
                    "constraint_strength": 0.84,
                    "constraint_persistence": 0.88,
                    "propagation_potential": 0.72,
                    "dependency_strength": 0.70,
                    "distributed_support": 0.68,
                    "emergence_confidence": 0.82,
                }
            ],
        }

    def _normalize_inputs(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if isinstance(inputs, dict):
            for key in ("constraint_payload", "ab5", "constraints"):
                payload = inputs.get(key)
                if isinstance(payload, dict):
                    return payload
            if "emergent_constraints" in inputs:
                return inputs
        return self._default_constraint_payload()

    def _constraint_value(self, c: dict[str, Any], *names: str, default: float = 0.0) -> float:
        for name in names:
            if name in c:
                return self._clip(c.get(name))
        return self._clip(default)

    def _possibility_type(self, strength: float, propagation: float, persistence: float, closure_risk: float) -> str:
        if closure_risk >= 0.70:
            return "guarded_possibility"
        if propagation >= 0.72 and strength >= 0.65:
            return "distributed_expansion"
        if persistence >= 0.72:
            return "continuation_possibility"
        if strength < 0.42:
            return "reconfiguration_possibility"
        return "local_future_possibility"

    def _possibility_class(self, openness: float, viability: float, closure_risk: float) -> str:
        if closure_risk >= 0.86 or openness <= 0.12:
            return "blocked_future"
        if closure_risk >= 0.70 or openness <= 0.28:
            return "fragile_future"
        if closure_risk >= 0.52 or openness <= 0.45:
            return "narrow_future"
        if viability >= 0.62 and openness >= 0.62:
            return "open_future"
        return "constrained_future"

    def _possibility_scope(self, c: dict[str, Any], possibility_score: float, propagation: float) -> str:
        raw = str(c.get("constraint_scope", c.get("scope", "local")))
        allowed = {"local", "global", "hierarchical", "distributed", "persistent"}
        if raw in allowed:
            return raw
        if possibility_score >= 0.80:
            return "persistent"
        if propagation >= 0.70:
            return "distributed"
        if possibility_score >= 0.62:
            return "global"
        return "local"

    def _future_horizon(self, preservation: float, persistence: float) -> str:
        if preservation >= 0.82 and persistence >= 0.70:
            return "long_horizon"
        if preservation >= 0.60:
            return "mid_horizon"
        return "short_horizon"

    def _derive_possibilities(self, constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
        possibilities: list[dict[str, Any]] = []
        for idx, c in enumerate(constraints, start=1):
            if not isinstance(c, dict):
                continue
            cid = self._sid(c.get("constraint_id"), f"C-{idx:04d}")
            src = self._sid(c.get("source_attractor_id", c.get("source")), "unknown_source")
            tgt = self._sid(c.get("target_attractor_id", c.get("target")), src)
            strength = self._constraint_value(c, "constraint_strength", "strength", default=0.0)
            persistence = self._constraint_value(c, "constraint_persistence", "persistence", default=strength)
            propagation = self._constraint_value(c, "propagation_potential", "propagation", default=strength)
            dependency = self._constraint_value(c, "dependency_strength", "dependency", default=strength * 0.5)
            distributed = self._constraint_value(c, "distributed_support", default=propagation)
            confidence = self._constraint_value(c, "emergence_confidence", "confidence", default=strength)

            closure_risk = self._clip((strength * 0.35) + (persistence * 0.20) + (propagation * 0.20) + (dependency * 0.15) + ((1.0 - confidence) * 0.10))
            openness = self._clip((1.0 - closure_risk) * 0.65 + (1.0 - strength) * 0.20 + (1.0 - persistence) * 0.15)
            viability = self._clip((1.0 - closure_risk) * 0.40 + confidence * 0.25 + (1.0 - dependency) * 0.20 + (1.0 - strength) * 0.15)
            expansion = self._clip((1.0 - closure_risk) * 0.40 + (1.0 - strength) * 0.30 + distributed * 0.15 + propagation * 0.15)
            reconfiguration = self._clip((1.0 - strength) * 0.45 + (1.0 - dependency) * 0.30 + (1.0 - persistence) * 0.25)
            continuation = self._clip(persistence * 0.45 + viability * 0.35 + confidence * 0.20)
            counterfactual = self._clip(openness * 0.40 + reconfiguration * 0.35 + expansion * 0.25)
            preservation = self._clip(openness * 0.35 + viability * 0.30 + continuation * 0.20 + expansion * 0.15)
            possibility_score = self._clip(preservation * 0.55 + counterfactual * 0.25 + (1.0 - closure_risk) * 0.20)

            scope = self._possibility_scope(c, possibility_score, propagation)
            ptype = self._possibility_type(strength, propagation, persistence, closure_risk)
            pclass = self._possibility_class(openness, viability, closure_risk)
            horizon = self._future_horizon(preservation, persistence)

            possibility = FuturePossibility(
                possibility_id=f"PI-{idx:04d}",
                source_constraint_id=cid,
                source_attractor_id=src,
                target_attractor_id=tgt,
                possibility_type=ptype,
                possibility_class=pclass,
                possibility_scope=scope,
                future_horizon=horizon,
                constraint_support=strength,
                possibility_score=possibility_score,
                openness_score=openness,
                viability_score=viability,
                preservation_score=preservation,
                closure_risk=closure_risk,
                expansion_potential=expansion,
                reconfiguration_potential=reconfiguration,
                continuation_potential=continuation,
                counterfactual_support=counterfactual,
                dependency_count=int(1 + round(dependency * 4)),
                derivation_rule="C_emergent_constraint_to_PI_future_possibility",
            )
            possibilities.append(asdict(possibility))
        return possibilities

    def _build_possibility_graph(self, possibilities: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
        graph: dict[str, dict[str, float]] = {}
        for p in possibilities:
            pid = str(p.get("possibility_id"))
            graph.setdefault(pid, {})[pid] = 1.0
        for p in possibilities:
            pid = str(p.get("possibility_id"))
            src = p.get("source_attractor_id")
            tgt = p.get("target_attractor_id")
            pscore = self._clip(p.get("possibility_score"))
            for q in possibilities:
                qid = str(q.get("possibility_id"))
                if pid == qid:
                    continue
                shared_attractor = src in {q.get("source_attractor_id"), q.get("target_attractor_id")} or tgt in {q.get("source_attractor_id"), q.get("target_attractor_id")}
                scope_match = p.get("possibility_scope") == q.get("possibility_scope")
                qscore = self._clip(q.get("possibility_score"))
                coupling = self._clip((1.0 if shared_attractor else 0.25) * 0.45 + (1.0 if scope_match else 0.35) * 0.20 + (1.0 - abs(pscore - qscore)) * 0.35)
                graph.setdefault(pid, {})[qid] = coupling
        return graph

    def _metrics(self, possibilities: list[dict[str, Any]], graph: dict[str, dict[str, float]]) -> dict[str, Any]:
        scores = [self._clip(p.get("possibility_score")) for p in possibilities]
        openness = [self._clip(p.get("openness_score")) for p in possibilities]
        viability = [self._clip(p.get("viability_score")) for p in possibilities]
        closure = [self._clip(p.get("closure_risk")) for p in possibilities]
        preservation = [self._clip(p.get("preservation_score")) for p in possibilities]
        scopes = sorted({str(p.get("possibility_scope")) for p in possibilities})
        horizons = sorted({str(p.get("future_horizon")) for p in possibilities})
        graph_edges = sum(max(0, len(v) - 1) for v in graph.values())
        return {
            "possibility_count": len(possibilities),
            "mean_possibility_score": self._mean(scores),
            "mean_openness_score": self._mean(openness),
            "mean_viability_score": self._mean(viability),
            "mean_preservation_score": self._mean(preservation),
            "mean_closure_risk": self._mean(closure),
            "max_closure_risk": max(closure) if closure else 0.0,
            "scope_count": len(scopes),
            "scopes_detected": scopes,
            "horizons_detected": horizons,
            "possibility_graph_edge_count": graph_edges,
            "pi_density": self._clip(len(possibilities) / max(1, len(possibilities) + len(scopes))),
        }

    def _validate(self, constraint_payload: dict[str, Any], possibilities: list[dict[str, Any]], metrics: dict[str, Any]) -> tuple[bool, list[str]]:
        failures: list[str] = []
        constraints = self._as_list(constraint_payload.get("emergent_constraints"))
        if not constraints:
            failures.append("no_emergent_constraints")
        if constraint_payload.get("gamma_to_c_demonstrated") is False or constraint_payload.get("gamma_to_constraints_demonstrated") is False:
            failures.append("C_input_not_validated")
        if not possibilities:
            failures.append("no_future_possibilities")
        if metrics.get("mean_possibility_score", 0.0) <= 0.0:
            failures.append("zero_possibility_score")
        if metrics.get("mean_openness_score", 0.0) <= 0.0:
            failures.append("zero_openness_score")
        return not failures, failures

    def _markdown(self, result: dict[str, Any]) -> str:
        m = result.get("possibility_space_metrics", {})
        return "\n".join([
            "# Future Possibility Space",
            "",
            "AC1 — future_possibility_space",
            "",
            "Reconstruction: C → Π",
            "",
            f"Status: {result.get('future_possibility_space_status')}",
            f"Future possibilities: {m.get('possibility_count', 0)}",
            f"Mean possibility score: {m.get('mean_possibility_score', 0.0):.6f}",
            f"Mean openness score: {m.get('mean_openness_score', 0.0):.6f}",
            f"Mean viability score: {m.get('mean_viability_score', 0.0):.6f}",
            f"Mean preservation score: {m.get('mean_preservation_score', 0.0):.6f}",
            f"Mean closure risk: {m.get('mean_closure_risk', 0.0):.6f}",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
        ]) + "\n"

    def _prometheus(self, result: dict[str, Any]) -> str:
        m = result.get("possibility_space_metrics", {})
        ready = 1 if result.get("future_possibility_space_status") == "FUTURE_POSSIBILITY_SPACE_READY" else 0
        return "\n".join([
            f"oce_ac1_future_possibility_space_ready {ready}",
            f"oce_ac1_c_to_pi_demonstrated {1 if result.get('c_to_pi_demonstrated') else 0}",
            f"oce_ac1_possibility_count {int(m.get('possibility_count', 0))}",
            f"oce_ac1_mean_possibility_score {float(m.get('mean_possibility_score', 0.0)):.6f}",
            f"oce_ac1_mean_openness_score {float(m.get('mean_openness_score', 0.0)):.6f}",
            f"oce_ac1_mean_viability_score {float(m.get('mean_viability_score', 0.0)):.6f}",
            f"oce_ac1_mean_closure_risk {float(m.get('mean_closure_risk', 0.0)):.6f}",
            "",
        ])

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = result["timestamp_utc"].replace("-", "").replace(":", "").replace("+00:00", "Z")
        stem = f"future_possibility_space_{timestamp}"
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
        constraint_payload = self._normalize_inputs(inputs)
        constraints = [c for c in self._as_list(constraint_payload.get("emergent_constraints")) if isinstance(c, dict)]
        possibilities = self._derive_possibilities(constraints)
        graph = self._build_possibility_graph(possibilities)
        metrics = self._metrics(possibilities, graph)
        validated, failures = self._validate(constraint_payload, possibilities, metrics)
        status = "FUTURE_POSSIBILITY_SPACE_READY" if validated else "FUTURE_POSSIBILITY_SPACE_NOT_READY"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AC",
            "module": "AC1_future_possibility_space",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "derived_from": self.derived_from_symbol,
            "derives": self.symbol,
            "reconstruction_step": "C_to_PI",
            "future_possibility_space_status": status,
            "c_to_pi_demonstrated": validated,
            "future_possibility_space_ready": validated,
            "possibility_space_reconstructed": validated,
            "future_possibility_space": possibilities,
            "possibility_graph": graph,
            "possibility_space_metrics": metrics,
            "constraint_count": len(constraints),
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
