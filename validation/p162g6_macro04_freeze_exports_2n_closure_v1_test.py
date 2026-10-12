from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker, ScopedEffectHandle
from ontology.reference_runtime_freeze_protocol import ReferenceRuntimeFreezeProtocol

class Factory:
    def __init__(self, root):
        self.root=root;self.broker=ScopedHandleBroker()
        self.effector=GovernedFilesystemEffector(root_registry={'r':str(root)},handle_broker=self.broker)
        self.issued=[]
    def __call__(self,operation,path,slot):
        assert operation=='FS_WRITE_REPLACE_BYTES'
        rel=Path(path).relative_to(self.root).as_posix()
        target=self.effector.canonical_target('r',rel)
        ident='test-'+str(len(self.issued))
        h=ScopedEffectHandle(ident,'lease','reservation','claim','adapter','effector',operation,target,'scope','adapter','2099-01-01')
        self.broker._issued[ident]=h
        self.issued.append(h)
        return GovernedFilesystemEffectContext(slots={slot:[h]},effector=self.effector,root_id='r',root_path=self.root,adapter_id='adapter',effector_id='effector')

with TemporaryDirectory() as d:
    root=Path(d);out=root/'exports';out.mkdir()
    (root/'ontology_inventory.txt').write_text('inventory',encoding='utf-8')
    (root/'scientific_validation_report.json').write_text('{}',encoding='utf-8')
    (root/'scientific_validation_report.txt').write_text('report',encoding='utf-8')
    p=ReferenceRuntimeFreezeProtocol(root=root)
    for method,name in [(p.export_validation_bundle,'validation_bundle.json'),(p.export_longitudinal_metrics,'longitudinal_metrics.json')]:
        try: method(out)
        except RuntimeError as exc: assert 'provider_required' in str(exc)
        else: raise AssertionError('ambient_write_accepted')
        assert not (out/name).exists()
    print('DEGRADATION_TEST_OK')
    f=Factory(root);p.filesystem_effect_context_provider=f
    validation=p.export_validation_bundle(out)
    assert validation.name=='validation_bundle.json'
    bundle=json.loads(validation.read_text())
    assert bundle['ontology_inventory.txt']['exists'] is True
    assert len(bundle['ontology_inventory.txt']['sha256'])==64
    metrics=p.export_longitudinal_metrics(out)
    assert json.loads(metrics.read_text())=={'available':False,'experiment_files':[]}
    assert len(f.issued)==2 and all(x.handle_id in f.broker._used for x in f.issued)
    print('FUNCTIONAL_TEST_OK')
    print('REAL_TCB_OK')
    print('EXACT_HANDLE_CONSUMPTION_OK')
    exp=root/'runtime_experiments';exp.mkdir();(exp/'experiment_001.json').write_text('{"x":1}')
    metrics=p.export_longitudinal_metrics(out)
    obj=json.loads(metrics.read_text())
    assert obj['available'] is True and len(obj['experiment_files'])==1
    assert obj['experiment_files'][0]['file']=='experiment_001.json'
    assert len(obj['experiment_files'][0]['sha256'])==64
    assert len(f.issued)==3 and all(x.handle_id in f.broker._used for x in f.issued)
    print('NON_REGRESSION_TEST_OK')
    p.filesystem_effect_context_provider=lambda op,path,slot: None
    prior=metrics.read_bytes()
    try:p.export_longitudinal_metrics(out)
    except RuntimeError as exc:assert 'preissued_' in str(exc)
    else:raise AssertionError('null_provider_accepted')
    assert metrics.read_bytes()==prior
    print('DEGRADATION_NULL_CONTEXT_OK')
print('P162G6_MACRO04_FREEZE_EXPORTS_2N_TEST_OK')
