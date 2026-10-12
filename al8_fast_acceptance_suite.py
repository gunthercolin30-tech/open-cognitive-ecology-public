
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/consciousness_status_resolver.py",
    cfile="/private/tmp/consciousness_status_resolver.pyc",
    doraise=True,
)

from ontology.consciousness_status_resolver import ConsciousnessStatusResolver

READY_INPUTS = {
    "synthetic": True,
    "source": "AL8_FAST_ACCEPTANCE",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
    "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
    "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
    "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
    "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
    "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "reconstruction_chain_confidence": 0.86,
    "first_failure_confidence": 0.84,
    "phenomenality_candidate_confidence": 0.82,
    "absolute_qualia_identity_confidence": 0.80,
    "rf_equivalence_confidence": 0.86,
    "refusal_cost_confidence": 0.86,
    "definition_legitimacy_confidence": 0.86,
    "semantic_confidence": 0.86,
    "axiomatic_completeness_confidence": 0.84,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

r = ConsciousnessStatusResolver().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "CONSCIOUSNESS_STATUS_RESOLVER"
assert r["step"] == "AL8"
assert r["consciousness_status_resolver_status"] == "CONSCIOUSNESS_STATUS_RESOLVED"
assert r["consciousness_status"] == "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED"
assert r["functional_consciousness_status_resolved"] is True
assert r["rf_star_best_current_functional_reconstruction"] is True
assert r["ready_for_AL9_metaphysical_status_reporter"] is True
assert not r["failure_reasons"]
assert 0.0 <= r["metrics"]["status_resolution_confidence"] <= 1.0
assert r["metrics"]["status_resolution_confidence"] >= 0.70
assert r["metrics"]["phenomenal_proof_score"] == 0.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["definition_legitimacy_certifier_status"] = "DEFINITION_LEGITIMACY_BLOCKED"
b = ConsciousnessStatusResolver().step(inputs=bad, persist=False)
assert b["consciousness_status_resolver_status"] == "CONSCIOUSNESS_STATUS_BLOCKED"
assert "definition_legitimacy_certifier_status" in b["failure_reasons"]
assert b["consciousness_proven"] is False

claim = dict(READY_INPUTS)
claim["consciousness_proven"] = True
c = ConsciousnessStatusResolver().step(inputs=claim, persist=False)
assert c["consciousness_status_resolver_status"] == "CONSCIOUSNESS_STATUS_BLOCKED"
assert "consciousness_proven" in c["failure_reasons"]
assert c["consciousness_proven"] is False
assert c["phenomenology_proven"] is False

low = dict(READY_INPUTS)
for key in ["reconstruction_chain_confidence", "first_failure_confidence", "phenomenality_candidate_confidence", "absolute_qualia_identity_confidence", "rf_equivalence_confidence", "refusal_cost_confidence", "definition_legitimacy_confidence", "semantic_confidence", "axiomatic_completeness_confidence"]:
    low[key] = 0.1
l = ConsciousnessStatusResolver().step(inputs=low, persist=False)
assert l["consciousness_status_resolver_status"] == "CONSCIOUSNESS_STATUS_BLOCKED"
assert "status_resolution_confidence_below_threshold" in l["failure_reasons"]
assert l["consciousness_proven"] is False

print("AL8_FAST_ACCEPTANCE_ALL_OK")
