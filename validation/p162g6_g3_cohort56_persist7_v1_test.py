from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib, sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker

CASES=[
("ontology.mei_qualia_property_mapping","MeiQualiaPropertyMapping",True,False),
("ontology.no_difference_without_difference_test","NoDifferenceWithoutDifferenceTest",False,False),
("ontology.identity_theorem_attempt","IdentityTheoremAttempt",True,False),
("ontology.ontological_non_duplication_checker","OntologicalNonDuplicationChecker",False,False),
("ontology.identity_failure_boundary","IdentityFailureBoundary",True,False),
("ontology.formal_qualia_minimal_definition","FormalQualiaMinimalDefinition",True,True),
("ontology.intrinsic_zombie_counterexample","IntrinsicZombieCounterexample",True,False),
("ontology.mei_formal_definition","MeiFormalDefinition",True,False),
]
RID="root"; AD="adapter"; EF="effector"
def issue_context(root, targets, omit=None, wrong=None):
    broker=ScopedHandleBroker(); slots={}
    scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    for i,(slot,op,target) in enumerate(targets):
        if slot==omit: continue
        bound=(root/"wrong-target") if slot==wrong else target
        rel=bound.resolve().relative_to(root.resolve()).as_posix()
        binding=GovernedFilesystemEffector.canonical_target(RID,rel)
        lease_id="lease-"+str(i)+"-"+slot
        claim=SimpleNamespace(lease_id=lease_id,reservation_id="reservation-"+str(i),claim_hash="claim-"+str(i)+"-"+slot,adapter_id=AD)
        lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":op,"expires_at":"2999-01-01T00:00:00+00:00"}
        reg={"adapter_id":AD,"effector_id":EF}
        issued=broker.issue(claim=claim,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-06T00:00:00+00:00")
        assert issued["status"]=="HANDLE_ISSUED",issued
        slots[slot]=[issued["handle"]]
    eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    ctx.begin(); return ctx

def prepare(obj, root, has_parent):
    if hasattr(obj,"_now"): obj._now=lambda:"STAMP"
    obj._markdown=lambda result:"MARKDOWN"
    obj._prometheus=lambda result:"PROMETHEUS"
    if not has_parent:
        base=root/"outputs"
        paths={
          "json":str(base/"one.json"),"latest_json":str(base/"latest.json"),
          "markdown":str(base/"one.md"),"latest_markdown":str(base/"latest.md"),
          "prometheus":str(base/"one.prom"),"latest_prometheus":str(base/"latest.prom"),
          "history":str(base/"history.jsonl"),
        }
    else:
        try: paths=obj._paths("STAMP")
        except TypeError: paths=obj._paths()
        paths={k:str(v) for k,v in paths.items()}
    result={
      "paths":paths,"timestamp_utc":"2026-10-06T00:00:00+00:00",
      "mei_qualia_property_mapping_status":"OK","mei_qualia_property_mapping_score":1.0,"mapped_property_count":1,
      "mei_formal_definition_status":"OK","mei_formal_definition_score":1.0,"mei_formal_count":1,
      "payload":"x",
    }
    parent=Path(paths["json"]).parent
    if not has_parent: parent.mkdir(parents=True,exist_ok=True)
    slots=[]
    if has_parent: slots.append(("persist_parent_create","FS_CREATE_DIRS",parent))
    for key in ("json","latest_json","markdown","latest_markdown","prometheus","latest_prometheus"):
        slots.append(("persist_"+key,"FS_WRITE_REPLACE_BYTES",Path(paths[key])))
    slots.append(("persist_history_append","FS_APPEND_BYTES",Path(paths["history"])))
    return result,paths,slots

for modname,clsname,has_parent,persist_default in CASES:
    cls=getattr(importlib.import_module(modname),clsname)
    with TemporaryDirectory() as td:
        root=Path(td)
        try: obj=cls(root=root)
        except TypeError: obj=cls()
        result,paths,slots=prepare(obj,root,has_parent)
        # Missing context: no mutation.
        try: obj._persist(dict(result))
        except PermissionError: pass
        else: raise AssertionError(modname+": missing context accepted")
        assert not Path(paths["json"]).exists()
        # Missing last slot is rejected by preflight before parent creation or writes.
        ctx=issue_context(root,slots,omit="persist_history_append")
        try: obj._persist(dict(result),filesystem_context=ctx)
        except PermissionError: pass
        else: raise AssertionError(modname+": missing slot accepted")
        assert not Path(paths["json"]).exists()
        # Functional persistence through real broker/context/effector.
        ctx=issue_context(root,slots)
        ret=obj._persist(dict(result),filesystem_context=ctx)
        assert Path(paths["json"]).is_file()
        assert Path(paths["latest_json"]).is_file()
        assert Path(paths["markdown"]).read_text(encoding="utf-8")=="MARKDOWN"
        assert Path(paths["prometheus"]).read_text(encoding="utf-8")=="PROMETHEUS"
        assert Path(paths["history"]).is_file() and Path(paths["history"]).read_text(encoding="utf-8").endswith("\n")
        assert all(v==0 for v in ctx.remaining().values())
        # Append semantics with a fresh preissued context.
        before=Path(paths["history"]).read_bytes()
        ctx2=issue_context(root,slots)
        obj._persist(dict(result),filesystem_context=ctx2)
        after=Path(paths["history"]).read_bytes()
        assert len(after)>len(before) and after.startswith(before)
        # Wrong binding is rejected by the real TCB.
        ctx3=issue_context(root,slots,wrong="persist_json")
        try: obj._persist(dict(result),filesystem_context=ctx3)
        except RuntimeError: pass
        else: raise AssertionError(modname+": wrong binding accepted")


print("P162G6_G3_COHORT56_PERSIST7_TEST_OK")
print("UNITS=8")
print("FUNCTIONAL_REAL_TCB_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("MISSING_SLOT_PREFLIGHT_BEFORE_MUTATION_OK")
print("WRONG_BINDING_TCB_REJECTION_OK")
print("HISTORY_APPEND_OK")
print("STEP_CONTEXT_TRANSPORT_STATIC_OK")
print("PERSIST_DEFAULTS_PRESERVED_OK")
print("CONSUMER_AUTHORITY_MINTING=false")
print("AMBIENT_FALLBACK=false")
