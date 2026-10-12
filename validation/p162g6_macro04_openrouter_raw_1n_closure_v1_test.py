from __future__ import annotations
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from ontology.openrouter_autonomous_provider_adapter import OpenRouterAutonomousProviderAdapter
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker

SLOT = "macro04_openrouter_raw_response"

def context_for(root, path):
    broker = ScopedHandleBroker()
    adapter='p162g6_test_adapter'; effector_id='p162g6_test_effector'
    scope={'ambient_authority':False,'child_inheritance':False,'transferable':False}
    claim=SimpleNamespace(lease_id='lease',reservation_id='reservation',adapter_id=adapter,claim_hash='claim')
    lease={'lease_id':'lease','reservation_id':'reservation','expires_at':'2099-01-01T00:00:00Z','operation_id':'FS_WRITE_REPLACE_BYTES'}
    registry={'adapter_id':adapter,'effector_id':effector_id}
    target='filesystem://test/'+path.relative_to(root).as_posix()
    issued=broker.issue(claim=claim,lease=lease,registry_entry=registry,requested_scope=scope,authorized_scope=scope,target_binding=target,audience=adapter,now_iso='2026-10-08T00:00:00Z')
    assert issued['status']=='HANDLE_ISSUED',issued
    handle=issued['handle']
    effector=GovernedFilesystemEffector(root_registry={'test':str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(slots={SLOT:[handle]},effector=effector,root_id='test',root_path=root,adapter_id=adapter,effector_id=effector_id)
    return ctx,broker,handle

def run():
    with tempfile.TemporaryDirectory(prefix='p162g6-openrouter-test-') as tmp:
        root=Path(tmp)
        adapter=OpenRouterAutonomousProviderAdapter(root=root)
        data={'id':'résponse','choices':[{'message':{'content':'bonjour'}}], 'unicode':'\u2603'}
        target=adapter._raw_path_for('Q-1')
        assert not target.exists()
        try: adapter._persist_raw_response('Q-1',data)
        except PermissionError: pass
        else: raise AssertionError('missing_authority_not_blocked')
        assert not target.exists()
        ctx,broker,handle=context_for(root,target)
        result=adapter._persist_raw_response('Q-1',data,fs_context=ctx)
        assert result==str(target)
        expected=json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True).encode('utf-8')
        assert target.read_bytes()==expected
        assert ctx.remaining()[SLOT]==0 and handle.handle_id in broker._used
        try: adapter._persist_raw_response('Q-1',data,fs_context=ctx)
        except RuntimeError: pass
        else: raise AssertionError('context_replay_not_blocked')
        target.write_bytes(b'prior')
        ctx2,broker2,handle2=context_for(root,target)
        assert adapter._persist_raw_response('Q-1',data,fs_context=ctx2)==str(target)
        assert target.read_bytes()==expected
        assert handle2.handle_id in broker2._used
        # No network request, API key, or result persistence is required for the scoped test.
        assert adapter._extract_text(data)=='bonjour'
        assert adapter._raw_path_for('../danger').parent==adapter.raw_dir
        assert not (root/'danger').exists()
        print('DEGRADATION_TEST_OK')
        print('FUNCTIONAL_TEST_OK')
        print('REAL_TCB_OK')
        print('EXACT_HANDLE_CONSUMPTION_OK')
        print('NON_REGRESSION_TEST_OK')
        print('P162G6_MACRO04_OPENROUTER_RAW_1N_TEST_OK')
if __name__=='__main__': run()
