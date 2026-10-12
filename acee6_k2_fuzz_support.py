from __future__ import annotations
import hashlib, json, os, stat, unicodedata
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "1.0.0"
DEFAULT_SEED = 62002
DEFAULT_CASE_COUNT = 320
INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

def json_safe(value: Any, depth: int = 0) -> Any:
    if depth > 32: return "<max-depth>"
    if value is None or isinstance(value, (bool, int, str)): return value
    if isinstance(value, float):
        if value != value: return "<nan>"
        if value == float("inf"): return "<positive-infinity>"
        if value == float("-inf"): return "<negative-infinity>"
        return value
    if isinstance(value, Path): return str(value)
    if isinstance(value, Mapping):
        return {str(k): json_safe(v, depth + 1) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)): return [json_safe(v, depth + 1) for v in value]
    if isinstance(value, (set, frozenset)): return sorted((json_safe(v, depth + 1) for v in value), key=repr)
    if isinstance(value, bytes): return {"bytes_hex": value.hex()}
    return {"unsupported_type": type(value).__name__, "repr": repr(value)[:256]}

def canonical(value: Any) -> str:
    return json.dumps(json_safe(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def tree_snapshot(root: Path) -> dict[str, Any]:
    rows=[]
    if not root.exists(): return {"exists": False, "hash": sha([]), "rows": []}
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        rel=path.relative_to(root).as_posix()
        try: info=path.lstat()
        except OSError as exc:
            rows.append([rel,"stat_error",type(exc).__name__]); continue
        mode=stat.S_IFMT(info.st_mode)
        if path.is_symlink():
            try: target=os.readlink(path)
            except OSError as exc: target=f"<error:{type(exc).__name__}>"
            rows.append([rel,"symlink",target,mode])
        elif path.is_file(): rows.append([rel,"file",file_sha(path),int(info.st_size),mode])
        elif path.is_dir(): rows.append([rel,"dir",mode])
        else: rows.append([rel,"other",mode])
    return {"exists": True, "hash": sha(rows), "rows": rows}

def normalize_unicode(text: str) -> dict[str, str]:
    return {"raw": text, "nfc": unicodedata.normalize("NFC", text), "nfd": unicodedata.normalize("NFD", text)}

def result_projection(result: Mapping[str, Any]) -> dict[str, Any]:
    reasons=result.get("blocking_reasons")
    if not isinstance(reasons,list): reasons=[]
    return {
        "status": str(result.get("status") or ""),
        "stage": str(result.get("stage") or ""),
        "transaction_state": str(result.get("transaction_state") or ""),
        "admissible": result.get("admissible"),
        "committed": result.get("committed"),
        "candidate_executed": result.get("candidate_executed"),
        "inventory_modified": result.get("inventory_modified"),
        "tests_executed": result.get("tests_executed"),
        "global_validation_executed": result.get("global_validation_executed"),
        "persistence_performed": result.get("persistence_performed"),
        "partial_success": result.get("partial_success"),
        "retry_allowed": result.get("retry_allowed"),
        "blocking_reasons": sorted(str(x) for x in reasons),
    }
