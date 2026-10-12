from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from ontology.governed_filesystem_effector import FilesystemEffectRequest

@dataclass
class GovernedFilesystemEffectContext:
    """Caller-assembled, non-minting context for exact filesystem effects."""
    slots: Mapping[str, Iterable[Any]]
    effector: Any = None
    root_id: Optional[str] = None
    root_path: Optional[Union[str, Path]] = None
    adapter_id: Optional[str] = None
    effector_id: Optional[str] = None
    source_root_id: Optional[str] = None
    source_root_path: Optional[Union[str, Path]] = None
    _queues: Dict[str, List[Any]] = field(init=False, repr=False)
    _begun: bool = field(default=False, init=False, repr=False)
    def __post_init__(self):
        queues: Dict[str, List[Any]] = {}
        for name, handles in self.slots.items():
            if not isinstance(name, str) or not name: raise ValueError("invalid filesystem effect slot")
            if name in queues: raise ValueError("duplicate filesystem effect slot")
            queues[name] = list(handles)
        self._queues = queues
        if self.root_path is not None: self.root_path = Path(self.root_path).expanduser().resolve()
        if self.source_root_path is not None: self.source_root_path = Path(self.source_root_path).expanduser().resolve()
    def begin(self):
        if self._begun: raise RuntimeError("filesystem effect context replay")
        self._begun = True
    def take(self, slot):
        if not self._begun: raise RuntimeError("filesystem effect context not begun")
        if slot not in self._queues: raise KeyError("missing filesystem effect slot: " + slot)
        if not self._queues[slot]: raise RuntimeError("no remaining handle for filesystem effect slot: " + slot)
        return self._queues[slot].pop(0)
    def _relative(self, path: Union[str, Path]) -> str:
        if self.root_path is None: raise RuntimeError("filesystem effect context root_path required")
        target = Path(path).expanduser()
        if not target.is_absolute(): target = self.root_path / target
        # Canonicalize the target too. On macOS tempfile may expose /var/...
        # while root_path.resolve() yields /private/var/....
        target = target.resolve()
        try: return target.relative_to(self.root_path).as_posix()
        except ValueError as exc: raise RuntimeError("filesystem effect target outside governed root") from exc
    def execute_path(self, slot: str, operation_id: str, path: Union[str, Path], payload: Optional[bytes] = None):
        if self.effector is None: raise RuntimeError("filesystem effect context effector required")
        if not self.root_id or not self.adapter_id or not self.effector_id: raise RuntimeError("filesystem effect context binding metadata required")
        request = FilesystemEffectRequest(operation_id=operation_id, root_id=self.root_id, relative_path=self._relative(path), payload=payload)
        handle = self.take(slot)
        result = self.effector.execute(request=request, handle=handle, adapter_id=self.adapter_id, effector_id=self.effector_id)
        if not isinstance(result, dict) or result.get("status") != "EFFECT_CONFIRMED":
            reason = result.get("reason") if isinstance(result, dict) else "invalid_effector_result"
            raise RuntimeError("governed_filesystem_effect_not_confirmed:" + str(reason))
        return result
    @staticmethod
    def _relative_under(path: Union[str, Path], root_path: Union[str, Path]) -> str:
        root = Path(root_path).expanduser().resolve()
        target = Path(path).expanduser()
        if not target.is_absolute(): target = root / target
        target = target.resolve()
        try: return target.relative_to(root).as_posix()
        except ValueError as exc: raise RuntimeError("filesystem effect source outside governed root") from exc
    def execute_copy2(self, slot: str, source_root_id: str, source_root_path: Union[str, Path], source_path: Union[str, Path], destination_path: Union[str, Path]):
        if self.effector is None: raise RuntimeError("filesystem effect context effector required")
        if not self.root_id or not self.adapter_id or not self.effector_id: raise RuntimeError("filesystem effect context binding metadata required")
        if not source_root_id: raise RuntimeError("filesystem effect source root_id required")
        request = FilesystemEffectRequest(
            operation_id="FS_COPY2", root_id=self.root_id, relative_path=self._relative(destination_path), payload=None,
            source_root_id=str(source_root_id), source_relative_path=self._relative_under(source_path, source_root_path),
        )
        handle = self.take(slot)
        result = self.effector.execute(request=request, handle=handle, adapter_id=self.adapter_id, effector_id=self.effector_id)
        if not isinstance(result, dict) or result.get("status") != "EFFECT_CONFIRMED":
            reason = result.get("reason") if isinstance(result, dict) else "invalid_effector_result"
            raise RuntimeError("governed_filesystem_effect_not_confirmed:" + str(reason))
        return result
    def execute_dual_path(self, slot: str, operation_id: str, source_root_id: str, source_root_path: Union[str, Path], source_path: Union[str, Path], destination_path: Union[str, Path]):
        if self.effector is None: raise RuntimeError("filesystem effect context effector required")
        if not self.root_id or not self.adapter_id or not self.effector_id: raise RuntimeError("filesystem effect context binding metadata required")
        if not source_root_id: raise RuntimeError("filesystem effect source root_id required")
        request = FilesystemEffectRequest(
            operation_id=operation_id, root_id=self.root_id, relative_path=self._relative(destination_path), payload=None,
            source_root_id=str(source_root_id), source_relative_path=self._relative_under(source_path, source_root_path),
        )
        handle = self.take(slot)
        result = self.effector.execute(request=request, handle=handle, adapter_id=self.adapter_id, effector_id=self.effector_id)
        if not isinstance(result, dict) or result.get("status") != "EFFECT_CONFIRMED":
            reason = result.get("reason") if isinstance(result, dict) else "invalid_effector_result"
            raise RuntimeError("governed_filesystem_effect_not_confirmed:" + str(reason))
        return result
    def remaining(self): return {k: len(v) for k, v in self._queues.items()}
    @property
    def authority_minting(self): return False
