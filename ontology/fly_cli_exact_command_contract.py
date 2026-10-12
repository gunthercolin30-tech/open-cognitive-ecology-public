from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Optional, Tuple
FLY_EXECUTABLE="fly"
OP_AUTH_WHOAMI="FLY_AUTH_WHOAMI"
OP_STATUS="FLY_APP_STATUS"
OP_APPS_LIST="FLY_APPS_LIST"
OP_SSH_IDENTITY_PROBE="FLY_SSH_IDENTITY_PROBE"
ALLOWED_OPERATIONS=frozenset({OP_AUTH_WHOAMI,OP_STATUS,OP_APPS_LIST,OP_SSH_IDENTITY_PROBE})
_APP=re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_SSH_COMMAND="hostname && uname -a"
@dataclass(frozen=True)
class FlyCommandSpec:
 operation_id:str
 app_name:Optional[str]=None
def _app(value):
 if not isinstance(value,str): raise ValueError("app_name_required")
 v=value.strip()
 if not _APP.fullmatch(v): raise ValueError("invalid_bounded_fly_app_name")
 return v
def compile_fly_argv(spec):
 if not isinstance(spec,FlyCommandSpec): raise TypeError("FlyCommandSpec_required")
 op=spec.operation_id
 if op not in ALLOWED_OPERATIONS: raise PermissionError("unknown_fly_operation")
 if op==OP_AUTH_WHOAMI:
  if spec.app_name is not None: raise ValueError("app_name_forbidden")
  return (FLY_EXECUTABLE,"auth","whoami")
 if op==OP_APPS_LIST:
  if spec.app_name is not None: raise ValueError("app_name_forbidden")
  return (FLY_EXECUTABLE,"apps","list")
 app=_app(spec.app_name)
 if op==OP_STATUS: return (FLY_EXECUTABLE,"status","--app",app)
 if op==OP_SSH_IDENTITY_PROBE: return (FLY_EXECUTABLE,"ssh","console","--app",app,"-C",_SSH_COMMAND)
 raise PermissionError("unreachable_operation")
def raw_argv_is_authority(_): return False
