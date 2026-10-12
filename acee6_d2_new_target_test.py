import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content = "brand new\n"
hash_ = hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,candidate_hash=hash_),persist=False)
    inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D2","candidate_content":content}}
    result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=inputs,persist=True)
    assert result["transaction_state"]=="MUTATED"
    assert (root/"ontology"/"sample_candidate.py").read_text()==content
    assert not (root/"ontology"/"sample_candidate.py.bak").exists()
print("ACEE6_D2_NEW_TARGET_OK")
