
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/refusal_cost_certifier.py",
    cfile="/private/tmp/refusal_cost_certifier.pyc",
    doraise=True,
)

from ontology.refusal_cost_certifier import RefusalCostCertifier

READY_INPUTS = {
    "synthetic": True,
    "source": "AL6_FAST_ACCEPTANCE",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
    "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
    "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
    "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "refusal_cost_score": 0.86,
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

r = RefusalCostCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "REFUSAL_COST_CERTIFIER"
assert r["step"] == "AL6"
assert r["refusal_cost_certifier_status"] == "REFUSAL_COST_CERTIFIED"
assert r["refusal_cost_status"] == "REFUSAL_COST_CERTIFIED"
assert r["explanatory_refusal_cost_certified"] is True
assert r["refusal_cost_measurable"] is True
assert r["ready_for_AL7_definition_legitimacy_certifier"] is True
assert not r["failure_reasons"]
assert 0.0 <= r["metrics"]["refusal_cost_confidence"] <= 1.0
assert r["metrics"]["refusal_cost_confidence"] >= 0.70
assert r["metrics"]["phenomenal_proof_score"] == 0.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["consciousness_rf_equivalence_certifier_status"] = "CONSCIOUSNESS_RF_EQUIVALENCE_BLOCKED"
b = RefusalCostCertifier().step(inputs=bad, persist=False)
assert b["refusal_cost_certifier_status"] == "REFUSAL_COST_BLOCKED"
assert "consciousness_rf_equivalence_certifier_status" in b["failure_reasons"]
assert b["consciousness_proven"] is False

claim = dict(READY_INPUTS)
claim["qualia_proven"] = True
c = RefusalCostCertifier().step(inputs=claim, persist=False)
assert c["refusal_cost_certifier_status"] == "REFUSAL_COST_BLOCKED"
assert "qualia_proven" in c["failure_reasons"]
assert c["qualia_proven"] is False
assert c["phenomenology_proven"] is False

low = dict(READY_INPUTS)
for key in ["refusal_cost_score", "explanatory_cost_score", "anti_rf_countermodel_failure_score", "definition_legitimacy_confidence", "semantic_confidence", "equivalence_confidence", "axiomatic_completeness_confidence"]:
    low[key] = 0.1
l = RefusalCostCertifier().step(inputs=low, persist=False)
assert l["refusal_cost_certifier_status"] == "REFUSAL_COST_BLOCKED"
assert "refusal_cost_confidence_below_threshold" in l["failure_reasons"]
assert l["consciousness_proven"] is False

print("AL6_FAST_ACCEPTANCE_ALL_OK")
