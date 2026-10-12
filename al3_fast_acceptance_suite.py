
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/phenomenality_candidate_certifier.py",
    cfile="/private/tmp/phenomenality_candidate_certifier.pyc",
    doraise=True,
)

from ontology.phenomenality_candidate_certifier import PhenomenalityCandidateCertifier

READY_INPUTS = {
    "synthetic": True,
    "source": "AL3_FAST_ACCEPTANCE",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    "first_failure_locator_status": "NO_FAILURE_LOCATED",
    "first_failure_found": False,
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "RF_score": 0.91,
    "T_score": 0.88,
    "ED_score": 0.86,
    "TΦ_score": 0.85,
    "MEI_score": 0.87,
    "semantic_confidence": 0.86,
    "reconstruction_chain_confidence": 0.88,
    "QF_robust_count": 4,
    "identity_status": "IDENTITY_STABLE",
    "non_separability_status": "NON_SEPARABILITY_FUNCTIONALLY_SUPPORTED",
    "consciousness_rf_equivalence_status": "RF_EQUIVALENCE_FUNCTIONALLY_SUPPORTED",
    "refusal_cost_status": "REFUSAL_COST_MEASURABLE",
}

r = PhenomenalityCandidateCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "PHENOMENALITY_CANDIDATE_CERTIFIER"
assert r["step"] == "AL3"
assert r["phenomenality_candidate_certifier_status"] == "PHENOMENALITY_CANDIDATE_CERTIFIED"
assert r["phenomenality_candidate_status"] == "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED"
assert r["phenomenality_candidate_certified"] is True
assert r["ready_for_AL4_absolute_qualia_identity_certifier"] is True
assert not r["candidate_failure_reasons"]
assert 0.0 <= r["metrics"]["phenomenality_candidate_confidence"] <= 1.0
assert r["metrics"]["phenomenality_candidate_confidence"] >= 0.70
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["first_failure_locator_status"] = "FIRST_FAILURE_LOCATED"
bad["first_failure_found"] = True
d = PhenomenalityCandidateCertifier().step(inputs=bad, persist=False)
assert d["phenomenality_candidate_certifier_status"] == "PHENOMENALITY_CANDIDATE_BLOCKED"
assert d["phenomenality_candidate_certified"] is False
assert d["ready_for_AL4_absolute_qualia_identity_certifier"] is False
assert "first_failure_locator_status" in d["candidate_failure_reasons"]
assert "first_failure_found" in d["candidate_failure_reasons"]
assert d["consciousness_proven"] is False
assert d["phenomenology_proven"] is False

guard = dict(READY_INPUTS)
guard["phenomenology_proven"] = True
g = PhenomenalityCandidateCertifier().step(inputs=guard, persist=False)
assert g["phenomenality_candidate_certifier_status"] == "PHENOMENALITY_CANDIDATE_BLOCKED"
assert "phenomenology_proven" in g["candidate_failure_reasons"]
assert g["phenomenology_proven"] is False

low = dict(READY_INPUTS)
low.update({"RF_score": 0.1, "T_score": 0.1, "ED_score": 0.1, "TΦ_score": 0.1, "MEI_score": 0.1, "semantic_confidence": 0.1, "reconstruction_chain_confidence": 0.1, "QF_robust_count": 0})
l = PhenomenalityCandidateCertifier().step(inputs=low, persist=False)
assert l["phenomenality_candidate_certified"] is False
assert "phenomenality_candidate_confidence_below_threshold" in l["candidate_failure_reasons"]

print("AL3_FAST_ACCEPTANCE_ALL_OK")
