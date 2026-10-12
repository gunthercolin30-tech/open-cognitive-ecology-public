"""P162-G6.5c1 Git read-only PROCESS facade; c10e6R hardened."""
from __future__ import annotations
import os
import subprocess as _sp
_ALLOWED={"rev-parse","log","remote","tag","status","diff","show","ls-files"}
_FORBIDDEN={"--exec","-c","--config-env","--ext-diff","--textconv"}
_DANGEROUS=("GIT_CONFIG_","GIT_EXTERNAL_DIFF","GIT_PAGER","GIT_SSH","GIT_ASKPASS")
def _bad(tail):
    return any(x in _FORBIDDEN or x.startswith("-c=") or x.startswith("--config-env=") or x.startswith("--ext-diff=") or x.startswith("--textconv=") for x in tail)
def _safe_env(caller=None):
    e=dict(os.environ if caller is None else caller)
    for k in list(e):
        if any(k==p or k.startswith(p) for p in _DANGEROUS): e.pop(k,None)
    e["GIT_PAGER"]="cat"; e["PAGER"]="cat"; return e
def _effect_argv(a):
    return a[:2]+["--no-ext-diff"]+a[2:] if a[1] in {"diff","show"} and "--no-ext-diff" not in a[2:] else a
class _Facade:
    PIPE=_sp.PIPE; STDOUT=_sp.STDOUT; DEVNULL=_sp.DEVNULL
    def _check(self,args):
        a=list(args)
        if len(a)<2 or a[0]!="git" or a[1] not in _ALLOWED: raise PermissionError("git operation not registered read-only")
        if _bad(a[2:]): raise PermissionError("git process/config delegation forbidden")
        if a[1]=="remote" and a[2:]!=["-v"]: raise PermissionError("remote limited to -v")
        if a[1]=="tag" and a[2:]!=["-l"]: raise PermissionError("tag limited to -l")
        return a
    def run(self,args,**kw):
        a=_effect_argv(self._check(args)); kw.pop("shell",None); kw["env"]=_safe_env(kw.get("env")); return _sp.run(a,shell=False,**kw)
    def check_output(self,args,**kw):
        a=_effect_argv(self._check(args)); kw.pop("shell",None); kw["env"]=_safe_env(kw.get("env")); return _sp.check_output(a,**kw)
governed_git_subprocess=_Facade()
