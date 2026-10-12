from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.external_replication_evidence_aggregator import ExternalReplicationEvidenceAggregator
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker

RID="root"; AD="adapter"; EF="effector"
def make_context(root, targets):
    broker=ScopedHandleBroker(); handles=[]
    scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    for i,target in enumerate(targets):
        rel=target.resolve().relative_to(root.resolve()).as_posix()
        binding=GovernedFilesystemEffector.canonical_target(RID,rel)
        claim=SimpleNamespace(lease_id="lease"+str(i),reservation_id="reservation"+str(i),claim_hash="claim"+str(i),adapter_id=AD)
        lease={"lease_id":"lease"+str(i),"reservation_id":"reservation"+str(i),"operation_id":"FS_WRITE_REPLACE_BYTES","expires_at":"2999-01-01T00:00:00+00:00"}
        issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":AD,"effector_id":EF},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-05T00:00:00+00:00")
        assert issued["status"]=="HANDLE_ISSUED",issued
        handles.append(issued["handle"])
    eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(slots={"external_replication_json_write":handles},effector=eff,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    ctx.begin(); return ctx

with TemporaryDirectory() as td:
    root=Path(td); target=root/"state.json"
    obj=ExternalReplicationEvidenceAggregator.__new__(ExternalReplicationEvidenceAggregator)
    try:
        obj._write_json(target,{"v":1},fs_context=None); raise AssertionError("missing_context_not_rejected")
    except PermissionError: pass
    assert not target.exists()
    target.write_text('{"old":true}',encoding="utf-8")
    ctx=make_context(root,[target])
    obj._write_json(target,{"v":2},fs_context=ctx)
    assert '"v": 2' in target.read_text(encoding="utf-8")
    assert "old" not in target.read_text(encoding="utf-8")
    assert ctx.remaining()["external_replication_json_write"]==0
    try:
        obj._write_json(target,{"v":3},fs_context=ctx); raise AssertionError("replay_not_rejected")
    except RuntimeError: pass
    wrong=root/"wrong.json"; ctx2=make_context(root,[wrong])
    try:
        obj._write_json(target,{"v":4},fs_context=ctx2); raise AssertionError("wrong_binding_not_rejected")
    except RuntimeError: pass
    assert not wrong.exists()
print("P162G6_INDEX40_REAL_TCB_OK")
print("EXISTING_JSON_REPLACE_SEMANTICS_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("REPLAY_FAIL_CLOSED_OK")
print("TARGET_BINDING_FAIL_CLOSED_OK")
print("AUTHORITY_MINTING=false")
print("AMBIENT_FALLBACK=false")
