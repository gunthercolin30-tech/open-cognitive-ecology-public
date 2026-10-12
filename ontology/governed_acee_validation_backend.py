from __future__ import annotations
import os, signal, subprocess, sys, time
from pathlib import Path
from typing import Any, Dict, Sequence
TIMEOUT_MAX_SECONDS=3600.0
def _minimal_env() -> Dict[str,str]:
    env={k:v for k in ("PATH","HOME","TMPDIR","LANG","LC_ALL","PYTHONPATH") if (v:=os.environ.get(k)) is not None}
    env.setdefault("PYTHONPYCACHEPREFIX","/private/tmp/oce_pycache")
    return env
def _closed_argv(argv: Sequence[str]) -> tuple[str,...]:
    value=tuple(str(x) for x in argv)
    if not value or value[0] not in {sys.executable,"python3","python"}:
        raise PermissionError("python_command_required")
    if value[1:] not in (("-m","validation.main"),("-m","validation.main","--full")):
        raise PermissionError("closed_validation_command_required")
    return value
def run_closed_validation(argv: Sequence[str], *, cwd: Path, timeout_seconds: float) -> Dict[str,Any]:
    argv=_closed_argv(argv); timeout=float(timeout_seconds)
    if timeout<0.1 or timeout>TIMEOUT_MAX_SECONDS: raise PermissionError("timeout_outside_bound")
    start=time.perf_counter()
    process=subprocess.Popen(list(argv),cwd=str(Path(cwd).resolve()),env=_minimal_env(),text=True,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False,start_new_session=True,close_fds=True)
    try:
        stdout,stderr=process.communicate(timeout=timeout)
        return {"returncode":process.returncode,"timed_out":False,"duration_seconds":round(time.perf_counter()-start,6),
                "stdout":stdout or "","stderr":stderr or "","process_group_terminated":False,"forced_kill":False}
    except subprocess.TimeoutExpired as exc:
        stdout=exc.stdout.decode() if isinstance(exc.stdout,bytes) else (exc.stdout or "")
        stderr=exc.stderr.decode() if isinstance(exc.stderr,bytes) else (exc.stderr or "")
        forced=False
        try: os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError: pass
        try: tail_out,tail_err=process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            forced=True
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            tail_out,tail_err=process.communicate()
        return {"returncode":process.returncode,"timed_out":True,"duration_seconds":round(time.perf_counter()-start,6),
                "stdout":stdout+(tail_out or ""),"stderr":stderr+(tail_err or ""),
                "process_group_terminated":True,"forced_kill":forced}
