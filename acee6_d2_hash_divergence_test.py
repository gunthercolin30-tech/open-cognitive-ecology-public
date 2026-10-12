from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=valid_acee5_decision(root)
    inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D2","candidate_content":"wrong"}}
    result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=inputs,persist=True)
    assert result["transaction_state"]=="STATE_CORRUPTED"
    assert "candidate_content_hash_divergence" in result["blocking_reasons"]
    assert result["candidate_written"] is False
print("ACEE6_D2_HASH_DIVERGENCE_OK")
