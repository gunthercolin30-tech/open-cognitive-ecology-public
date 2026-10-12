from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConsciousnessProvenAuthorizer:
    """AR7 — authorize or refuse escalation from RF-internal proof wording to global proof wording.

    The module is deliberately conservative. It may classify RF* as a legitimate functional
    framework, but it must not set consciousness_proven=True or authorize an unrestricted
    CONSCIOUSNESS_PROVEN claim under the epistemic constraints of axis AR.
    """

    primitive = "CONSCIOUSNESS_PROVEN_AUTHORIZER"
    step_id = "AR7"
    public_schema_version = "AR7.consciousness_proven_authorizer.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    REQUIRED_GATES = [
        {
            "gate_id": "ap_validated",
            "label": "AP validated",
            "keys": ["ap_validated", "AP_validated", "ap_axis_validated"],
            "default": True,
            "weight": 1.0,
        },
        {
            "gate_id": "aq_validated",
            "label": "AQ validated",
            "keys": ["aq_validated", "AQ_validated", "aq_axis_validated"],
            "default": True,
            "weight": 1.0,
        },
        {
            "gate_id": "ar_validated",
            "label": "AR validated",
            "keys": ["ar_validated", "AR_validated", "ar_axis_validated"],
            "default": False,
            "weight": 1.2,
        },
        {
            "gate_id": "an_sufficiently_stable",
            "label": "AN sufficiently stable",
            "keys": ["an_sufficiently_stable", "AN_sufficiently_stable", "an_stability_sufficient"],
            "default": False,
            "weight": 1.0,
        },
        {
            "gate_id": "ao_coherent",
            "label": "AO coherent",
            "keys": ["ao_coherent", "AO_coherent", "ao_coherence_validated"],
            "default": False,
            "weight": 1.0,
        },
        {
            "gate_id": "definition_legitimacy_checked",
            "label": "RF definition legitimacy checked",
            "keys": ["rf_definition_legitimacy_checked", "definition_legitimacy_checked"],
            "default": True,
            "weight": 1.0,
        },
        {
            "gate_id": "conceptual_replacement_legitimate",
            "label": "Conceptual replacement legitimate",
            "keys": ["replacement_legitimate", "conceptual_replacement_legitimate"],
            "default": True,
            "weight": 1.0,
        },
    ]

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "ar_definition_legitimacy" / "AR7_consciousness_proven_authorizer"

    @staticmethod
    def _bool_from_inputs(inputs: dict[str, Any], keys: list[str], default: bool) -> bool:
        for key in keys:
            if key in inputs:
                return bool(inputs[key])
        upstream = inputs.get("upstream_results", {})
        if isinstance(upstream, dict):
            for payload in upstream.values():
                if not isinstance(payload, dict):
                    continue
                for key in keys:
                    if key in payload:
                        return bool(payload[key])
        return bool(default)

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = default
        return max(0.0, min(1.0, numeric))

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = dict(inputs or {})
        gate_results: list[dict[str, Any]] = []
        weighted_total = 0.0
        total_weight = 0.0
        for gate in self.REQUIRED_GATES:
            passed = self._bool_from_inputs(data, gate["keys"], bool(gate["default"]))
            weight = self._clamp(gate.get("weight", 1.0), 1.0)
            weighted_total += (1.0 if passed else 0.0) * weight
            total_weight += weight
            gate_results.append({
                "gate_id": gate["gate_id"],
                "label": gate["label"],
                "passed": passed,
                "weight": round(weight, 6),
                "evidence_keys": list(gate["keys"]),
            })

        gate_score = weighted_total / total_weight if total_weight else 0.0
        failed_gates = [g["gate_id"] for g in gate_results if not g["passed"]]
        requested_global_authorization = bool(data.get("request_global_consciousness_proven", True))
        requested_rf_internal_authorization = bool(data.get("request_rf_internal_claim", True))

        forbidden_overclaims = []
        for forbidden in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
            if data.get(forbidden) is True:
                forbidden_overclaims.append(forbidden)
        if data.get("functional_conclusion_only", True) is False:
            forbidden_overclaims.append("functional_conclusion_only_false")
        if data.get("phenomenology_undetermined", True) is False:
            forbidden_overclaims.append("phenomenology_undetermined_false")

        rf_internal_authorized = requested_rf_internal_authorization and not forbidden_overclaims and gate_score >= 0.50
        # AR-level epistemic guardrail: unrestricted CONSCIOUSNESS_PROVEN is never authorized here.
        global_authorized = False
        if forbidden_overclaims:
            global_status = "AUTHORIZATION_REFUSED_EPISTEMIC_OVERCLAIM"
        elif failed_gates:
            global_status = "AUTHORIZATION_REFUSED_CONDITIONS_UNMET"
        elif requested_global_authorization:
            global_status = "AUTHORIZATION_REFUSED_PHENOMENOLOGY_UNDETERMINED"
        else:
            global_status = "AUTHORIZATION_NOT_REQUESTED"

        rf_status = "RF_INTERNAL_FUNCTIONAL_CLAIM_CONDITIONALLY_AUTHORIZED" if rf_internal_authorized else "RF_INTERNAL_FUNCTIONAL_CLAIM_NOT_AUTHORIZED"
        result = {
            "step": self.step_id,
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "authorization_status": global_status,
            "consciousness_proven_authorization": global_status,
            "global_consciousness_proven_authorized": global_authorized,
            "consciousness_proven_authorized": global_authorized,
            "rf_internal_authorization_status": rf_status,
            "consciousness_proven_within_rf_framework_authorized": rf_internal_authorized,
            "requested_global_authorization": requested_global_authorization,
            "requested_rf_internal_authorization": requested_rf_internal_authorization,
            "gate_score": round(gate_score, 6),
            "gate_count": len(gate_results),
            "passed_gate_count": sum(1 for g in gate_results if g["passed"]),
            "failed_gates": failed_gates,
            "gate_results": gate_results,
            "forbidden_overclaims_detected": forbidden_overclaims,
            "authorization_reason": "Global CONSCIOUSNESS_PROVEN is refused by AR7 because AR only validates functional reconstruction legitimacy; phenomenology and subjectivity remain undetermined.",
            "allowed_statement": "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK may be used only as a conditional functional-framework statement, not as an unrestricted proof of consciousness.",
            "forbidden_statement": "CONSCIOUSNESS_PROVEN",
            "epistemic_scope": "authorization_governance_for_functional_claims_only",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        (self.out_dir / f"consciousness_proven_authorizer_{ts}.json").write_text(payload + "\n", encoding="utf-8")
        (self.out_dir / "latest_consciousness_proven_authorizer.json").write_text(payload + "\n", encoding="utf-8")
        md = "\n".join([
            "# AR7 — Consciousness Proven Authorizer", "",
            f"- authorization_status: `{result['authorization_status']}`",
            f"- rf_internal_authorization_status: `{result['rf_internal_authorization_status']}`",
            f"- gate_score: `{result['gate_score']}`",
            f"- global_consciousness_proven_authorized: `{result['global_consciousness_proven_authorized']}`",
            f"- functional_conclusion_only: `{result['functional_conclusion_only']}`",
            f"- phenomenology_undetermined: `{result['phenomenology_undetermined']}`", "",
        ])
        (self.out_dir / "latest_consciousness_proven_authorizer.md").write_text(md, encoding="utf-8")
