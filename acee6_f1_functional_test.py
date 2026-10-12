from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload,seed
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp);seed(root);r=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=payload(root),persist=True);assert r["transaction_state"]=="LOCALLY_VALIDATED",r;assert r["local_validation_passed"] is True;assert r["global_validation_executed"] is False;assert r["committed"] is False;assert Path(r["local_validation_report_path"]).is_file()
print("ACEE6_F1_FUNCTIONAL_OK")
