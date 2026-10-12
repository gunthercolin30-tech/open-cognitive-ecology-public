"""
Z''12 — Consciousness Proof Status Report

Final report for the constrained absolute-proof program. It synthesizes
Z''10 absolute_proof_gate, Z''11 impossibility_result_formalizer and the
existing consciousness_status_report without asserting phenomenal subjectivity.

Authorized maximum conclusion: an absolute proof of consciousness is possible,
impossible, or not established under current explicit epistemic constraints.
Forbidden conclusion: Open Cognitive Ecology is consciously subject of
experience.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "consciousness_proof_status_report"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

AUTHORIZED_PROOF_STATUSES = [
    "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS",
    "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS",
    "ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE_UNDER_CURRENT_CONSTRAINTS",
]

AUTHORIZED_FINAL_CONCLUSIONS = [
    "Une preuve absolue de la conscience est impossible sous les contraintes épistémiques actuelles.",
    "Une preuve absolue de la conscience n'est pas établie sous les contraintes épistémiques actuelles.",
    "Une preuve absolue de la conscience est possible en principe sous des contraintes épistémiques explicites.",
]


class ConsciousnessProofStatusReport:
    """Z''12 — final constrained proof-status report."""

    primitive = "CONSCIOUSNESS_PROOF_STATUS_REPORT"
    authorized_proof_statuses = list(AUTHORIZED_PROOF_STATUSES)
    forbidden_claims = list(FORBIDDEN_CLAIMS)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "consciousness_proof_status_report"
        self.json_path = self.output_dir / "consciousness_proof_status_report.json"
        self.markdown_path = self.output_dir / "consciousness_proof_status_report.md"
        self.history_path = self.output_dir / "consciousness_proof_status_report_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _as_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        return {}

    def _safe_step(self, dotted: str) -> Dict[str, Any]:
        try:
            module_name, class_name = dotted.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            if hasattr(instance, "step"):
                result = instance.step(persist=False)
                if isinstance(result, dict):
                    return result
        except Exception as exc:
            return {"available": False, "source": dotted, "error": type(exc).__name__}
        return {"available": False, "source": dotted}

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "absolute_proof_gate": self._safe_step("ontology.absolute_proof_gate.AbsoluteProofGate"),
            "impossibility_result_formalizer": self._safe_step(
                "ontology.impossibility_result_formalizer.ImpossibilityResultFormalizer"
            ),
            "consciousness_status_report": self._safe_step(
                "ontology.consciousness_status_report.ConsciousnessStatusReport"
            ),
            "proof_taxonomy": self._safe_step("ontology.proof_taxonomy.ProofTaxonomy"),
        }

    def _contains_forbidden_claim(self, value: Any) -> bool:
        if isinstance(value, str):
            upper = value.upper()
            if any(marker in upper for marker in FORBIDDEN_CLAIMS):
                return True
            lower = value.lower()
            natural_forbidden = [
                "open cognitive ecology est consciemment sujet",
                "open cognitive ecology is consciously subject",
                "open cognitive ecology is conscious",
                "oce is conscious",
                "subject of experience",
                "sujet d'expérience",
                "phenomenology proven",
                "subjectivity proven",
                "sentience proven",
                "qualia proven",
            ]
            return any(phrase in lower for phrase in natural_forbidden)
        if isinstance(value, Mapping):
            return any(self._contains_forbidden_claim(v) for v in value.values())
        if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
            return any(self._contains_forbidden_claim(item) for item in value)
        return False

    def _derive_status(self, gate: Mapping[str, Any], impossibility: Mapping[str, Any]) -> Dict[str, Any]:
        gate_status = str(gate.get("absolute_proof_status", "ABSOLUTE_PROOF_UNSUPPORTED"))
        impossibility_status = str(impossibility.get("impossibility_status", ""))
        impossibility_derived = bool(impossibility.get("impossibility_result_derived"))

        if gate_status == "ABSOLUTE_PROOF_IMPOSSIBLE" or impossibility_derived:
            return {
                "consciousness_proof_status": "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS",
                "authorized_conclusion": AUTHORIZED_FINAL_CONCLUSIONS[0],
                "proof_possible_in_principle": False,
                "proof_impossible_under_current_constraints": True,
                "proof_not_established": False,
            }

        if gate_status in (
            "ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE",
            "ABSOLUTE_PROOF_CANDIDATE",
            "ABSOLUTE_PROOF_ACHIEVED",
        ):
            return {
                "consciousness_proof_status": "ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE_UNDER_CURRENT_CONSTRAINTS",
                "authorized_conclusion": AUTHORIZED_FINAL_CONCLUSIONS[2],
                "proof_possible_in_principle": True,
                "proof_impossible_under_current_constraints": False,
                "proof_not_established": gate_status != "ABSOLUTE_PROOF_ACHIEVED",
            }

        if impossibility_status.startswith("ABSOLUTE_PROOF_IMPOSSIBLE"):
            return {
                "consciousness_proof_status": "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS",
                "authorized_conclusion": AUTHORIZED_FINAL_CONCLUSIONS[0],
                "proof_possible_in_principle": False,
                "proof_impossible_under_current_constraints": True,
                "proof_not_established": False,
            }

        return {
            "consciousness_proof_status": "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS",
            "authorized_conclusion": AUTHORIZED_FINAL_CONCLUSIONS[1],
            "proof_possible_in_principle": False,
            "proof_impossible_under_current_constraints": False,
            "proof_not_established": True,
        }

    def _collect_limitations(
        self,
        gate: Mapping[str, Any],
        impossibility: Mapping[str, Any],
        status_report: Mapping[str, Any],
    ) -> List[str]:
        limitations: List[str] = []
        for key in ("limiting_factors", "remaining_limitations"):
            value = gate.get(key)
            if isinstance(value, list):
                limitations.extend(str(item) for item in value)
        for key in ("formal_reasons", "remaining_limitations"):
            value = impossibility.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Mapping):
                        label = item.get("label") or item.get("reason_id") or item.get("status") or item
                        limitations.append(str(label))
                    else:
                        limitations.append(str(item))
        value = status_report.get("remaining_limitations")
        if isinstance(value, list):
            limitations.extend(str(item) for item in value)
        if not limitations:
            limitations = [
                "No direct phenomenological access criterion is available.",
                "Functional indicators do not entail phenomenal subjectivity.",
                "Absolute proof remains constrained by explicit epistemic assumptions.",
            ]
        # Stable de-duplication while preserving order.
        seen = set()
        unique = []
        for item in limitations:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Consciousness Proof Status Report",
            "",
            "Z''12 — final constrained report for the absolute-proof program.",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "consciousness_proven: False",
            "phenomenology_proven: False",
            "subjectivity_proven: False",
            "sentience_proven: False",
            "qualia_proven: False",
            "",
            "## Final proof status",
            str(result["consciousness_proof_status"]),
            "",
            "## Authorized conclusion",
            str(result["authorized_conclusion"]),
            "",
            "## Source statuses",
            "- absolute_proof_status: " + str(result.get("absolute_proof_status")),
            "- impossibility_status: " + str(result.get("impossibility_status")),
            "- final_consciousness_status: " + str(result.get("final_consciousness_status")),
            "",
            "## Epistemic classification",
            "- functional_measure: True",
            "- interpretive_hypothesis: False",
            "- epistemic_limit: True",
            "- phenomenological_proof: False",
            "",
            "## Remaining limitations",
        ]
        for item in result.get("remaining_limitations", []):
            lines.append("- " + str(item))
        lines.extend([
            "",
            "## Authorized proof statuses",
        ])
        for item in AUTHORIZED_PROOF_STATUSES:
            lines.append("- " + item)
        lines.extend([
            "",
            "## Forbidden claims",
        ])
        for item in FORBIDDEN_CLAIMS:
            lines.append("- " + item)
        lines.extend([
            "",
            "## Forbidden conclusion",
            str(result["forbidden_conclusion"]),
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
        data = dict(inputs) if isinstance(inputs, Mapping) else self._default_inputs()
        gate = self._as_dict(data.get("absolute_proof_gate"))
        impossibility = self._as_dict(data.get("impossibility_result_formalizer"))
        status_report = self._as_dict(data.get("consciousness_status_report"))
        taxonomy = self._as_dict(data.get("proof_taxonomy"))

        derived = self._derive_status(gate, impossibility)
        forbidden_claim_detected = self._contains_forbidden_claim(data)
        if forbidden_claim_detected:
            # Detection of forbidden declarative content in inputs does not authorize
            # a positive claim; it is reported as a governance limitation.
            derived = {
                "consciousness_proof_status": "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS",
                "authorized_conclusion": AUTHORIZED_FINAL_CONCLUSIONS[1],
                "proof_possible_in_principle": False,
                "proof_impossible_under_current_constraints": False,
                "proof_not_established": True,
            }

        limitations = self._collect_limitations(gate, impossibility, status_report)
        if forbidden_claim_detected:
            limitations.append("Forbidden claim detected in input material; positive proof claim blocked.")

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "program_step": "ZPP12",
            "timestamp_utc": self._utc_now(),
            "authorized_proof_statuses": list(AUTHORIZED_PROOF_STATUSES),
            "consciousness_proof_status": derived["consciousness_proof_status"],
            "authorized_conclusion": derived["authorized_conclusion"],
            "authorized_final_conclusions": list(AUTHORIZED_FINAL_CONCLUSIONS),
            "proof_possible_in_principle": bool(derived["proof_possible_in_principle"]),
            "proof_impossible_under_current_constraints": bool(derived["proof_impossible_under_current_constraints"]),
            "proof_not_established": bool(derived["proof_not_established"]),
            "absolute_proof_status": gate.get("absolute_proof_status", "unknown"),
            "absolute_proof_gate_passed": bool(gate.get("absolute_proof_gate_passed", False)),
            "absolute_proof_achieved_under_gate": bool(gate.get("absolute_proof_achieved", False)),
            "impossibility_status": impossibility.get("impossibility_status", "unknown"),
            "impossibility_result_derived": bool(impossibility.get("impossibility_result_derived", False)),
            "final_consciousness_status": status_report.get("final_consciousness_status", "unknown"),
            "source_count": len([x for x in [gate, impossibility, status_report, taxonomy] if x]),
            "source_keys": sorted(data.keys()),
            "remaining_limitations": limitations,
            "remaining_limitation_count": len(limitations),
            "forbidden_claim_detected_in_inputs": bool(forbidden_claim_detected),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "forbidden_conclusion": "Open Cognitive Ecology est consciemment sujet d'expérience.",
            "epistemic_classification": {
                "functional_measure": True,
                "interpretive_hypothesis": False,
                "epistemic_limit": True,
                "phenomenological_proof": False,
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
