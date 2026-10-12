from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.open_source_replication_readiness import OpenSourceReplicationReadiness
RID="root";AD="adapter";EF="effector"
def ctx(root,target):
    b=ScopedHandleBroker()
    rel=target.resolve().relative_to(root.resolve()).as_posix()
    binding=GovernedFilesystemEffector.canonical_target(RID,rel)
    c=SimpleNamespace(lease_id="lease",reservation_id="reservation",claim_hash="claim-"+target.name,adapter_id=AD)
    lease={"lease_id":"lease","reservation_id":"reservation","operation_id":"FS_WRITE_REPLACE_BYTES","expires_at":"2999-01-01T00:00:00+00:00"}
    reg={"adapter_id":AD,"effector_id":EF};scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    issued=b.issue(claim=c,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-05T00:00:00+00:00")
    assert issued["status"]=="HANDLE_ISSUED",issued
    e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b)
    x=GovernedFilesystemEffectContext(slots={"replication_prometheus_write":[issued["handle"]]},effector=e,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    x.begin();return x
def result():
    return {"replication_readiness_score":0.8,"external_reproduction_preparedness":0.7,"replication_protocol_completeness":0.6,"component_scores":{"alpha":0.5}}
with TemporaryDirectory() as td:
    root=Path(td);target=root/"readiness.prom";obj=OpenSourceReplicationReadiness(root=root)
    try: obj._write_prometheus(target,result(),fs_context=None);raise AssertionError("missing_context")
    except PermissionError: pass
    assert not target.exists()
    target.write_text("OLD-CONTENT\n",encoding="utf-8")
    c=ctx(root,target);obj._write_prometheus(target,result(),fs_context=c)
    data=target.read_text(encoding="utf-8")
    assert "OLD-CONTENT" not in data and "oce_open_source_replication_readiness_score 0.8" in data
    assert c.remaining()["replication_prometheus_write"]==0
    try: obj._write_prometheus(target,result(),fs_context=c);raise AssertionError("replay")
    except RuntimeError: pass
    wrong=root/"wrong.prom";cw=ctx(root,wrong)
    try: obj._write_prometheus(target,result(),fs_context=cw);raise AssertionError("wrong_binding")
    except RuntimeError: pass
    assert not wrong.exists()
print("P162G6_INDEX90_REAL_TCB_OK")
print("EXISTING_PROMETHEUS_REPLACE_SEMANTICS_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("REPLAY_FAIL_CLOSED_OK")
print("TARGET_BINDING_FAIL_CLOSED_OK")
print("AUTHORITY_MINTING=false")
print("AMBIENT_FALLBACK=false")
