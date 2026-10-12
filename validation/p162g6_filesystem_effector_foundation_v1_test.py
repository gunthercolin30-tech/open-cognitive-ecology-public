from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.governed_filesystem_effector import GovernedFilesystemEffector,FilesystemEffectRequest
def h(op,target,**kw):
 d=dict(adapter_id="a",effector_id="fs",operation_id=op,target_binding=target,ambient_authority=False,transferable=False,child_inheritance=False);d.update(kw);return SimpleNamespace(**d)
with TemporaryDirectory() as td:
 root=Path(td);e=GovernedFilesystemEffector(root_registry={"r":str(root)})
 r=FilesystemEffectRequest("FS_WRITE_BYTES","r","x.bin",b"abc");t=e.canonical_target("r","x.bin")
 assert e.execute(request=r,handle=None,adapter_id="a",effector_id="fs")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
 assert e.execute(request=r,handle=h("FS_WRITE_BYTES",t,ambient_authority=True),adapter_id="a",effector_id="fs")["reason"]=="ambient_authority_forbidden"
 assert e.execute(request=r,handle=h("FS_WRITE_BYTES","filesystem://r/y.bin"),adapter_id="a",effector_id="fs")["reason"]=="target_mismatch"
 out=e.execute(request=r,handle=h("FS_WRITE_BYTES",t),adapter_id="a",effector_id="fs");assert out["status"]=="EFFECT_CONFIRMED";assert (root/"x.bin").read_bytes()==b"abc"
 assert e.execute(request=r,handle=h("FS_WRITE_BYTES",t),adapter_id="a",effector_id="fs")["status"]=="EFFECT_FAILED_CONFIRMED"
 (root/"link").symlink_to(root.parent,target_is_directory=True)
 rr=FilesystemEffectRequest("FS_WRITE_BYTES","r","link/escape.bin",b"x");tt=e.canonical_target("r","link/escape.bin")
 assert e.execute(request=rr,handle=h("FS_WRITE_BYTES",tt),adapter_id="a",effector_id="fs")["reason"]=="target_outside_registered_root"
print("P162G6_FILESYSTEM_EFFECTOR_FOUNDATION_TEST_OK")
