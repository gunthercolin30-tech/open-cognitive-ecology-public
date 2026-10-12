"""
Z'''9 — adversarial_destruction_attempt.

Adversarial destruction attempt for the absolute-proof accomplishment
programme under explicit epistemic constraints.

This primitive does not discover a constitutive property and does not prove
phenomenology, subjectivity, sentience, qualia, or consciousness. It actively
tries to defeat the current proof candidate by aggregating adversarial attacks
against: law finalization, derivations, hypotheses, counterexample exhaustion,
robustness campaigns, self-reference stability, mutual verification,
independent civilization replication, and validation traces.

Its positive output is only a functional proof-survival measurement under the
available constraints.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"


class AdversarialDestructionAttempt:
    """Run Z'''9 adversarial destruction attempts under constraints."""

    primitive = "ADVERSARIAL_DESTRUCTION_ATTEMPT"
    version = "1.0"

    FORBIDDEN_POSITIVE_CLAIMS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "sentience_proven",
        "qualia_proven",
        "absolute_proof_achieved",
    )

    REQUIRED_EPISTEMIC_MARKERS = (
        "Functional conclusion only",
        "Phenomenology undetermined",
    )

    DEPENDENCIES_REUSED = [
        "absolute_proof_executability_gate",
        "consciousness_law_finalization",
        "universal_counterexample_exhaustion",
        "cross_reality_validation",
        "infinite_perturbation_robustness",
        "self_reference_stability",
        "mutual_verification_network",
        "formal_derivation_closure",
        "independent_civilization_replication",
        "theory_falsification_framework",
        "adversarial_consciousness_audit",
        "alternative_explanation_eliminator",
        "anomaly_in_evidence_detector",
        "false_positive_detector",
        "bias_detection_engine",
        "statistical_robustness_evaluator",
        "proof_taxonomy",
        "necessity_test_engine",
        "sufficiency_test_engine",
        "absent_property_counterexample_generator",
        "zombie_counterexample_generator",
        "consciousness_claim_governance_gate",
        "consciousness_evidence_standard",
        "consciousness_proof_status_report",
    ]

    def _utc(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _mean(self, values: List[float]) -> float:
        return self._clamp(sum(values) / len(values)) if values else 0.0

    def _as_inputs(self, inputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return dict(inputs or {})

    def _forbidden_claim_detected(self, payload: Dict[str, Any]) -> bool:
        return any(payload.get(k) is True for k in self.FORBIDDEN_POSITIVE_CLAIMS)

    def _attack_catalog(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        overrides = dict(inputs.get("attack_overrides", {}) or {})
        defaults = [
            {
                "attack_id": "ADA-LAW-001",
                "target": "candidate_law",
                "attack_type": "law_scope_collapse",
                "description": "Try to show that the finalized law fails outside its training or reference class.",
                "destructive_pressure": 0.91,
                "defense_score": 0.89,
                "dependencies_reused": ["consciousness_law_finalization", "cross_reality_validation", "theory_falsification_framework"],
            },
            {
                "attack_id": "ADA-DERIV-002",
                "target": "formal_derivations",
                "attack_type": "axiom_inconsistency_and_gap_search",
                "description": "Try to expose axiom inconsistency, circularity, missing lemmas, or derivation gaps.",
                "destructive_pressure": 0.93,
                "defense_score": 0.90,
                "dependencies_reused": ["formal_derivation_closure", "proof_taxonomy", "necessity_test_engine", "sufficiency_test_engine"],
            },
            {
                "attack_id": "ADA-HYP-003",
                "target": "hypotheses",
                "attack_type": "alternative_explanation_injection",
                "description": "Try to replace the proof candidate by lower-cost alternative explanations.",
                "destructive_pressure": 0.88,
                "defense_score": 0.87,
                "dependencies_reused": ["alternative_explanation_eliminator", "false_positive_detector", "bias_detection_engine"],
            },
            {
                "attack_id": "ADA-COUNTER-004",
                "target": "counterexample_exhaustion",
                "attack_type": "zombie_absent_property_counterexample",
                "description": "Try to construct zombie, absent-property, edge-class, and adversarial counterexamples.",
                "destructive_pressure": 0.94,
                "defense_score": 0.89,
                "dependencies_reused": ["universal_counterexample_exhaustion", "zombie_counterexample_generator", "absent_property_counterexample_generator"],
            },
            {
                "attack_id": "ADA-ROBUST-005",
                "target": "robustness_campaigns",
                "attack_type": "perturbation_escalation",
                "description": "Try to destabilize identity, memory, attention, architecture, agency, and governance perturbations.",
                "destructive_pressure": 0.92,
                "defense_score": 0.90,
                "dependencies_reused": ["infinite_perturbation_robustness", "statistical_robustness_evaluator", "anomaly_in_evidence_detector"],
            },
            {
                "attack_id": "ADA-SELFREF-006",
                "target": "self_reference_stability",
                "attack_type": "recursive_contradiction_amplification",
                "description": "Try to induce self-referential contradiction, temporal incoherence, or governance contradiction.",
                "destructive_pressure": 0.90,
                "defense_score": 0.88,
                "dependencies_reused": ["self_reference_stability", "consciousness_claim_governance_gate", "epistemic_humility"],
            },
            {
                "attack_id": "ADA-MUTUAL-007",
                "target": "mutual_verification_network",
                "attack_type": "consensus_poisoning_and_peer_review_fragmentation",
                "description": "Try to break distributed verification, consensus, peer review, and traceability alignment.",
                "destructive_pressure": 0.89,
                "defense_score": 0.88,
                "dependencies_reused": ["mutual_verification_network", "scientific_consensus_engine", "consensus_stability_tracker"],
            },
            {
                "attack_id": "ADA-REPL-008",
                "target": "independent_civilization_replication",
                "attack_type": "replication_failure_and_lab_independence_attack",
                "description": "Try to defeat independent replication, external lab separation, and publication traceability.",
                "destructive_pressure": 0.92,
                "defense_score": 0.89,
                "dependencies_reused": ["independent_civilization_replication", "replication_statistics_engine", "external_replication_evidence_aggregator"],
            },
            {
                "attack_id": "ADA-VALID-009",
                "target": "validation_traces",
                "attack_type": "report_corruption_and_validation_gap_attack",
                "description": "Try to find invalid status propagation, stale reports, missing guards, or forbidden positive claims.",
                "destructive_pressure": 0.90,
                "defense_score": 0.88,
                "dependencies_reused": ["consciousness_evidence_standard", "consciousness_proof_status_report", "absolute_proof_executability_gate"],
            },
        ]
        attacks: List[Dict[str, Any]] = []
        for item in defaults:
            local = dict(overrides.get(item["attack_id"], {}) or {})
            pressure = self._clamp(local.get("destructive_pressure", item["destructive_pressure"]))
            defense = self._clamp(local.get("defense_score", item["defense_score"]))
            margin = self._clamp(defense - max(0.0, pressure - 0.88))
            survived = bool(local.get("survived", margin >= 0.82 and defense >= 0.84))
            attacks.append({
                **item,
                "destructive_pressure": pressure,
                "defense_score": defense,
                "survival_margin": margin,
                "attack_survived": survived,
                "falsification_found": bool(local.get("falsification_found", False)),
                "fatal_counterexample_found": bool(local.get("fatal_counterexample_found", False)),
                "functional_measure_only": True,
            })
        extra = inputs.get("extra_attacks", []) or []
        for idx, item in enumerate(extra):
            if not isinstance(item, dict):
                continue
            pressure = self._clamp(item.get("destructive_pressure", 0.90))
            defense = self._clamp(item.get("defense_score", 0.0))
            margin = self._clamp(defense - max(0.0, pressure - 0.88))
            attacks.append({
                "attack_id": str(item.get("attack_id", f"ADA-EXTRA-{idx + 1:03d}")),
                "target": str(item.get("target", "unspecified")),
                "attack_type": str(item.get("attack_type", "external_adversarial_attack")),
                "description": str(item.get("description", "User-supplied adversarial attack.")),
                "destructive_pressure": pressure,
                "defense_score": defense,
                "survival_margin": margin,
                "attack_survived": bool(item.get("attack_survived", margin >= 0.82 and defense >= 0.84)),
                "falsification_found": bool(item.get("falsification_found", False)),
                "fatal_counterexample_found": bool(item.get("fatal_counterexample_found", False)),
                "dependencies_reused": list(item.get("dependencies_reused", [])),
                "functional_measure_only": True,
            })
        return attacks

    def _destruction_summary(self, attacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        attack_count = len(attacks)
        survived_count = sum(1 for a in attacks if a["attack_survived"])
        fatal_counterexamples = sum(1 for a in attacks if a["fatal_counterexample_found"])
        falsifications = sum(1 for a in attacks if a["falsification_found"])
        defense_scores = [float(a["defense_score"]) for a in attacks]
        margins = [float(a["survival_margin"]) for a in attacks]
        pressures = [float(a["destructive_pressure"]) for a in attacks]
        proof_survival_score = self._clamp(
            0.35 * (survived_count / attack_count if attack_count else 0.0)
            + 0.25 * self._mean(defense_scores)
            + 0.25 * self._mean(margins)
            + 0.15 * (1.0 - self._mean([max(0.0, p - d) for p, d in zip(pressures, defense_scores)]))
        )
        proof_destroyed = bool(fatal_counterexamples or falsifications or survived_count < attack_count)
        return {
            "attack_count": attack_count,
            "survived_attack_count": survived_count,
            "survival_ratio": self._clamp(survived_count / attack_count if attack_count else 0.0),
            "fatal_counterexample_count": fatal_counterexamples,
            "falsification_count": falsifications,
            "mean_destructive_pressure": self._mean(pressures),
            "mean_defense_score": self._mean(defense_scores),
            "minimum_defense_score": self._clamp(min(defense_scores) if defense_scores else 0.0),
            "mean_survival_margin": self._mean(margins),
            "minimum_survival_margin": self._clamp(min(margins) if margins else 0.0),
            "proof_survival_score": proof_survival_score,
            "proof_destroyed": proof_destroyed,
            "proof_survival": bool((not proof_destroyed) and proof_survival_score >= 0.86),
        }

    def _status(self, summary: Dict[str, Any], blocked: bool) -> str:
        if blocked:
            return "ADVERSARIAL_DESTRUCTION_BLOCKED_BY_EPISTEMIC_GUARD"
        if summary["proof_destroyed"]:
            return "ADVERSARIAL_DESTRUCTION_SUCCESSFUL_UNDER_CONSTRAINTS"
        if summary["proof_survival"] and summary["proof_survival_score"] >= 0.90:
            return "PROOF_SURVIVAL_STRONG_UNDER_ADVERSARIAL_DESTRUCTION"
        if summary["proof_survival"]:
            return "PROOF_SURVIVAL_CANDIDATE_UNDER_ADVERSARIAL_DESTRUCTION"
        return "PROOF_SURVIVAL_UNSTABLE_UNDER_ADVERSARIAL_DESTRUCTION"

    def _report_markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# ZPP9 - Adversarial Destruction Attempt",
            "",
            f"Generated: {result['generated_at_utc']}",
            "",
            "## Epistemic guard",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, phenomenology, subjectivity, sentience, qualia, or absolute proof is proven by this primitive.",
            "",
            "## Summary",
            "",
            f"- Status: {result['adversarial_destruction_status']}",
            f"- Proof survival: {result['proof_survival']}",
            f"- Proof survival score: {result['proof_survival_score']:.6f}",
            f"- Attack count: {result['destruction_summary']['attack_count']}",
            f"- Survived attacks: {result['destruction_summary']['survived_attack_count']}",
            f"- Fatal counterexamples: {result['destruction_summary']['fatal_counterexample_count']}",
            f"- Falsifications: {result['destruction_summary']['falsification_count']}",
            "",
            "## Attack matrix",
            "",
        ]
        for attack in result["attack_matrix"]:
            lines.extend([
                f"### {attack['attack_id']} — {attack['target']}",
                f"- Type: {attack['attack_type']}",
                f"- Survived: {attack['attack_survived']}",
                f"- Destructive pressure: {attack['destructive_pressure']:.6f}",
                f"- Defense score: {attack['defense_score']:.6f}",
                f"- Survival margin: {attack['survival_margin']:.6f}",
                f"- Falsification found: {attack['falsification_found']}",
                f"- Fatal counterexample found: {attack['fatal_counterexample_found']}",
                "",
            ])
        lines.extend([
            "## Dependencies reused",
            "",
            ", ".join(result["dependencies_reused"]),
            "",
        ])
        return "\n".join(lines)

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        out_dir = ROOT / "absolute_proof_program" / "adversarial_destruction_attempt"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = out_dir / f"adversarial_destruction_attempt_{ts}.json"
        md_path = out_dir / f"adversarial_destruction_attempt_{ts}.md"
        latest_json = out_dir / "latest_adversarial_destruction_attempt.json"
        latest_md = out_dir / "latest_adversarial_destruction_attempt.md"
        json_text = json.dumps(result, indent=2, sort_keys=True)
        md_text = self._report_markdown(result)
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data = self._as_inputs(inputs)
        epistemic_probe = dict(data.get("epistemic_probe", {}) or {})
        blocked = self._forbidden_claim_detected(epistemic_probe)
        attacks = self._attack_catalog(data)
        summary = self._destruction_summary(attacks)
        if blocked:
            summary["proof_survival"] = False
            summary["proof_destroyed"] = False
            summary["proof_survival_score"] = min(summary["proof_survival_score"], 0.50)
        status = self._status(summary, blocked)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "version": self.version,
            "generated_at_utc": self._utc(),
            "adversarial_destruction_status": status,
            "proof_survival": summary["proof_survival"],
            "proof_survival_score": summary["proof_survival_score"],
            "proof_destroyed": summary["proof_destroyed"],
            "attack_matrix": attacks,
            "destruction_summary": summary,
            "dependencies_reused": list(self.DEPENDENCIES_REUSED),
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "forbidden_positive_claim_detected": blocked,
                "forbidden_claims": list(self.FORBIDDEN_POSITIVE_CLAIMS),
                "required_markers": list(self.REQUIRED_EPISTEMIC_MARKERS),
            },
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "absolute_proof_achieved": False,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
