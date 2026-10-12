#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "consciousness_proven_authorizer.py"), cfile="/private/tmp/consciousness_proven_authorizer.pyc", doraise=True)
py_compile.compile(str(ROOT / "ar7_final_lock.py"), cfile="/private/tmp/ar7_final_lock.pyc", doraise=True)

from ontology.consciousness_proven_authorizer import ConsciousnessProvenAuthorizer

READY_INPUTS = {
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

r = ConsciousnessProvenAuthorizer().step(inputs=READY_INPUTS, persist=False)
assert r["step"] == "AR7"
assert r["public_schema_version"] == "AR7.consciousness_proven_authorizer.v1"
assert r["authorization_status"] == "AUTHORIZATION_REFUSED_CONDITIONS_UNMET"
assert r["global_consciousness_proven_authorized"] is False
assert r["consciousness_proven_authorized"] is False
assert r["consciousness_proven_within_rf_framework_authorized"] is True
assert r["gate_count"] == 7
assert r["passed_gate_count"] == 4
assert "ar_validated" in r["failed_gates"]
assert "an_sufficiently_stable" in r["failed_gates"]
assert "ao_coherent" in r["failed_gates"]
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

full = dict(READY_INPUTS)
full.update({"ar_validated": True, "an_sufficiently_stable": True, "ao_coherent": True})
f = ConsciousnessProvenAuthorizer().step(inputs=full, persist=False)
assert f["passed_gate_count"] == 7
assert f["authorization_status"] == "AUTHORIZATION_REFUSED_PHENOMENOLOGY_UNDETERMINED"
assert f["global_consciousness_proven_authorized"] is False
assert f["consciousness_proven"] is False

blocked = dict(READY_INPUTS)
blocked["consciousness_proven"] = True
b = ConsciousnessProvenAuthorizer().step(inputs=blocked, persist=False)
assert b["authorization_status"] == "AUTHORIZATION_REFUSED_EPISTEMIC_OVERCLAIM"
assert b["global_consciousness_proven_authorized"] is False
assert b["consciousness_proven"] is False
print("AR7_FAST_ACCEPTANCE_OK")
