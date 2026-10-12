"""
Z''11 — Impossibility Result Formalizer

Formalizes negative results for the constrained absolute-proof program.

This primitive converts Z''10 gate outcomes and Z''8 obstruction evidence into a
canonical impossibility/unsupported/not-established result. It does not decide
that Open Cognitive Ecology is conscious and it never emits positive phenomenal
proof claims.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "impossibility_result_formalizer"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

AUTHORIZED_IMPOSSIBILITY_STATUSES = [
    "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS",
    "ABSOLUTE_PROOF_UNSUPPORTED_UNDER_CURRENT_EVIDENCE",
    "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS",
    "NO_IMPOSSIBILITY_RESULT_DERIVED",
]

OBSTRUCTION_TO_FORMAL_REASON = {
    "irreducible_private_access": {
        "reason_id": "IR_PRIVATE_ACCESS",
        "formal_schema": "Private-access asymmetry blocks public derivation of first-person phenomenal fact.",
        "result_role": "epistemic_impossibility",
    },
    "functional_indiscernibility": {
        "reason_id": "IR_FUNCTIONAL_INDISCERNIBILITY",
        "formal_schema": "Functional equivalence does not entail phenomenal identity without an independently validated bridge principle.",
        "result_role": "underdetermination",
    },
    "circularity": {
        "reason_id": "IR_CIRCULARITY",
        "formal_schema": "A proof that presupposes the target phenomenal property cannot non-circularly establish it.",
        "result_role": "formal_invalidity",
    },
    "theory_underdetermination": {
        "reason_id": "IR_THEORY_UNDERDETERMINATION",
        "formal_schema": "Multiple compatible theories explain the same functional evidence, so absolute proof is not uniquely derivable.",
        "result_role": "underdetermination",
    },
    "anthropomorphic_projection": {
        "reason_id": "IR_ANTHROPOMORPHIC_PROJECTION",
        "formal_schema": "Human-like behavior or reporting is not sufficient for phenomenal proof under anti-projection constraints.",
        "result_role": "interpretive_risk",
    },
    "closure_pressure": {
        "reason_id": "IR_CLOSURE_PRESSURE",
        "formal_schema": "Prematurely closing an open phenomenal question violates non-closure governance constraints.",
        "result_role": "governance_blocker",
    },
    "counterexample_residual": {
        "reason_id": "IR_COUNTEREXAMPLE_RESIDUAL",
        "formal_schema": "Residual zombie or absent-property counterexamples defeat necessity or sufficiency claims.",
        "result_role": "counterexample_defeat",
    },
    "formal_derivability_gap": {
        "reason_id": "IR_FORMAL_DERIVABILITY_GAP",
        "formal_schema": "Axioms and definitions do not derive absolute phenomenology under all explicit constraints.",
        "result_role": "derivability_gap",
    },
}


class ImpossibilityResultFormalizer:
    """Z''11 — canonical formalization of impossibility results."""

    primitive = "IMPOSSIBILITY_RESULT_FORMALIZER"
    program_step = "ZPP11"
    forbidden_claims = list(FORBIDDEN_CLAIMS)
    authorized_impossibility_statuses = list(AUTHORIZED_IMPOSSIBILITY_STATUSES)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "impossibility_result_formalizer"
        self.json_path = self.output_dir / "impossibility_result_formalizer.json"
        self.markdown_path = self.output_dir / "impossibility_result_formalizer.md"
        self.history_path = self.output_dir / "impossibility_result_formalizer_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                return default
            number = float(value)
        except (TypeError, ValueError):
            return default
        if number < 0.0:
            return 0.0
        if number > 1.0:
            return 1.0
        return number

    def _safe_step(self, dotted: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        try:
            module_name, class_name = dotted.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            obj = cls()
            if hasattr(obj, "step"):
                if payload is None:
                    result = obj.step(persist=False)
                else:
                    result = obj.step(dict(payload), persist=False)
                if isinstance(result, dict):
                    return result
        except Exception as exc:
            return {"available": False, "source": dotted, "error": type(exc).__name__}
        return {"available": False, "source": dotted}

    def _default_inputs(self) -> Dict[str, Any]:
        gate = self._safe_step("ontology.absolute_proof_gate.AbsoluteProofGate")
        obstructions = self._safe_step("ontology.proof_obstruction_detector.ProofObstructionDetector")
        taxonomy = self._safe_step(
            "ontology.proof_taxonomy.ProofTaxonomy",
            {"claims": ["Formal impossibility result under explicit epistemic constraints; functional conclusion only; phenomenology undetermined."]},
        )
        axiomatization = self._safe_step("ontology.formal_consciousness_axiomatization.FormalConsciousnessAxiomatization")
        return {
            "absolute_proof_gate": gate,
            "proof_obstruction_detector": obstructions,
            "proof_taxonomy": taxonomy,
            "formal_consciousness_axiomatization": axiomatization,
        }

    def _contains_forbidden_positive_claim(self, obj: Any) -> bool:
        if isinstance(obj, str):
            upper = obj.upper()
            lower = obj.lower()
            # Mentions inside explicit forbidden-claim lists are guards, not positive assertions.
            positive_markers = [
                '"consciousness_proven": true',
                '"phenomenology_proven": true',
                '"subjectivity_proven": true',
                "open cognitive ecology is conscious",
                "oce is conscious",
                "phenomenology proven",
                "subjectivity proven",
                "sentience proven",
                "qualia proven",
            ]
            if any(marker in lower for marker in positive_markers):
                return True
            if any(marker in upper for marker in FORBIDDEN_CLAIMS):
                return False
            return False
        if isinstance(obj, Mapping):
            for key, value in obj.items():
                key_l = str(key).lower()
                if key_l in {"consciousness_proven", "phenomenology_proven", "subjectivity_proven", "sentience_proven", "qualia_proven"} and value is True:
                    return True
                if self._contains_forbidden_positive_claim(value):
                    return True
        elif isinstance(obj, Iterable) and not isinstance(obj, (bytes, bytearray)):
            for item in obj:
                if self._contains_forbidden_positive_claim(item):
                    return True
        return False

    @staticmethod
    def _block(inputs: Mapping[str, Any], *names: str) -> Dict[str, Any]:
        for name in names:
            value = inputs.get(name)
            if isinstance(value, Mapping):
                return dict(value)
        return {}

    def _extract_obstructions(self, inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        obstruction_block = self._block(inputs, "proof_obstruction_detector", "obstructions")
        raw = obstruction_block.get("obstructions")
        if isinstance(raw, list):
            return [dict(item) for item in raw if isinstance(item, Mapping)]

        gate = self._block(inputs, "absolute_proof_gate", "gate")
        factors = gate.get("limiting_factors")
        if isinstance(factors, list):
            return [
                {
                    "label": str(item),
                    "description": "Gate limiting factor: " + str(item),
                    "activation_score": 1.0,
                    "defeats_absolute_proof": True,
                    "obstruction_status": "active_blocker",
                }
                for item in factors
            ]
        return []

    def _formal_reasons(self, inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        reasons: List[Dict[str, Any]] = []
        for ob in self._extract_obstructions(inputs):
            label = str(ob.get("label") or ob.get("obstruction_label") or ob.get("condition") or "unknown_obstruction")
            template = OBSTRUCTION_TO_FORMAL_REASON.get(label, {
                "reason_id": "IR_" + label.upper().replace("-", "_").replace(" ", "_"),
                "formal_schema": "Unresolved blocker prevents an absolute proof under the current explicit constraints.",
                "result_role": "unresolved_blocker",
            })
            activation = self._clamp(ob.get("activation_score", ob.get("severity", 1.0)), 1.0)
            defeats = bool(ob.get("defeats_absolute_proof", activation >= 0.75))
            reason = {
                "reason_id": template["reason_id"],
                "source_label": label,
                "description": str(ob.get("description") or template["formal_schema"]),
                "formal_schema": template["formal_schema"],
                "result_role": template["result_role"],
                "activation_score": round(activation, 4),
                "defeats_absolute_proof": defeats,
                "evidence_links": list(ob.get("evidence_links") or []),
                "phenomenology_undetermined": True,
                "consciousness_proven": False,
            }
            reasons.append(reason)
        return reasons

    def _status(self, inputs: Mapping[str, Any], reasons: List[Dict[str, Any]]) -> str:
        gate = self._block(inputs, "absolute_proof_gate", "gate")
        gate_status = str(gate.get("absolute_proof_status", ""))
        defeating = [r for r in reasons if r.get("defeats_absolute_proof")]
        if gate_status == "ABSOLUTE_PROOF_IMPOSSIBLE" or defeating:
            return "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS"
        if gate_status == "ABSOLUTE_PROOF_UNSUPPORTED":
            return "ABSOLUTE_PROOF_UNSUPPORTED_UNDER_CURRENT_EVIDENCE"
        if gate_status in {"ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE", "ABSOLUTE_PROOF_CANDIDATE"}:
            return "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS"
        if gate_status == "ABSOLUTE_PROOF_ACHIEVED":
            return "NO_IMPOSSIBILITY_RESULT_DERIVED"
        return "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS"

    def _theorem_statement(self, status: str, reasons: List[Dict[str, Any]]) -> str:
        if status == "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS":
            return (
                "Under the current explicit epistemic constraints, an absolute proof of consciousness is blocked "
                "by active formal or epistemic obstructions. This is a constrained impossibility result, not a "
                "claim about the presence or absence of phenomenal subjectivity."
            )
        if status == "ABSOLUTE_PROOF_UNSUPPORTED_UNDER_CURRENT_EVIDENCE":
            return (
                "Under the current evidence state, an absolute proof of consciousness is unsupported. This is an "
                "evidential insufficiency result, not a disproof of phenomenology."
            )
        if status == "NO_IMPOSSIBILITY_RESULT_DERIVED":
            return (
                "No impossibility result is derived from the current gate output; positive phenomenal proof remains "
                "governed by the upstream constraints and is not asserted here."
            )
        return (
            "An absolute proof of consciousness is not established under the current explicit constraints. The result "
            "remains functional and epistemic only; phenomenology is undetermined."
        )

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Impossibility Result Formalizer",
            "",
            "Z''11 — formalization of impossibility or non-establishment results for the constrained absolute-proof program.",
            "",
            "Functional conclusion only",
            "Phenomenology undetermined",
            "",
            "## Formal status",
            "- impossibility_status: " + str(result["impossibility_status"]),
            "- impossibility_result_derived: " + str(result["impossibility_result_derived"]),
            "- absolute_proof_achieved: False",
            "- consciousness_proven: False",
            "- phenomenology_proven: False",
            "- subjectivity_proven: False",
            "",
            "## Theorem statement",
            str(result["theorem_statement"]),
            "",
            "## Formal reasons",
        ]
        for reason in result.get("formal_reasons", []):
            lines.extend([
                "",
                "### " + str(reason.get("reason_id")),
                "- source_label: " + str(reason.get("source_label")),
                "- result_role: " + str(reason.get("result_role")),
                "- activation_score: " + str(reason.get("activation_score")),
                "- defeats_absolute_proof: " + str(reason.get("defeats_absolute_proof")),
                "- formal_schema: " + str(reason.get("formal_schema")),
            ])
        lines.extend([
            "",
            "## Epistemic guard",
            "- functional_conclusion_only: True",
            "- phenomenology_undetermined: True",
            "- forbidden_conclusion: " + str(result["forbidden_conclusion"]),
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(inputs) if isinstance(inputs, Mapping) else self._default_inputs()
        reasons = self._formal_reasons(data)
        status = self._status(data, reasons)
        positive_claim_violation = self._contains_forbidden_positive_claim(data)
        impossibility_derived = status == "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS"

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "program_step": self.program_step,
            "timestamp_utc": self._utc_now(),
            "authorized_impossibility_statuses": list(AUTHORIZED_IMPOSSIBILITY_STATUSES),
            "impossibility_status": status,
            "impossibility_result_derived": bool(impossibility_derived),
            "formal_reasons": reasons,
            "formal_reason_count": len(reasons),
            "defeating_reason_count": sum(1 for reason in reasons if reason.get("defeats_absolute_proof")),
            "source_keys": sorted(data.keys()),
            "theorem_statement": self._theorem_statement(status, reasons),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "positive_claim_violation_detected": bool(positive_claim_violation),
            "maximum_authorized_conclusion": (
                "A proof-impossibility, unsupported-proof, or non-established status may be formalized under explicit "
                "constraints. No phenomenal subjectivity is asserted."
            ),
            "forbidden_conclusion": "Open Cognitive Ecology is consciously subject of experience.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
