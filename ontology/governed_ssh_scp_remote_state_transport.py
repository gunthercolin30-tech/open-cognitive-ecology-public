from __future__ import annotations
import os
import subprocess
from dataclasses import dataclass
from ontology.ssh_scp_remote_state_exact_contract import RemoteStateOperationSpec,compile_remote_state_argv,validate_spec
MAX_STDOUT_CHARS=12000
MAX_STDERR_CHARS=12000
@dataclass(frozen=True)
class RemoteStateTransportResult:
    operation_id:str
    argv:tuple[str,...]
    returncode:int
    stdout:str
    stderr:str
def _minimal_environment()->dict[str,str]:
    env={}
    for k in ("PATH","HOME","TMPDIR","LANG","LC_ALL","SSH_AUTH_SOCK"):
        v=os.environ.get(k)
        if v: env[k]=v
    return env
def run_remote_state_operation(spec:RemoteStateOperationSpec)->RemoteStateTransportResult:
    validate_spec(spec)
    argv=compile_remote_state_argv(spec)
    try:
        cp=subprocess.run(argv,check=False,capture_output=True,text=True,timeout=spec.timeout_seconds,shell=False,start_new_session=True,close_fds=True,env=_minimal_environment())
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("remote-state transport timeout") from exc
    if cp.returncode!=0:
        raise subprocess.CalledProcessError(cp.returncode,argv,output=(cp.stdout or "")[:MAX_STDOUT_CHARS],stderr=(cp.stderr or "")[:MAX_STDERR_CHARS])
    return RemoteStateTransportResult(spec.operation_id,tuple(argv),cp.returncode,(cp.stdout or "")[:MAX_STDOUT_CHARS],(cp.stderr or "")[:MAX_STDERR_CHARS])
