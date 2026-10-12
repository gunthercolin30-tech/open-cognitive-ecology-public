from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed,payload
from acee6_b1_test_support import fixed_now
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root=Path(tmp); seed(root); p=payload(root)
    first=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
    (root/'ontology_inventory.txt').write_text('alpha\nsample_candidate\nrogue\n')
    replay=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
    assert replay['transaction_state']=='STATE_CORRUPTED',replay
    assert 'existing_inventory_file_divergence' in replay['blocking_reasons']
with TemporaryDirectory() as tmp:
    root=Path(tmp); seed(root)
    p=payload(root,deps=['missing_dependency'])
    result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
    assert result['transaction_state']=='ROLLED_BACK',result
    assert any('unknown_dependencies:missing_dependency' in x for x in result['blocking_reasons'])
print('ACEE6_E_CROSS_VIEW_DIVERGENCE_OK')
