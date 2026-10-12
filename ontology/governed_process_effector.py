"""P162-G6.5b governed PROCESS mediation TCB."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,subprocess
from pathlib import Path
P162_G65B_PROCESS_MEDIATED=True
@dataclass(frozen=True)
class ProcessEffectRequest:
 executable_id:str; argv:tuple[str,...]; cwd:str|None; environment_profile:str; stdin_policy:str; timeout_seconds:float; child_policy:str="NO_DESCENDANTS"; idempotency_class:str="UNKNOWN"
class ProcessTrustedTransport:
 def run(self,*,executable,argv,cwd,env,stdin_bytes,timeout):
  try:
   cp=subprocess.run([executable,*argv[1:]],cwd=cwd,env=env,input=stdin_bytes,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,shell=False,check=False,close_fds=True)
   return {"status":"EFFECT_CONFIRMED" if cp.returncode==0 else "EFFECT_FAILED_CONFIRMED","returncode":cp.returncode,"stdout":cp.stdout,"stderr":cp.stderr,"timed_out":False,"uncertainty":False}
  except subprocess.TimeoutExpired as exc:
   return {"status":"EFFECT_STATE_INDETERMINATE","returncode":None,"stdout":exc.stdout or b"","stderr":exc.stderr or b"","timed_out":True,"uncertainty":True}
  except Exception:
   return {"status":"EFFECT_STATE_INDETERMINATE","returncode":None,"stdout":b"","stderr":b"","timed_out":False,"uncertainty":True}
class GovernedProcessEffector:
 def __init__(self,*,executable_registry,environment_registry,transport=None):
  self.executable_registry=dict(executable_registry); self.environment_registry={k:dict(v) for k,v in environment_registry.items()}; self.transport=transport or ProcessTrustedTransport()
 @staticmethod
 def canonical_target(executable_id): return "process://"+executable_id
 @staticmethod
 def _argv_hash(argv): return hashlib.sha256(json.dumps(list(argv),separators=(",",":")).encode()).hexdigest()
 def _blocked(self,r,reason): return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":reason,"executable_id":r.executable_id,"argv_hash":self._argv_hash(r.argv),"returncode":None,"timed_out":False,"uncertainty":False}
 def execute(self,*,request,handle,adapter_id):
  if not isinstance(request.argv,tuple) or not request.argv: return self._blocked(request,"structured_argv_required")
  if any(not isinstance(x,str) or "\x00" in x for x in request.argv): return self._blocked(request,"invalid_argv")
  if request.stdin_policy not in {"CLOSED","INHERIT_FORBIDDEN"}: return self._blocked(request,"stdin_policy_not_registered")
  if request.child_policy!="NO_DESCENDANTS": return self._blocked(request,"child_process_rights_not_granted")
  spec=self.executable_registry.get(request.executable_id)
  if not isinstance(spec,dict): return self._blocked(request,"unknown_executable_id")
  executable=str(Path(spec.get("path","")).resolve())
  if not Path(executable).is_file(): return self._blocked(request,"executable_not_resolved")
  if request.argv[0]!=request.executable_id: return self._blocked(request,"argv0_identity_mismatch")
  pref=tuple(spec.get("argv_prefix",()))
  if tuple(request.argv[1:1+len(pref)])!=pref: return self._blocked(request,"argv_prefix_outside_registry")
  env=self.environment_registry.get(request.environment_profile)
  if env is None: return self._blocked(request,"unknown_environment_profile")
  if getattr(handle,"target_binding",None)!=self.canonical_target(request.executable_id): return self._blocked(request,"target_outside_scoped_handle")
  if getattr(handle,"operation_id",None)!="PROCESS_EXECUTE": return self._blocked(request,"operation_outside_scoped_handle")
  if getattr(handle,"adapter_id",None)!=adapter_id: return self._blocked(request,"adapter_mismatch")
  out=self.transport.run(executable=executable,argv=request.argv,cwd=request.cwd,env={str(k):str(v) for k,v in env.items()},stdin_bytes=None,timeout=float(request.timeout_seconds))
  return {**out,"executable_id":request.executable_id,"argv_hash":self._argv_hash(request.argv)}
