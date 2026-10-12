from pathlib import Path
from acee7_fast_acceptance_suite import context
from ontology.acee_validation_runner import AceeValidationRunner
r=AceeValidationRunner(root=Path("/nonexistent")).step(inputs=context(),persist=False)
assert r["validation_passed"] is True and r["rollback_required"] is False
assert len(r["evidence_manifest"])==3 and r["phenomenology_undetermined"] is True
print("ACEE_VALIDATION_RUNNER_FINAL_LOCK_OK")
