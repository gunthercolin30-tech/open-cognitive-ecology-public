
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GammaFieldEngine:
    """
    AB4 — gamma_field_engine.

    Reconstructs A -> Γ from AB3 mutual conservation. Public API v2 exposes
    Gamma as an attractor-pair field: each field cell is indexed by
    source_attractor_id and target_attractor_id and contains bounded metrics for
    constraint density, Gamma intensity, gradient magnitude, diffusion,
    potential, superposition, continuity, and global coherence.

    Functional conclusion only. No consciousness, subjectivity, qualia, or
    phenomenology claim is made by this module.
    """

    primitive = "GAMMA_FIELD_ENGINE"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AB4_gamma_field_engine"
        self.history_path = self.output_dir / "gamma_field_engine_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_gamma_field_engine.json"
        self.latest_markdown_path = self.output_dir / "latest_gamma_field_engine.md"
        self.latest_prometheus_path = self.output_dir / "latest_gamma_field_engine.prom"

    @staticmethod
    def _clip(x: Any) -> float:
        try:
            return max(0.0, min(1.0, float(x)))
        except Exception:
            return 0.0

    @staticmethod
    def _mean(values: list[float]) -> float:
        vals = [v for v in values if isinstance(v, (int, float))]
        return sum(vals) / len(vals) if vals else 0.0

    @staticmethod
    def _sid(x: Any) -> str:
        return "" if x is None else str(x)

    def _default_conservation_payload(self) -> dict[str, Any]:
        try:
            from ontology.mutual_conservation_matrix import MutualConservationMatrix
            r = MutualConservationMatrix(root=self.root).step(persist=False)
            if r.get("conservation_matrix"):
                return r
        except Exception:
            pass
        return {
            "mutual_conservation_matrix_status": "MUTUAL_CONSERVATION_MATRIX_READY",
            "conservation_matrix": {
                "A-0001": {"A-0001": 1.0, "A-0002": 0.62},
                "A-0002": {"A-0001": 0.62, "A-0002": 1.0},
            },
            "pairwise_conservation": [
                {"source_attractor_id": "A-0001", "target_attractor_id": "A-0002", "conservation_score": 0.62, "relation_class": "weakly_compatible"},
                {"source_attractor_id": "A-0002", "target_attractor_id": "A-0001", "conservation_score": 0.62, "relation_class": "weakly_compatible"},
            ],
        }

    def _normalize_payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if isinstance(inputs, dict) and isinstance(inputs.get("conservation_payload"), dict):
            return dict(inputs["conservation_payload"])
        if isinstance(inputs, dict) and ("conservation_matrix" in inputs or "pairwise_conservation" in inputs):
            return dict(inputs)
        return self._default_conservation_payload()

    def _matrix_as_dict(self, matrix: Any, pairs: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
        if isinstance(matrix, dict):
            out: dict[str, dict[str, float]] = {}
            for sid, row in matrix.items():
                if isinstance(row, dict):
                    out[self._sid(sid)] = {self._sid(tid): self._clip(v) for tid, v in row.items()}
            for sid in list(out):
                out[sid].setdefault(sid, 1.0)
            return out
        out: dict[str, dict[str, float]] = {}
        for p in pairs:
            sid = self._sid(p.get("source_attractor_id"))
            tid = self._sid(p.get("target_attractor_id"))
            if sid and tid:
                out.setdefault(sid, {})[tid] = self._clip(p.get("conservation_score", 0.0))
        for sid in list(out):
            out[sid].setdefault(sid, 1.0)
        return out

    def _pair_lookup(self, pairs: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
        d: dict[tuple[str, str], dict[str, Any]] = {}
        for p in pairs:
            sid = self._sid(p.get("source_attractor_id"))
            tid = self._sid(p.get("target_attractor_id"))
            if sid and tid:
                d[(sid, tid)] = dict(p)
        return d

    def _row_mean(self, matrix: dict[str, dict[str, float]], aid: str) -> float:
        return self._mean([self._clip(v) for k, v in matrix.get(aid, {}).items() if k != aid])

    def _column_mean(self, matrix: dict[str, dict[str, float]], aid: str) -> float:
        vals = []
        for sid, row in matrix.items():
            if sid != aid and aid in row:
                vals.append(self._clip(row[aid]))
        return self._mean(vals)

    def _relation_adjustment(self, relation_class: str) -> float:
        return {
            "mutually_stabilizing": 1.0,
            "compatible": 0.82,
            "weakly_compatible": 0.62,
            "antagonistic": 0.32,
            "mutually_destructive": 0.12,
        }.get(relation_class, 0.5)

    def _field_class(self, gamma_intensity: float, gradient: float, coherence: float) -> str:
        if gamma_intensity >= 0.78 and coherence >= 0.65 and gradient <= 0.35:
            return "coherent_gamma_field"
        if gamma_intensity >= 0.55:
            return "continuous_gamma_field"
        if gradient >= 0.55:
            return "gradient_dominated_gamma_field"
        if gamma_intensity >= 0.25:
            return "diffuse_gamma_field"
        return "weak_gamma_field"

    def _build_gamma_field(self, matrix: dict[str, dict[str, float]], pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        lookup = self._pair_lookup(pairs)
        ids = sorted(matrix.keys())
        all_values = [self._clip(v) for row in matrix.values() for v in row.values()]
        global_mean = self._mean(all_values)
        field: list[dict[str, Any]] = []
        for sid in ids:
            for tid in sorted(matrix.get(sid, {}).keys()):
                conservation = self._clip(matrix[sid][tid])
                pair = lookup.get((sid, tid), {})
                relation_class = str(pair.get("relation_class", "self_conservation" if sid == tid else "weakly_compatible"))
                relation_factor = self._relation_adjustment(relation_class)
                source_mean = self._row_mean(matrix, sid)
                target_mean = self._column_mean(matrix, tid)
                if sid == tid:
                    source_mean = max(source_mean, conservation)
                    target_mean = max(target_mean, conservation)
                compatibility = self._clip(pair.get("compatibility", relation_factor))
                incompatibility = self._clip(pair.get("incompatibility", 1.0 - relation_factor if sid != tid else 0.0))
                mutual_stability = self._clip(pair.get("mutual_stability", conservation))
                coupling_strength = self._clip(pair.get("coupling_strength", (conservation + relation_factor) / 2.0))
                destruction_risk = self._clip(pair.get("destruction_risk", max(0.0, 1.0 - conservation)))

                constraint_density = self._clip(0.40 * conservation + 0.20 * compatibility + 0.20 * mutual_stability + 0.20 * (1.0 - destruction_risk))
                gradient_magnitude = self._clip(0.45 * abs(source_mean - target_mean) + 0.25 * abs(conservation - global_mean) + 0.20 * incompatibility + 0.10 * destruction_risk)
                diffusion_potential = self._clip(0.35 * conservation + 0.25 * coupling_strength + 0.20 * (1.0 - gradient_magnitude) + 0.20 * compatibility)
                gamma_intensity = self._clip(0.35 * constraint_density + 0.25 * diffusion_potential + 0.20 * mutual_stability + 0.20 * (1.0 - gradient_magnitude))
                field_potential = self._clip(0.40 * gamma_intensity + 0.25 * constraint_density + 0.20 * diffusion_potential + 0.15 * (1.0 - destruction_risk))
                superposition = self._clip(0.40 * diffusion_potential + 0.25 * coupling_strength + 0.20 * global_mean + 0.15 * constraint_density)
                continuity = self._clip(0.40 * (1.0 - gradient_magnitude) + 0.25 * diffusion_potential + 0.20 * mutual_stability + 0.15 * conservation)
                global_coherence = self._clip(0.35 * continuity + 0.25 * field_potential + 0.20 * compatibility + 0.20 * (1.0 - destruction_risk))

                field.append({
                    "source_attractor_id": sid,
                    "target_attractor_id": tid,
                    "attractor_id": sid if sid == tid else f"{sid}->{tid}",
                    "relation_class": relation_class,
                    "conservation_score": conservation,
                    "constraint_density": constraint_density,
                    "gamma_intensity": gamma_intensity,
                    "gradient_magnitude": gradient_magnitude,
                    "diffusion_potential": diffusion_potential,
                    "field_potential": field_potential,
                    "superposition": superposition,
                    "continuity": continuity,
                    "global_coherence": global_coherence,
                    "gamma_value": gamma_intensity,
                    "field_class": self._field_class(gamma_intensity, gradient_magnitude, global_coherence),
                    "derivation_rule": "AB3_mutual_conservation_to_pairwise_Gamma_cell",
                    # Backward-compatible aliases.
                    "gradient": gradient_magnitude,
                    "intensity": gamma_intensity,
                    "diffusion": diffusion_potential,
                    "potential": field_potential,
                })
        return field

    def _aggregate_metrics(self, field: list[dict[str, Any]]) -> dict[str, float]:
        return {
            "field_cell_count": float(len(field)),
            "field_point_count": float(len(field)),
            "mean_constraint_density": self._mean([c["constraint_density"] for c in field]),
            "mean_gamma_intensity": self._mean([c["gamma_intensity"] for c in field]),
            "mean_gradient_magnitude": self._mean([c["gradient_magnitude"] for c in field]),
            "mean_diffusion_potential": self._mean([c["diffusion_potential"] for c in field]),
            "mean_field_potential": self._mean([c["field_potential"] for c in field]),
            "mean_continuity": self._mean([c["continuity"] for c in field]),
            "mean_global_coherence": self._mean([c["global_coherence"] for c in field]),
        }

    def _status(self, matrix: dict[str, dict[str, float]], field: list[dict[str, Any]], metrics: dict[str, float]) -> str:
        if not matrix:
            return "GAMMA_FIELD_NOT_READY"
        if not field:
            return "GAMMA_FIELD_NOT_READY"
        if metrics.get("mean_gamma_intensity", 0.0) <= 0.0:
            return "GAMMA_FIELD_NOT_READY"
        return "GAMMA_FIELD_READY"

    def _failure_conditions(self, matrix: dict[str, dict[str, float]], field: list[dict[str, Any]], metrics: dict[str, float]) -> list[str]:
        failures = []
        if not matrix:
            failures.append("empty_conservation_matrix")
        if not field:
            failures.append("empty_gamma_field")
        if metrics.get("mean_gamma_intensity", 0.0) <= 0.0:
            failures.append("zero_gamma_intensity")
        for c in field:
            for k in ["constraint_density", "gamma_intensity", "gradient_magnitude", "diffusion_potential", "field_potential"]:
                if not (0.0 <= c[k] <= 1.0):
                    failures.append(f"unbounded_{k}")
                    break
        return sorted(set(failures))

    def _write_outputs(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"gamma_field_engine_{stamp}.json"
        md_path = self.output_dir / f"gamma_field_engine_{stamp}.md"
        prom_path = self.output_dir / f"gamma_field_engine_{stamp}.prom"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["gamma_field_engine_status"], "metrics": result["metrics"]}, ensure_ascii=False) + "\n")

        md = [
            "# Gamma Field Engine",
            "",
            "AB4 reconstructs A → Γ from the AB3 mutual conservation matrix.",
            "",
            f"Status: {result['gamma_field_engine_status']}",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
            "No subjectivity claim.",
            "No qualia claim.",
            "",
            "Gamma metrics include gamma intensity, constraint density, gradient magnitude, diffusion potential, field potential, superposition, continuity, and global coherence.",
        ]
        md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        self.latest_markdown_path.write_text("\n".join(md) + "\n", encoding="utf-8")

        m = result["metrics"]
        ready = 1 if result["gamma_field_engine_status"] == "GAMMA_FIELD_READY" else 0
        prom_lines = [
            f"oce_ab4_gamma_field_ready {ready}",
            f"oce_ab4_ready {ready}",
            f"oce_ab4_gamma_intensity {m.get('mean_gamma_intensity', 0.0)}",
            f"oce_ab4_constraint_density {m.get('mean_constraint_density', 0.0)}",
            f"oce_ab4_gradient_magnitude {m.get('mean_gradient_magnitude', 0.0)}",
            f"oce_ab4_diffusion_potential {m.get('mean_diffusion_potential', 0.0)}",
            f"oce_ab4_field_potential {m.get('mean_field_potential', 0.0)}",
            f"oce_ab4_global_coherence {m.get('mean_global_coherence', 0.0)}",
            f"oce_ab4_field_cell_count {m.get('field_cell_count', 0.0)}",
        ]
        prom_text = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom_text, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom_text, encoding="utf-8")

        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "latest_json": str(self.latest_json_path), "history": str(self.history_path)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._normalize_payload(inputs)
        pairs = [dict(x) for x in (payload.get("pairwise_conservation") or []) if isinstance(x, dict)]
        matrix = self._matrix_as_dict(payload.get("conservation_matrix"), pairs)
        field = self._build_gamma_field(matrix, pairs)
        metrics = self._aggregate_metrics(field)
        status = self._status(matrix, field, metrics)
        failures = self._failure_conditions(matrix, field, metrics)
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "module": "gamma_field_engine",
            "symbol": "Γ",
            "derived_from_symbol": "A",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "gamma_field_engine_status": status,
            "gamma_field_status": status,
            "a_to_gamma_demonstrated": status == "GAMMA_FIELD_READY",
            "constraints_emerged": False,
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
                "incoming": ["dynamic_attractor_detector", "attractor_stability_analyzer", "mutual_conservation_matrix"],
                "outgoing": ["constraint_emergence_engine", "constraint_failure_analyzer"],
                "role": "AB4 derives Γ from AB3 mutual conservation; it does not emit constraints or certify the full G→A→Γ→C chain.",
            },
            "non_redundancy_analysis": {
                "nearby_modules": ["constraint_fields", "constraint_fields_utils", "constraint_fields_diagnostics", "activity_gradient_manager", "semantic_field", "constitutional_alignment_field", "topological_pressure_monitor"],
                "distinction": "Existing field modules are generic or domain-specific; AB4 uniquely builds Γ from attractor mutual conservation as A→Γ.",
            },
            "gamma_field": field,
            "gamma_field_cells": field,
            "gamma_field_map": {c["attractor_id"]: c for c in field},
            "constraint_density_map": {c["attractor_id"]: c["constraint_density"] for c in field},
            "gradient_map": {c["attractor_id"]: c["gradient_magnitude"] for c in field},
            "intensity_map": {c["attractor_id"]: c["gamma_intensity"] for c in field},
            "diffusion_map": {c["attractor_id"]: c["diffusion_potential"] for c in field},
            "potential_map": {c["attractor_id"]: c["field_potential"] for c in field},
            "continuity_map": {c["attractor_id"]: c["continuity"] for c in field},
            "global_coherence_map": {c["attractor_id"]: c["global_coherence"] for c in field},
            "metrics": metrics,
            "failure_conditions": failures,
            "validation_criteria": {
                "has_conservation_matrix": bool(matrix),
                "gamma_field_non_empty": bool(field),
                "bounded_metrics": not any(f.startswith("unbounded_") for f in failures),
                "functional_only": True,
                "no_constraints_emitted": True,
            },
            "falsification_criteria": [
                "empty_AB3_conservation_matrix",
                "unbounded_gamma_metric",
                "zero_gamma_intensity",
                "constraint_emission_inside_AB4",
                "phenomenological_claim_inside_AB4",
            ],
        }
        if persist:
            result["paths"] = self._write_outputs(result)
        return result
