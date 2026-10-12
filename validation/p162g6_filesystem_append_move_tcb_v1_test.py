from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from ontology.governed_execution_adapter import ExecutionClaimManager
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.governed_filesystem_effector import GovernedFilesystemEffector,FilesystemEffectRequest
NOW="2026-10-02T08:30:00+00:00"
def lease(op):
    return {"lease_id":"L-"+op,"reservation_id":"R-"+op,"executor_id":"E","capability_instance_id":"CI","operation_id":op,"invocation_request_hash":"IH-"+op,"effective_execution_scope_hash":"SH-"+op,"audience":"FSA","reservation_status":"RESERVED","used":False,"revoked":False,"expires_at":"2999-01-01T00:00:00+00:00"}
def reg(op):
    return {"adapter_id":"FSA","adapter_hash":"FSH","effector_id":"FILESYSTEM","capability_ids":["FILESYSTEM_CAP"],"operation_ids":[op],"status":"ACTIVE"}
def state():
    return {"lease_state_version":1,"reservation_state_version":1,"token_state_version":1,"target_state_version":1,"capability_runtime_attestation":"OK","adapter_attestation":"FSH","critical_precondition_snapshot":{"ok":True},"security_state":"VERIFIED","revoked":False,"target_current":True,"critical_preconditions_satisfied":True,"credential_identity_verified":True}
def claim(op):
    r=ExecutionClaimManager().claim(lease=lease(op),registry_entry=reg(op),executor_instance_id="E",capability_instance_id="CI",capability_id="FILESYSTEM_CAP",operation_id=op,invocation_request_hash="IH-"+op,effective_execution_scope_hash="SH-"+op,point_of_effect_state=state(),now_iso=NOW)
    assert r["status"]=="EXECUTION_STARTED"; return r["claim"]
def issue(hb,op,target):
    c=claim(op); sc={"operation":op,"target_binding":target,"ambient_authority":False,"child_inheritance":False,"transferable":False}
    r=hb.issue(claim=c,lease=lease(op),registry_entry=reg(op),requested_scope=sc,authorized_scope=sc,target_binding=target,audience="FSA",now_iso=NOW)
    assert r["status"]=="HANDLE_ISSUED"; return r["handle"]

with TemporaryDirectory() as td:
    root=Path(td); (root/"log").write_bytes(b"A")
    hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"r":str(root)},handle_broker=hb)
    target=e.canonical_target("r","log"); h=issue(hb,"FS_APPEND_BYTES",target)
    q=FilesystemEffectRequest("FS_APPEND_BYTES","r","log",b"B")
    assert e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")["status"]=="EFFECT_CONFIRMED"
    assert (root/"log").read_bytes()==b"AB"
    assert e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")["reason"]=="handle_replay_or_unknown"

with TemporaryDirectory() as td:
    root=Path(td); (root/"log").write_bytes(b"")
    hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"r":str(root)},handle_broker=hb)
    target=e.canonical_target("r","log"); h=issue(hb,"FS_APPEND_BYTES",target)
    q=FilesystemEffectRequest("FS_APPEND_BYTES","r","log",b"Z")
    with ThreadPoolExecutor(max_workers=8) as pool:
        rr=list(pool.map(lambda _:e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM"),range(16)))
    assert sum(x["status"]=="EFFECT_CONFIRMED" for x in rr)==1
    assert (root/"log").read_bytes()==b"Z"

with TemporaryDirectory() as td:
    root=Path(td); outside=root.parent/(root.name+"_outside"); outside.write_bytes(b"X")
    try:
        (root/"link").symlink_to(outside)
        hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"r":str(root)},handle_broker=hb)
        target=e.canonical_target("r","link"); h=issue(hb,"FS_APPEND_BYTES",target)
        q=FilesystemEffectRequest("FS_APPEND_BYTES","r","link",b"Y")
        r=e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")
        assert r["reason"]=="target_symlink_forbidden" and outside.read_bytes()==b"X"
    finally:
        outside.unlink(missing_ok=True)

with TemporaryDirectory() as td:
    base=Path(td); src=base/"src"; dst=base/"dst"; src.mkdir(); dst.mkdir()
    (src/"a").write_bytes(b"NEW"); (dst/"b").write_bytes(b"OLD")
    hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb)
    target={"source":e.canonical_target("S","a"),"destination":e.canonical_target("D","b")}
    h=issue(hb,"FS_MOVE_OR_REPLACE",target)
    q=FilesystemEffectRequest("FS_MOVE_OR_REPLACE","D","b",None,"S","a")
    r=e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")
    assert r["status"]=="EFFECT_CONFIRMED" and not (src/"a").exists() and (dst/"b").read_bytes()==b"NEW"

with TemporaryDirectory() as td:
    base=Path(td); src=base/"src"; dst=base/"dst"; src.mkdir(); dst.mkdir(); (src/"a").write_bytes(b"x")
    hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb)
    wrong={"source":e.canonical_target("S","a"),"destination":e.canonical_target("D","c")}
    h=issue(hb,"FS_MOVE_OR_REPLACE",wrong)
    q=FilesystemEffectRequest("FS_MOVE_OR_REPLACE","D","b",None,"S","a")
    assert e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")["reason"]=="target_mismatch"

with TemporaryDirectory() as td:
    base=Path(td); src=base/"src"; dst=base/"dst"; src.mkdir(); dst.mkdir(); (src/"a").write_bytes(b"abc")
    hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb)
    target={"source":e.canonical_target("S","a"),"destination":e.canonical_target("D","b")}
    h=issue(hb,"FS_COPY2",target)
    q=FilesystemEffectRequest("FS_COPY2","D","b",None,"S","a")
    assert e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")["status"]=="EFFECT_CONFIRMED"
    assert (dst/"b").read_bytes()==b"abc"

print("P162G6_FILESYSTEM_APPEND_MOVE_TCB_CROWN_OK")
