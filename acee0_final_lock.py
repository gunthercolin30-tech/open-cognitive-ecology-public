\
from acee0_fast_acceptance_suite import build_context
from ontology.acee_integration_auditor import AceeIntegrationAuditor

result = AceeIntegrationAuditor().step(inputs=build_context(), persist=False)
assert result["audit_status"] == "ACEE_INTEGRATION_AUDIT_COMPLETE"
assert result["audit_completed"] is True
assert 0.0 <= result["coverage_score"] <= 1.0
assert result["recommendation_justifications_complete"] is True
assert all(item["justification"] for item in result["recommended_actions"])
assert result["consciousness_proven"] is False
assert result["subjectivity_proven"] is False
assert result["qualia_proven"] is False
assert result["phenomenology_proven"] is False
assert result["collective_consciousness_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("ACEE_INTEGRATION_AUDITOR_FINAL_LOCK_OK")
