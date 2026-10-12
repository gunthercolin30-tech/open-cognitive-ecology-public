from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from ontology.governed_execution_adapter import ExecutionClaimManager
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.governed_filesystem_effector import GovernedFilesystemEffector,FilesystemEffectRequest
NOW="2026-10-02T08:30:00+00:00"
def lease():
    return {"lease_id":"L","reservation_id":"R","executor_id":"E","capability_instance_id":"CI","operation_id":"FS_COPY2","invocation_request_hash":"IH","effective_execution_scope_hash":"SH","audience":"FSA","reservation_status":"RESERVED","used":False,"revoked":False,"expires_at":"2999-01-01T00:00:00+00:00"}
def reg():
    return {"adapter_id":"FSA","adapter_hash":"FSH","effector_id":"FILESYSTEM","capability_ids":["FILESYSTEM_CAP"],"operation_ids":["FS_COPY2"],"status":"ACTIVE"}
def state():
    return {"lease_state_version":1,"reservation_state_version":1,"token_state_version":1,"target_state_version":1,"capability_runtime_attestation":"OK","adapter_attestation":"FSH","critical_precondition_snapshot":{"ok":True},"security_state":"VERIFIED","revoked":False,"target_current":True,"critical_preconditions_satisfied":True,"credential_identity_verified":True}
def claim():
    r=ExecutionClaimManager().claim(lease=lease(),registry_entry=reg(),executor_instance_id="E",capability_instance_id="CI",capability_id="FILESYSTEM_CAP",operation_id="FS_COPY2",invocation_request_hash="IH",effective_execution_scope_hash="SH",point_of_effect_state=state(),now_iso=NOW)
    assert r["status"]=="EXECUTION_STARTED"; return r["claim"]
def issue(hb,c,target):
    sc={"operation":"FS_COPY2","source":target["source"],"destination":target["destination"],"ambient_authority":False,"child_inheritance":False,"transferable":False}
    r=hb.issue(claim=c,lease=lease(),registry_entry=reg(),requested_scope=sc,authorized_scope=sc,target_binding=target,audience="FSA",now_iso=NOW)
    assert r["status"]=="HANDLE_ISSUED"; return r["handle"]
with TemporaryDirectory() as td:
    root=Path(td); src=root/"src"; dst=root/"dst"; src.mkdir(); dst.mkdir()
    (src/"a").write_bytes(b"abc"); os.chmod(src/"a",0o640)
    hb=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb)
    target={"source":"filesystem://S/a","destination":"filesystem://D/b"}
    h=issue(hb,claim(),target); q=FilesystemEffectRequest("FS_COPY2","D","b",None,"S","a")
    r=e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")
    assert r["status"]=="EFFECT_CONFIRMED" and (dst/"b").read_bytes()==b"abc"
    assert (dst/"b").stat().st_mode&0o777==0o640
    assert e.execute(request=q,handle=h,adapter_id="FSA",effector_id="FILESYSTEM")["reason"]=="handle_replay_or_unknown"
    hb2=ScopedHandleBroker(); h2=issue(hb2,claim(),{"source":"filesystem://S/a","destination":"filesystem://D/c"})
    e2=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb2)
    assert e2.execute(request=q,handle=h2,adapter_id="FSA",effector_id="FILESYSTEM")["reason"]=="target_mismatch"
    outside=root/"outside"; outside.write_bytes(b"x"); (src/"link").symlink_to(outside)
    hb3=ScopedHandleBroker(); t3={"source":"filesystem://S/link","destination":"filesystem://D/z"}; h3=issue(hb3,claim(),t3)
    q3=FilesystemEffectRequest("FS_COPY2","D","z",None,"S","link")
    e3=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb3)
    assert e3.execute(request=q3,handle=h3,adapter_id="FSA",effector_id="FILESYSTEM")["reason"]=="source_outside_registered_root"
    hb4=ScopedHandleBroker(); t4={"source":"filesystem://S/a","destination":"filesystem://D/concurrent"}; h4=issue(hb4,claim(),t4)
    q4=FilesystemEffectRequest("FS_COPY2","D","concurrent",None,"S","a")
    e4=GovernedFilesystemEffector(root_registry={"S":str(src),"D":str(dst)},handle_broker=hb4)
    with ThreadPoolExecutor(max_workers=8) as pool:
        rr=list(pool.map(lambda _:e4.execute(request=q4,handle=h4,adapter_id="FSA",effector_id="FILESYSTEM"),range(16)))
    assert sum(x["status"]=="EFFECT_CONFIRMED" for x in rr)==1
    assert sum(x.get("reason")=="handle_replay_or_unknown" for x in rr)==15
print("P162G6_FILESYSTEM_COPY2_TCB_CROWN_OK")
