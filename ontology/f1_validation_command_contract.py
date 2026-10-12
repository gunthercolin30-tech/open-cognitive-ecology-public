"""P162-G6.5c7b closed F1 validation-command source contract."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence

REQUIRED_ROLES=("functional","fast_guard","fast_acceptance","final_lock","degradation","non_regression","specialized")
ALLOWED_KINDS=("VALIDATION_MAIN","REGISTERED_SCRIPT")

@dataclass(frozen=True)
class F1ValidationCommandDescriptor:
    role: str
    kind: str
    script_id: str | None = None
    args: tuple[str,...] = ()
    full_validation: bool = False

def _bounded_atom(x:str)->str:
    if not isinstance(x,str) or not x or len(x)>128:
        raise ValueError("invalid argument atom")
    if "\x00" in x or "\n" in x or "\r" in x:
        raise ValueError("control character forbidden")
    return x

def validate_descriptor(raw:Mapping)->F1ValidationCommandDescriptor:
    allowed={"role","kind","script_id","args","full_validation"}
    if set(raw)-allowed: raise ValueError("unknown descriptor field")
    role=raw.get("role"); kind=raw.get("kind")
    if role not in REQUIRED_ROLES: raise ValueError("unknown F1 role")
    if kind not in ALLOWED_KINDS: raise ValueError("unknown command kind")
    args=tuple(_bounded_atom(x) for x in raw.get("args",()))
    full=raw.get("full_validation",False)
    if not isinstance(full,bool): raise ValueError("full_validation must be boolean")
    sid=raw.get("script_id")
    if kind=="VALIDATION_MAIN":
        if sid is not None or args: raise ValueError("validation.main takes no opaque args")
    else:
        if not isinstance(sid,str) or not sid or "/" in sid or "\\" in sid or sid.endswith(".py"):
            raise ValueError("REGISTERED_SCRIPT requires opaque registry id, not path")
        if full: raise ValueError("full flag only applies to validation.main")
    return F1ValidationCommandDescriptor(role,kind,sid,args,full)

def validate_f1_contract(raw:Sequence[Mapping])->tuple[F1ValidationCommandDescriptor,...]:
    if not isinstance(raw,(list,tuple)) or len(raw)!=len(REQUIRED_ROLES):
        raise ValueError("exactly seven F1 descriptors required")
    ds=tuple(validate_descriptor(x) for x in raw)
    if tuple(x.role for x in ds)!=REQUIRED_ROLES:
        raise ValueError("F1 role order mismatch")
    return ds

def compile_descriptor(d:F1ValidationCommandDescriptor, script_registry:Mapping[str,str])->tuple[str,...]:
    if d.kind=="VALIDATION_MAIN":
        return ("PYTHON_MODULE","validation.main","--full") if d.full_validation else ("PYTHON_MODULE","validation.main")
    if d.script_id not in script_registry: raise ValueError("unresolved registered script")
    target=script_registry[d.script_id]
    if not isinstance(target,str) or not target: raise ValueError("invalid registry target")
    return ("REGISTERED_SCRIPT",d.script_id,*d.args)
