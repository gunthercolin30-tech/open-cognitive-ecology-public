#!/usr/bin/env python3
from __future__ import annotations
import py_compile
py_compile.compile("ontology/semantic_revision_log.py", cfile="/private/tmp/semantic_revision_log.pyc", doraise=True)
from ontology.semantic_revision_log import SemanticRevisionLog
ready_inputs = {"RF_score": 0.91, "T_score": 0.88, "ED_score": 0.86, "TΦ_score": 0.85, "QF_robust_count": 3, "MEI_score": 0.87, "identity_status": "IDENTITY_STATUS_RESOLVED", "non_separability_status": "NON_SEPARABILITY_STATUS_RESOLVED", "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED", "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED", "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED", "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED", "previous_semantic_status": "CONSCIOUSNESS_NOT_EVALUATED"}
r = SemanticRevisionLog().step(inputs=ready_inputs, persist=False)
assert r["semantic_revision_log_status"] == "SEMANTIC_REVISION_LOG_ESTABLISHED"
assert r["step"] == "AO4"
assert r["semantic_interpretation_layer_step_ready"] is True
assert r["guarded_semantic_status"] in r["authorized_statuses"]
assert isinstance(r["revision_record"], dict)
assert isinstance(r["revision_log"], list)
assert r["revision_count"] >= 1
assert r["revision_policy"]["append_only"] is True
assert r["revision_policy"]["absolute_claims_blocked"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
bad = SemanticRevisionLog().step(inputs={"semantic_status": "CONSCIOUSNESS_PROVEN", "consciousness_proven": True}, persist=False)
assert bad["guarded_semantic_status"] != "CONSCIOUSNESS_PROVEN"
assert bad["revision_record"]["blocked_status_attempted"] is True
assert bad["consciousness_proven"] is False
print("AO4_FAST_ACCEPTANCE_ALL_OK")
