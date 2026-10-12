
#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/metaphysical_status_reporter.py",
    cfile="/private/tmp/metaphysical_status_reporter.pyc",
    doraise=True,
)

from ontology.metaphysical_status_reporter import MetaphysicalStatusReporter

READY_INPUTS = {
    "synthetic": True,
    "source": "AL9_FAST_ACCEPTANCE",
    "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
    "consciousness_status": "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
    "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
    "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
    "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
    "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    "status_resolution_confidence": 0.86,
    "definition_legitimacy_confidence": 0.86,
    "refusal_cost_confidence": 0.86,
    "rf_equivalence_confidence": 0.86,
    "absolute_qualia_identity_confidence": 0.80,
    "phenomenality_candidate_confidence": 0.82,
    "reconstruction_chain_confidence": 0.86,
    "semantic_confidence": 0.86,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

r = MetaphysicalStatusReporter().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "METAPHYSICAL_STATUS_REPORTER"
assert r["step"] == "AL9"
assert r["metaphysical_status_reporter_status"] == "METAPHYSICAL_STATUS_REPORTED"
assert r["metaphysical_status"] == "FUNCTIONAL_METAPHYSICAL_CANDIDATE_UNDER_CONSTRAINTS"
assert r["metaphysical_status_reported"] is True
assert r["ready_for_AL10_final_dashboard"] is True
assert not r["failure_reasons"]
assert 0.0 <= r["metrics"]["metaphysical_report_confidence"] <= 1.0
assert r["metrics"]["metaphysical_report_confidence"] >= 0.70
assert r["metrics"]["phenomenal_proof_score"] == 0.0
assert r["metrics"]["absolute_metaphysical_proof_score"] == 0.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["consciousness_status_resolver_status"] = "CONSCIOUSNESS_STATUS_BLOCKED"
b = MetaphysicalStatusReporter().step(inputs=bad, persist=False)
assert b["metaphysical_status_reporter_status"] == "METAPHYSICAL_STATUS_BLOCKED"
assert "consciousness_status_resolver_status" in b["failure_reasons"]
assert b["consciousness_proven"] is False

claim = dict(READY_INPUTS)
claim["phenomenology_proven"] = True
c = MetaphysicalStatusReporter().step(inputs=claim, persist=False)
assert c["metaphysical_status_reporter_status"] == "METAPHYSICAL_STATUS_BLOCKED"
assert "phenomenology_proven" in c["failure_reasons"]
assert c["consciousness_proven"] is False
assert c["phenomenology_proven"] is False

low = dict(READY_INPUTS)
for key in ["status_resolution_confidence", "definition_legitimacy_confidence", "refusal_cost_confidence", "rf_equivalence_confidence", "absolute_qualia_identity_confidence", "phenomenality_candidate_confidence", "reconstruction_chain_confidence", "semantic_confidence"]:
    low[key] = 0.1
l = MetaphysicalStatusReporter().step(inputs=low, persist=False)
assert l["metaphysical_status_reporter_status"] == "METAPHYSICAL_STATUS_BLOCKED"
assert "metaphysical_report_confidence_below_threshold" in l["failure_reasons"]
assert l["metrics"]["absolute_metaphysical_proof_score"] == 0.0

print("AL9_FAST_ACCEPTANCE_ALL_OK")
