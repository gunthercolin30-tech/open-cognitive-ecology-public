import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
original="VALUE = 1\n"; content="def broken(:\n"; digest=hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
 root=Path(tmp); (root/"ontology").mkdir(); target=root/"ontology"/"candidate_module.py"; target.write_text(original); decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,candidate_hash=digest),persist=False); result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D3","candidate_content":content}},persist=True); assert result["transaction_state"]=="ROLLED_BACK",result; assert result["rollback_executed"] is True; assert target.read_text()==original
print("ACEE6_D3_FAILURE_ROLLBACK_OK")
