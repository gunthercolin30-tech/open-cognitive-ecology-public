from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import ast, importlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
CASES=[("ontology.shared_reference_frame_detector","SharedReferenceFrameDetector"),("ontology.coalition_detector","CoalitionDetector"),("ontology.reference_frame_merging","ReferenceFrameMerging"),("ontology.conflict_detector","ConflictDetector"),("ontology.reference_frame_fragmentation","ReferenceFrameFragmentation")]
RID="root"; AD="adapter"; EF="effector"
def make_ctx(root,target,omit=None,wrong=None):
    broker=ScopedHandleBroker(); slots={}; scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    for i,(slot,op,p) in enumerate([("atomic_parent_create","FS_CREATE_DIRS",target.parent),("atomic_write_replace","FS_WRITE_REPLACE_BYTES",target)]):
        if slot==omit: continue
        bound=(root/"wrong") if slot==wrong else p
        rel=bound.resolve().relative_to(root.resolve()).as_posix()
        binding=GovernedFilesystemEffector.canonical_target(RID,rel)
        claim=SimpleNamespace(lease_id="lease-"+str(i),reservation_id="res-"+str(i),claim_hash="claim-"+str(i),adapter_id=AD)
        lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":op,"expires_at":"2999-01-01T00:00:00+00:00"}
        issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":AD,"effector_id":EF},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-06T00:00:00+00:00")
        assert issued["status"]=="HANDLE_ISSUED",issued
        slots[slot]=[issued["handle"]]
    c=GovernedFilesystemEffectContext(slots=slots,effector=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker),root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    c.begin(); return c
for modname,clsname in CASES:
    mod=importlib.import_module(modname); cls=getattr(mod,clsname)
    with TemporaryDirectory() as td:
        root=Path(td); target=root/"nested"/"out.json"; payload={"z":"é","a":[1,2]}
        try: cls._atomic_write(target,payload,None)
        except PermissionError: pass
        else: raise AssertionError(modname+": missing context accepted")
        assert not target.parent.exists()
        c=make_ctx(root,target,omit="atomic_write_replace")
        try: cls._atomic_write(target,payload,c)
        except PermissionError: pass
        else: raise AssertionError(modname+": missing slot accepted")
        assert not target.parent.exists()
        c=make_ctx(root,target); cls._atomic_write(target,payload,c)
        expected=(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")
        assert target.read_bytes()==expected and all(v==0 for v in c.remaining().values())
        try: cls._atomic_write(target,payload,c)
        except (PermissionError,RuntimeError,KeyError): pass
        else: raise AssertionError(modname+": replay accepted")
        target2=root/"nested"/"wrongbind.json"; c2=make_ctx(root,target2,wrong="atomic_write_replace")
        try: cls._atomic_write(target2,payload,c2)
        except RuntimeError: pass
        else: raise AssertionError(modname+": wrong binding accepted")
        assert not target2.exists()
    tree=ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    hs=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="_atomic_write"]
    ss=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="step"]
    assert len(hs)==1 and len(ss)==1
    htxt=ast.unparse(hs[0]); stxt=ast.unparse(ss[0])
    assert not any(x in htxt for x in ("mkstemp","fdopen","os.replace","os.unlink","path.parent.mkdir"))
    assert "fs_context" in [a.arg for a in ss[0].args.args+ss[0].args.kwonlyargs]
    assert "fs_context" in stxt and ".begin(" not in htxt and "ScopedHandleBroker" not in htxt
coal=(ROOT/"ontology/coalition_detector.py").read_text(encoding="utf-8")
assert "SharedReferenceFrameDetector(root=self.root).step(" in coal and "persist=False" in coal
print("P162G6_G3_CC4FE5_ATOMIC_WRITE_COHORT_TEST_OK")
print("UNITS=5"); print("HISTORICAL_N=15"); print("FUNCTIONAL_REAL_TCB_OK")
print("EXACT_JSON_BYTES_OK"); print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("MISSING_SLOT_PREFLIGHT_BEFORE_MUTATION_OK"); print("WRONG_BINDING_TCB_REJECTION_OK")
print("REPLAY_FAIL_CLOSED_OK"); print("STEP_CONTEXT_TRANSPORT_STATIC_OK")
print("KNOWN_INTERNAL_PERSIST_FALSE_ROUTE_OK"); print("CONSUMER_AUTHORITY_MINTING=false"); print("AMBIENT_FALLBACK=false")
