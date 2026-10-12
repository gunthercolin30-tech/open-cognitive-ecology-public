from __future__ import annotations
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from ontology.reflexive_threshold_history_archive import ReflexiveThresholdHistoryArchive
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
SLOT="macro04_reflexive_markdown"
def make_provider(root):
    issued_contexts=[]
    def provider(operation,path,slot):
        assert operation=="FS_WRITE_REPLACE_BYTES" and slot==SLOT
        broker=ScopedHandleBroker()
        adapter='p162g6_test_adapter'; effector_id='p162g6_test_effector'
        scope={'ambient_authority':False,'child_inheritance':False,'transferable':False}
        claim=SimpleNamespace(lease_id='lease',reservation_id='reservation',adapter_id=adapter,claim_hash='claim')
        lease={'lease_id':'lease','reservation_id':'reservation','expires_at':'2099-01-01T00:00:00Z','operation_id':operation}
        registry={'adapter_id':adapter,'effector_id':effector_id}
        target='filesystem://test/'+path.relative_to(root).as_posix()
        issued=broker.issue(claim=claim,lease=lease,registry_entry=registry,requested_scope=scope,authorized_scope=scope,target_binding=target,audience=adapter,now_iso='2026-10-08T00:00:00Z')
        assert issued['status']=='HANDLE_ISSUED',issued
        handle=issued['handle']
        effector=GovernedFilesystemEffector(root_registry={'test':str(root)},handle_broker=broker)
        ctx=GovernedFilesystemEffectContext(slots={SLOT:[handle]},effector=effector,root_id='test',root_path=root,adapter_id=adapter,effector_id=effector_id)
        issued_contexts.append((ctx,broker,handle))
        return ctx
    return provider,issued_contexts

def run():
    with tempfile.TemporaryDirectory(prefix='p162g6-reflexive-test-') as tmp:
        root=Path(tmp)
        path=root/'reflexive_threshold'/'reflexive_threshold_history_archive'/'report.md'
        path.parent.mkdir(parents=True)
        data={'run_id':'essai-été','history_coverage_score':0.5,'archive_strength':0.3,'stages_expected':14,'stages_present':1,'total_artifacts':2,'functional_conclusion':'functional conclusion only','stages':{'S1':{'present':True,'artifact_count':2}}}
        denied=ReflexiveThresholdHistoryArchive(root=root)
        try: denied._write_markdown(path,data)
        except PermissionError: pass
        else: raise AssertionError('missing_authority_not_blocked')
        assert not path.exists()
        provider,issued=make_provider(root)
        archive=ReflexiveThresholdHistoryArchive(root=root,filesystem_effect_context_provider=provider)
        archive._write_markdown(path,data)
        expected='# X1 — Reflexive Threshold History Archive\n'
        assert path.read_text(encoding='utf-8').startswith(expected)
        assert 'essai-été' in path.read_text(encoding='utf-8')
        assert path.read_bytes().endswith(b'\n')
        ctx,broker,handle=issued[-1]
        assert ctx.remaining()[SLOT]==0 and handle.handle_id in broker._used
        old=path.read_bytes()
        path.write_bytes(b'old')
        archive._write_markdown(path,data)
        assert path.read_bytes()==old
        assert len(issued)==2
        assert issued[-1][2].handle_id in issued[-1][1]._used
        assert archive.step(inputs={},persist=False)['functional_conclusion_only'] is True
        print('DEGRADATION_TEST_OK')
        print('FUNCTIONAL_TEST_OK')
        print('REAL_TCB_OK')
        print('EXACT_HANDLE_CONSUMPTION_OK')
        print('NON_REGRESSION_TEST_OK')
        print('P162G6_MACRO04_REFLEXIVE_MARKDOWN_1N_TEST_OK')
if __name__=='__main__': run()
