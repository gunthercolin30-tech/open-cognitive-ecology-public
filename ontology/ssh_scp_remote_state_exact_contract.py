from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import ipaddress,re
OP_REMOTE_MKDIR="REMOTE_MKDIR";OP_REMOTE_STATE_PUSH="REMOTE_STATE_PUSH";OP_REMOTE_STATE_PULL="REMOTE_STATE_PULL"
ALLOWED_OPERATIONS=frozenset({OP_REMOTE_MKDIR,OP_REMOTE_STATE_PUSH,OP_REMOTE_STATE_PULL})
HISTORICAL_REMOTE_ROOT_DEFAULT="~/open-cognitive-ecology";HISTORICAL_TIMEOUT_DEFAULT=30
USER_RE=re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")
HOST_RE=re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$")
REMOTE_ROOT_RE=re.compile(r"^(?:~|/)[A-Za-z0-9_./-]{1,240}$")
TIMEOUT_MIN_SECONDS=1;TIMEOUT_MAX_SECONDS=120;REMOTE_SUBDIR="distributed_state";REMOTE_FILENAME="remote_live_state_echo.json"
@dataclass(frozen=True)
class RemoteStateOperationSpec:
 operation_id:str;host:str;user:str;remote_root:str;timeout_seconds:int;batch_mode:bool;local_state_path:str;remote_echo_path:str
def _user(v):
 if type(v) is not str or not USER_RE.fullmatch(v):raise ValueError("invalid ssh user")
 return v
def _host(v):
 if type(v) is not str or not v or v.startswith("-") or any(c in v for c in "@:/[] \t\r\n"):raise ValueError("invalid ssh host")
 try:ipaddress.IPv4Address(v);return v
 except ValueError:pass
 if not HOST_RE.fullmatch(v):raise ValueError("invalid ssh host")
 return v
def _root(v):
 if type(v) is not str or not REMOTE_ROOT_RE.fullmatch(v):raise ValueError("invalid remote root")
 if v.startswith("-") or "//" in v or "/../" in v or v.endswith("/..") or "/./" in v:raise ValueError("unsafe remote root")
 r=v.rstrip("/")
 if r in {"","~"}:raise ValueError("remote root too broad")
 return r
def _timeout(v):
 if type(v) is not int or not 1<=v<=120:raise ValueError("invalid timeout")
 return v
def _local(v):
 if type(v) is not str or not v or chr(0) in v:raise ValueError("invalid local path")
 p=Path(v).expanduser()
 if not p.is_absolute():raise ValueError("local path must be absolute")
 return str(p)
def validate_spec(s):
 if type(s) is not RemoteStateOperationSpec:raise TypeError("typed spec required")
 if s.operation_id not in ALLOWED_OPERATIONS:raise ValueError("unknown remote-state operation")
 _user(s.user);_host(s.host);_root(s.remote_root);_timeout(s.timeout_seconds)
 if type(s.batch_mode) is not bool:raise ValueError("batch_mode must be bool")
 _local(s.local_state_path);_local(s.remote_echo_path);return s
def compile_remote_state_argv(s):
 validate_spec(s);target=f"{_user(s.user)}@{_host(s.host)}";rd=f"{_root(s.remote_root)}/{REMOTE_SUBDIR}";rf=f"{rd}/{REMOTE_FILENAME}";opts=["-o",f"ConnectTimeout={_timeout(s.timeout_seconds)}"]
 if s.batch_mode:opts=["-o","BatchMode=yes",*opts]
 if s.operation_id==OP_REMOTE_MKDIR:return tuple(["ssh",*opts,target,"mkdir","-p",rd])
 if s.operation_id==OP_REMOTE_STATE_PUSH:return tuple(["scp",*opts,"-q",_local(s.local_state_path),f"{target}:{rf}"])
 if s.operation_id==OP_REMOTE_STATE_PULL:return tuple(["scp",*opts,"-q",f"{target}:{rf}",_local(s.remote_echo_path)])
 raise AssertionError("closed operation set violated")
