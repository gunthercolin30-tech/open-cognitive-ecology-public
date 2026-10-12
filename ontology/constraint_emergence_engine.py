from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EmergentConstraint:
    constraint_id: str
    source_attractor_id: str
    target_attractor_id: str
    scope: str
    constraint_type: str
    constraint_strength: float
    local_constraint: float
    global_constraint: float
    hierarchical_level: int
    hierarchy_weight: float
    distributed_support: float
    persistence: float
    dependency_strength: float
    conservation_score: float
    propagation_potential: float
    emergence_confidence: float
    derivation_rule: str


class ConstraintEmergenceEngine:
    """
    AB5 — constraint_emergence_engine.

    Reconstructs Γ -> C by deriving bounded, functional constraints from the
    Gamma field emitted by AB4. It computes local/global, hierarchical,
    distributed, persistent and propagative constraints without asserting
    consciousness, subjectivity, qualia, or phenomenology.
    """

    primitive = "CONSTRAINT_EMERGENCE_ENGINE"
    symbol = "C"
    derived_from_symbol = "Γ"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AB5_constraint_emergence_engine"
        self.history_path = self.output_dir / "constraint_emergence_engine_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_constraint_emergence_engine.json"
        self.latest_markdown_path = self.output_dir / "latest_constraint_emergence_engine.md"
        self.latest_prometheus_path = self.output_dir / "latest_constraint_emergence_engine.prom"

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

    def _default_gamma_payload(self) -> dict[str, Any]:
        try:
            from ontology.gamma_field_engine import GammaFieldEngine
            payload = GammaFieldEngine(root=self.root).step(persist=False)
            if payload.get("gamma_field"):
                return payload
        except Exception:
            pass
        return {
            "gamma_field_engine_status": "GAMMA_FIELD_READY",
            "a_to_gamma_demonstrated": True,
            "gamma_field": [
                {
                    "source_attractor_id": "A-0001",
                    "target_attractor_id": "A-0001",
                    "constraint_density": 0.86,
                    "gamma_intensity": 0.82,
                    "gradient_magnitude": 0.12,
                    "diffusion_potential": 0.74,
                    "field_potential": 0.83,
                    "continuity": 0.88,
                    "global_coherence": 0.84,
                    "conservation_score": 1.0,
                },
                {
                    "source_attractor_id": "A-0001",
                    "target_attractor_id": "A-0002",
                    "constraint_density": 0.52,
                    "gamma_intensity": 0.56,
                    "gradient_magnitude": 0.38,
                    "diffusion_potential": 0.60,
                    "field_potential": 0.57,
                    "continuity": 0.61,
                    "global_coherence": 0.59,
                    "conservation_score": 0.62,
                },
            ],
        }

    def _normalize_payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if isinstance(inputs, dict):
            if isinstance(inputs.get("gamma_payload"), dict):
                return dict(inputs["gamma_payload"])
            if isinstance(inputs.get("gamma_field"), list):
                return dict(inputs)
        return self._default_gamma_payload()

    def _normalize_cell(self, cell: dict[str, Any], idx: int) -> dict[str, Any]:
        source = self._sid(cell.get("source_attractor_id", cell.get("source", cell.get("attractor_id"))), f"source_{idx}")
        target = self._sid(cell.get("target_attractor_id", cell.get("target", cell.get("attractor_id"))), source)
        density = self._clip(cell.get("constraint_density", cell.get("density", cell.get("gamma_value", 0.0))))
        intensity = self._clip(cell.get("gamma_intensity", cell.get("intensity", cell.get("gamma_value", density))))
        gradient = self._clip(cell.get("gradient_magnitude", cell.get("gradient", 0.0)))
        diffusion = self._clip(cell.get("diffusion_potential", cell.get("diffusion", 0.0)))
        potential = self._clip(cell.get("field_potential", cell.get("potential", cell.get("gamma_value", density))))
        continuity = self._clip(cell.get("continuity", 1.0 - gradient))
        coherence = self._clip(cell.get("global_coherence", cell.get("coherence", continuity)))
        conservation = self._clip(cell.get("conservation_score", cell.get("mutual_conservation", intensity)))
        return {
            "source_attractor_id": source,
            "target_attractor_id": target,
            "constraint_density": density,
            "gamma_intensity": intensity,
            "gradient_magnitude": gradient,
            "diffusion_potential": diffusion,
            "field_potential": potential,
            "continuity": continuity,
            "global_coherence": coherence,
            "conservation_score": conservation,
        }

    def _scope(self, source: str, target: str, distributed_support: float, hierarchy_weight: float) -> str:
        if source == target:
            return "local"
        if distributed_support >= 0.70 and hierarchy_weight >= 0.60:
            return "global"
        if hierarchy_weight >= 0.55:
            return "hierarchical"
        return "distributed"

    def _ctype(self, strength: float, gradient: float, persistence: float, propagation: float) -> str:
        if strength >= 0.78 and persistence >= 0.65:
            return "persistent_constraint"
        if propagation >= 0.70:
            return "propagating_constraint"
        if gradient >= 0.55:
            return "boundary_constraint"
        if strength >= 0.50:
            return "structural_constraint"
        return "weak_emergent_constraint"

    def _hierarchical_level(self, strength: float, global_constraint: float, distributed_support: float) -> int:
        score = self._clip(0.45 * strength + 0.35 * global_constraint + 0.20 * distributed_support)
        if score >= 0.80:
            return 3
        if score >= 0.55:
            return 2
        if score >= 0.30:
            return 1
        return 0

    def _derive_constraints(self, gamma_field: list[dict[str, Any]]) -> list[EmergentConstraint]:
        cells = [self._normalize_cell(c, i) for i, c in enumerate(gamma_field) if isinstance(c, dict)]
        constraints: list[EmergentConstraint] = []
        n = max(1, len(cells))
        global_density = self._mean([c["constraint_density"] for c in cells])
        global_intensity = self._mean([c["gamma_intensity"] for c in cells])
        global_coherence = self._mean([c["global_coherence"] for c in cells])
        for idx, c in enumerate(cells, start=1):
            density = c["constraint_density"]
            intensity = c["gamma_intensity"]
            gradient = c["gradient_magnitude"]
            diffusion = c["diffusion_potential"]
            potential = c["field_potential"]
            continuity = c["continuity"]
            coherence = c["global_coherence"]
            conservation = c["conservation_score"]
            local_constraint = self._clip(0.35 * density + 0.30 * intensity + 0.20 * potential + 0.15 * (1.0 - gradient))
            global_constraint = self._clip(0.30 * global_density + 0.25 * global_intensity + 0.25 * global_coherence + 0.20 * coherence)
            distributed_support = self._clip(0.35 * diffusion + 0.25 * continuity + 0.20 * conservation + 0.20 * (1.0 / n))
            persistence = self._clip(0.35 * continuity + 0.25 * potential + 0.20 * conservation + 0.20 * (1.0 - gradient))
            dependency_strength = self._clip(0.35 * intensity + 0.25 * density + 0.20 * conservation + 0.20 * gradient)
            propagation_potential = self._clip(0.40 * diffusion + 0.25 * intensity + 0.20 * distributed_support + 0.15 * coherence)
            constraint_strength = self._clip(0.30 * local_constraint + 0.25 * global_constraint + 0.20 * persistence + 0.15 * dependency_strength + 0.10 * propagation_potential)
            if density >= 0.85 and intensity >= 0.85 and potential >= 0.80:
                constraint_strength = max(
                    constraint_strength,
                    self._clip(0.30 * density + 0.30 * intensity + 0.20 * potential + 0.10 * diffusion + 0.10 * conservation),
                )
            hierarchy_weight = self._clip(0.45 * global_constraint + 0.30 * dependency_strength + 0.25 * persistence)
            level = self._hierarchical_level(constraint_strength, global_constraint, distributed_support)
            scope = self._scope(c["source_attractor_id"], c["target_attractor_id"], distributed_support, hierarchy_weight)
            ctype = self._ctype(constraint_strength, gradient, persistence, propagation_potential)
            emergence_confidence = self._clip(0.35 * constraint_strength + 0.25 * coherence + 0.20 * persistence + 0.20 * conservation)
            constraints.append(EmergentConstraint(
                constraint_id=f"C-{idx:04d}",
                source_attractor_id=c["source_attractor_id"],
                target_attractor_id=c["target_attractor_id"],
                scope=scope,
                constraint_type=ctype,
                constraint_strength=constraint_strength,
                local_constraint=local_constraint,
                global_constraint=global_constraint,
                hierarchical_level=level,
                hierarchy_weight=hierarchy_weight,
                distributed_support=distributed_support,
                persistence=persistence,
                dependency_strength=dependency_strength,
                conservation_score=conservation,
                propagation_potential=propagation_potential,
                emergence_confidence=emergence_confidence,
                derivation_rule="Gamma_field_density_intensity_gradient_diffusion_to_emergent_constraint",
            ))
        return constraints

    def _metrics(self, constraints: list[EmergentConstraint]) -> dict[str, Any]:
        strengths = [c.constraint_strength for c in constraints]
        return {
            "constraint_count": len(constraints),
            "local_constraint_count": sum(1 for c in constraints if c.scope == "local"),
            "global_constraint_count": sum(1 for c in constraints if c.scope == "global"),
            "hierarchical_constraint_count": sum(1 for c in constraints if c.scope == "hierarchical" or c.hierarchical_level >= 2),
            "distributed_constraint_count": sum(1 for c in constraints if c.scope == "distributed"),
            "persistent_constraint_count": sum(1 for c in constraints if c.persistence >= 0.55),
            "mean_constraint_strength": self._mean(strengths),
            "mean_local_constraint": self._mean([c.local_constraint for c in constraints]),
            "mean_global_constraint": self._mean([c.global_constraint for c in constraints]),
            "mean_distributed_support": self._mean([c.distributed_support for c in constraints]),
            "mean_persistence": self._mean([c.persistence for c in constraints]),
            "mean_dependency_strength": self._mean([c.dependency_strength for c in constraints]),
            "mean_propagation_potential": self._mean([c.propagation_potential for c in constraints]),
            "mean_emergence_confidence": self._mean([c.emergence_confidence for c in constraints]),
            "max_hierarchical_level": max([c.hierarchical_level for c in constraints], default=0),
        }

    def _status(self, constraints: list[EmergentConstraint], metrics: dict[str, Any]) -> str:
        if not constraints:
            return "CONSTRAINT_EMERGENCE_NOT_READY"
        if metrics.get("mean_constraint_strength", 0.0) >= 0.20 and metrics.get("mean_emergence_confidence", 0.0) >= 0.20:
            return "CONSTRAINT_EMERGENCE_READY"
        return "CONSTRAINT_EMERGENCE_PARTIAL"

    def _failure_conditions(self, gamma_field: list[Any], constraints: list[EmergentConstraint], metrics: dict[str, Any]) -> list[str]:
        failures: list[str] = []
        if not gamma_field:
            failures.append("empty_gamma_field")
        if not constraints:
            failures.append("no_emergent_constraints")
        if constraints and metrics.get("mean_constraint_strength", 0.0) <= 0.0:
            failures.append("zero_constraint_strength")
        if any(not (0.0 <= c.constraint_strength <= 1.0) for c in constraints):
            failures.append("unbounded_constraint_metric")
        return failures

    def _write_outputs(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"constraint_emergence_engine_{ts}.json"
        md_path = self.output_dir / f"constraint_emergence_engine_{ts}.md"
        prom_path = self.output_dir / f"constraint_emergence_engine_{ts}.prom"

        data = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(data, encoding="utf-8")
        self.latest_json_path.write_text(data, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

        metrics = result.get("metrics", {})
        md_lines = [
            "# Constraint Emergence Engine — AB5",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
            "",
            f"Status: {result.get('constraint_emergence_engine_status')}",
            f"Derived transition: Γ → C",
            f"Constraint count: {metrics.get('constraint_count', 0)}",
            f"Mean constraint strength: {metrics.get('mean_constraint_strength', 0.0):.6f}",
            f"Mean emergence confidence: {metrics.get('mean_emergence_confidence', 0.0):.6f}",
            "",
            "## Constraint families",
            "- emergent constraints",
            "- local constraints",
            "- global constraints",
            "- hierarchical constraints",
            "- distributed constraints",
            "- persistent constraints",
            "- dependencies",
            "- constraint conservation",
            "- propagation",
        ]
        md_text = "\n".join(md_lines) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        self.latest_markdown_path.write_text(md_text, encoding="utf-8")

        ready = 1 if result.get("constraint_emergence_engine_status") == "CONSTRAINT_EMERGENCE_READY" else 0
        prom_lines = [
            f"oce_ab5_constraint_emergence_ready {ready}",
            f"oce_ab5_ready {ready}",
            f"oce_ab5_constraint_count {metrics.get('constraint_count', 0)}",
            f"oce_ab5_emergent_constraints {metrics.get('constraint_count', 0)}",
            f"oce_ab5_mean_constraint_strength {metrics.get('mean_constraint_strength', 0.0)}",
            f"oce_ab5_mean_emergence_confidence {metrics.get('mean_emergence_confidence', 0.0)}",
            f"oce_ab5_mean_dependency_strength {metrics.get('mean_dependency_strength', 0.0)}",
            f"oce_ab5_mean_propagation_potential {metrics.get('mean_propagation_potential', 0.0)}",
            f"oce_ab5_persistent_constraint_count {metrics.get('persistent_constraint_count', 0)}",
        ]
        prom_text = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom_text, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom_text, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "latest_prometheus": str(self.latest_prometheus_path),
            "history": str(self.history_path),
        }


    def _constraint_public_dict(self, constraint: EmergentConstraint) -> dict[str, Any]:
        data = asdict(constraint)
        data["constraint_scope"] = constraint.scope
        data["constraint_persistence"] = constraint.persistence
        data["source"] = constraint.source_attractor_id
        data["target"] = constraint.target_attractor_id
        return data

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._normalize_payload(inputs)
        gamma_field = payload.get("gamma_field") or payload.get("gamma_field_points") or []
        if not isinstance(gamma_field, list):
            gamma_field = []
        constraints = self._derive_constraints(gamma_field)
        metrics = self._metrics(constraints)
        status = self._status(constraints, metrics)
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "module": "constraint_emergence_engine",
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "constraint_emergence_engine_status": status,
            "constraint_emergence_status": status,
            "gamma_to_constraints_demonstrated": status == "CONSTRAINT_EMERGENCE_READY",
            "gamma_to_c_demonstrated": status == "CONSTRAINT_EMERGENCE_READY",
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "no_consciousness_claim": True,
                "no_subjectivity_claim": True,
                "no_qualia_claim": True,
            },
            "dependency_audit": {
                "incoming": ["gamma_field_engine", "mutual_conservation_matrix", "constraint_fields", "constraint_genesis", "dynamics_of_constraints"],
                "outgoing": ["constraint_failure_analyzer"],
                "role": "AB5 derives emergent constraints from Γ; it does not rebuild Γ and does not validate the full AB chain.",
            },
            "non_redundancy_analysis": {
                "nearby_modules": ["constraint_genesis", "constraint_fields", "constraint_fields_utils", "constraint_fields_diagnostics", "constraint_induced_domain", "dynamics_of_constraints", "emergence_detection_engine"],
                "distinction": "Existing modules cover generic constraints or diagnostics; AB5 uniquely derives C from the AB4 Gamma field in the Δ→R→G→A→Γ→C reconstruction.",
            },
            "emergent_constraints": [self._constraint_public_dict(c) for c in constraints],
            "constraints": [self._constraint_public_dict(c) for c in constraints],
            "local_constraints": [self._constraint_public_dict(c) for c in constraints if c.scope == "local"],
            "global_constraints": [self._constraint_public_dict(c) for c in constraints if c.scope == "global"],
            "hierarchical_constraints": [self._constraint_public_dict(c) for c in constraints if c.scope == "hierarchical" or c.hierarchical_level >= 2],
            "distributed_constraints": [self._constraint_public_dict(c) for c in constraints if c.scope == "distributed"],
            "persistent_constraints": [self._constraint_public_dict(c) for c in constraints if c.persistence >= 0.55],
            "dependency_map": {c.constraint_id: {"source_attractor_id": c.source_attractor_id, "target_attractor_id": c.target_attractor_id, "dependency_strength": c.dependency_strength} for c in constraints},
            "constraint_conservation_map": {c.constraint_id: c.conservation_score for c in constraints},
            "propagation_map": {c.constraint_id: c.propagation_potential for c in constraints},
            "metrics": metrics,
            "failure_conditions": self._failure_conditions(gamma_field, constraints, metrics),
            "validation_criteria": {
                "gamma_field_present": bool(gamma_field),
                "constraints_non_empty": bool(constraints),
                "bounded_constraint_metrics": all(0.0 <= c.constraint_strength <= 1.0 for c in constraints),
                "functional_only": True,
            },
            "falsification_criteria": [
                "empty_gamma_field",
                "no_emergent_constraints",
                "unbounded_constraint_metric",
                "constraint_emergence_without_gamma",
                "phenomenological_claim_inside_AB5",
            ],
        }
        if persist:
            result["paths"] = self._write_outputs(result)
        return result
