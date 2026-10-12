from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import ast
import importlib
import io
import tempfile
import zipfile

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.reflexive_threshold_external_review_bundle import ReflexiveThresholdExternalReviewBundle
import ontology.reflexive_threshold_external_review_bundle as bundle_mod


class Broker:
    def __init__(self, allowed):
        self.allowed=set(allowed); self.used=set()
    def consume_once(self, handle_id):
        if handle_id not in self.allowed or handle_id in self.used:
            return False
        self.used.add(handle_id); return True


def handle(hid, target):
    return SimpleNamespace(
        handle_id=hid, adapter_id="adapter", effector_id="effector",
        operation_id="FS_WRITE_REPLACE_BYTES", target_binding=target,
        ambient_authority=False, transferable=False, child_inheritance=False,
        single_use=True,
    )


def context(root, target_rel="pkg/external_review_bundle.zip", hid="h1"):
    binding="filesystem://testroot/"+target_rel
    broker=Broker({hid})
    eff=GovernedFilesystemEffector(root_registry={"testroot":str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(
        slots={"external_review_bundle_zip_write":[handle(hid,binding)]},
        effector=eff, root_id="testroot", root_path=root,
        adapter_id="adapter", effector_id="effector",
    )
    ctx.begin()
    return ctx


def make_source(root):
    d=root/"pkg"; d.mkdir()
    (d/"a.txt").write_text("A",encoding="utf-8")
    sub=d/"sub"; sub.mkdir()
    (sub/"b.txt").write_text("B",encoding="utf-8")
    return d, d/"external_review_bundle.zip"


def zip_members(path):
    with zipfile.ZipFile(path,"r") as z:
        return sorted(z.namelist()), {n:z.read(n) for n in z.namelist()}


def test_missing_context_preserves_existing_target():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d,zp=make_source(root); zp.write_bytes(b"OLD")
        obj=ReflexiveThresholdExternalReviewBundle(root=root)
        try: obj._zip_dir(d,zp)
        except PermissionError: pass
        else: raise AssertionError("missing context accepted")
        assert zp.read_bytes()==b"OLD"


def test_governed_create_produces_valid_zip():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d,zp=make_source(root); ctx=context(root)
        ReflexiveThresholdExternalReviewBundle(root=root)._zip_dir(d,zp,fs_context=ctx)
        names,data=zip_members(zp)
        assert names==["a.txt","sub/b.txt"]
        assert data["a.txt"]==b"A" and data["sub/b.txt"]==b"B"
        assert ctx.remaining()["external_review_bundle_zip_write"]==0
        assert ctx.authority_minting is False


def test_governed_replace_existing_target():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d,zp=make_source(root); zp.write_bytes(b"OLD")
        ctx=context(root)
        ReflexiveThresholdExternalReviewBundle(root=root)._zip_dir(d,zp,fs_context=ctx)
        assert zp.read_bytes()!=b"OLD"
        assert zip_members(zp)[0]==["a.txt","sub/b.txt"]


def test_target_binding_mismatch_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d,zp=make_source(root); zp.write_bytes(b"OLD")
        ctx=context(root,target_rel="pkg/wrong.zip")
        try: ReflexiveThresholdExternalReviewBundle(root=root)._zip_dir(d,zp,fs_context=ctx)
        except RuntimeError as e: assert "not_confirmed" in str(e)
        else: raise AssertionError("target mismatch accepted")
        assert zp.read_bytes()==b"OLD"


def test_context_replay_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d,zp=make_source(root); ctx=context(root)
        obj=ReflexiveThresholdExternalReviewBundle(root=root)
        obj._zip_dir(d,zp,fs_context=ctx)
        first=zp.read_bytes()
        (d/"a.txt").write_text("CHANGED",encoding="utf-8")
        try: obj._zip_dir(d,zp,fs_context=ctx)
        except RuntimeError: pass
        else: raise AssertionError("replay accepted")
        assert zp.read_bytes()==first


def test_outside_root_fails_closed():
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as out:
        root=Path(td); d,zp=make_source(root); outside=Path(out)/"x.zip"
        ctx=context(root)
        try: ReflexiveThresholdExternalReviewBundle(root=root)._zip_dir(d,outside,fs_context=ctx)
        except RuntimeError as e: assert "outside governed root" in str(e)
        else: raise AssertionError("outside-root target accepted")
        assert not outside.exists()


def test_archive_build_failure_preserves_existing_target():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d,zp=make_source(root); zp.write_bytes(b"OLD")
        ctx=context(root)
        with patch.object(bundle_mod.zipfile,"ZipFile",side_effect=RuntimeError("synthetic build failure")):
            try: ReflexiveThresholdExternalReviewBundle(root=root)._zip_dir(d,zp,fs_context=ctx)
            except RuntimeError as e: assert "synthetic build failure" in str(e)
            else: raise AssertionError("build failure swallowed")
        assert zp.read_bytes()==b"OLD"
        assert ctx.remaining()["external_review_bundle_zip_write"]==1


def test_zip_function_has_no_direct_target_mutator():
    source=Path(bundle_mod.__file__).read_text(encoding="utf-8")
    tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="ReflexiveThresholdExternalReviewBundle")
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="_zip_dir")
    attrs=[n.func.attr for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "unlink" not in attrs
    assert "write_text" not in attrs and "write_bytes" not in attrs and "open" not in attrs
    calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call)]
    zipcalls=[n for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=="ZipFile"]
    assert len(zipcalls)==1
    assert isinstance(zipcalls[0].args[0],ast.Name) and zipcalls[0].args[0].id=="payload_buffer"


def test_step_transports_context_to_zip_dir():
    source=Path(bundle_mod.__file__).read_text(encoding="utf-8")
    tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="ReflexiveThresholdExternalReviewBundle")
    step=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="step")
    calls=[n for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="_zip_dir"]
    assert len(calls)==1
    kw={k.arg:k.value for k in calls[0].keywords}
    assert "fs_context" in kw and isinstance(kw["fs_context"],ast.Name) and kw["fs_context"].id=="fs_context"
