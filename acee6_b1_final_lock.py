from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, DEPENDENCIES

with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=valid_acee5_decision(root)
    executor=AceeInstallationExecutor(root=root,now_utc=fixed_now())
    a=executor.step(decision); b=executor.step(decision)
    assert a["result_hash"]==b["result_hash"]
    assert a["status"]=="ACEE6_INSTALLATION_PLAN_ADMISSIBLE"
    assert len(DEPENDENCIES)==len(set(DEPENDENCIES))
    assert a["functional_conclusion_only"] is True
    assert a["phenomenology_undetermined"] is True
print("ACEE6_B1_MANIFEST_ADMISSION_FINAL_LOCK_OK")
