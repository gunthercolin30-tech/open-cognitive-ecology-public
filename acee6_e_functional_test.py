from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed,payload,fixed_now,AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp); seed(root); r=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=payload(root),persist=True)
 assert r['transaction_state']=='INVENTORIES_UPDATED',r
 assert r['inventory_modified'] is True and r['candidate_executed'] is False and r['tests_executed'] is False and r['global_validation_executed'] is False and r['committed'] is False
 assert 'sample_candidate' in (root/'ontology_inventory.txt').read_text()
print('ACEE6_E_FUNCTIONAL_OK')
