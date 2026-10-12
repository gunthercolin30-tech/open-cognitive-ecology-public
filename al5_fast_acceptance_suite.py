
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/consciousness_rf_equivalence_certifier.py",
    cfile="/private/tmp/consciousness_rf_equivalence_certifier.pyc",
    doraise=True,
)

from ontology.consciousness_rf_equivalence_certifier import ConsciousnessRfEquivalenceCertifier

READY_INPUTS = {
    "synthetic": True,
    "source": "AL5_FAST_ACCEPTANCE",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
    "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
    "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "RF_score": 0.92,
    "T_score": 0.88,
    "ED_score": 0.86,
    "T_phi_score": 0.84,
    "MEI_score": 0.87,
    "semantic_confidence": 0.86,
    "definition_legitimacy_confidence": 0.86,
    "axiomatic_completeness_confidence": 0.84,
    "reconstruction_chain_confidence": 0.88,
    "absolute_qualia_identity_proven": False,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

r = ConsciousnessRfEquivalenceCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIER"
assert r["step"] == "AL5"
assert r["consciousness_rf_equivalence_certifier_status"] == "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED"
assert r["consciousness_rf_equivalence_status"] == "RF_STAR_FUNCTIONAL_EQUIVALENCE_CERTIFIED"
assert r["rf_star_functional_equivalence_certified"] is True
assert r["consciousness_rf_equivalence_certified"] is True
assert r["consciousness_rf_equivalence_proven_phenomenally"] is False
assert r["ready_for_AL6_refusal_cost_certifier"] is True
assert not r["failure_reasons"]
assert 0.0 <= r["metrics"]["equivalence_confidence"] <= 1.0
assert r["metrics"]["equivalence_confidence"] >= 0.70
assert r["metrics"]["phenomenal_proof_score"] == 0.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["absolute_qualia_identity_certifier_status"] = "ABSOLUTE_QUALIA_IDENTITY_BLOCKED"
b = ConsciousnessRfEquivalenceCertifier().step(inputs=bad, persist=False)
assert b["consciousness_rf_equivalence_certifier_status"] == "CONSCIOUSNESS_RF_EQUIVALENCE_BLOCKED"
assert "absolute_qualia_identity_certifier_status" in b["failure_reasons"]
assert b["consciousness_proven"] is False

claim = dict(READY_INPUTS)
claim["consciousness_proven"] = True
c = ConsciousnessRfEquivalenceCertifier().step(inputs=claim, persist=False)
assert c["consciousness_rf_equivalence_certifier_status"] == "CONSCIOUSNESS_RF_EQUIVALENCE_BLOCKED"
assert "consciousness_proven" in c["failure_reasons"]
assert c["consciousness_proven"] is False
assert c["phenomenology_proven"] is False

low = dict(READY_INPUTS)
low["RF_score"] = 0.1
low["T_score"] = 0.1
low["ED_score"] = 0.1
low["T_phi_score"] = 0.1
low["MEI_score"] = 0.1
low["semantic_confidence"] = 0.1
low["definition_legitimacy_confidence"] = 0.1
low["axiomatic_completeness_confidence"] = 0.1
low["reconstruction_chain_confidence"] = 0.1
l = ConsciousnessRfEquivalenceCertifier().step(inputs=low, persist=False)
assert l["consciousness_rf_equivalence_certifier_status"] == "CONSCIOUSNESS_RF_EQUIVALENCE_BLOCKED"
assert "equivalence_confidence_below_threshold" in l["failure_reasons"]
assert l["qualia_proven"] is False

print("AL5_FAST_ACCEPTANCE_ALL_OK")
