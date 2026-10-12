from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import ast, importlib, sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="root"; AD="adapter"; EF="effector"
CASES=[
 ("ontology.self_description_registry","SelfDescriptionRegistry","self_description_registry",{"reflexive_model_usage":{},"self_descriptions":[]}),
 ("ontology.reflexive_model_usage_tester","ReflexiveModelUsageTester","reflexive_model_usage_tester",{"trajectory_memory":{},"memory_integration":{},"identity_continuity":{},"rupture_detection":{}}),
]
def make_ctx(root,outdir,stem,omit=None,wrong=None):
    broker=ScopedHandleBroker(); scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    spec=[("persist_parent_create","FS_CREATE_DIRS",outdir),("persist_json","FS_WRITE_REPLACE_BYTES",outdir/("latest_"+stem+".json")),("persist_markdown","FS_WRITE_REPLACE_BYTES",outdir/("latest_"+stem+".md")),("persist_prometheus","FS_WRITE_REPLACE_BYTES",outdir/("latest_"+stem+".prom")),("persist_history_append","FS_APPEND_BYTES",outdir/(stem+"_history.jsonl"))]
    slots={}
    for i,(slot,op,path) in enumerate(spec):
        if slot==omit: continue
        bound=(root/"wrong") if slot==wrong else path
        rel=bound.resolve().relative_to(root.resolve()).as_posix()
        claim=SimpleNamespace(lease_id="lease"+str(i),reservation_id="res"+str(i),claim_hash="claim"+str(i),adapter_id=AD)
        lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":op,"expires_at":"2999-01-01T00:00:00+00:00"}
        issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":AD,"effector_id":EF},requested_scope=scope,authorized_scope=scope,target_binding=GovernedFilesystemEffector.canonical_target(RID,rel),audience=AD,now_iso="2026-10-06T00:00:00+00:00")
        assert issued["status"]=="HANDLE_ISSUED",issued
        slots[slot]=[issued["handle"]]
    ctx=GovernedFilesystemEffectContext(slots=slots,effector=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker),root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    ctx.begin(); return ctx
for modname,clsname,stem,inputs in CASES:
    mod=importlib.import_module(modname); cls=getattr(mod,clsname); original=mod.OUTPUT_DIR
    try:
      with TemporaryDirectory() as td:
        root=Path(td).resolve(); out=root/stem; mod.OUTPUT_DIR=out; obj=cls()
        dry=obj.step(inputs,persist=False); assert isinstance(dry,dict); assert not out.exists()
        try: obj.step(inputs,persist=True)
        except PermissionError: pass
        else: raise AssertionError("ambient persistence accepted")
        assert not out.exists()
        ctx=make_ctx(root,out,stem,omit="persist_prometheus")
        try: obj.step(inputs,persist=True,fs_context=ctx)
        except PermissionError: pass
        else: raise AssertionError("incomplete authority accepted")
        assert not out.exists()
        ctx=make_ctx(root,out,stem,wrong="persist_parent_create")
        try: obj.step(inputs,persist=True,fs_context=ctx)
        except RuntimeError: pass
        else: raise AssertionError("wrong binding accepted")
        assert not out.exists()
        ctx=make_ctx(root,out,stem); result=obj.step(inputs,persist=True,fs_context=ctx)
        assert all(v==0 for v in ctx.remaining().values())
        paths={k:Path(v) for k,v in result["paths"].items()}; assert all(paths[k].is_file() for k in ("json","markdown","prometheus","history")); assert len(paths["history"].read_text().splitlines())==1
        try: obj.step(inputs,persist=True,fs_context=ctx)
        except (RuntimeError,KeyError,PermissionError): pass
        else: raise AssertionError("handle replay accepted")
      tree=ast.parse(Path(mod.__file__).read_text()); cs=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==clsname]; assert len(cs)==1; ps=[n for n in cs[0].body if isinstance(n,ast.FunctionDef) and n.name=="_persist"]; assert len(ps)==1
      txt=ast.unparse(ps[0]); assert ".mkdir(" not in txt and ".write_text(" not in txt and ".open(" not in txt; assert txt.count("execute_path")==5; assert "ScopedHandleBroker" not in txt
    finally: mod.OUTPUT_DIR=original
print("P162G6_G3_CCP02B_ATOMIC_REMEDIATION_TEST_OK")
print("FUNCTIONAL_TEST_OK")
print("DEGRADATION_TEST_OK")
print("NON_REGRESSION_TEST_OK")
print("REAL_TCB_OK")
print("EXACT_HANDLE_CONSUMPTION_OK")
