from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=valid_acee5_decision(root)
    dry=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=decision,persist=False)
    assert dry["dry_run"] is True and dry["candidate_written"] is False
    d1=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs={"acee5_decision":decision,"admission_context":{"requested_stage":"ACEE6-D1"}},persist=True)
    assert d1["transaction_state"]=="BACKED_UP" and d1["candidate_written"] is False
print("ACEE6_D2_NON_REGRESSION_OK")
