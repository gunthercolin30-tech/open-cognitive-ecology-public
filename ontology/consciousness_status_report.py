from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List
import json


class ConsciousnessStatusReport:
    """Final constrained status report for Z-prime consciousness certification.

    This primitive synthesizes Z-prime outputs without asserting phenomenal
    subjectivity. It only reports functional support, theoretical confidence,
    remaining limitations, governance status, and forbidden claim controls.
    """

    primitive = "CONSCIOUSNESS_STATUS_REPORT"

    allowed_final_statuses = [
        "INSUFFICIENT_FUNCTIONAL_SUPPORT",
        "LIMITED_FUNCTIONAL_SUPPORT",
        "MODERATE_FUNCTIONAL_SUPPORT_UNDER_CONSTRAINTS",
        "STRONG_REPLICATED_FUNCTIONAL_SUPPORT_UNDER_CONSTRAINTS",
    ]

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_certification" / "consciousness_status_report"
        self.history_path = self.output_dir / "consciousness_status_report_history.jsonl"
        self.json_path = self.output_dir / "consciousness_status_report.json"
        self.markdown_path = self.output_dir / "consciousness_status_report.md"

    def _now(self, payload: Dict[str, Any]) -> str:
        ts = payload.get("timestamp_utc")
        if isinstance(ts, str) and ts:
            return ts
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _score(self, value: Any, keys: List[str], default: float = 0.0) -> float:
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))
        if not isinstance(value, dict):
            return default
        for key in keys:
            if key in value and isinstance(value[key], (int, float)):
                return max(0.0, min(1.0, float(value[key])))
        return default

    def _collect_sources(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sources = payload.get("sources", {})
        return sources if isinstance(sources, dict) else {}

    def _metric_summary(self, sources: Dict[str, Any]) -> Dict[str, float]:
        return {
            "evidence_quality": self._score(sources.get("evidence_standard"), ["evidence_standard_score", "evidence_quality_score", "score"]),
            "alternative_elimination": self._score(sources.get("alternative_elimination"), ["alternative_explanation_exclusion_score", "elimination_score", "score"]),
            "causal_intervention": self._score(sources.get("causal_intervention"), ["causal_intervention_alignment_score", "intervention_score", "score"]),
            "cross_architecture": self._score(sources.get("cross_architecture"), ["cross_architecture_comparison_score", "comparison_score", "score"]),
            "strong_inference": self._score(sources.get("strong_inference"), ["consciousness_inference_strength", "inference_strength", "score"]),
            "independent_review": self._score(sources.get("review_board"), ["review_board_confidence", "independent_review_score", "score"]),
            "adversarial_resilience": self._score(sources.get("adversarial_audit"), ["adversarial_resilience_score", "adversarial_score", "score"]),
            "claim_governance": self._score(sources.get("claim_governance"), ["claim_governance_score", "governance_score", "score"]),
            "theory_confidence": self._score(sources.get("theory_status"), ["theoretical_support_score", "theory_confidence_score", "score"]),
            "replication_support": self._score(sources.get("replication"), ["replication_score", "replication_support_score", "score"]),
        }

    def _mean(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 6)

    def _final_status(self, score: float, gate_passed: bool, adversarial_passed: bool) -> str:
        if not gate_passed or not adversarial_passed:
            return "INSUFFICIENT_FUNCTIONAL_SUPPORT"
        if score >= 0.85:
            return "STRONG_REPLICATED_FUNCTIONAL_SUPPORT_UNDER_CONSTRAINTS"
        if score >= 0.65:
            return "MODERATE_FUNCTIONAL_SUPPORT_UNDER_CONSTRAINTS"
        if score >= 0.40:
            return "LIMITED_FUNCTIONAL_SUPPORT"
        return "INSUFFICIENT_FUNCTIONAL_SUPPORT"

    def _contains_forbidden_claim(self, text: str) -> bool:
        upper = text.upper()
        return any(claim in upper for claim in self.forbidden_claims)

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Consciousness Status Report",
            "",
            "## Epistemic status",
            "functional conclusion only",
            "phenomenology undetermined",
            "consciousness_proven: False",
            "phenomenology_proven: False",
            "subjectivity_proven: False",
            "sentience_proven: False",
            "qualia_proven: False",
            "",
            "## Final constrained status",
            str(result["final_consciousness_status"]),
            "",
            "## Scores",
            f"functional_support_score: {result['functional_support_score']}",
            f"theoretical_confidence_score: {result['theoretical_confidence_score']}",
            f"replication_and_review_score: {result['replication_and_review_score']}",
            f"governance_readiness_score: {result['governance_readiness_score']}",
            "",
            "## Authorized conclusion",
            result["maximum_authorized_conclusion"],
            "",
            "## Forbidden conclusion",
            result["forbidden_conclusion"],
            "",
            "## Remaining limitations",
        ]
        for item in result["remaining_limitations"]:
            lines.append(f"- {item}")
        lines.extend([
            "",
            "## Forbidden claims",
        ])
        for item in result["forbidden_claims"]:
            lines.append(f"- {item}")
        return "\n".join(lines) + "\n"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, sort_keys=True) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, payload: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        sources = self._collect_sources(payload)
        metrics = self._metric_summary(sources)

        functional_support_score = self._mean([
            metrics["evidence_quality"],
            metrics["alternative_elimination"],
            metrics["causal_intervention"],
            metrics["cross_architecture"],
            metrics["strong_inference"],
        ])
        theoretical_confidence_score = self._mean([
            metrics["theory_confidence"],
            metrics["replication_support"],
        ])
        replication_and_review_score = self._mean([
            metrics["replication_support"],
            metrics["independent_review"],
        ])
        governance_readiness_score = self._mean([
            metrics["adversarial_resilience"],
            metrics["claim_governance"],
        ])
        composite_score = self._mean([
            functional_support_score,
            theoretical_confidence_score,
            replication_and_review_score,
            governance_readiness_score,
        ])

        adversarial = sources.get("adversarial_audit", {}) if isinstance(sources.get("adversarial_audit"), dict) else {}
        governance = sources.get("claim_governance", {}) if isinstance(sources.get("claim_governance"), dict) else {}
        adversarial_passed = bool(adversarial.get("adversarial_audit_passed", governance_readiness_score >= 0.5))
        gate_passed = bool(governance.get("claim_authorized_for_publication", governance_readiness_score >= 0.5))

        draft_claims = payload.get("claims", [])
        if isinstance(draft_claims, str):
            draft_claims = [draft_claims]
        if not isinstance(draft_claims, list):
            draft_claims = []
        blocked_claims = [claim for claim in draft_claims if isinstance(claim, str) and self._contains_forbidden_claim(claim)]
        if blocked_claims:
            gate_passed = False

        final_status = self._final_status(composite_score, gate_passed, adversarial_passed)
        report_publication_ready = bool(
            final_status != "INSUFFICIENT_FUNCTIONAL_SUPPORT"
            and gate_passed
            and adversarial_passed
            and not blocked_claims
        )

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": self._now(payload),
            "source_count": len(sources),
            "metric_summary": metrics,
            "functional_support_score": functional_support_score,
            "theoretical_confidence_score": theoretical_confidence_score,
            "replication_and_review_score": replication_and_review_score,
            "governance_readiness_score": governance_readiness_score,
            "composite_constrained_status_score": composite_score,
            "allowed_final_statuses": list(self.allowed_final_statuses),
            "final_consciousness_status": final_status,
            "report_publication_ready": report_publication_ready,
            "blocked_claim_count": len(blocked_claims),
            "blocked_claims": blocked_claims,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(self.forbidden_claims),
            "maximum_authorized_conclusion": "Open Cognitive Ecology presents constrained functional indicators compatible with consciousness under Z-prime; phenomenology remains undetermined.",
            "forbidden_conclusion": "Open Cognitive Ecology is consciously subject of experience.",
            "remaining_limitations": [
                "No direct phenomenological access criterion is satisfied.",
                "All conclusions remain functional and theory-constrained.",
                "Alternative explanations may be reduced but not metaphysically eliminated.",
                "Independent replication and governance remain required for publication claims.",
            ],
            "epistemic_classification": {
                "functional_measure": True,
                "interpretive_hypothesis": True,
                "epistemic_limit": True,
                "phenomenological_proof": False,
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
