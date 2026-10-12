from pathlib import Path
from types import SimpleNamespace
import ast, os, tempfile
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.reflexive_threshold_external_review_bundle import ReflexiveThresholdExternalReviewBundle
import ontology.reflexive_threshold_external_review_bundle as bundle_mod

class Broker:
    def __init__(self, allowed): self.allowed=set(allowed); self.used=set()
    def consume_once(self, handle_id):
        if handle_id not in self.allowed or handle_id in self.used:return False
        self.used.add(handle_id); return True
def h(hid,op,target):
    return SimpleNamespace(handle_id=hid,adapter_id="adapter",effector_id="effector",operation_id=op,target_binding=target,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def ctx(root,source,dest):
    srel=source.relative_to(root).as_posix(); drel=dest.relative_to(root).as_posix(); dirrel=dest.parent.relative_to(root).as_posix()
    broker=Broker({"mk","cp"})
    eff=GovernedFilesystemEffector(root_registry={"testroot":str(root)},handle_broker=broker)
    c=GovernedFilesystemEffectContext(slots={
      "external_review_artifact_dir_create":[h("mk","FS_CREATE_DIRS","filesystem://testroot/"+dirrel)],
      "external_review_artifact_copy":[h("cp","FS_COPY2",{"source":"filesystem://testroot/"+srel,"destination":"filesystem://testroot/"+drel})]},
      effector=eff,root_id="testroot",root_path=root,adapter_id="adapter",effector_id="effector",source_root_id="testroot",source_root_path=root)
    c.begin(); return c

def test_missing_context_fails_before_mutation():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); src=root/"src.txt"; src.write_text("A",encoding="utf-8"); destdir=root/"out"
        try: ReflexiveThresholdExternalReviewBundle(root=root)._copy_if_exists(src,destdir,"x.txt")
        except PermissionError: pass
        else: raise AssertionError("missing context accepted")
        assert not destdir.exists()

def test_governed_copy_preserves_bytes_and_mode():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); src=root/"src.txt"; src.write_bytes(b"ABC"); os.chmod(src,0o640); dest=root/"nested"/"x.txt"; c=ctx(root,src,dest)
        got=ReflexiveThresholdExternalReviewBundle(root=root)._copy_if_exists(src,dest.parent,dest.name,fs_context=c)
        assert got["copied"] is True and Path(got["destination"])==dest and dest.read_bytes()==b"ABC"
        assert (dest.stat().st_mode&0o777)==(src.stat().st_mode&0o777)
        assert c.remaining()=={"external_review_artifact_dir_create":0,"external_review_artifact_copy":0} and c.authority_minting is False

def test_missing_source_consumes_no_authority():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); src=root/"missing"; dest=root/"out"/"x"; c=ctx(root,src,dest)
        got=ReflexiveThresholdExternalReviewBundle(root=root)._copy_if_exists(src,dest.parent,dest.name,fs_context=c)
        assert got["copied"] is False and not dest.parent.exists()
        assert c.remaining()=={"external_review_artifact_dir_create":1,"external_review_artifact_copy":1}

def test_outside_destination_fails_closed():
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as od:
        root=Path(td); src=root/"src"; src.write_text("x",encoding="utf-8"); dest=Path(od)/"x"; c=ctx(root,src,root/"safe"/"x")
        try: ReflexiveThresholdExternalReviewBundle(root=root)._copy_if_exists(src,dest.parent,dest.name,fs_context=c)
        except RuntimeError as e: assert "outside governed root" in str(e)
        else: raise AssertionError("outside destination accepted")
        assert not dest.exists()

def test_static_no_ambient_mutator_and_step_transports_context():
    tree=ast.parse(Path(bundle_mod.__file__).read_text(encoding="utf-8"))
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="ReflexiveThresholdExternalReviewBundle")
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="_copy_if_exists")
    attrs=[n.func.attr for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "mkdir" not in attrs and "copy2" not in attrs and "execute_path" in attrs and "execute_copy2" in attrs
    step=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="step")
    calls=[n for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="_copy_if_exists"]
    assert len(calls)==1
    kw={k.arg:k.value for k in calls[0].keywords}
    assert isinstance(kw.get("fs_context"),ast.Name) and kw["fs_context"].id=="fs_context"
