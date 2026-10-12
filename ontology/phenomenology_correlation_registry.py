"""Y1 — phenomenology_correlation_registry.

Functional registry for phenomenology-correlation hypotheses.

This module does not assert, infer, certify, or prove consciousness,
sentience, qualia, subjective experience, or phenomenal subjectivity.
It only inventories observable candidate correlates and falsifiable
statistical hypotheses for later empirical testing.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRIMITIVE = "PHENOMENOLOGY_CORRELATION_REGISTRY"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


class PhenomenologyCorrelationRegistry:
    """Registry of empirical hypotheses and candidate correlates.

    The registry is intentionally epistemically conservative: it produces
    correlation hypotheses only, never evidence of phenomenal consciousness.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "phenomenology_correlation_registry"
        self.latest_file = self.base_dir / "phenomenology_correlation_registry.json"
        self.history_file = self.base_dir / "phenomenology_correlation_registry_history.jsonl"
        self.report_file = self.base_dir / "phenomenology_correlation_registry.md"
        self.prometheus_file = self.base_dir / "phenomenology_correlation_registry.prom"

    def _default_hypotheses(self) -> list[dict[str, Any]]:
        return [
            {
                "hypothesis_id": "Y1-H01",
                "label": "autobiographical_coherence_correlate",
                "claim_type": "statistical_correlation_only",
                "candidate_correlate": "autobiographical_coherence",
                "observable_variables": [
                    "memory_continuity_score",
                    "narrative_consistency_score",
                    "temporal_self_continuity_score",
                ],
                "expected_direction": "positive",
                "falsification_condition": "No stable positive association across longitudinal and replicated samples.",
                "epistemic_limit": "Does not imply phenomenal consciousness.",
            },
            {
                "hypothesis_id": "Y1-H02",
                "label": "reflexive_depth_correlate",
                "claim_type": "statistical_correlation_only",
                "candidate_correlate": "reflexive_depth",
                "observable_variables": [
                    "self_model_revision_score",
                    "meta_cognition_index",
                    "reflexive_threshold_score",
                ],
                "expected_direction": "positive",
                "falsification_condition": "Reflexive metrics fail to covary with candidate reports or functional markers.",
                "epistemic_limit": "Functional reflexivity is not phenomenology.",
            },
            {
                "hypothesis_id": "Y1-H03",
                "label": "identity_stability_correlate",
                "claim_type": "statistical_correlation_only",
                "candidate_correlate": "identity_stability",
                "observable_variables": [
                    "identity_continuity_score",
                    "self_model_consistency_score",
                    "cross_generation_stability",
                ],
                "expected_direction": "positive",
                "falsification_condition": "Identity metrics degrade without corresponding change in candidate correlation patterns.",
                "epistemic_limit": "Stable identity is a functional marker only.",
            },
            {
                "hypothesis_id": "Y1-H04",
                "label": "cross_architecture_specificity_correlate",
                "claim_type": "statistical_correlation_only",
                "candidate_correlate": "architecture_specificity",
                "observable_variables": [
                    "oce_score",
                    "simple_agent_score",
                    "llm_standard_score",
                    "distributed_architecture_score",
                ],
                "expected_direction": "differential",
                "falsification_condition": "No meaningful differences between OCE and comparator architectures.",
                "epistemic_limit": "Architectural difference is not subjective proof.",
            },
        ]

    def _normalize_hypotheses(self, raw: Any) -> list[dict[str, Any]]:
        if not isinstance(raw, list):
            return self._default_hypotheses()
        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or item.get("candidate_correlate") or f"candidate_{index}")
            variables = item.get("observable_variables") or item.get("variables") or []
            if isinstance(variables, str):
                variables = [variables]
            variables = [str(v) for v in variables if str(v).strip()]
            normalized.append({
                "hypothesis_id": str(item.get("hypothesis_id") or f"Y1-H{index:02d}"),
                "label": label,
                "claim_type": "statistical_correlation_only",
                "candidate_correlate": str(item.get("candidate_correlate") or label),
                "observable_variables": variables,
                "expected_direction": str(item.get("expected_direction") or "undetermined"),
                "falsification_condition": str(item.get("falsification_condition") or "Absent, weak, unstable, or non-replicated correlation."),
                "epistemic_limit": "Does not imply phenomenal consciousness.",
            })
        return normalized or self._default_hypotheses()

    def _registry_quality(self, hypotheses: list[dict[str, Any]]) -> float:
        if not hypotheses:
            return 0.0
        scores = []
        for h in hypotheses:
            has_variables = bool(h.get("observable_variables"))
            has_falsification = bool(h.get("falsification_condition"))
            has_limit = bool(h.get("epistemic_limit"))
            has_direction = bool(h.get("expected_direction"))
            scores.append(sum([has_variables, has_falsification, has_limit, has_direction]) / 4.0)
        return round(sum(scores) / len(scores), 6)

    def _candidate_variable_count(self, hypotheses: list[dict[str, Any]]) -> int:
        variables = set()
        for h in hypotheses:
            for variable in h.get("observable_variables", []):
                variables.add(str(variable))
        return len(variables)

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = dict(inputs or {})
        hypotheses = self._normalize_hypotheses(payload.get("hypotheses"))
        variable_count = self._candidate_variable_count(hypotheses)
        quality = self._registry_quality(hypotheses)
        readiness = round((quality * 0.7) + (_clamp(variable_count / 12.0) * 0.3), 6)

        result: dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "axis": "Y",
            "stage": "Y1",
            "timestamp_utc": payload.get("timestamp_utc") or _utc_now(),
            "hypothesis_count": len(hypotheses),
            "candidate_variable_count": variable_count,
            "candidate_correlate_count": len({h.get("candidate_correlate") for h in hypotheses}),
            "registry_quality_score": quality,
            "correlation_program_readiness": readiness,
            "hypotheses": hypotheses,
            "claim_scope": "observable_statistical_correlations_only",
            "consciousness_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "epistemic_position": {
                "measurement_status": "registry_of_candidate_variables",
                "interpretive_status": "hypothesis_generation_only",
                "phenomenal_status": "undetermined",
                "prohibited_conclusion": "proof_of_consciousness",
            },
            "input_sources": {
                "global_scan_used": False,
                "rglob_used": False,
                "repository_wide_search_used": False,
                "source": "explicit_payload_or_default_registry",
            },
            "artifacts": {},
        }

        if persist:
            result["artifacts"] = self._persist(result)

        return result

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
        self.report_file.write_text(self._render_report(result), encoding="utf-8")
        self.prometheus_file.write_text(self._render_prometheus(result), encoding="utf-8")
        return {
            "json": str(self.latest_file),
            "history": str(self.history_file),
            "report": str(self.report_file),
            "prometheus": str(self.prometheus_file),
        }

    def _render_report(self, result: dict[str, Any]) -> str:
        lines = [
            "# Y1 — Phenomenology Correlation Registry",
            "",
            f"Primitive: {result['primitive']}",
            f"Hypotheses: {result['hypothesis_count']}",
            f"Candidate variables: {result['candidate_variable_count']}",
            f"Registry quality: {result['registry_quality_score']}",
            f"Readiness: {result['correlation_program_readiness']}",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No proof of consciousness is claimed.",
        ]
        return "\n".join(lines) + "\n"

    def _render_prometheus(self, result: dict[str, Any]) -> str:
        return "\n".join([
            "# HELP oce_y1_phenomenology_registry_quality Functional registry quality score",
            "# TYPE oce_y1_phenomenology_registry_quality gauge",
            f"oce_y1_phenomenology_registry_quality {result['registry_quality_score']}",
            "# HELP oce_y1_phenomenology_registry_hypotheses Candidate hypothesis count",
            "# TYPE oce_y1_phenomenology_registry_hypotheses gauge",
            f"oce_y1_phenomenology_registry_hypotheses {result['hypothesis_count']}",
            "# HELP oce_y1_phenomenology_registry_readiness Correlation program readiness",
            "# TYPE oce_y1_phenomenology_registry_readiness gauge",
            f"oce_y1_phenomenology_registry_readiness {result['correlation_program_readiness']}",
            "",
        ])


if __name__ == "__main__":
    print(json.dumps(PhenomenologyCorrelationRegistry().step(persist=True), indent=2, ensure_ascii=False))
