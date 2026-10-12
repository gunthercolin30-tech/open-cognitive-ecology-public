from __future__ import annotations
from typing import Any, Dict
import os, subprocess
from ontology.fly_cli_exact_command_contract import FlyCommandSpec, compile_fly_argv
TIMEOUT_MIN_SECONDS=1
TIMEOUT_MAX_SECONDS=120
STDOUT_LIMIT=6000
STDERR_LIMIT=3000
_ENV_KEYS=("PATH","HOME","TMPDIR","LANG","LC_ALL")
def _minimal_env():
 env={k:os.environ[k] for k in _ENV_KEYS if k in os.environ}
 env.setdefault("PATH","/usr/local/bin:/usr/bin:/bin")
 return env
def run_fly_operation(spec: FlyCommandSpec, timeout_seconds: int) -> Dict[str,Any]:
 argv=compile_fly_argv(spec)
 if isinstance(timeout_seconds,bool) or not isinstance(timeout_seconds,int): raise TypeError("integer_timeout_required")
 if not TIMEOUT_MIN_SECONDS <= timeout_seconds <= TIMEOUT_MAX_SECONDS: raise ValueError("bounded_timeout_required")
 command=list(argv)
 try:
  completed=subprocess.run(command,capture_output=True,text=True,timeout=timeout_seconds,check=False,shell=False,start_new_session=True,close_fds=True,env=_minimal_env())
  return {"command":command,"returncode":completed.returncode,"success":completed.returncode==0,"stdout":completed.stdout[-STDOUT_LIMIT:],"stderr":completed.stderr[-STDERR_LIMIT:]}
 except FileNotFoundError as exc:
  return {"command":command,"returncode":None,"success":False,"stdout":"","stderr":f"FileNotFoundError: {exc}"}
 except subprocess.TimeoutExpired as exc:
  return {"command":command,"returncode":None,"success":False,"stdout":(exc.stdout or "")[-STDOUT_LIMIT:] if isinstance(exc.stdout,str) else "","stderr":f"TimeoutExpired after {timeout_seconds}s"}
 except Exception as exc:
  return {"command":command,"returncode":None,"success":False,"stdout":"","stderr":f"{type(exc).__name__}: {exc}"}
