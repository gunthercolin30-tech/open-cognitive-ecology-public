import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content="LOCKED = True\n"; digest=hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
 root=Path(tmp); (root/"ontology").mkdir(); decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,candidate_hash=digest),persist=False); r=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D3","candidate_content":content}},persist=True); assert r["stage"]=="ACEE6-D3"; assert r["public_schema_version"]=="0.7.0"; assert r["status"]=="ACEE6_TRANSACTION_COMPILATION_COMPLETE"; assert r["transaction_state"]=="COMPILED"; assert r["candidate_compiled"] is True; assert r["candidate_executed"] is False; assert r["inventory_modified"] is False; assert r["tests_executed"] is False; assert r["global_validation_executed"] is False; assert r["committed"] is False
print("ACEE6_D3_TRANSACTIONAL_COMPILATION_FINAL_LOCK_OK")
