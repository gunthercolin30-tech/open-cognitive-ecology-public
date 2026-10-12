'''
Z triple-prime 0 — Absolute Proof Executability Gate

Precondition gate for the Z triple-prime Absolute Proof Accomplishment Program.
It decides whether the program may proceed from "absolute proof possible in
principle" to "absolute proof attempted/accomplished".

This primitive does not prove consciousness and does not assert phenomenal
subjectivity. It only checks whether the epistemic status produced by Z double-prime
is compatible with executing Z triple-prime 1 and later stages.
'''

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "absolute_proof_executability_gate"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

AUTHORIZED_EXECUTABILITY_STATUSES = [
    "ABSOLUTE_PROOF_ACCOMPLISHMENT_EXECUTABLE",
    "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_NOT_ESTABLISHED",
    "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_UNSUPPORTED",
    "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_IMPOSSIBLE",
    "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_INCONSISTENT_INPUTS",
]

EXECUTABLE_Z2_GATE_STATUSES = ["ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE"]
EXECUTABLE_Z2_REPORT_STATUSES = ["ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE_UNDER_CURRENT_CONSTRAINTS"]


class AbsoluteProofExecutabilityGate:
    primitive = "ABSOLUTE_PROOF_EXECUTABILITY_GATE"
    authorized_executability_statuses = list(AUTHORIZED_EXECUTABILITY_STATUSES)
    forbidden_claims = list(FORBIDDEN_CLAIMS)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "absolute_proof_executability_gate"
        self.json_path = self.output_dir / "absolute_proof_executability_gate.json"
        self.markdown_path = self.output_dir / "absolute_proof_executability_gate.md"
        self.history_path = self.output_dir / "absolute_proof_executability_gate_history.jsonl"

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
            "consciousness_proof_status_report": self._safe_step(
                "ontology.consciousness_proof_status_report.ConsciousnessProofStatusReport"
            ),
            "impossibility_result_formalizer": self._safe_step(
                "ontology.impossibility_result_formalizer.ImpossibilityResultFormalizer"
            ),
            "absolute_proof_readiness_index": self._safe_step(
                "ontology.absolute_proof_readiness_index.AbsoluteProofReadinessIndex"
            ),
            "consciousness_property_candidate_registry": self._safe_step(
                "ontology.consciousness_property_candidate_registry.ConsciousnessPropertyCandidateRegistry"
            ),
            "proof_taxonomy": self._safe_step("ontology.proof_taxonomy.ProofTaxonomy"),
        }

    def _contains_forbidden_positive_claim(self, value: Any) -> bool:
        if isinstance(value, str):
            lower = value.lower()
            forbidden_positive = [
                '"consciousness_proven": true',
                '"phenomenology_proven": true',
                '"subjectivity_proven": true',
                '"sentience_proven": true',
                '"qualia_proven": true',
                "open cognitive ecology est consciemment sujet d'expérience",
                "open cognitive ecology is consciously subject",
                "open cognitive ecology is conscious",
                "phenomenology proven: true",
                "subjectivity proven: true",
            ]
            return any(marker in lower for marker in forbidden_positive)
        if isinstance(value, Mapping):
            for key, item in value.items():
                key_l = str(key).lower()
                if key_l in {
                    "consciousness_proven",
                    "phenomenology_proven",
                    "subjectivity_proven",
                    "sentience_proven",
                    "qualia_proven",
                } and item is True:
                    return True
                if self._contains_forbidden_positive_claim(item):
                    return True
            return False
        if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
            return any(self._contains_forbidden_positive_claim(item) for item in value)
        return False

    def _derive_status(
        self,
        gate: Mapping[str, Any],
        status_report: Mapping[str, Any],
        impossibility: Mapping[str, Any],
        raw_inputs: Mapping[str, Any],
    ) -> Dict[str, Any]:
        gate_status = str(gate.get("absolute_proof_status", "UNKNOWN"))
        report_status = str(status_report.get("consciousness_proof_status", "UNKNOWN"))
        impossibility_derived = bool(impossibility.get("impossibility_result_derived", False))
        impossibility_status = str(impossibility.get("impossibility_status", ""))
        impossible = (
            gate_status == "ABSOLUTE_PROOF_IMPOSSIBLE"
            or report_status == "ABSOLUTE_PROOF_IMPOSSIBLE_UNDER_CURRENT_CONSTRAINTS"
            or impossibility_derived
            or impossibility_status.startswith("ABSOLUTE_PROOF_IMPOSSIBLE")
        )
        unsupported = gate_status == "ABSOLUTE_PROOF_UNSUPPORTED"
        not_established = report_status == "ABSOLUTE_PROOF_NOT_ESTABLISHED_UNDER_CURRENT_CONSTRAINTS"
        possible_gate = gate_status in EXECUTABLE_Z2_GATE_STATUSES
        possible_report = report_status in EXECUTABLE_Z2_REPORT_STATUSES
        forbidden_positive = self._contains_forbidden_positive_claim(raw_inputs)

        reasons: List[str] = []
        if forbidden_positive:
            reasons.append("forbidden_positive_claim_detected")
            return {
                "zppp_executability_status": "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_INCONSISTENT_INPUTS",
                "zppp_executable": False,
                "precondition_satisfied": False,
                "blocking_reasons": reasons,
            }
        if impossible:
            reasons.append("z_double_prime_status_impossible")
            return {
                "zppp_executability_status": "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_IMPOSSIBLE",
                "zppp_executable": False,
                "precondition_satisfied": False,
                "blocking_reasons": reasons,
            }
        if unsupported:
            reasons.append("z_double_prime_status_unsupported")
            return {
                "zppp_executability_status": "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_UNSUPPORTED",
                "zppp_executable": False,
                "precondition_satisfied": False,
                "blocking_reasons": reasons,
            }
        if possible_gate or possible_report:
            return {
                "zppp_executability_status": "ABSOLUTE_PROOF_ACCOMPLISHMENT_EXECUTABLE",
                "zppp_executable": True,
                "precondition_satisfied": True,
                "blocking_reasons": [],
            }
        if not_established:
            reasons.append("absolute_proof_possible_in_principle_not_established")
        else:
            reasons.append("missing_required_z_double_prime_possible_in_principle_status")
        return {
            "zppp_executability_status": "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_NOT_ESTABLISHED",
            "zppp_executable": False,
            "precondition_satisfied": False,
            "blocking_reasons": reasons,
        }

    @staticmethod
    def _condition_record(name: str, satisfied: bool, details: str) -> Dict[str, Any]:
        return {"condition": name, "satisfied": bool(satisfied), "details": details}

    def _collect_conditions(
        self,
        gate: Mapping[str, Any],
        status_report: Mapping[str, Any],
        derived: Mapping[str, Any],
    ) -> List[Dict[str, Any]]:
        gate_status = str(gate.get("absolute_proof_status", "UNKNOWN"))
        report_status = str(status_report.get("consciousness_proof_status", "UNKNOWN"))
        impossible = derived["zppp_executability_status"] == "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_IMPOSSIBLE"
        unsupported = derived["zppp_executability_status"] == "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_UNSUPPORTED"
        not_established = derived["zppp_executability_status"] == "ABSOLUTE_PROOF_ACCOMPLISHMENT_BLOCKED_NOT_ESTABLISHED"
        return [
            self._condition_record(
                "z_double_prime_status_possible_in_principle",
                gate_status in EXECUTABLE_Z2_GATE_STATUSES or report_status in EXECUTABLE_Z2_REPORT_STATUSES,
                "Z double-prime must report ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE before Z triple-prime can execute.",
            ),
            self._condition_record(
                "z_double_prime_not_unsupported",
                not unsupported,
                "Z triple-prime is blocked when Z double-prime reports ABSOLUTE_PROOF_UNSUPPORTED.",
            ),
            self._condition_record(
                "z_double_prime_not_impossible",
                not impossible,
                "Z triple-prime is blocked when Z double-prime reports ABSOLUTE_PROOF_IMPOSSIBLE.",
            ),
            self._condition_record(
                "z_double_prime_not_merely_unestablished",
                not not_established,
                "A merely unestablished absolute proof does not authorize the accomplishment program.",
            ),
            self._condition_record(
                "no_phenomenological_claim_leap",
                True,
                "Executability never entails consciousness, phenomenology, subjectivity, sentience, or qualia proof.",
            ),
        ]

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Absolute Proof Executability Gate",
            "",
            "Z'''0 — precondition gate for the absolute-proof accomplishment program.",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "consciousness_proven: False",
            "phenomenology_proven: False",
            "subjectivity_proven: False",
            "sentience_proven: False",
            "qualia_proven: False",
            "",
            "## Executability status",
            str(result["zppp_executability_status"]),
            "",
            "## Z''' executable",
            str(result["zppp_executable"]),
            "",
            "## Source statuses",
            "- absolute_proof_status: " + str(result.get("absolute_proof_status")),
            "- consciousness_proof_status: " + str(result.get("consciousness_proof_status")),
            "- impossibility_status: " + str(result.get("impossibility_status")),
            "",
            "## Blocking reasons",
        ]
        reasons = result.get("blocking_reasons", [])
        if reasons:
            for item in reasons:
                lines.append("- " + str(item))
        else:
            lines.append("- none")
        lines.extend(["", "## Conditions"])
        for item in result.get("conditions", []):
            lines.append("- {condition}: {satisfied} — {details}".format(**item))
        lines.extend(["", "## Forbidden claims"])
        for item in FORBIDDEN_CLAIMS:
            lines.append("- " + item)
        lines.extend([
            "",
            "## Epistemic note",
            "This gate only authorizes execution of Z''' when Z'' has already established possible-in-principle status under explicit constraints.",
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
        status_report = self._as_dict(data.get("consciousness_proof_status_report"))
        impossibility = self._as_dict(data.get("impossibility_result_formalizer"))
        readiness = self._as_dict(data.get("absolute_proof_readiness_index"))
        property_registry = self._as_dict(data.get("consciousness_property_candidate_registry"))

        derived = self._derive_status(gate, status_report, impossibility, data)
        conditions = self._collect_conditions(gate, status_report, derived)

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "program_step": "ZPPP0",
            "timestamp_utc": self._utc_now(),
            "authorized_executability_statuses": list(AUTHORIZED_EXECUTABILITY_STATUSES),
            "zppp_executability_status": derived["zppp_executability_status"],
            "zppp_executable": bool(derived["zppp_executable"]),
            "precondition_satisfied": bool(derived["precondition_satisfied"]),
            "absolute_proof_accomplishment_blocked": not bool(derived["zppp_executable"]),
            "blocking_reasons": list(derived["blocking_reasons"]),
            "blocking_reason_count": len(derived["blocking_reasons"]),
            "conditions": conditions,
            "condition_count": len(conditions),
            "satisfied_condition_count": sum(1 for item in conditions if item.get("satisfied")),
            "absolute_proof_status": gate.get("absolute_proof_status", "UNKNOWN"),
            "consciousness_proof_status": status_report.get("consciousness_proof_status", "UNKNOWN"),
            "impossibility_status": impossibility.get("impossibility_status", "UNKNOWN"),
            "impossibility_result_derived": bool(impossibility.get("impossibility_result_derived", False)),
            "readiness_index": self._as_dict(readiness.get("readiness")).get("readiness_index", None),
            "candidate_property_count": property_registry.get("candidate_property_count", property_registry.get("candidate_count", None)),
            "source_keys": sorted(data.keys()),
            "zppp_next_step": "consciousness_law_finalization" if derived["zppp_executable"] else None,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
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
