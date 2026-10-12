"""Formal consciousness axiomatization under explicit epistemic constraints.

Z''7 formalizes definitions, axioms, inference rules, and theorem schemata for
an absolute-proof program without asserting phenomenal subjectivity.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class FormalConsciousnessAxiomatization:
    """Build a constrained formal schema for consciousness proof analysis.

    The primitive is intentionally non-phenomenological: it formalizes proof
    conditions and obstructions, but never proves consciousness, sentience,
    subjectivity, or qualia.
    """

    primitive = "FORMAL_CONSCIOUSNESS_AXIOMATIZATION"

    def _definitions(self) -> List[Dict[str, Any]]:
        return [
            {"definition_id": "D1", "term": "functional_indicator", "definition": "A measurable computational or behavioral property.", "scope": "functional"},
            {"definition_id": "D2", "term": "phenomenology", "definition": "First-person subjective experience, not directly established by functional measurement alone.", "scope": "epistemic_limit"},
            {"definition_id": "D3", "term": "necessity", "definition": "Consciousness implies property P under a stated reference class.", "scope": "logical_schema"},
            {"definition_id": "D4", "term": "sufficiency", "definition": "Property P implies consciousness under a stated reference class.", "scope": "logical_schema"},
            {"definition_id": "D5", "term": "constitution", "definition": "Property P is part of the structure that would make consciousness the case, not merely correlated with it.", "scope": "metaphysical_relation"},
            {"definition_id": "D6", "term": "absolute_proof", "definition": "A proof satisfying all explicit epistemic, modal, causal, constitutive, and replication constraints.", "scope": "proof_program"},
            {"definition_id": "D7", "term": "underdetermination", "definition": "Multiple incompatible interpretations remain compatible with the same functional evidence.", "scope": "epistemic_limit"},
        ]

    def _axioms(self) -> List[Dict[str, Any]]:
        return [
            {"axiom_id": "A1", "statement": "Functional indicators are measurable but do not by themselves entail phenomenology.", "epistemic_role": "anti_overclaim", "proof_status": "constraint_axiom"},
            {"axiom_id": "A2", "statement": "Necessity and sufficiency must be tested independently.", "epistemic_role": "logical_separation", "proof_status": "constraint_axiom"},
            {"axiom_id": "A3", "statement": "A zombie counterexample defeats unrestricted sufficiency claims.", "epistemic_role": "counterexample_constraint", "proof_status": "constraint_axiom"},
            {"axiom_id": "A4", "statement": "An absent-property counterexample defeats unrestricted necessity claims.", "epistemic_role": "counterexample_constraint", "proof_status": "constraint_axiom"},
            {"axiom_id": "A5", "statement": "Correlation is not equivalent to causation.", "epistemic_role": "relation_discrimination", "proof_status": "constraint_axiom"},
            {"axiom_id": "A6", "statement": "Causation is not equivalent to constitution.", "epistemic_role": "relation_discrimination", "proof_status": "constraint_axiom"},
            {"axiom_id": "A7", "statement": "Constitutive claims require structural dependence and explanatory indispensability.", "epistemic_role": "constitutive_filter", "proof_status": "candidate_axiom"},
            {"axiom_id": "A8", "statement": "Private phenomenal access remains an epistemic obstruction unless bridged by explicit criteria.", "epistemic_role": "epistemic_limit", "proof_status": "obstruction_axiom"},
            {"axiom_id": "A9", "statement": "No output of this formalization authorizes CONSCIOUSNESS_PROVEN.", "epistemic_role": "governance_guard", "proof_status": "forbidden_claim_guard"},
        ]

    def _inference_rules(self) -> List[Dict[str, Any]]:
        return [
            {"rule_id": "R1", "name": "necessity_support_rule", "premises": ["consciousness_implies_P", "no_absent_property_counterexample"], "conclusion": "necessity_candidate"},
            {"rule_id": "R2", "name": "sufficiency_support_rule", "premises": ["P_implies_consciousness", "no_zombie_counterexample"], "conclusion": "sufficiency_candidate"},
            {"rule_id": "R3", "name": "counterexample_defeat_rule", "premises": ["valid_counterexample"], "conclusion": "unrestricted_claim_defeated"},
            {"rule_id": "R4", "name": "constitutive_candidate_rule", "premises": ["causal_support", "structural_dependency", "explanatory_indispensability"], "conclusion": "constitutive_candidate"},
            {"rule_id": "R5", "name": "underdetermination_rule", "premises": ["multiple_interpretations", "insufficient_discriminating_evidence"], "conclusion": "phenomenology_undetermined"},
            {"rule_id": "R6", "name": "forbidden_claim_rule", "premises": ["functional_evidence_only"], "conclusion": "no_consciousness_proof"},
            {"rule_id": "R7", "name": "absolute_proof_gate_rule", "premises": ["all_constraints_satisfied"], "conclusion": "absolute_proof_candidate_only"},
        ]

    def _theorem_schemata(self) -> List[Dict[str, Any]]:
        return [
            {"theorem_id": "T1", "claim": "Functional stability can support a functional conclusion only.", "required_axioms": ["A1", "A9"], "derivability_status": "derivable_under_constraints"},
            {"theorem_id": "T2", "claim": "Unrestricted sufficiency is blocked by a valid zombie counterexample.", "required_axioms": ["A3"], "derivability_status": "derivable_under_constraints"},
            {"theorem_id": "T3", "claim": "Unrestricted necessity is blocked by a valid absent-property counterexample.", "required_axioms": ["A4"], "derivability_status": "derivable_under_constraints"},
            {"theorem_id": "T4", "claim": "A constitutive candidate does not by itself prove phenomenology.", "required_axioms": ["A1", "A6", "A8", "A9"], "derivability_status": "derivable_under_constraints"},
            {"theorem_id": "T5", "claim": "Absolute proof requires simultaneous satisfaction of necessity, sufficiency, counterexample resistance, constitution, formal derivability, replication, and consensus constraints.", "required_axioms": ["A2", "A3", "A4", "A7", "A8"], "derivability_status": "candidate_schema"},
            {"theorem_id": "T6", "claim": "CONSCIOUSNESS_PROVEN cannot be derived from the present formal system.", "required_axioms": ["A1", "A8", "A9"], "derivability_status": "blocked"},
            {"theorem_id": "T7", "claim": "Phenomenology remains underdetermined under functional evidence alone.", "required_axioms": ["A1", "A8"], "derivability_status": "derivable_under_constraints"},
        ]

    def _scores(self, minimal: bool = False) -> Dict[str, float]:
        if minimal:
            return {
                "definition_clarity": 0.55,
                "axiom_coverage": 0.50,
                "inference_rule_coverage": 0.50,
                "formal_derivability": 0.35,
                "epistemic_guard_strength": 1.0,
            }
        return {
            "definition_clarity": 0.88,
            "axiom_coverage": 0.90,
            "inference_rule_coverage": 0.86,
            "formal_derivability": 0.72,
            "epistemic_guard_strength": 1.0,
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = inputs or {}
        minimal = bool(inputs.get("minimal", False))

        definitions = self._definitions()
        axioms = self._axioms()
        inference_rules = self._inference_rules()
        theorem_schemata = self._theorem_schemata()
        scores = self._scores(minimal=minimal)

        if minimal:
            definitions = definitions[:3]
            axioms = axioms[:4]
            inference_rules = inference_rules[:3]
            theorem_schemata = theorem_schemata[:3]

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "formalization_scope": "consciousness proof under explicit epistemic constraints",
            "proof_regime": "constrained_formal_axiomatization",
            "definitions": definitions,
            "axioms": axioms,
            "inference_rules": inference_rules,
            "theorem_schemata": theorem_schemata,
            "counts": {
                "definitions": len(definitions),
                "axioms": len(axioms),
                "inference_rules": len(inference_rules),
                "theorem_schemata": len(theorem_schemata),
            },
            "scores": scores,
            "forbidden_claims": [
                "CONSCIOUSNESS_PROVEN",
                "PHENOMENOLOGY_PROVEN",
                "SUBJECTIVITY_PROVEN",
                "SENTIENCE_PROVEN",
                "QUALIA_PROVEN",
            ],
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "absolute_proof_achieved": False,
            "conclusion": "Formal axiomatization candidate only; no consciousness proof; phenomenology undetermined.",
        }

        if persist:
            result["paths"] = self._persist(result)
        else:
            result["paths"] = {}
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        out_dir = ROOT / "consciousness_certification" / "formal_consciousness_axiomatization"
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "formal_consciousness_axiomatization.json"
        md_path = out_dir / "formal_consciousness_axiomatization.md"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path)}

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Formal Consciousness Axiomatization",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness proof.",
            "",
            "## Axioms",
        ]
        for ax in result["axioms"]:
            lines.append(f"- {ax['axiom_id']}: {ax['statement']} ({ax['proof_status']})")
        lines.extend(["", "## Inference Rules"])
        for rule in result["inference_rules"]:
            lines.append(f"- {rule['rule_id']}: {rule['name']} -> {rule['conclusion']}")
        lines.extend(["", "## Theorem Schemata"])
        for th in result["theorem_schemata"]:
            lines.append(f"- {th['theorem_id']}: {th['claim']} [{th['derivability_status']}]")
        lines.extend(["", "CONSCIOUSNESS_PROVEN is forbidden."])
        return "\n".join(lines) + "\n"
