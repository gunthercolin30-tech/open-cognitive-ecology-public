import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content="locked\n"; hash_=hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,candidate_hash=hash_),persist=False)
    result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D2","candidate_content":content}},persist=True)
    assert result["stage"]=="ACEE6-D2"
    assert result["public_schema_version"]=="0.6.0"
    assert result["transaction_state"]=="MUTATED"
    assert result["candidate_written"] is True
    assert result["candidate_compiled"] is False
    assert result["inventory_modified"] is False
    assert result["tests_executed"] is False
print("ACEE6_D2_ATOMIC_MUTATION_FINAL_LOCK_OK")
