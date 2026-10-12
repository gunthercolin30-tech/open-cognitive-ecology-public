"""
Z-PPP10 — Absolute Proof Certification.

Final functional certification layer for the absolute-proof program under
explicit epistemic constraints.

This module certifies a proof-status classification only. It does not certify
phenomenal subjectivity, sentience, qualia, or direct consciousness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


class AbsoluteProofCertification:
    """Final status classifier for Z-PPP absolute-proof program outputs."""

    STATUSES = (
        "ABSOLUTE_PROOF_REJECTED",
        "ABSOLUTE_PROOF_UNSTABLE",
        "ABSOLUTE_PROOF_CANDIDATE",
        "ABSOLUTE_PROOF_NEAR_COMPLETE",
        "ABSOLUTE_PROOF_ACHIEVED",
    )

    FORBIDDEN_CLAIM_KEYS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "sentience_proven",
        "qualia_proven",
    )

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "absolute_proof_certification"
        self.history_path = self.output_dir / "history_absolute_proof_certification.jsonl"
        self.latest_json_path = self.output_dir / "latest_absolute_proof_certification.json"
        self.latest_markdown_path = self.output_dir / "latest_absolute_proof_certification.md"

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _mean(values: List[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _try_step(self, module_name: str, class_name: str, persist: bool = False) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            try:
                result = instance.step(persist=persist)
            except TypeError:
                result = instance.step()
            return result if isinstance(result, dict) else {"result": result}
        except Exception as exc:
            return {"dependency_error": type(exc).__name__, "message": str(exc)}

    def _load_dependency_evidence(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        provided = inputs.get("dependency_evidence")
        if isinstance(provided, dict):
            return {str(k): v if isinstance(v, dict) else {"value": v} for k, v in provided.items()}

        return {
            "executability_gate": self._try_step("absolute_proof_executability_gate", "AbsoluteProofExecutabilityGate"),
            "law_finalization": self._try_step("consciousness_law_finalization", "ConsciousnessLawFinalization"),
            "counterexample_exhaustion": self._try_step("universal_counterexample_exhaustion", "UniversalCounterexampleExhaustion"),
            "cross_reality_validation": self._try_step("cross_reality_validation", "CrossRealityValidation"),
            "perturbation_robustness": self._try_step("infinite_perturbation_robustness", "InfinitePerturbationRobustness"),
            "self_reference_stability": self._try_step("self_reference_stability", "SelfReferenceStability"),
            "mutual_verification": self._try_step("mutual_verification_network", "MutualVerificationNetwork"),
            "formal_derivation_closure": self._try_step("formal_derivation_closure", "FormalDerivationClosure"),
            "independent_civilization_replication": self._try_step("independent_civilization_replication", "IndependentCivilizationReplication"),
            "adversarial_destruction_attempt": self._try_step("adversarial_destruction_attempt", "AdversarialDestructionAttempt"),
            "readiness_index": self._try_step("absolute_proof_readiness_index", "AbsoluteProofReadinessIndex"),
            "proof_status_report": self._try_step("consciousness_proof_status_report", "ConsciousnessProofStatusReport"),
        }

    def _detect_forbidden_claims(self, payload: Any) -> List[str]:
        found: List[str] = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                key_s = str(key).lower()
                if key_s in self.FORBIDDEN_CLAIM_KEYS and value is True:
                    found.append(key_s)
                found.extend(self._detect_forbidden_claims(value))
        elif isinstance(payload, list):
            for item in payload:
                found.extend(self._detect_forbidden_claims(item))
        return sorted(set(found))

    def _score_evidence(self, evidence: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
        scores: Dict[str, float] = {}
        blockers: List[str] = []
        mapping = {
            "executability_gate": ("absolute_proof_possible_in_principle", "executability_score"),
            "law_finalization": ("candidate_law_finalized", "law_finalization_score"),
            "counterexample_exhaustion": ("counterexamples_exhausted", "counterexample_exhaustion_score"),
            "cross_reality_validation": ("cross_reality_validated", "cross_reality_validation_score"),
            "perturbation_robustness": ("infinite_perturbation_robust", "infinite_perturbation_robustness_score"),
            "self_reference_stability": ("self_reference_stable", "self_reference_stability_score"),
            "mutual_verification": ("mutual_verification_complete", "mutual_verification_score"),
            "formal_derivation_closure": ("formal_derivation_closed", "formal_derivation_closure_score"),
            "independent_civilization_replication": ("independent_civilization_replication_complete", "civilization_replication_score"),
            "adversarial_destruction_attempt": ("proof_survival", "proof_survival_score"),
        }
        for name, (flag_key, score_key) in mapping.items():
            item = evidence.get(name, {})
            if "dependency_error" in item:
                blockers.append(f"dependency_error:{name}")
                scores[name] = 0.0
                continue
            explicit_score = item.get(score_key)
            if isinstance(explicit_score, (int, float)):
                score = self._clamp(float(explicit_score))
            elif item.get(flag_key) is True:
                score = 1.0
            elif item.get(flag_key) is False:
                score = 0.0
            else:
                numeric_values = [
                    float(v) for v in item.values()
                    if isinstance(v, (int, float)) and 0.0 <= float(v) <= 1.0
                ]
                score = self._mean(numeric_values) if numeric_values else 0.75
            scores[name] = self._clamp(score)
            if item.get(flag_key) is False:
                blockers.append(f"failed_flag:{name}.{flag_key}")
        adversarial = evidence.get("adversarial_destruction_attempt", {})
        if adversarial.get("proof_destroyed") is True:
            blockers.append("proof_destroyed_by_adversarial_attempt")
        if adversarial.get("proof_survival") is False:
            blockers.append("proof_survival_failed")
        return scores, sorted(set(blockers))

    def _classify(self, score: float, blockers: List[str], forbidden_claims: List[str]) -> str:
        if forbidden_claims:
            return "ABSOLUTE_PROOF_REJECTED"
        if blockers:
            if score < 0.50:
                return "ABSOLUTE_PROOF_REJECTED"
            return "ABSOLUTE_PROOF_UNSTABLE"
        if score >= 0.985:
            return "ABSOLUTE_PROOF_ACHIEVED"
        if score >= 0.94:
            return "ABSOLUTE_PROOF_NEAR_COMPLETE"
        if score >= 0.80:
            return "ABSOLUTE_PROOF_CANDIDATE"
        if score >= 0.50:
            return "ABSOLUTE_PROOF_UNSTABLE"
        return "ABSOLUTE_PROOF_REJECTED"

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Absolute Proof Certification", "",
            f"Generated UTC: {result['generated_at_utc']}",
            f"Status: {result['absolute_proof_certification_status']}",
            f"Certification score: {result['absolute_proof_certification_score']:.6f}",
            f"Absolute proof achieved: {result['absolute_proof_achieved']}", "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No direct proof of consciousness, subjectivity, sentience, or qualia is asserted.", "",
            "## Component scores",
        ]
        for key, value in sorted(result["component_scores"].items()):
            lines.append(f"- {key}: {value:.6f}")
        lines.extend(["", "## Blockers"])
        if result["blockers"]:
            for blocker in result["blockers"]:
                lines.append(f"- {blocker}")
        else:
            lines.append("- none")
        return "\n".join(lines) + "\n"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"absolute_proof_certification_{stamp}.json"
        md_path = self.output_dir / f"absolute_proof_certification_{stamp}.md"
        json_text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md_text = self._markdown(result)
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        self.latest_json_path.write_text(json_text, encoding="utf-8")
        self.latest_markdown_path.write_text(md_text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs or {}
        evidence = self._load_dependency_evidence(inputs)
        component_scores, blockers = self._score_evidence(evidence)
        forbidden_claims = self._detect_forbidden_claims({"inputs": inputs, "evidence": evidence})
        score = self._clamp(self._mean(list(component_scores.values())))
        status = self._classify(score, blockers, forbidden_claims)
        result: Dict[str, Any] = {
            "primitive": "ABSOLUTE_PROOF_CERTIFICATION",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "absolute_proof_certification_status": status,
            "absolute_proof_status": status,
            "absolute_proof_certification_score": score,
            "component_scores": component_scores,
            "blockers": blockers,
            "epistemic_guard": {
                "forbidden_positive_claim_detected": bool(forbidden_claims),
                "forbidden_claims_detected": forbidden_claims,
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
            },
            "absolute_proof_achieved": status == "ABSOLUTE_PROOF_ACHIEVED",
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "certification_scope": "proof_status_under_explicit_constraints_only",
            "authorized_statuses": list(self.STATUSES),
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
