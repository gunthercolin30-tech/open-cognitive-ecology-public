from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload,seed
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp);seed(root);p=payload(root);c=p["admission_context"]["local_validation_commands"];c[0],c[1]=c[1],c[0];r=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True);assert r["transaction_state"]=="INVENTORIES_UPDATED",r;assert "local_validation_order_invalid" in r["blocking_reasons"];assert r["tests_executed"] is False
print("ACEE6_F1_ORDER_CONTRACT_OK")
