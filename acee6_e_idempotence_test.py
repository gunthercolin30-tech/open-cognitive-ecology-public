from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed,payload,fixed_now,AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp); seed(root); p=payload(root); ex=AceeInstallationExecutor(root=root,now_utc=fixed_now()); a=ex.step(inputs=p,persist=True); before={x:(root/x).read_bytes() for x in ['dependency_registry.py','ontology_inventory.txt','ontology_inventory.py','ontology/ontology_inventory.py','global_module_catalog.txt']}; b=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True); after={x:(root/x).read_bytes() for x in before}; assert b['transaction_state']=='INVENTORIES_UPDATED',b; assert before==after
print('ACEE6_E_IDEMPOTENCE_OK')
