from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload,seed
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp);seed(root);p=payload(root);a=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True);b=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True);assert a["transaction_state"]=="LOCALLY_VALIDATED",a;assert b["local_validation_replayed"] is True;assert a["local_validation_report_hash"]==b["local_validation_report_hash"]
print("ACEE6_F1_IDEMPOTENCE_OK")
