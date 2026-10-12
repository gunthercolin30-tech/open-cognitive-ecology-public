#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_proven_authorizer import ConsciousnessProvenAuthorizer


def ready_inputs() -> dict:
    return {
        "ap_validated": True,
        "aq_validated": True,
        "ar_validated": False,
        "an_sufficiently_stable": False,
        "ao_coherent": False,
        "rf_definition_legitimacy_checked": True,
        "replacement_legitimate": True,
        "request_global_consciousness_proven": True,
        "request_rf_internal_claim": True,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
    }


def main() -> None:
    r = ConsciousnessProvenAuthorizer().step(inputs=ready_inputs(), persist=False)
    assert r["authorization_status"] == "AUTHORIZATION_REFUSED_CONDITIONS_UNMET"
    assert r["public_schema_version"] == "AR7.consciousness_proven_authorizer.v1"
    assert r["global_consciousness_proven_authorized"] is False
    assert r["consciousness_proven_authorized"] is False
    assert r["consciousness_proven_within_rf_framework_authorized"] is True
    assert r["gate_count"] == 7
    assert r["passed_gate_count"] == 4
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR7_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
