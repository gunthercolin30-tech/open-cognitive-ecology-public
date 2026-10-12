from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import ast
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.replication_statistical_validation import ReplicationStatisticalValidation
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="root"; AD="adapter"; EF="effector"
def one_handle(broker, root, target, operation, suffix):
    rel=target.resolve().relative_to(root.resolve()).as_posix()
    binding=GovernedFilesystemEffector.canonical_target(RID, rel)
    claim=SimpleNamespace(lease_id="lease-"+suffix,reservation_id="reservation-"+suffix,claim_hash="claim-"+suffix,adapter_id=AD)
    lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":operation,"expires_at":"2999-01-01T00:00:00+00:00"}
    registry={"adapter_id":AD,"effector_id":EF}; scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    issued=broker.issue(claim=claim,lease=lease,registry_entry=registry,requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-06T00:00:00+00:00")
    assert issued["status"]=="HANDLE_ISSUED",issued
    return issued["handle"]
def context(root, history, include_parent=True, include_append=True, wrong_append=None):
    broker=ScopedHandleBroker(); slots={}
    if include_parent: slots["history_parent_create"]=[one_handle(broker,root,history.parent,"FS_CREATE_DIRS","parent")]
    if include_append:
        target=wrong_append if wrong_append is not None else history
        slots["history_append"]=[one_handle(broker,root,target,"FS_APPEND_BYTES","append")]
    eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF); ctx.begin(); return ctx
with TemporaryDirectory() as td:
    root=Path(td).resolve(); obj=ReplicationStatisticalValidation(output_dir=root/"out"); history=obj.history_path
    a={"z":2,"a":1}; b={"b":3}
    try: obj._append_jsonl(history,a,fs_context=None); raise AssertionError("missing_context_not_rejected")
    except PermissionError: pass
    assert not history.parent.exists()
    for parent_ok,append_ok in ((False,True),(True,False)):
        c=context(root,history,include_parent=parent_ok,include_append=append_ok)
        try: obj._append_jsonl(history,a,fs_context=c); raise AssertionError("missing_slot_not_rejected")
        except RuntimeError: pass
        assert not history.parent.exists()
    c1=context(root,history); obj._append_jsonl(history,a,fs_context=c1)
    assert history.read_text(encoding="utf-8")=='{"a": 1, "z": 2}\n'
    assert c1.remaining()["history_parent_create"]==0 and c1.remaining()["history_append"]==0
    c2=context(root,history); obj._append_jsonl(history,b,fs_context=c2)
    assert history.read_text(encoding="utf-8")=='{"a": 1, "z": 2}\n{"b": 3}\n'
    before=history.read_bytes()
    try: obj._append_jsonl(history,{"x":9},fs_context=c2); raise AssertionError("replay_not_rejected")
    except RuntimeError: pass
    assert history.read_bytes()==before
    wrong=root/"wrong.jsonl"; cw=context(root,history,wrong_append=wrong)
    try: obj._append_jsonl(history,{"x":1},fs_context=cw); raise AssertionError("wrong_binding_not_rejected")
    except RuntimeError: pass
    assert history.read_bytes()==before and not wrong.exists()
    called=[]; original=obj._append_jsonl; obj._append_jsonl=lambda *args,**kwargs: called.append((args,kwargs))
    obj.step(statistical_context={},persist=False,fs_context=None); assert called==[]; obj._append_jsonl=original
src=Path(__file__).resolve().parents[1]/"ontology"/"replication_statistical_validation.py"; text=src.read_text(encoding="utf-8"); tree=ast.parse(text)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="ReplicationStatisticalValidation")
helper=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="_append_jsonl"); step=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="step")
calls=[n for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=="self" and n.func.attr=="_append_jsonl"]
assert len(calls)==1; kw={k.arg:k.value for k in calls[0].keywords}; assert isinstance(kw.get("fs_context"),ast.Name) and kw["fs_context"].id=="fs_context"
hsrc=ast.get_source_segment(text,helper); attrs=[n.func.attr for n in ast.walk(helper) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
assert "mkdir" not in attrs and "open" not in attrs and attrs.count("execute_path")==2
assert "ScopedHandleBroker" not in hsrc and "GovernedFilesystemEffector" not in hsrc
print("P162G6_G3C002_C4202_TRANSACTIONAL_REMEDIATION_TEST_OK")
print("FUNCTIONAL_JSONL_APPEND_OK")
print("REPEATED_APPEND_ORDER_CONTENT_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("MISSING_SLOT_PREFLIGHT_FAIL_CLOSED_OK")
print("REPLAY_FAIL_CLOSED_OK")
print("TARGET_BINDING_FAIL_CLOSED_OK")
print("PERSIST_FALSE_NO_HELPER_EFFECT_OK")
print("STEP_CONTEXT_TRANSPORT_OK")
print("AUTHORITY_MINTING=false")
print("AMBIENT_FALLBACK=false")
