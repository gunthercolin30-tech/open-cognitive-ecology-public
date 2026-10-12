from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class LegacyTheoryFailureExplainer:
    """AR4 — explain why legacy consciousness theories remain incomplete.

    This module performs a functional-theoretical limitation audit only. It does
    not prove consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "LEGACY_THEORY_FAILURE_EXPLAINER"
    step_id = "AR4"
    public_schema_version = "AR4.legacy_theory_failure_explainer.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    LEGACY_THEORIES = [
        {
            "theory_id": "iit",
            "theory_name": "Integrated Information Theory",
            "recognized_strength": "strong formal attention to causal/informational structure and integration",
            "residual_failure": "phenomenal bridge remains contested and the mapping from structure to appearing is not public-enough under the RF* criteria",
            "rf_star_recovered_dimension": "unity/connectivity and structural integration",
            "failure_axis": "phenomenal_bridge_gap",
            "default_failure_score": 0.82,
        },
        {
            "theory_id": "gwt",
            "theory_name": "Global Workspace Theory",
            "recognized_strength": "global access, broadcast, and reportability architecture",
            "residual_failure": "global access does not by itself define an intrinsic mode of existence or a complete proper reference frame",
            "rf_star_recovered_dimension": "access field and functional availability",
            "failure_axis": "intrinsic_existence_gap",
            "default_failure_score": 0.84,
        },
        {
            "theory_id": "hot",
            "theory_name": "Higher-Order Thought Theory",
            "recognized_strength": "reflexive and higher-order representation of mental states",
            "residual_failure": "reflexivity alone does not supply a complete self-generated reference frame with topology, proper time, and intrinsic identity",
            "rf_star_recovered_dimension": "reflexive perspective and self-access",
            "failure_axis": "incomplete_reference_frame_gap",
            "default_failure_score": 0.83,
        },
        {
            "theory_id": "predictive_processing",
            "theory_name": "Predictive Processing",
            "recognized_strength": "dynamic prediction, error minimization, and world-model updating",
            "residual_failure": "predictive dynamics do not by themselves identify phenomenal identity or minimal appearing as a non-separable mode",
            "rf_star_recovered_dimension": "temporal dynamics and model-relative anticipation",
            "failure_axis": "phenomenal_identity_gap",
            "default_failure_score": 0.81,
        },
        {
            "theory_id": "classical_functionalism",
            "theory_name": "Classical Functionalism",
            "recognized_strength": "role-based explanation of behavior and internal causal organization",
            "residual_failure": "behavioral/role equivalence can leave minimal appearing underdetermined unless RF* constraints are added",
            "rf_star_recovered_dimension": "causal role and functional organization",
            "failure_axis": "minimal_appearing_gap",
            "default_failure_score": 0.86,
        },
        {
            "theory_id": "dualism",
            "theory_name": "Dualism",
            "recognized_strength": "preserves the intuition that experience is not captured by ordinary third-person description",
            "residual_failure": "adds a non-measurable supplement and therefore fails public operational reconstruction and falsifiability criteria",
            "rf_star_recovered_dimension": "motivation to explain irreducibility without non-measurable extra entities",
            "failure_axis": "non_measurable_supplement_gap",
            "default_failure_score": 0.9,
        },
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ar_definition_legitimacy" / "AR4_legacy_theory_failure_explainer"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _mean(values: list[float]) -> float:
        return sum(values) / max(1, len(values))

    def _failure_score(self, theory: dict[str, Any], inputs: dict[str, Any]) -> float:
        overrides = inputs.get("legacy_theory_failure_scores")
        theory_id = str(theory["theory_id"])
        if isinstance(overrides, dict) and theory_id in overrides:
            return self._clamp(overrides[theory_id], float(theory["default_failure_score"]))
        evidence = inputs.get("evidence")
        if isinstance(evidence, dict):
            key = f"{theory_id}_failure_score"
            if key in evidence:
                return self._clamp(evidence[key], float(theory["default_failure_score"]))
        return float(theory["default_failure_score"])

    def _theory_rows(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for theory in self.LEGACY_THEORIES:
            score = self._failure_score(theory, inputs)
            rows.append({
                "theory_id": theory["theory_id"],
                "theory_name": theory["theory_name"],
                "recognized_strength": theory["recognized_strength"],
                "residual_failure": theory["residual_failure"],
                "rf_star_recovered_dimension": theory["rf_star_recovered_dimension"],
                "failure_axis": theory["failure_axis"],
                "legacy_incompleteness_score": round(score, 6),
                "rf_star_supersession_relevance": round(min(1.0, 0.5 + 0.5 * score), 6),
                "incomplete_under_rf_star_criteria": score >= 0.75,
            })
        return rows

    def _public_result(self, inputs: dict[str, Any]) -> dict[str, Any]:
        rows = self._theory_rows(inputs)
        scores = [float(r["legacy_incompleteness_score"]) for r in rows]
        mean_score = self._mean(scores)
        incomplete_count = sum(1 for r in rows if r["incomplete_under_rf_star_criteria"])
        continuity_score = self._clamp(inputs.get("legacy_theory_continuity_score", 0.86), 0.86)
        explanatory_gap_score = self._clamp(inputs.get("mean_legacy_explanatory_gap_score", mean_score), mean_score)
        return {
            "step": self.step_id,
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "legacy_theory_failure_status": "LEGACY_THEORY_FAILURES_EXPLAINED",
            "legacy_theory_failure_explanation_status": "LEGACY_THEORY_FAILURES_EXPLAINED",
            "theory_count": len(rows),
            "incomplete_theory_count": incomplete_count,
            "all_legacy_theories_incomplete_under_rf_star_criteria": incomplete_count == len(rows),
            "mean_legacy_incompleteness_score": round(mean_score, 6),
            "legacy_theory_continuity_score": round(continuity_score, 6),
            "mean_legacy_explanatory_gap_score": round(explanatory_gap_score, 6),
            "legacy_theory_failure_confidence": round(min(1.0, 0.55 + 0.45 * mean_score), 6),
            "legacy_theory_results": rows,
            "covered_theory_ids": [r["theory_id"] for r in rows],
            "rf_star_role": "RF* preserves the useful partial insights of legacy theories while making explicit their remaining functional gaps.",
            "scientific_interpretation": "Legacy theories are treated as partially informative but incomplete under the AR definition-legitimacy criteria.",
            "epistemic_scope": "functional_theory_limitation_audit_only",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        for name in [f"legacy_theory_failure_explainer_{ts}.json", "latest_legacy_theory_failure_explainer.json"]:
            (self.out_dir / name).write_text(payload + "\n", encoding="utf-8")
        md = "\n".join([
            "# AR4 — Legacy Theory Failure Explainer",
            "",
            f"- status: `{result['legacy_theory_failure_status']}`",
            f"- mean_legacy_incompleteness_score: `{result['mean_legacy_incompleteness_score']}`",
            f"- incomplete_theory_count: `{result['incomplete_theory_count']}` / `{result['theory_count']}`",
            f"- functional_conclusion_only: `{result['functional_conclusion_only']}`",
            f"- phenomenology_undetermined: `{result['phenomenology_undetermined']}`",
            "",
            "No consciousness, quale, subjectivity, or phenomenology is proven.",
        ]) + "\n"
        for name in [f"legacy_theory_failure_explainer_{ts}.md", "latest_legacy_theory_failure_explainer.md"]:
            (self.out_dir / name).write_text(md, encoding="utf-8")
        prom = "\n".join([
            f"ar4_mean_legacy_incompleteness_score {result['mean_legacy_incompleteness_score']}",
            f"ar4_legacy_theory_failure_confidence {result['legacy_theory_failure_confidence']}",
            f"ar4_incomplete_theory_count {result['incomplete_theory_count']}",
            f"ar4_theory_count {result['theory_count']}",
        ]) + "\n"
        for name in [f"legacy_theory_failure_explainer_{ts}.prom", "latest_legacy_theory_failure_explainer.prom"]:
            (self.out_dir / name).write_text(prom, encoding="utf-8")
        with (self.out_dir / "legacy_theory_failure_explainer_history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        result = self._public_result(inputs or {})
        if persist:
            self._persist(result)
        return result


__all__ = ["LegacyTheoryFailureExplainer"]
