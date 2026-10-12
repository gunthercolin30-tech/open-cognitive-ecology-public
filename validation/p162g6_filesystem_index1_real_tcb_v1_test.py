from __future__ import annotations
import hashlib, stat
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import pytest
from ontology.acee_installation_executor import AceeInstallationExecutor
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
ADAPTER="p162g6-index1-adapter"; EFFECTOR="p162g6-filesystem-effector"; ROOT_ID="repo"
def _handle(broker,operation,target_binding,serial):
    claim=SimpleNamespace(lease_id=f"lease-{serial}",reservation_id=f"res-{serial}",claim_hash=f"claim-{serial}",adapter_id=ADAPTER)
    lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":operation,"expires_at":"2999-01-01T00:00:00Z"}
    scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":ADAPTER,"effector_id":EFFECTOR},requested_scope=scope,authorized_scope=scope,target_binding=target_binding,audience=ADAPTER,now_iso="2026-10-05T00:00:00Z")
    assert issued["status"]=="HANDLE_ISSUED"; return issued["handle"]
def _provider(root,source,destination):
    broker=ScopedHandleBroker(); eff=GovernedFilesystemEffector(root_registry={ROOT_ID:str(root)},handle_broker=broker)
    sr=source.resolve().relative_to(root.resolve()).as_posix(); dr=destination.resolve().relative_to(root.resolve()).as_posix()
    binding={"source":f"filesystem://{ROOT_ID}/{sr}","destination":f"filesystem://{ROOT_ID}/{dr}"}
    h=_handle(broker,"FS_COPY2",binding,"copy")
    def provider(operation_id,target):
        assert operation_id=="FS_COPY2" and Path(target)==destination
        return GovernedFilesystemEffectContext(slots={"p162g6_index1_backup_copy2":[h]},effector=eff,root_id=ROOT_ID,root_path=root,adapter_id=ADAPTER,effector_id=EFFECTOR)
    return provider
def test_real_tcb_copy_preserves_bytes_mode_and_cleans_temp():
    with TemporaryDirectory() as td:
        root=Path(td);(root/"ontology").mkdir();src=root/"ontology/source.py";dst=root/"ontology/source.py.bak"
        src.write_bytes(b"alpha\n");src.chmod(0o640)
        e=AceeInstallationExecutor(filesystem_effect_context_provider=_provider(root,src,dst),root=root)
        digest,mode,fs,ds=e._copy_backup_atomically(src,dst)
        assert digest==hashlib.sha256(b"alpha\n").hexdigest() and dst.read_bytes()==b"alpha\n"
        assert stat.S_IMODE(dst.stat().st_mode)==0o640 and fs is True and ds is True
        assert not [p for p in dst.parent.iterdir() if ".p162g-copy2." in p.name]
def test_existing_backup_is_replaced():
    with TemporaryDirectory() as td:
        root=Path(td);(root/"ontology").mkdir();src=root/"ontology/source.py";dst=root/"ontology/source.py.bak"
        src.write_bytes(b"new");src.chmod(0o600);dst.write_bytes(b"old")
        AceeInstallationExecutor(filesystem_effect_context_provider=_provider(root,src,dst),root=root)._copy_backup_atomically(src,dst)
        assert dst.read_bytes()==b"new" and stat.S_IMODE(dst.stat().st_mode)==0o600
def test_missing_provider_fails_closed():
    with TemporaryDirectory() as td:
        root=Path(td);(root/"ontology").mkdir();src=root/"ontology/source.py";dst=root/"ontology/source.py.bak";src.write_bytes(b"x")
        with pytest.raises(RuntimeError,match="governed_filesystem_effect_context_provider_required"): AceeInstallationExecutor(root=root)._copy_backup_atomically(src,dst)
        assert not dst.exists()
def test_wrong_target_handle_fails_closed():
    with TemporaryDirectory() as td:
        root=Path(td);(root/"ontology").mkdir();src=root/"ontology/source.py";dst=root/"ontology/source.py.bak";src.write_bytes(b"x")
        broker=ScopedHandleBroker();eff=GovernedFilesystemEffector(root_registry={ROOT_ID:str(root)},handle_broker=broker)
        sr=src.resolve().relative_to(root.resolve()).as_posix();wrong={"source":f"filesystem://{ROOT_ID}/{sr}","destination":f"filesystem://{ROOT_ID}/ontology/wrong.bak"}
        h=_handle(broker,"FS_COPY2",wrong,"wrong")
        def provider(operation_id,target): return GovernedFilesystemEffectContext(slots={"p162g6_index1_backup_copy2":[h]},effector=eff,root_id=ROOT_ID,root_path=root,adapter_id=ADAPTER,effector_id=EFFECTOR)
        with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"): AceeInstallationExecutor(filesystem_effect_context_provider=provider,root=root)._copy_backup_atomically(src,dst)
        assert not dst.exists()
def test_handle_replay_fails_closed_without_corrupting_backup():
    with TemporaryDirectory() as td:
        root=Path(td);(root/"ontology").mkdir();src=root/"ontology/source.py";dst=root/"ontology/source.py.bak";src.write_bytes(b"x")
        e=AceeInstallationExecutor(filesystem_effect_context_provider=_provider(root,src,dst),root=root);e._copy_backup_atomically(src,dst);before=dst.read_bytes()
        with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"): e._copy_backup_atomically(src,dst)
        assert dst.read_bytes()==before
def test_copy_failure_preserves_existing_destination_and_cleans_temp(monkeypatch):
    with TemporaryDirectory() as td:
        root=Path(td);(root/"ontology").mkdir();src=root/"ontology/source.py";dst=root/"ontology/source.py.bak";src.write_bytes(b"new");dst.write_bytes(b"old")
        import ontology.governed_filesystem_effector as mod
        def broken(source,tmp): Path(tmp).write_bytes(b"partial");raise OSError("injected")
        monkeypatch.setattr(mod.shutil,"copy2",broken)
        with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"): AceeInstallationExecutor(filesystem_effect_context_provider=_provider(root,src,dst),root=root)._copy_backup_atomically(src,dst)
        assert dst.read_bytes()==b"old" and not [p for p in dst.parent.iterdir() if ".p162g-copy2." in p.name]
