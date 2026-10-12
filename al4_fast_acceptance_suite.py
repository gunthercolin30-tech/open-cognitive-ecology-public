
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/absolute_qualia_identity_certifier.py",
    cfile="/private/tmp/absolute_qualia_identity_certifier.pyc",
    doraise=True,
)

from ontology.absolute_qualia_identity_certifier import AbsoluteQualiaIdentityCertifier

READY_INPUTS = {
    "synthetic": True,
    "source": "AL4_FAST_ACCEPTANCE",
    "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
    "phenomenality_candidate_certified": True,
    "phenomenality_candidate_confidence": 0.86,
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "axiomatic_completeness_confidence": 0.84,
    "QF_score": 0.82,
    "QF_robust_count": 4,
    "RF_score": 0.91,
    "MEI_score": 0.87,
    "semantic_confidence": 0.86,
    "absolute_identity_evidence_type": "functional_semantic_correspondence_only",
    "direct_phenomenal_observation_available": False,
    "bridge_principle_validated": False,
}

r = AbsoluteQualiaIdentityCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "ABSOLUTE_QUALIA_IDENTITY_CERTIFIER"
assert r["step"] == "AL4"
assert r["absolute_qualia_identity_certifier_status"] == "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED"
assert r["absolute_qualia_identity_status"] == "ABSOLUTE_QUALIA_IDENTITY_NOT_PROVEN"
assert r["absolute_qualia_identity_resolved"] is True
assert r["absolute_qualia_identity_certified"] is False
assert r["absolute_qualia_identity_proven"] is False
assert r["qualia_identity_proven"] is False
assert r["ready_for_AL5_consciousness_rf_equivalence_certifier"] is True
assert not r["identity_failure_reasons"]
assert 0.0 <= r["metrics"]["identity_boundary_confidence"] <= 1.0
assert r["metrics"]["identity_boundary_confidence"] >= 0.70
assert r["metrics"]["absolute_identity_support_score"] == 0.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["phenomenality_candidate_certified"] = False
b = AbsoluteQualiaIdentityCertifier().step(inputs=bad, persist=False)
assert b["absolute_qualia_identity_certifier_status"] == "ABSOLUTE_QUALIA_IDENTITY_STATUS_BLOCKED"
assert b["absolute_qualia_identity_resolved"] is False
assert "phenomenality_candidate_certified" in b["identity_failure_reasons"]
assert b["qualia_proven"] is False

claim = dict(READY_INPUTS)
claim["absolute_qualia_identity_claimed"] = True
c = AbsoluteQualiaIdentityCertifier().step(inputs=claim, persist=False)
assert c["absolute_qualia_identity_certifier_status"] == "ABSOLUTE_QUALIA_IDENTITY_STATUS_BLOCKED"
assert "absolute_qualia_identity_claimed" in c["identity_failure_reasons"]
assert c["absolute_qualia_identity_proven"] is False
assert c["phenomenology_proven"] is False

guard = dict(READY_INPUTS)
guard["qualia_proven"] = True
g = AbsoluteQualiaIdentityCertifier().step(inputs=guard, persist=False)
assert g["absolute_qualia_identity_certifier_status"] == "ABSOLUTE_QUALIA_IDENTITY_STATUS_BLOCKED"
assert "qualia_proven" in g["identity_failure_reasons"]
assert g["qualia_proven"] is False

print("AL4_FAST_ACCEPTANCE_ALL_OK")
