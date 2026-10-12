from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from ontology.external_influence_dashboard import ExternalInfluenceDashboard
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
import json

def main():
    with TemporaryDirectory(prefix='oce-external-dashboard-') as td:
        root=Path(td); folder=root/'exports'
        o=ExternalInfluenceDashboard();o.export_dir=folder
        plain=o.step(persist=False)
        assert plain['exports_generated'] is False and not folder.exists()
        try: o.step(persist=True)
        except PermissionError: pass
        else: raise AssertionError('missing authority accepted')
        assert not folder.exists()
        issued=[]
        def provider(op,path,slot):
            broker=ScopedHandleBroker();adapter='macro04_dashboard_test';effector_id='macro04_effector'
            scope={'ambient_authority':False,'child_inheritance':False,'transferable':False}
            claim=SimpleNamespace(lease_id='lease',reservation_id='reservation',adapter_id=adapter,claim_hash='claim')
            lease={'lease_id':'lease','reservation_id':'reservation','expires_at':'2099-01-01T00:00:00Z','operation_id':op}
            registry={'adapter_id':adapter,'effector_id':effector_id}
            target='filesystem://test/'+path.relative_to(root).as_posix()
            response=broker.issue(claim=claim,lease=lease,registry_entry=registry,requested_scope=scope,authorized_scope=scope,target_binding=target,audience=adapter,now_iso='2026-10-08T00:00:00Z')
            assert response['status']=='HANDLE_ISSUED',response
            handle=response['handle'];effector=GovernedFilesystemEffector(root_registry={'test':str(root)},handle_broker=broker)
            ctx=GovernedFilesystemEffectContext(slots={slot:[handle]},effector=effector,root_id='test',root_path=root,adapter_id=adapter,effector_id=effector_id)
            issued.append((op,path,ctx,broker,handle,slot))
            return ctx
        o.filesystem_effect_context_provider=provider
        result=o.step(persist=True)
        assert result['exports_generated'] is True
        assert len(issued)==6,[(x[0],str(x[1])) for x in issued]
        assert issued[0][0]=='FS_CREATE_DIRS'
        assert all(x[2].remaining()=={x[5]:0} and x[4].handle_id in x[3]._used for x in issued)
        assert json.loads((folder/'latest_external_influence_dashboard.json').read_text())==result
        assert (folder/'external_influence_dashboard.html').read_text().startswith('<!DOCTYPE html>') or '<html' in (folder/'external_influence_dashboard.html').read_text().lower()
        assert (folder/'external_influence_dashboard.prom').stat().st_size>0
        assert json.loads((folder/'external_influence_dashboard_grafana.json').read_text())['schemaVersion']==39
        assert [x[0] for x in issued].count('FS_WRITE_REPLACE_BYTES')==5
        # Existing directory: five effects, no new directory authority.
        issued.clear(); second=o.step(persist=True)
        assert second['exports_generated'] and len(issued)==5
        # Replay a consumed context: must refuse.
        consumed=issued[0][2];old=(folder/'latest_external_influence_dashboard.json').read_bytes()
        o.filesystem_effect_context_provider=lambda *a:consumed
        try: o.step(persist=True)
        except (PermissionError,RuntimeError): pass
        else: raise AssertionError('replayed authority accepted')
        assert (folder/'latest_external_influence_dashboard.json').read_bytes()==old
        # Refusal before any publication if directory missing.
        folder2=root/'absent';o.export_dir=folder2;o.filesystem_effect_context_provider=None
        try:o.step(persist=True)
        except PermissionError:pass
        else:raise AssertionError('ambient mkdir accepted')
        assert not folder2.exists()
        print('DEGRADATION_TEST_OK')
        print('FUNCTIONAL_TEST_OK')
        print('REAL_TCB_OK')
        print('EXACT_HANDLE_CONSUMPTION_OK')
        print('NON_REGRESSION_TEST_OK')
        print('P162G6_MACRO04_EXTERNAL_DASHBOARD_1N_TEST_OK')
if __name__=='__main__':main()
