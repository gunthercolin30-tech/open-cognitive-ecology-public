from __future__ import annotations
import io, tarfile, zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology import occ_reproducibility_persistence as rp
from ontology.governed_execution_adapter import ExecutionClaimManager
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

NOW="2026-10-05T12:00:00+00:00"
ADAPTER="FSA"; EFFECTOR="FILESYSTEM"

def _handle(hb, n, op, target):
    lease={"lease_id":"L"+str(n),"reservation_id":"R"+str(n),"executor_id":"E",
           "capability_instance_id":"CI","operation_id":op,"invocation_request_hash":"IH",
           "effective_execution_scope_hash":"SH","audience":ADAPTER,
           "reservation_status":"RESERVED","used":False,"revoked":False,
           "expires_at":"2999-01-01T00:00:00+00:00"}
    reg={"adapter_id":ADAPTER,"adapter_hash":"FSH","effector_id":EFFECTOR,
         "capability_ids":["FILESYSTEM_CAP"],"operation_ids":[op],"status":"ACTIVE"}
    state={"lease_state_version":1,"reservation_state_version":1,"token_state_version":1,
           "target_state_version":n,"capability_runtime_attestation":"OK","adapter_attestation":"FSH",
           "critical_precondition_snapshot":{"ok":True},"security_state":"VERIFIED","revoked":False,
           "target_current":True,"critical_preconditions_satisfied":True,"credential_identity_verified":True}
    c=ExecutionClaimManager().claim(
        lease=lease,registry_entry=reg,executor_instance_id="E",capability_instance_id="CI",
        capability_id="FILESYSTEM_CAP",operation_id=op,invocation_request_hash="IH",
        effective_execution_scope_hash="SH",point_of_effect_state=state,now_iso=NOW)["claim"]
    scope={"operation":op,"target":target,"ambient_authority":False,"child_inheritance":False,"transferable":False}
    r=hb.issue(claim=c,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,
               target_binding=target,audience=ADAPTER,now_iso=NOW)
    assert r["status"]=="HANDLE_ISSUED"
    return r["handle"]

def _ctx(root, dirs, files):
    hb=ScopedHandleBroker()
    slots={"archive_create_dir":[], "archive_write_file":[]}
    n=0
    for rel in dirs:
        n+=1; slots["archive_create_dir"].append(_handle(hb,n,"FS_CREATE_DIR","filesystem://ROOT/"+rel))
    for rel in files:
        n+=1; slots["archive_write_file"].append(_handle(hb,n,"FS_WRITE_REPLACE_BYTES","filesystem://ROOT/"+rel))
    eff=GovernedFilesystemEffector(root_registry={"ROOT":str(root)},handle_broker=hb)
    return GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id="ROOT",root_path=root,adapter_id=ADAPTER,effector_id=EFFECTOR)

def test_zip_real_tcb_nested_and_no_extractall(monkeypatch):
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"ok.zip"
        with zipfile.ZipFile(archive,"w") as zf:
            zf.writestr("a/profile.json",b'{"ok":true}')
            zf.writestr("b/deep/report.json",b'{"status":"PASS"}')
        def forbidden(*a,**k): raise AssertionError("extractall ambient bypass")
        monkeypatch.setattr(zipfile.ZipFile,"extractall",forbidden)
        ctx=_ctx(root,["out","out/a","out/b","out/b/deep"],["out/a/profile.json","out/b/deep/report.json"])
        r=rp.safe_extract_archive(archive,root/"out",filesystem_context=ctx)
        assert r["status"]=="PASS" and r["governed_create_dir_count"]==4 and r["governed_write_count"]==2
        assert (root/"out/a/profile.json").read_bytes()==b'{"ok":true}'
        assert (root/"out/b/deep/report.json").read_bytes()==b'{"status":"PASS"}'
        assert ctx.remaining()=={"archive_create_dir":0,"archive_write_file":0}

def test_tar_real_tcb_regular_file():
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"ok.tar"; data=b"abc"
        with tarfile.open(archive,"w") as tf:
            info=tarfile.TarInfo("x/y.bin"); info.size=len(data); tf.addfile(info,io.BytesIO(data))
        ctx=_ctx(root,["out","out/x"],["out/x/y.bin"])
        r=rp.safe_extract_archive(archive,root/"out",filesystem_context=ctx)
        assert r["status"]=="PASS" and (root/"out/x/y.bin").read_bytes()==data

def test_missing_context_fails_closed_without_destination():
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"ok.zip"
        with zipfile.ZipFile(archive,"w") as zf: zf.writestr("a",b"x")
        try: rp.safe_extract_archive(archive,root/"out",filesystem_context=None)
        except RuntimeError as exc: assert str(exc)=="governed_filesystem_context_required"
        else: raise AssertionError("missing context accepted")
        assert not (root/"out").exists()

def test_cardinality_mismatch_before_any_effect():
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"ok.zip"
        with zipfile.ZipFile(archive,"w") as zf: zf.writestr("a/b",b"x")
        ctx=_ctx(root,["out"],["out/a/b"])
        try: rp.safe_extract_archive(archive,root/"out",filesystem_context=ctx)
        except RuntimeError as exc: assert "archive_create_dir_authority_cardinality_mismatch" in str(exc)
        else: raise AssertionError("cardinality mismatch accepted")
        assert not (root/"out").exists()
        assert ctx.remaining()=={"archive_create_dir":1,"archive_write_file":1}

def test_unsafe_zip_rejected_before_authority_consumption():
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"bad.zip"
        with zipfile.ZipFile(archive,"w") as zf: zf.writestr("../escape",b"x")
        ctx=_ctx(root,["out"],[])
        r=rp.safe_extract_archive(archive,root/"out",filesystem_context=ctx)
        assert r["status"]=="FAIL" and r["reason"]=="ARCHIVE_MEMBER_PATH_UNSAFE"
        assert ctx.remaining()=={"archive_create_dir":1,"archive_write_file":0}
        assert not (root/"out").exists()

def test_destination_symlink_rejected_before_authority():
    with TemporaryDirectory() as td:
        root=Path(td); outside=root/"outside"; outside.mkdir(); (root/"out").symlink_to(outside)
        archive=root/"ok.zip"
        with zipfile.ZipFile(archive,"w") as zf: zf.writestr("a",b"x")
        ctx=_ctx(root,[],["outside/a"])
        r=rp.safe_extract_archive(archive,root/"out",filesystem_context=ctx)
        assert r["status"]=="FAIL" and r["reason"]=="ARCHIVE_DESTINATION_SYMLINK_REJECTED"
        assert not (outside/"a").exists()

def test_existing_file_replace_is_governed():
    with TemporaryDirectory() as td:
        root=Path(td); out=root/"out"; out.mkdir(); (out/"a").write_bytes(b"old")
        archive=root/"ok.zip"
        with zipfile.ZipFile(archive,"w") as zf: zf.writestr("a",b"new")
        ctx=_ctx(root,[],["out/a"])
        r=rp.safe_extract_archive(archive,out,filesystem_context=ctx)
        assert r["status"]=="PASS" and (out/"a").read_bytes()==b"new"

def test_context_replay_fails_closed():
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"ok.zip"
        with zipfile.ZipFile(archive,"w") as zf: zf.writestr("a",b"x")
        ctx=_ctx(root,["out"],["out/a"])
        assert rp.safe_extract_archive(archive,root/"out",filesystem_context=ctx)["status"]=="PASS"
        try: rp.safe_extract_archive(archive,root/"out2",filesystem_context=ctx)
        except RuntimeError:
            pass
        else: raise AssertionError("context replay accepted")
