from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload,seed
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp);seed(root);names=["dependency_registry.py","ontology_inventory.txt","ontology_inventory.py","ontology/ontology_inventory.py","global_module_catalog.txt"];before={n:(root/n).read_bytes() for n in names};r=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=payload(root,"degradation"),persist=True);assert r["transaction_state"]=="ROLLED_BACK",r;assert r["rollback_executed"] is True;assert all((root/n).read_bytes()==b for n,b in before.items())
print("ACEE6_F1_FAILURE_ROLLBACK_OK")
