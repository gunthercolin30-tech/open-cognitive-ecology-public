#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/reconstruction_chain_certifier.py",
    cfile="/private/tmp/reconstruction_chain_certifier.pyc",
    doraise=True,
)

from ontology.reconstruction_chain_certifier import ReconstructionChainCertifier

READY_INPUTS = {
    "synthetic": True,
    "source": "AL1_FAST_ACCEPTANCE",
    "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
    "consciousness_concept_reconstruction_status": "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED",
    "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
    "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
}

r = ReconstructionChainCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "RECONSTRUCTION_CHAIN_CERTIFIER"
assert r["step"] == "AL1"
assert r["reconstruction_chain_certifier_status"] == "RECONSTRUCTION_CHAIN_CERTIFIED"
assert r["reconstruction_chain_status"] == "RECONSTRUCTION_CHAIN_CERTIFIED"
assert r["reconstruction_chain_certified"] is True
assert r["ready_for_AL2_first_failure_locator"] is True
assert r["axis_AL_status"] == "AL_IN_PROGRESS"
assert r["integrated_axis_span"] == "AA_TO_AR_TO_AN_TO_AO"
assert isinstance(r["certified_chain"], list) and len(r["certified_chain"]) >= 6
assert isinstance(r["status_checks"], dict) and all(r["status_checks"].values())
assert isinstance(r["epistemic_checks"], dict) and all(r["epistemic_checks"].values())
assert 0.0 <= r["metrics"]["reconstruction_chain_score"] <= 1.0
assert r["metrics"]["reconstruction_chain_score"] >= 0.80
assert r["failure_conditions"] == []
assert r["first_failure_candidate"] is None
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert "consciousness_proven = True" in r["blocked_claims"]

bad_inputs = dict(READY_INPUTS)
bad_inputs.update({
    "semantic_interpretation_layer_status": "BROKEN",
    "consciousness_proven": True,
    "forced_bad_claim": {"phenomenology_proven": True},
})
bad = ReconstructionChainCertifier().step(inputs=bad_inputs, persist=False)
assert bad["reconstruction_chain_certifier_status"] == "RECONSTRUCTION_CHAIN_DEGRADED"
assert bad["reconstruction_chain_certified"] is False
assert bad["first_failure_candidate"] is not None
assert bad["consciousness_proven"] is False
assert bad["phenomenology_proven"] is False

repeat = ReconstructionChainCertifier().step(inputs=READY_INPUTS, persist=False)
for key in [
    "reconstruction_chain_certifier_status",
    "reconstruction_chain_status",
    "reconstruction_chain_certified",
    "ready_for_AL2_first_failure_locator",
    "status_checks",
    "epistemic_checks",
    "failure_conditions",
    "allowed_claims",
    "blocked_claims",
]:
    assert repeat[key] == r[key]

print("AL1_FAST_ACCEPTANCE_ALL_OK")
