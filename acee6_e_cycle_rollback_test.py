from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed,payload,fixed_now,AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp); seed(root); (root/'dependency_registry.py').write_text("# Auto-generated dependency registry\n\nDEPENDENCY_REGISTRY = {'alpha':['sample_candidate']}\n",encoding='utf-8'); before=(root/'ontology_inventory.txt').read_bytes(); r=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=payload(root,deps=['alpha']),persist=True); assert r['transaction_state']=='ROLLED_BACK',r; assert (root/'ontology_inventory.txt').read_bytes()==before
print('ACEE6_E_CYCLE_ROLLBACK_OK')
