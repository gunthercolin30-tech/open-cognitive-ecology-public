"""P162-G6.5c2b exact/bounded Git PROCESS mediation; c10e6R hardened."""
from __future__ import annotations
import os, re
import subprocess as _sp
_ALLOWED={"rev-parse","log","remote","tag","branch","status","diff","show","ls-files"}
_FORBIDDEN={"--exec","-c","--config-env","--ext-diff","--textconv"}
_DANGEROUS=("GIT_CONFIG_","GIT_EXTERNAL_DIFF","GIT_PAGER","GIT_SSH","GIT_ASKPASS")
def _bad(tail):
    return any(x in _FORBIDDEN or x.startswith("-c=") or x.startswith("--config-env=") or x.startswith("--ext-diff=") or x.startswith("--textconv=") for x in tail)
def _bounded(args):
    a=list(args)
    if len(a)<2 or a[0]!="git" or a[1] not in _ALLOWED: raise PermissionError("git operation outside bounded grammar")
    verb=a[1]; tail=a[2:]
    if _bad(tail): raise PermissionError("git process/config delegation forbidden")
    if verb=="remote" and tail!=["-v"]: raise PermissionError("remote limited to -v")
    if verb=="branch" and tail!=["--show-current"]: raise PermissionError("branch limited")
    if verb=="tag" and tail not in (["-l"],["--points-at","HEAD"]): raise PermissionError("tag limited")
    if verb=="rev-parse":
        allowed={"HEAD","--abbrev-ref","--show-toplevel","--is-inside-work-tree"}
        if not tail or any(x not in allowed for x in tail): raise PermissionError("rev-parse limited")
    if verb=="log":
        for x in tail:
            if x.startswith("-") and not (re.fullmatch(r"-\d+",x) or x.startswith("--pretty=") or x in {"--decorate","--oneline","--format=%H","--format=%H%x00"}): raise PermissionError("log limited")
    return a
def _safe_env(caller=None):
    e=dict(os.environ if caller is None else caller)
    for k in list(e):
        if any(k==p or k.startswith(p) for p in _DANGEROUS): e.pop(k,None)
    e["GIT_PAGER"]="cat"; e["PAGER"]="cat"; return e
def _effect_argv(a):
    return a[:2]+["--no-ext-diff"]+a[2:] if a[1] in {"diff","show"} and "--no-ext-diff" not in a[2:] else a
class _Facade:
    PIPE=_sp.PIPE; STDOUT=_sp.STDOUT; DEVNULL=_sp.DEVNULL
    CalledProcessError=_sp.CalledProcessError; TimeoutExpired=_sp.TimeoutExpired
    def run(self,args,**kw):
        a=_effect_argv(_bounded(args)); kw.pop("shell",None); kw["env"]=_safe_env(kw.get("env")); return _sp.run(a,shell=False,**kw)
    def check_output(self,args,**kw):
        a=_effect_argv(_bounded(args)); kw.pop("shell",None); kw["env"]=_safe_env(kw.get("env")); return _sp.check_output(a,**kw)
governed_git_subprocess=_Facade()
