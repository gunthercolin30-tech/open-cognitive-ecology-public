"""P162-G6.5c6 governed isolated generated-probe PROCESS runner."""
from __future__ import annotations
import hashlib
from pathlib import Path
from types import SimpleNamespace
from ontology.governed_process_effector import GovernedProcessEffector, ProcessEffectRequest

ADAPTER_ID="p162g65c6.isolated-generated-probe"

def _bounded_extra_args(args):
    out=[]
    for x in args:
        if not isinstance(x,str) or not x or len(x)>64:
            raise PermissionError("invalid probe argument")
        if "/" in x or "\\" in x or x in {".",".."}:
            raise PermissionError("path-like probe argument forbidden")
        out.append(x)
    return tuple(out)

def run_isolated_generated_probe(*,script,sandbox,args=(),timeout_seconds=30):
    sb=Path(sandbox).resolve()
    sc=Path(script).resolve()
    if not sb.is_dir(): raise PermissionError("sandbox must exist")
    if sc.parent!=sb or not sc.is_file() or sc.is_symlink():
        raise PermissionError("script must be a regular direct child of sandbox")
    if timeout_seconds!=30: raise PermissionError("probe timeout fixed at 30 seconds")
    extra=_bounded_extra_args(args)
    script_hash=hashlib.sha256(sc.read_bytes()).hexdigest()
    eid="python-current-isolated"
    argv=(eid,"-I",str(sc),str(sb),*extra)
    eff=GovernedProcessEffector(
      executable_registry={eid:{"path":__import__("sys").executable,"argv_prefix":["-I",str(sc),str(sb)]}},
      environment_registry={"isolated-probe":{}})
    handle=SimpleNamespace(target_binding=eff.canonical_target(eid),
      operation_id="PROCESS_EXECUTE",adapter_id=ADAPTER_ID)
    req=ProcessEffectRequest(eid,argv,str(sb),"isolated-probe","CLOSED",30.0,
      "NO_DESCENDANTS","READ_ONLY_OBSERVATION")
    result=eff.execute(request=req,handle=handle,adapter_id=ADAPTER_ID)
    result["probe_script_sha256"]=script_hash
    result["probe_script"]=str(sc)
    result["sandbox"]=str(sb)
    return result

def as_completed_process(result):
    return SimpleNamespace(
      returncode=result.get("returncode"),
      stdout=(result.get("stdout") or b"").decode("utf-8",errors="replace"),
      stderr=(result.get("stderr") or b"").decode("utf-8",errors="replace"))
