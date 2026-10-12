from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.civilizational_state_persistence import CivilizationalStatePersistence
from ontology.persistent_civilizational_runtime import PersistentCivilizationalRuntime
from ontology.state_replication_integrity_validator import StateReplicationIntegrityValidator
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="root"; AD="adapter"; EF="effector"; SLOT="state_write_replace"
def context(root,target):
    b=ScopedHandleBroker(); rel=target.resolve().relative_to(root.resolve()).as_posix()
    binding=GovernedFilesystemEffector.canonical_target(RID,rel)
    c=SimpleNamespace(lease_id="lease",reservation_id="reservation",claim_hash="claim-"+target.name,adapter_id=AD)
    lease={"lease_id":"lease","reservation_id":"reservation","operation_id":"FS_WRITE_REPLACE_BYTES","expires_at":"2999-01-01T00:00:00+00:00"}
    reg={"adapter_id":AD,"effector_id":EF}; scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    issued=b.issue(claim=c,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-06T00:00:00+00:00")
    assert issued["status"]=="HANDLE_ISSUED",issued
    e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b)
    x=GovernedFilesystemEffectContext(slots={SLOT:[issued["handle"]]},effector=e,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF); x.begin(); return x
class CapturePersistence:
    def __init__(self): self.calls=[]
    def load(self,*a,**k): return {"state":{}}
    def save(self,*a,**k): self.calls.append((a,k)); return {"success":True}
class Governor:
    def step(self,**kw): return {"governed":True}
with TemporaryDirectory() as td:
    root=Path(td); store=root/"state"; store.mkdir(); p=CivilizationalStatePersistence(str(store)); target=store/"latest_state.json"
    target.write_text("SENTINEL",encoding="utf-8")
    try: p.save({"a":1})
    except PermissionError: pass
    else: raise AssertionError("missing context accepted")
    assert target.read_text(encoding="utf-8")=="SENTINEL"
    c=context(root,target); r=p.save({"a":1},filesystem_context=c)
    assert r["success"] is True and c.remaining()[SLOT]==0 and p.load()["state"]=={"a":1}
    before=target.read_bytes()
    try: p.save({"a":2},filesystem_context=c)
    except RuntimeError: pass
    else: raise AssertionError("replay accepted")
    assert target.read_bytes()==before
    wrong=store/"wrong.json"; cw=context(root,wrong); before=target.read_bytes()
    try: p.save({"a":3},filesystem_context=cw)
    except RuntimeError: pass
    else: raise AssertionError("wrong binding accepted")
    assert target.read_bytes()==before and not wrong.exists()
    cs=context(root,target); rr=p.step({"step":1},filesystem_context=cs)
    assert rr["state_restored"] is True and rr["load_result"]["state"]=={"step":1}
    cap=CapturePersistence(); rt=PersistentCivilizationalRuntime.__new__(PersistentCivilizationalRuntime)
    rt.primitive="PERSISTENT_CIVILIZATIONAL_RUNTIME"; rt.persistence=cap; rt.governor=Governor(); marker=object(); rt.step(filesystem_context=marker)
    assert cap.calls[-1][1]["filesystem_context"] is marker
    cap2=CapturePersistence(); v=StateReplicationIntegrityValidator.__new__(StateReplicationIntegrityValidator); v.persistence=cap2
    marker2=object(); state={"civilization":"open_cognitive_ecology","version":1}; cap2.load=lambda *a,**k: {"state":state}
    out=v.step(state,filesystem_context=marker2)
    assert out["validation_success"] is True and cap2.calls[-1][1]["filesystem_context"] is marker2
print("P162G6_WAVE2_REMEDIATION01_STATE_PERSISTENCE_OK")
print("FUNCTIONAL_SAVE_LOAD_OK"); print("MISSING_CONTEXT_FAIL_CLOSED_OK"); print("REPLAY_FAIL_CLOSED_OK")
print("TARGET_BINDING_FAIL_CLOSED_OK"); print("INTERNAL_STEP_PROPAGATION_OK"); print("TWO_PRODUCTION_CALLERS_PROPAGATION_OK")
print("AUTHORITY_MINTING=false"); print("AMBIENT_FALLBACK=false")
