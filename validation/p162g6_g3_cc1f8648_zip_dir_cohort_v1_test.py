from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import ast, importlib, io, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
CASES=[
("ontology.reflexive_threshold_replication_result_evaluator","ReflexiveThresholdReplicationResultEvaluator"),
("ontology.reflexive_threshold_final_scientific_synthesis","ReflexiveThresholdFinalScientificSynthesis"),
]
RID="root"; AD="adapter"; EF="effector"; SLOT="zip_bundle_write"
def make_ctx(root,target,wrong=False):
    broker=ScopedHandleBroker(); scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    bound=(root/"wrong.zip") if wrong else target
    rel=bound.resolve().relative_to(root.resolve()).as_posix()
    binding=GovernedFilesystemEffector.canonical_target(RID,rel)
    claim=SimpleNamespace(lease_id="lease",reservation_id="res",claim_hash="claim",adapter_id=AD)
    lease={"lease_id":"lease","reservation_id":"res","operation_id":"FS_WRITE_REPLACE_BYTES","expires_at":"2999-01-01T00:00:00+00:00"}
    issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":AD,"effector_id":EF},
        requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,
        now_iso="2026-10-06T00:00:00+00:00")
    assert issued["status"]=="HANDLE_ISSUED",issued
    ctx=GovernedFilesystemEffectContext(slots={SLOT:[issued["handle"]]},
        effector=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker),
        root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    ctx.begin(); return ctx
def members_and_bytes(path):
    with zipfile.ZipFile(path,"r") as z:
        return z.namelist(),{n:z.read(n) for n in z.namelist()}
for modname,clsname in CASES:
    mod=importlib.import_module(modname); cls=getattr(mod,clsname)
    with TemporaryDirectory() as td:
        root=Path(td); src=root/"src"; src.mkdir()
        (src/"a.txt").write_bytes(b"A"); (src/"sub").mkdir(); (src/"sub"/"b.bin").write_bytes(b"B")
        target=src/"bundle.zip"
        target.write_bytes(b"OLD")
        before=target.read_bytes()
        try: cls._zip_dir(None,src,target,fs_context=None)
        except PermissionError: pass
        else: raise AssertionError(modname+": missing context accepted")
        assert target.read_bytes()==before
        ctx=make_ctx(root,target)
        cls._zip_dir(None,src,target,fs_context=ctx)
        names,data=members_and_bytes(target)
        assert names==["a.txt","sub/b.bin"],names
        assert data=={"a.txt":b"A","sub/b.bin":b"B"}
        assert ctx.remaining()[SLOT]==0
        try: cls._zip_dir(None,src,target,fs_context=ctx)
        except (PermissionError,RuntimeError,KeyError): pass
        else: raise AssertionError(modname+": replay accepted")
        stable=target.read_bytes()
        bad=make_ctx(root,target,wrong=True)
        try: cls._zip_dir(None,src,target,fs_context=bad)
        except RuntimeError: pass
        else: raise AssertionError(modname+": wrong binding accepted")
        assert target.read_bytes()==stable
    tree=ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    hs=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="_zip_dir"]
    ss=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="step"]
    assert len(hs)==1 and len(ss)==1
    h=ast.unparse(hs[0]); s=ast.unparse(ss[0])
    assert "io.BytesIO()" in h and "FS_WRITE_REPLACE_BYTES" in h and "payload=payload_buffer.getvalue()" in h
    assert "zip_path.unlink" not in h
    assert "ZipFile(zip_path" not in h
    assert ".begin(" not in h and "ScopedHandleBroker" not in h
    assert "fs_context" in [a.arg for a in ss[0].args.args+ss[0].args.kwonlyargs]
    assert "_zip_dir(package_dir, zip_path, fs_context=fs_context)" in s
print("P162G6_G3_CC1F8648_ZIP_DIR_COHORT_TEST_OK")
print("UNITS=2"); print("HISTORICAL_N=2"); print("FUNCTIONAL_REAL_TCB_OK")
print("ZIP_MEMBERS_AND_CONTENTS_OK"); print("EXISTING_TARGET_ATOMIC_REPLACE_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK"); print("WRONG_BINDING_TCB_REJECTION_OK")
print("REPLAY_FAIL_CLOSED_OK"); print("WHOLE_TARGET_WRITE_GOVERNED_OK")
print("CALLER_CONTEXT_TRANSPORT_STATIC_OK"); print("CONSUMER_AUTHORITY_MINTING=false")
print("AMBIENT_FALLBACK=false")
