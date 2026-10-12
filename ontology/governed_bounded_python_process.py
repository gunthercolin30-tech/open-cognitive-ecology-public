"""P162-G6.5c5 bounded Python PROCESS profiles. Not a general Python runner."""
from __future__ import annotations
import os, sys
from pathlib import Path
from types import SimpleNamespace
from ontology.governed_process_effector import GovernedProcessEffector, ProcessEffectRequest

ADAPTER_ID="p162g65c5.bounded-python"
_ALLOWED={"PIP_FREEZE":("-m","pip","freeze"),"VALIDATION_MAIN":("-m","validation.main")}

def _minimal_env():
    return {k:v for k in ("PATH","HOME","TMPDIR","LANG","LC_ALL","PYTHONPATH")
            if (v:=os.environ.get(k)) is not None}

def run_bounded_python(operation_id,*,cwd,timeout_seconds):
    if operation_id not in _ALLOWED:
        raise PermissionError("unregistered bounded Python operation")
    exe=str(Path(sys.executable).resolve())
    if not Path(exe).is_file(): raise RuntimeError("python executable unresolved")
    eid="python-current"; argv=(eid,*_ALLOWED[operation_id])
    eff=GovernedProcessEffector(
      executable_registry={eid:{"path":exe,"argv_prefix":list(_ALLOWED[operation_id])}},
      environment_registry={"bounded-python":_minimal_env()})
    handle=SimpleNamespace(target_binding=eff.canonical_target(eid),
      operation_id="PROCESS_EXECUTE",adapter_id=ADAPTER_ID)
    req=ProcessEffectRequest(eid,argv,str(cwd),"bounded-python","CLOSED",
      float(timeout_seconds),"NO_DESCENDANTS","READ_ONLY_OBSERVATION")
    return eff.execute(request=req,handle=handle,adapter_id=ADAPTER_ID)

def pip_freeze(*,cwd,timeout_seconds=60):
    return run_bounded_python("PIP_FREEZE",cwd=cwd,timeout_seconds=timeout_seconds)

def validation_main(*,cwd,timeout_seconds=180):
    return run_bounded_python("VALIDATION_MAIN",cwd=cwd,timeout_seconds=timeout_seconds)
