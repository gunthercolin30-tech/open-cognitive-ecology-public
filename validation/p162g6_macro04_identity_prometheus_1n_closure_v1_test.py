from __future__ import annotations
from pathlib import Path
from types import SimpleNamespace
import tempfile
import ontology.identity_theorem_attempt as mod
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
SLOT='macro04_identity_prometheus_alias'
def provider_for(root):
    issued=[]
    def provider(operation,path,slot):
        assert operation=='FS_WRITE_REPLACE_BYTES' and slot==SLOT
        broker=ScopedHandleBroker(); adapter='p162g6_test_adapter';effector_id='p162g6_test_effector'
        scope={'ambient_authority':False,'child_inheritance':False,'transferable':False}
        claim=SimpleNamespace(lease_id='lease',reservation_id='reservation',adapter_id=adapter,claim_hash='claim')
        lease={'lease_id':'lease','reservation_id':'reservation','expires_at':'2099-01-01T00:00:00Z','operation_id':operation}
        registry={'adapter_id':adapter,'effector_id':effector_id}
        target='filesystem://test/'+path.relative_to(root).as_posix()
        response=broker.issue(claim=claim,lease=lease,registry_entry=registry,requested_scope=scope,authorized_scope=scope,target_binding=target,audience=adapter,now_iso='2026-10-08T00:00:00Z')
        assert response['status']=='HANDLE_ISSUED',response
        handle=response['handle']
        effector=GovernedFilesystemEffector(root_registry={'test':str(root)},handle_broker=broker)
        ctx=GovernedFilesystemEffectContext(slots={SLOT:[handle]},effector=effector,root_id='test',root_path=root,adapter_id=adapter,effector_id=effector_id)
        issued.append((ctx,broker,handle))
        return ctx
    return provider,issued

def run():
    with tempfile.TemporaryDirectory(prefix='p162g6-ak7-') as tmp:
        root=Path(tmp)
        paths=[root/'out'/'metrics.prom',root/'out'/'latest.prom']
        for p in paths: p.parent.mkdir(parents=True,exist_ok=True)
        result={'paths':{'prometheus':str(paths[0]),'latest_prometheus':str(paths[1])},'identity_theorem_attempt_score':0.7,'proof_gap_score':0.2,'functional_identity_score':0.6,'formal_identity_score':0.5,'ontological_identity_score':0.0,'phenomenological_identity_score':0.0,'functional_conclusion_only':True,'phenomenology_undetermined':True,'consciousness_proven':False}
        original=mod._AK7_V5_ORIGINAL_STEP
        mod._AK7_V5_ORIGINAL_STEP=lambda self,*a,**kw:dict(result)
        try:
            denied=mod.IdentityTheoremAttempt(root=root)
            returned=denied.step(persist=True)
            assert returned['functional_conclusion_only'] is True
            assert not any(p.exists() for p in paths)
            provider,issued=provider_for(root)
            obj=mod.IdentityTheoremAttempt(root=root,filesystem_effect_context_provider=provider)
            # Baseline existing file without newline, verify byte-preserving suffix.
            paths[0].write_bytes(b'legacy_metric 1.0')
            returned=obj.step(persist=True)
            assert returned['phenomenology_undetermined'] is True
            assert paths[0].read_bytes().startswith(b'legacy_metric 1.0\n')
            assert b'identity_theorem_attempt_score 0.7\n' in paths[0].read_bytes()
            assert b'ak7_identity_theorem_attempt_score 0.7\n' in paths[0].read_bytes()
            assert paths[1].read_bytes().startswith(b'ak7_identity_theorem_attempt_score 0.7\n')
            assert len(issued)==2
            assert all(ctx.remaining()[SLOT]==0 and handle.handle_id in broker._used for ctx,broker,handle in issued)
            old=[p.read_bytes() for p in paths]
            obj.step(persist=True)
            assert [p.read_bytes() for p in paths]==old and len(issued)==2
            obj.step(persist=False)
            assert [p.read_bytes() for p in paths]==old
            # Reuse a consumed context must not permit writes.
            consumed=issued[0][0]
            blocked=mod.IdentityTheoremAttempt(root=root,filesystem_effect_context_provider=lambda *a:consumed)
            paths[0].write_bytes(b'fresh')
            blocked.step(persist=True)
            assert paths[0].read_bytes()==b'fresh'
            print('DEGRADATION_TEST_OK')
            print('FUNCTIONAL_TEST_OK')
            print('REAL_TCB_OK')
            print('EXACT_HANDLE_CONSUMPTION_OK')
            print('NON_REGRESSION_TEST_OK')
            print('P162G6_MACRO04_IDENTITY_PROMETHEUS_1N_TEST_OK')
        finally:
            mod._AK7_V5_ORIGINAL_STEP=original
if __name__=='__main__': run()
