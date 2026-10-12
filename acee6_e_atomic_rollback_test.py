import os
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed,payload
from acee6_b1_test_support import fixed_now
from ontology.acee_installation_executor import AceeInstallationExecutor

FILES=['dependency_registry.py','ontology_inventory.txt','ontology_inventory.py','ontology/ontology_inventory.py','global_module_catalog.txt']
for fail_at in (1,2,5):
    with TemporaryDirectory() as tmp:
        root=Path(tmp); seed(root); p=payload(root)
        before={x:(root/x).read_bytes() for x in FILES}
        ex=AceeInstallationExecutor(root=root,now_utc=fixed_now())
        compiled=ex.step(inputs={**p,'admission_context':{**p['admission_context'],'requested_stage':'ACEE6-D3'}},persist=True)
        original=os.replace; count={'n':0}
        def injected(src,dst):
            if str(dst).endswith(tuple(FILES)):
                count['n']+=1
                if count['n']==fail_at: raise OSError('injected_replace_failure')
            return original(src,dst)
        os.replace=injected
        try: result=ex._update_inventories(compiled,p)
        finally: os.replace=original
        assert result['transaction_state']=='ROLLED_BACK',result
        assert before=={x:(root/x).read_bytes() for x in FILES}
        assert not list(root.rglob('*.tmp'))
print('ACEE6_E_ATOMIC_ROLLBACK_OK')
