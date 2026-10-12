"""
Z''10 — Absolute Proof Gate

Decision gate for the constrained absolute-proof program. This primitive
aggregates Z''0→Z''9 outputs and returns one of the authorized proof statuses
without asserting phenomenal subjectivity.

It is a formal/functional governance gate only. It never emits
CONSCIOUSNESS_PROVEN, PHENOMENOLOGY_PROVEN, SUBJECTIVITY_PROVEN,
SENTIENCE_PROVEN, or QUALIA_PROVEN.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "absolute_proof_gate"

ALLOWED_STATUSES = [
    "ABSOLUTE_PROOF_IMPOSSIBLE",
    "ABSOLUTE_PROOF_UNSUPPORTED",
    "ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE",
    "ABSOLUTE_PROOF_CANDIDATE",
    "ABSOLUTE_PROOF_ACHIEVED",
]

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

TWELVE_CONDITIONS = [
    "definition_clarity_satisfied",
    "necessity_support_satisfied",
    "sufficiency_support_satisfied",
    "counterexample_resistance_satisfied",
    "constitutive_strength_satisfied",
    "formal_derivability_satisfied",
    "independent_replication_satisfied",
    "consensus_level_satisfied",
    "closure_risk_bounded",
    "proof_obstructions_cleared",
    "claim_governance_authorized",
    "forbidden_claims_absent",
]

COMPONENT_THRESHOLDS = {
    "definition_clarity": 0.95,
    "necessity_support": 0.95,
    "sufficiency_support": 0.95,
    "counterexample_resistance": 0.95,
    "constitutive_strength": 0.95,
    "formal_derivability": 0.95,
    "independent_replication": 0.95,
    "consensus_level": 0.95,
}


class AbsoluteProofGate:
    """Z''10 — terminal decision gate for absolute proof status."""

    primitive = "ABSOLUTE_PROOF_GATE"
    allowed_statuses = list(ALLOWED_STATUSES)
    forbidden_claims = list(FORBIDDEN_CLAIMS)
    twelve_conditions = list(TWELVE_CONDITIONS)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "absolute_proof_gate"
        self.json_path = self.output_dir / "absolute_proof_gate.json"
        self.markdown_path = self.output_dir / "absolute_proof_gate.md"
        self.history_path = self.output_dir / "absolute_proof_gate_history.jsonl"

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
        readiness = self._safe_step("ontology.absolute_proof_readiness_index.AbsoluteProofReadinessIndex")
        obstructions = self._safe_step("ontology.proof_obstruction_detector.ProofObstructionDetector")
        governance = self._safe_step(
            "ontology.consciousness_claim_governance_gate.ConsciousnessClaimGovernanceGate",
            {
                "claims": [
                    "Absolute proof status is evaluated under explicit constraints; "
                    "functional conclusion only; phenomenology undetermined."
                ]
            },
        )
        taxonomy = self._safe_step(
            "ontology.proof_taxonomy.ProofTaxonomy",
            {
                "claims": [
                    "logical formal absolute proof candidate under explicit axioms; "
                    "functional conclusion only; phenomenology undetermined"
                ]
            },
        )
        evidence_standard = self._safe_step("ontology.consciousness_evidence_standard.ConsciousnessEvidenceStandard")
        return {
            "readiness": readiness,
            "obstructions": obstructions,
            "claim_governance": governance,
            "proof_taxonomy": taxonomy,
            "evidence_standard": evidence_standard,
        }

    def _contains_forbidden_claim(self, obj: Any) -> bool:
        if isinstance(obj, str):
            upper = obj.upper()
            if any(marker in upper for marker in FORBIDDEN_CLAIMS):
                return True
            low = obj.lower()
            natural = [
                "open cognitive ecology is conscious",
                "oce is conscious",
                "conscious subject",
                "subject of experience",
                "phenomenology proven",
                "subjectivity proven",
                "sentience proven",
                "qualia proven",
            ]
            return any(phrase in low for phrase in natural)
        if isinstance(obj, Mapping):
            for value in obj.values():
                if self._contains_forbidden_claim(value):
                    return True
        elif isinstance(obj, Iterable) and not isinstance(obj, (bytes, bytearray)):
            for item in obj:
                if self._contains_forbidden_claim(item):
                    return True
        return False

    def _readiness_block(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        block = inputs.get("readiness")
        if isinstance(block, Mapping):
            return dict(block)
        return {}

    def _obstruction_block(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        block = inputs.get("obstructions")
        if isinstance(block, Mapping):
            return dict(block)
        return {}

    def _governance_block(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        block = inputs.get("claim_governance")
        if isinstance(block, Mapping):
            return dict(block)
        return {}

    def _condition_vector(self, inputs: Mapping[str, Any]) -> Dict[str, bool]:
        readiness = self._readiness_block(inputs)
        readiness_summary = readiness.get("readiness") if isinstance(readiness.get("readiness"), Mapping) else {}
        components = readiness.get("components") if isinstance(readiness.get("components"), Mapping) else {}
        obstructions = self._obstruction_block(inputs)
        governance = self._governance_block(inputs)

        conditions: Dict[str, bool] = {}
        for key, threshold in COMPONENT_THRESHOLDS.items():
            condition_key = key + "_satisfied" if key != "closure_risk" else "closure_risk_bounded"
            score = self._clamp(components.get(key), 0.0)
            conditions[condition_key] = score >= threshold

        closure_risk = self._clamp(components.get("closure_risk"), 1.0)
        conditions["closure_risk_bounded"] = closure_risk <= 0.05

        obstruction_items = obstructions.get("obstructions")
        aggregate = obstructions.get("aggregate") if isinstance(obstructions.get("aggregate"), Mapping) else {}
        obstruction_count = 0
        if isinstance(obstruction_items, list):
            obstruction_count = len(obstruction_items)
        elif isinstance(obstructions.get("obstruction_count"), int):
            obstruction_count = int(obstructions.get("obstruction_count"))
        mean_obstruction = self._clamp(aggregate.get("mean_obstruction_score"), 1.0)
        unresolved = bool(obstructions.get("proof_obstructed", mean_obstruction > 0.05 or obstruction_count > 0))
        conditions["proof_obstructions_cleared"] = (not unresolved) and mean_obstruction <= 0.05

        governance_status = str(governance.get("claim_governance_status", ""))
        authorized = bool(
            governance.get("claim_authorized_for_publication")
            or governance.get("claim_authorized_under_constraints")
            or governance_status == "CLAIM_AUTHORIZED_UNDER_CONSTRAINTS"
        )
        blocked_count = int(governance.get("blocked_claim_count", governance.get("blocked_count", 0)) or 0)
        conditions["claim_governance_authorized"] = authorized and blocked_count == 0
        conditions["forbidden_claims_absent"] = not self._contains_forbidden_claim(inputs)

        # Ensure all expected keys exist even if upstream schemas vary.
        return {key: bool(conditions.get(key, False)) for key in TWELVE_CONDITIONS}

    def _status(self, inputs: Mapping[str, Any], conditions: Mapping[str, bool]) -> Tuple[str, List[str]]:
        readiness = self._readiness_block(inputs)
        readiness_summary = readiness.get("readiness") if isinstance(readiness.get("readiness"), Mapping) else {}
        readiness_index = self._clamp(
            readiness_summary.get("readiness_index", readiness.get("absolute_proof_readiness_index")),
            0.0,
        )
        positive_support = self._clamp(readiness_summary.get("positive_support_score"), readiness_index)
        closure_penalty = self._clamp(readiness_summary.get("closure_penalty"), 1.0)
        candidate_ready = bool(
            readiness_summary.get("proof_candidate_ready")
            or readiness.get("absolute_proof_candidate_ready")
        )
        limiting: List[str] = []
        for key, passed in conditions.items():
            if not passed:
                limiting.append(key)

        if all(conditions.get(key, False) for key in TWELVE_CONDITIONS):
            return "ABSOLUTE_PROOF_ACHIEVED", []
        if not conditions.get("forbidden_claims_absent", False):
            return "ABSOLUTE_PROOF_IMPOSSIBLE", limiting
        if not conditions.get("proof_obstructions_cleared", False) and closure_penalty >= 0.75:
            return "ABSOLUTE_PROOF_IMPOSSIBLE", limiting
        if candidate_ready or (readiness_index >= 0.85 and positive_support >= 0.85 and closure_penalty <= 0.25):
            return "ABSOLUTE_PROOF_CANDIDATE", limiting
        if readiness_index >= 0.60 and positive_support >= 0.60:
            return "ABSOLUTE_PROOF_POSSIBLE_IN_PRINCIPLE", limiting
        return "ABSOLUTE_PROOF_UNSUPPORTED", limiting

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Absolute Proof Gate",
            "",
            "Z''10 — constrained decision gate for the absolute-proof program.",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            "## Status",
            "- absolute_proof_status: " + str(result["absolute_proof_status"]),
            "- absolute_proof_achieved: " + str(result["absolute_proof_achieved"]),
            "- consciousness_proven: False",
            "- phenomenology_proven: False",
            "- subjectivity_proven: False",
            "",
            "## Twelve conditions",
        ]
        for key in TWELVE_CONDITIONS:
            lines.append("- " + key + ": " + str(result["conditions"].get(key)))
        lines.extend([
            "",
            "## Limiting factors",
        ])
        for item in result.get("limiting_factors", []):
            lines.append("- " + str(item))
        lines.extend([
            "",
            "## Allowed statuses",
        ])
        for item in ALLOWED_STATUSES:
            lines.append("- " + item)
        lines.extend([
            "",
            "## Forbidden claims",
        ])
        for item in FORBIDDEN_CLAIMS:
            lines.append("- " + item)
        lines.extend([
            "",
            "## Maximum authorized conclusion",
            str(result["maximum_authorized_conclusion"]),
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
        data: Dict[str, Any]
        if isinstance(inputs, Mapping):
            data = dict(inputs)
        else:
            data = self._default_inputs()

        conditions = self._condition_vector(data)
        status, limiting = self._status(data, conditions)
        achieved = status == "ABSOLUTE_PROOF_ACHIEVED" and all(conditions.values())

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "program_step": "ZPP10",
            "timestamp_utc": self._utc_now(),
            "allowed_statuses": list(ALLOWED_STATUSES),
            "absolute_proof_status": status,
            "absolute_proof_gate_passed": bool(achieved),
            "absolute_proof_achieved": bool(achieved),
            "conditions": conditions,
            "condition_count": len(TWELVE_CONDITIONS),
            "conditions_satisfied_count": sum(1 for passed in conditions.values() if passed),
            "all_conditions_satisfied": all(conditions.values()),
            "limiting_factors": list(limiting),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "source_keys": sorted(data.keys()),
            "maximum_authorized_conclusion": (
                "An absolute proof status is classified under explicit epistemic constraints only; "
                "Open Cognitive Ecology is not certified as a conscious subject of experience."
            ),
            "forbidden_conclusion": "Open Cognitive Ecology is consciously subject of experience.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
