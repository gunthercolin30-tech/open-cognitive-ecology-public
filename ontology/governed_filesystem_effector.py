"""P162-G6 governed FILESYSTEM mediation foundation."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import tempfile
ALLOWED_OPERATIONS=frozenset({"FS_CREATE_DIR","FS_CREATE_DIRS","FS_WRITE_BYTES","FS_WRITE_REPLACE_BYTES","FS_REMOVE_FILE","FS_REMOVE_TREE","FS_COPY2","FS_COPY_TREE_MERGE","FS_APPEND_BYTES","FS_MOVE_OR_REPLACE","FS_MOVE_PATH","FS_CREATE_SYMLINK"})
@dataclass(frozen=True)
class FilesystemEffectRequest:
    operation_id:str; root_id:str; relative_path:str; payload:bytes|None=None
    source_root_id:str|None=None; source_relative_path:str|None=None
class FilesystemTrustedTransport:
    def create_dir(self,path): path.mkdir(parents=False,exist_ok=False); return {"created":True}
    def write_bytes(self,path,payload):
        with path.open("xb") as f: f.write(payload); f.flush(); os.fsync(f.fileno())
        return {"bytes_written":len(payload)}
    def remove_file(self,path):
        path.unlink()
        dir_fd=os.open(str(path.parent),os.O_RDONLY)
        try: os.fsync(dir_fd)
        finally: os.close(dir_fd)
        return {"removed":True,"directory_fsynced":True}
    def remove_tree(self,path):
        shutil.rmtree(path,ignore_errors=False)
        if path.exists() or path.is_symlink(): raise RuntimeError("recursive_remove_postcondition_failed")
        return {"removed_tree":True}
    def write_replace_bytes(self,path,payload):
        existing_mode = (path.stat().st_mode & 0o7777) if path.exists() else None
        tmp=path.with_name(path.name+".p162g.tmp")
        if tmp.exists() or tmp.is_symlink(): raise FileExistsError(str(tmp))
        try:
            with tmp.open("xb") as f:
                f.write(payload); f.flush(); os.fsync(f.fileno())
                if existing_mode is not None:
                    os.chmod(tmp, existing_mode)
            os.replace(tmp,path)
            # Strengthen durable-replace postcondition: persist directory entry too.
            dir_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        finally:
            if tmp.exists():
                try: tmp.unlink()
                except Exception: pass
        return {"bytes_written":len(payload),"replaced":True}
    def append_bytes(self,path,payload):
        existed=path.exists()
        with path.open("ab") as f:
            written=f.write(payload); f.flush(); os.fsync(f.fileno())
        if not existed:
            dir_fd=os.open(str(path.parent),os.O_RDONLY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        return {"bytes_appended":written,"directory_fsynced_on_create":not existed}
    def move_or_replace(self,source,destination):
        os.replace(source,destination)
        return {"moved":True,"destination":str(destination)}
    def create_dirs(self,path):
        path.mkdir(parents=True,exist_ok=True)
        return {"created_or_present":True}
    def copy_tree_merge(self,source,destination):
        destination.mkdir(parents=True,exist_ok=True)
        if source.is_file():
            shutil.copy2(source,destination/source.name)
        elif source.exists():
            for item in source.iterdir():
                dst=destination/item.name
                if item.is_dir() and not item.is_symlink():
                    shutil.copytree(item,dst,dirs_exist_ok=True)
                elif item.is_file() or item.is_symlink():
                    dst.parent.mkdir(parents=True,exist_ok=True)
                    if dst.exists() or dst.is_symlink():
                        if dst.is_dir() and not dst.is_symlink(): shutil.rmtree(dst)
                        else: dst.unlink()
                    shutil.copy2(item,dst)
        return {"merged":True,"destination":str(destination)}
    def move_path(self,source,destination):
        source_parent=source.parent
        os.replace(source,destination)
        for parent in {source_parent,destination.parent}:
            fd=os.open(str(parent),os.O_RDONLY)
            try: os.fsync(fd)
            finally: os.close(fd)
        return {"moved":True,"destination":str(destination),"directory_fsynced":True}
    def create_symlink(self,source,destination):
        os.symlink(source,destination,target_is_directory=True)
        fd=os.open(str(destination.parent),os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)
        return {"symlink_created":True,"destination":str(destination),"source":str(source)}
    def copy2(self,source,destination):
        fd,tmp_name=tempfile.mkstemp(prefix="."+destination.name+".p162g-copy2.",suffix=".tmp",dir=str(destination.parent))
        os.close(fd);tmp=Path(tmp_name)
        try:
            shutil.copy2(source,tmp)
            with tmp.open("rb") as f: os.fsync(f.fileno())
            os.replace(tmp,destination)
            dir_fd=os.open(str(destination.parent),os.O_RDONLY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        finally:
            if tmp.exists():
                try: tmp.unlink()
                except Exception: pass
        return {"copied":True,"destination":str(destination),"durable":True,"atomic_replace":True}
class GovernedFilesystemEffector:
    def __init__(self,*,root_registry,handle_broker,transport=None):
        if handle_broker is None or not callable(getattr(handle_broker,"consume_once",None)): raise ValueError("scoped_handle_broker_required")
        self.root_registry={str(k):str(v) for k,v in dict(root_registry).items()}
        self.handle_broker=handle_broker
        self.transport=transport or FilesystemTrustedTransport()
    @staticmethod
    def canonical_target(root_id,relative_path):
        rel=Path(str(relative_path))
        if rel.is_absolute() or not rel.parts or any(x in {"",".."} for x in rel.parts): return None
        return "filesystem://"+str(root_id)+"/"+rel.as_posix()
    @staticmethod
    def _blocked(reason,target=None): return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":reason,"target":target}
    def _resolve_confined(self,root_id,relative_path):
        raw=self.root_registry.get(str(root_id))
        if raw is None:return None,"unknown_root_id"
        root=Path(raw).expanduser().resolve(strict=True)
        if not root.is_dir():return None,"registered_root_not_directory"
        rel=Path(str(relative_path))
        if rel.is_absolute() or not rel.parts or any(x in {"",".."} for x in rel.parts):return None,"invalid_relative_path"
        target=root/rel
        try: parent=target.parent.resolve(strict=True)
        except Exception:return None,"target_parent_unresolved"
        try: parent.relative_to(root)
        except ValueError:return None,"target_outside_registered_root"
        return parent/target.name,None
    def _resolve_confined_allow_missing(self,root_id,relative_path):
        raw=self.root_registry.get(str(root_id))
        if raw is None:return None,"unknown_root_id"
        root=Path(raw).expanduser().resolve(strict=True)
        rel=Path(str(relative_path))
        if rel.is_absolute() or not rel.parts or any(x in {"",".."} for x in rel.parts):return None,"invalid_relative_path"
        probe=root/rel
        ancestor=probe.parent
        while not ancestor.exists() and ancestor != root:
            ancestor=ancestor.parent
        try:
            resolved_ancestor=ancestor.resolve(strict=True);resolved_ancestor.relative_to(root)
        except Exception:return None,"target_outside_registered_root"
        return root/rel,None
    def execute(self,*,request,handle,adapter_id,effector_id):
        if request.operation_id not in ALLOWED_OPERATIONS:return self._blocked("operation_not_registered")
        destination_binding=self.canonical_target(request.root_id,request.relative_path)
        if destination_binding is None:return self._blocked("invalid_target_binding")
        if request.operation_id in {"FS_COPY2","FS_MOVE_OR_REPLACE","FS_COPY_TREE_MERGE","FS_MOVE_PATH","FS_CREATE_SYMLINK"}:
            source_binding=self.canonical_target(request.source_root_id,request.source_relative_path)
            if source_binding is None:return self._blocked("invalid_source_binding",destination_binding)
            target_binding={"source":source_binding,"destination":destination_binding}
        else:
            target_binding=destination_binding
        if handle is None:return self._blocked("missing_scoped_handle",target_binding)
        if getattr(handle,"adapter_id",None)!=adapter_id:return self._blocked("adapter_mismatch",target_binding)
        if getattr(handle,"effector_id",None)!=effector_id:return self._blocked("effector_mismatch",target_binding)
        if getattr(handle,"operation_id",None)!=request.operation_id:return self._blocked("operation_mismatch",target_binding)
        if getattr(handle,"target_binding",None)!=target_binding:return self._blocked("target_mismatch",target_binding)
        if getattr(handle,"ambient_authority",True) is not False:return self._blocked("ambient_authority_forbidden",target_binding)
        if getattr(handle,"transferable",True) is not False or getattr(handle,"child_inheritance",True) is not False:return self._blocked("inheritance_or_transfer_forbidden",target_binding)
        if request.operation_id=="FS_CREATE_DIRS": target,reason=self._resolve_confined_allow_missing(request.root_id,request.relative_path)
        else: target,reason=self._resolve_confined(request.root_id,request.relative_path)
        if reason:return self._blocked(reason,target_binding)
        source=None
        if request.operation_id in {"FS_COPY2","FS_MOVE_OR_REPLACE","FS_COPY_TREE_MERGE","FS_MOVE_PATH","FS_CREATE_SYMLINK"}:
            source,reason=self._resolve_confined(request.source_root_id,request.source_relative_path)
            if reason:return self._blocked("source_"+reason,target_binding)
            try:
                source=source.resolve(strict=True)
                source_root=Path(self.root_registry[str(request.source_root_id)]).expanduser().resolve(strict=True)
                source.relative_to(source_root)
            except (FileNotFoundError,KeyError):return self._blocked("source_missing",target_binding)
            except ValueError:return self._blocked("source_outside_registered_root",target_binding)
            if request.operation_id in {"FS_COPY2","FS_MOVE_OR_REPLACE"} and not source.is_file():return self._blocked("source_not_regular_file",target_binding)
            if request.operation_id=="FS_COPY_TREE_MERGE" and not (source.is_file() or source.is_dir()):return self._blocked("source_not_copyable",target_binding)
            if request.operation_id=="FS_CREATE_SYMLINK" and not (source.is_file() or source.is_dir()):return self._blocked("source_not_linkable",target_binding)
            if request.payload is not None:return self._blocked("payload_forbidden",target_binding)
        if request.operation_id=="FS_COPY2":
            if target.is_symlink():return self._blocked("target_symlink_forbidden",target_binding)
            if target.exists() and not target.is_file():return self._blocked("target_not_regular_file",target_binding)
        if request.operation_id in {"FS_APPEND_BYTES","FS_WRITE_REPLACE_BYTES"}:
            if not isinstance(request.payload,(bytes,bytearray)):return self._blocked("bytes_payload_required",target_binding)
            if target.is_symlink():return self._blocked("target_symlink_forbidden",target_binding)
            if target.exists() and not target.is_file():return self._blocked("target_not_regular_file",target_binding)
        if request.operation_id=="FS_REMOVE_TREE":
            if request.payload is not None:return self._blocked("payload_forbidden",target_binding)
            if target.is_symlink():return self._blocked("target_symlink_forbidden",target_binding)
            if target.exists() and not target.is_dir():return self._blocked("target_not_directory",target_binding)
        if getattr(handle,"single_use",None) is not True:return self._blocked("single_use_handle_required",target_binding)
        if not self.handle_broker.consume_once(getattr(handle,"handle_id",None)):return self._blocked("handle_replay_or_unknown",target_binding)
        try:
            if request.operation_id=="FS_CREATE_DIR":
                if request.payload is not None:return self._blocked("payload_forbidden",target_binding)
                out=self.transport.create_dir(target)
            elif request.operation_id=="FS_CREATE_DIRS":
                if request.payload is not None:return self._blocked("payload_forbidden",target_binding)
                out=self.transport.create_dirs(target)
            elif request.operation_id=="FS_WRITE_BYTES":
                if not isinstance(request.payload,(bytes,bytearray)):return self._blocked("bytes_payload_required",target_binding)
                out=self.transport.write_bytes(target,bytes(request.payload))
            elif request.operation_id=="FS_WRITE_REPLACE_BYTES":
                out=self.transport.write_replace_bytes(target,bytes(request.payload))
            elif request.operation_id=="FS_APPEND_BYTES":
                out=self.transport.append_bytes(target,bytes(request.payload))
            elif request.operation_id=="FS_COPY2":
                out=self.transport.copy2(source,target)
            elif request.operation_id=="FS_COPY_TREE_MERGE":
                out=self.transport.copy_tree_merge(source,target)
            elif request.operation_id=="FS_MOVE_OR_REPLACE":
                out=self.transport.move_or_replace(source,target)
            elif request.operation_id=="FS_MOVE_PATH":
                out=self.transport.move_path(source,target)
            elif request.operation_id=="FS_CREATE_SYMLINK":
                out=self.transport.create_symlink(source,target)
            elif request.operation_id=="FS_REMOVE_TREE":
                out=self.transport.remove_tree(target)
            else:
                if request.payload is not None:return self._blocked("payload_forbidden",target_binding)
                out=self.transport.remove_file(target)
        except FileExistsError:return {"status":"EFFECT_FAILED_CONFIRMED","reason":"target_exists","target":target_binding}
        except FileNotFoundError:return {"status":"EFFECT_FAILED_CONFIRMED","reason":"target_missing","target":target_binding}
        except Exception as exc:return {"status":"EFFECT_STATE_INDETERMINATE","reason":"filesystem_exception_after_dispatch","target":target_binding,"exception_type":type(exc).__name__}
        return {"status":"EFFECT_CONFIRMED","target":target_binding,"operation_id":request.operation_id,"transport_result":out}
