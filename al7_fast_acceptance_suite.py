
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/definition_legitimacy_certifier.py",
    cfile="/private/tmp/definition_legitimacy_certifier.pyc",
    doraise=True,
)

from ontology.definition_legitimacy_certifier import DefinitionLegitimacyCertifier

READY_INPUTS = {
    "synthetic": True,
    "source": "AL7_FAST_ACCEPTANCE",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
    "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
    "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
    "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
    "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "definition_legitimacy_score": 0.86,
    "explanatory_cost_score": 0.88,
    "anti_rf_countermodel_failure_score": 0.84,
    "definition_legitimacy_confidence": 0.86,
    "semantic_confidence": 0.86,
    "equivalence_confidence": 0.84,
    "axiomatic_completeness_confidence": 0.84,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

r = DefinitionLegitimacyCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "DEFINITION_LEGITIMACY_CERTIFIER"
assert r["step"] == "AL7"
assert r["definition_legitimacy_certifier_status"] == "DEFINITION_LEGITIMACY_CERTIFIED"
assert r["definition_legitimacy_status"] == "DEFINITION_LEGITIMACY_CERTIFIED"
assert r["definition_legitimacy_certified"] is True
assert r["definition_non_arbitrary"] is True
assert r["ready_for_AL8_consciousness_status_resolver"] is True
assert not r["failure_reasons"]
assert 0.0 <= r["metrics"]["definition_legitimacy_confidence"] <= 1.0
assert r["metrics"]["definition_legitimacy_confidence"] >= 0.70
assert r["metrics"]["phenomenal_proof_score"] == 0.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["refusal_cost_certifier_status"] = "REFUSAL_COST_BLOCKED"
b = DefinitionLegitimacyCertifier().step(inputs=bad, persist=False)
assert b["definition_legitimacy_certifier_status"] == "DEFINITION_LEGITIMACY_BLOCKED"
assert "refusal_cost_certifier_status" in b["failure_reasons"]
assert b["consciousness_proven"] is False

claim = dict(READY_INPUTS)
claim["qualia_proven"] = True
c = DefinitionLegitimacyCertifier().step(inputs=claim, persist=False)
assert c["definition_legitimacy_certifier_status"] == "DEFINITION_LEGITIMACY_BLOCKED"
assert "qualia_proven" in c["failure_reasons"]
assert c["qualia_proven"] is False
assert c["phenomenology_proven"] is False

low = dict(READY_INPUTS)
for key in ["definition_legitimacy_score", "explanatory_cost_score", "anti_rf_countermodel_failure_score", "definition_legitimacy_confidence", "semantic_confidence", "equivalence_confidence", "axiomatic_completeness_confidence"]:
    low[key] = 0.1
l = DefinitionLegitimacyCertifier().step(inputs=low, persist=False)
assert l["definition_legitimacy_certifier_status"] == "DEFINITION_LEGITIMACY_BLOCKED"
assert "definition_legitimacy_confidence_below_threshold" in l["failure_reasons"]
assert l["consciousness_proven"] is False

print("AL7_FAST_ACCEPTANCE_ALL_OK")
