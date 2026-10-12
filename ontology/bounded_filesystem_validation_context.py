from __future__ import annotations
from pathlib import Path
import shutil, tempfile
class BoundedFilesystemValidationContext:
    def __init__(self, *, prefix):
        if not isinstance(prefix,str) or not prefix.startswith("oce-") or "/" in prefix or "\\" in prefix: raise PermissionError("invalid bounded-validation prefix")
        self._root=Path(tempfile.mkdtemp(prefix=prefix)).resolve(); self._closed=False
    @property
    def root(self): return self._root
    def _target(self, relative):
        if self._closed: raise RuntimeError("bounded validation context closed")
        p=Path(relative)
        if p.is_absolute(): raise PermissionError("absolute target forbidden")
        candidate=(self._root/p).resolve(strict=False)
        try: candidate.relative_to(self._root)
        except ValueError: raise PermissionError("sandbox escape forbidden")
        cur=candidate
        while cur != self._root:
            if cur.exists() and cur.is_symlink(): raise PermissionError("symlink target forbidden")
            cur=cur.parent
        return candidate
    def mkdir(self, relative):
        p=self._target(relative); p.mkdir(parents=True,exist_ok=True); return p
    def write_text(self, relative, text, *, encoding="utf-8"):
        p=self._target(relative); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding=encoding); return p
    def copy2_from(self, source, relative):
        raw=Path(source)
        if raw.is_symlink(): raise PermissionError("symlink source forbidden")
        src=raw.resolve()
        if not src.is_file(): raise PermissionError("regular source file required")
        dst=self._target(relative); dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); return dst
    def copytree_from(self, source, relative):
        raw=Path(source)
        if raw.is_symlink(): raise PermissionError("symlink source forbidden")
        src=raw.resolve()
        if not src.is_dir(): raise PermissionError("regular source directory required")
        dst=self._target(relative); dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".DS_Store")); return dst
    def remove_tree(self):
        if self._closed: return
        root=self._root; self._closed=True; shutil.rmtree(root,ignore_errors=False)
        if root.exists(): raise RuntimeError("bounded validation cleanup failed")
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): self.remove_tree(); return False
