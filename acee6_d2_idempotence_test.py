import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content="stable\n"; hash_=hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,candidate_hash=hash_),persist=False)
    inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D2","candidate_content":content}}
    executor=AceeInstallationExecutor(root=root,now_utc=fixed_now())
    first=executor.step(inputs=inputs,persist=True); second=executor.step(inputs=inputs,persist=True)
    assert first["transaction_state"]==second["transaction_state"]=="MUTATED"
    assert second["mutation_replayed"] is True
print("ACEE6_D2_IDEMPOTENCE_OK")
