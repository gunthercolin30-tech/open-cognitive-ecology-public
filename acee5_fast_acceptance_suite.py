from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
def valid_context():
    h = "a" * 64
    return {
        "proposal_id": "proposal-001",
        "timestamp_utc": "2026-07-14T18:30:00Z",
        "candidate": {"module_name": "sample_candidate", "target_path": "ontology/sample_candidate.py", "content_sha256": h},
        "generation_evidence": {"proposal_only": True, "code_written": False, "code_installed": False},
        "backup_evidence": {"target_path": "ontology/sample_candidate.py", "backup_path": "ontology/sample_candidate.py.bak", "verified": True, "sha256": "b" * 64},
        "refiner_evidence": {"path": "refine_sample_candidate.py", "generated": True, "compilation_ready": True, "sha256": "c" * 64},
        "test_evidence": {"generated": True, "tests": ["sample_candidate_fast_acceptance_suite.py", "sample_candidate_functional_test.py", "sample_candidate_degradation_test.py", "sample_candidate_non_regression_test.py"]},
        "rollback_plan": {"available": True, "executor": "acee_rollback_engine", "artifacts": ["ontology/sample_candidate.py.bak"]},
        "inventory_plan": {"dependency_registry.py": True, "ontology_inventory.txt": True, "ontology_inventory.py": True, "ontology/ontology_inventory.py": True, "global_module_catalog.txt": True},
        "validation_evidence": {"runner": "acee_validation_runner", "command": "python3 -m validation.main", "executed": True, "overall_success": True, "error_count": 0, "report_sha256": "d" * 64, "candidate_content_sha256": h},
        "constitutional_evidence": {"compliant": True, "non_closure_preserved": True, "functional_conclusion_only": True, "phenomenology_undetermined": True},
    }

with TemporaryDirectory() as td:
 r=AceeGovernedCodeGenerationGate(root=Path(td)).step(inputs=valid_context(),persist=False)
 assert r["status"]=="ACEE_CODE_GENERATION_GOVERNED"
 assert r["installation_authorized"] is True
 assert all(r[k] is False for k in ("code_generated_by_gate","code_written_by_gate","code_installed_by_gate","validation_executed_by_gate","rollback_executed_by_gate"))
print("ACEE5_FAST_ACCEPTANCE_OK")
