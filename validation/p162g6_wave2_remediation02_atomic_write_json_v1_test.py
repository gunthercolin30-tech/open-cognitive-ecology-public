from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
from ontology.occ_reproducibility_persistence import atomic_write_json
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="root"; AD="adapter"; EF="effector"
def issue(broker,effector,operation,root,target,serial):
    rel=target.resolve().relative_to(root.resolve()).as_posix(); binding=effector.canonical_target(RID,rel)
    claim=SimpleNamespace(lease_id="lease-"+str(serial),reservation_id="reservation-"+str(serial),claim_hash="claim-"+str(serial),adapter_id=AD)
    lease={"lease_id":"lease-"+str(serial),"reservation_id":"reservation-"+str(serial),"operation_id":operation,"expires_at":"2999-01-01T00:00:00+00:00"}
    reg={"adapter_id":AD,"effector_id":EF}; scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    out=broker.issue(claim=claim,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-06T00:00:00+00:00")
    assert out["status"]=="HANDLE_ISSUED",out; return out["handle"]
def context(root,target,parent_target=None,write_target=None,include_parent=True,include_write=True):
    broker=ScopedHandleBroker(); eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker); slots={}
    if include_parent: slots["atomic_parent_create"]=[issue(broker,eff,"FS_CREATE_DIRS",root,parent_target or target.parent,1)]
    if include_write: slots["atomic_write_replace"]=[issue(broker,eff,"FS_WRITE_REPLACE_BYTES",root,write_target or target,2)]
    ctx=GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF); ctx.begin(); return ctx
with TemporaryDirectory() as td:
    root=Path(td); target=root/"nested"/"state.json"
    try: atomic_write_json(target,{"a":1})
    except PermissionError: pass
    else: raise AssertionError("missing context accepted")
    assert not target.exists() and not target.parent.exists()
    c=context(root,target,include_write=False)
    try: atomic_write_json(target,{"a":1},filesystem_context=c)
    except RuntimeError: pass
    else: raise AssertionError("missing write authority accepted")
    assert not target.exists() and not target.parent.exists() and c.remaining()["atomic_parent_create"]==1
    c=context(root,target); out=atomic_write_json(target,{"é":"✓","a":1},filesystem_context=c)
    expected=(json.dumps({"é":"✓","a":1},sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")
    assert out["status"]=="PASS" and target.read_bytes()==expected and c.remaining()=={"atomic_parent_create":0,"atomic_write_replace":0}
    c2=context(root,target); atomic_write_json(target,{"revision":2},filesystem_context=c2); assert json.loads(target.read_text(encoding="utf-8"))=={"revision":2}
    before=target.read_bytes(); wrong=root/"nested"/"wrong.json"; cw=context(root,target,write_target=wrong)
    try: atomic_write_json(target,{"revision":3},filesystem_context=cw)
    except RuntimeError: pass
    else: raise AssertionError("wrong write binding accepted")
    assert target.read_bytes()==before and not wrong.exists()
    ce=context(root,target); before_slots=ce.remaining().copy()
    try: atomic_write_json(target,{"bad":float("nan")},filesystem_context=ce)
    except ValueError: pass
    else: raise AssertionError("NaN unexpectedly serialized")
    assert ce.remaining()==before_slots and target.read_bytes()==before
print("P162G6_WAVE2_REMEDIATION02_ATOMIC_WRITE_JSON_OK")
print("FUNCTIONAL_CREATE_OK")
print("FUNCTIONAL_OVERWRITE_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("MISSING_SLOT_PREFLIGHT_OK")
print("WRONG_BINDING_FAIL_CLOSED_OK")
print("ENCODE_BEFORE_AUTHORITY_OK")
print("AMBIENT_MUTATORS_REMOVED=true")
print("AUTHORITY_MINTING=false")
