
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from urllib.parse import urlsplit

ALLOWED_METHODS={"GET","POST","PUT","PATCH","DELETE","HEAD"}
@dataclass(frozen=True)
class GovernedNetworkRequest:
    method:str
    url:str
    headers:Mapping[str,str]
    body:Optional[bytes]=None
    timeout_seconds:float=20.0
    idempotent:bool=False

class GovernedNetworkEffector:
    # Trusted HTTP TCB. It owns no ambient credential and receives no authority
    # except the already-governed handle/use supplied for this invocation.
    def __init__(self, *, transport, credential_resolver=None):
        if transport is None: raise ValueError("transport_required")
        self._transport=transport
        self._credential_resolver=credential_resolver

    @staticmethod
    def _target(url):
        p=urlsplit(str(url))
        if p.scheme not in {"https","http"} or not p.hostname:
            return None
        port=p.port
        return p.hostname if port is None else f"{p.hostname}:{port}"

    def execute(self, *, request, handle, brokered_use, adapter_id, effector_id,
                now_iso, authorization_header="Authorization"):
        if request.method not in ALLOWED_METHODS:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"method_not_allowed"}
        target=self._target(request.url)
        if not target:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"invalid_network_target"}
        if handle is None:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"missing_scoped_handle"}
        if getattr(handle,"adapter_id",None)!=adapter_id:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"adapter_mismatch"}
        if getattr(handle,"effector_id",None)!=effector_id:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"effector_mismatch"}
        if getattr(handle,"operation_id",None)!=request.method:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"operation_mismatch"}
        if getattr(handle,"target_binding",None)!=target:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"target_mismatch"}
        headers={str(k):str(v) for k,v in dict(request.headers or {}).items()}
        # Caller may never smuggle ambient Authorization into the trusted boundary.
        if authorization_header in headers:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"ambient_credential_header_forbidden"}
        credential_public=None
        if brokered_use is not None:
            if self._credential_resolver is None:
                return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"credential_resolver_missing"}
            resolved=self._credential_resolver.resolve_for_effector(
                brokered_use=brokered_use,adapter_id=adapter_id,effector_id=effector_id,
                operation=request.method,target=target,now_iso=now_iso)
            if resolved.get("status")!="CREDENTIAL_RESOLVED_FOR_EFFECTOR":
                return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":resolved.get("reason")}
            secret=resolved["secret"]
            headers[authorization_header]="Bearer "+secret
            credential_public=self._credential_resolver.public_record(resolved)
        try:
            result=self._transport(method=request.method,url=request.url,headers=headers,
                                   body=request.body,timeout_seconds=request.timeout_seconds)
        except TimeoutError:
            return {"status":"EFFECT_STATE_INDETERMINATE","reason":"transport_timeout_after_possible_dispatch",
                    "target":target,"method":request.method,"retry_allowed":False}
        except Exception as exc:
            return {"status":"EFFECT_STATE_INDETERMINATE","reason":"transport_exception_after_possible_dispatch",
                    "target":target,"method":request.method,"retry_allowed":False,
                    "exception_type":type(exc).__name__}
        return {"status":"EFFECT_CONFIRMED","target":target,"method":request.method,
                "retry_allowed":bool(request.idempotent),"credential":credential_public,
                "transport_result":result}


class UrllibTrustedTransport:
    # Concrete HTTP transport confined to the governed network TCB.
    def __call__(self, *, method, url, headers, body, timeout_seconds):
        import urllib.request
        req=urllib.request.Request(url=url,data=body,headers=dict(headers or {}),method=method)
        with urllib.request.urlopen(req,timeout=float(timeout_seconds)) as response:
            payload=response.read()
            return {"status_code":int(getattr(response,"status",200)),"body":payload,"headers":dict(response.headers.items()) if getattr(response,"headers",None) else {}}


class TrustedTcpConnectProbeTransport:
    def __call__(self, *, host, port, timeout_seconds):
        import socket
        with socket.create_connection((str(host), int(port)), timeout=float(timeout_seconds)):
            return {"connected": True}

class GovernedTcpProbeEffector:
    OPERATION_ID = "TCP_CONNECT_PROBE"
    def __init__(self, *, transport):
        if transport is None: raise ValueError("transport_required")
        self._transport=transport
    @staticmethod
    def _target(host,port):
        host=str(host or "").strip()
        try: port=int(port)
        except Exception: return None
        return f"{host}:{port}" if host and 1 <= port <= 65535 else None
    def execute(self, *, host, port, timeout_seconds, handle, adapter_id, effector_id):
        target=self._target(host,port)
        if not target: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"invalid_tcp_target","reachable":False}
        if handle is None: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"missing_scoped_handle","reachable":False}
        if getattr(handle,"adapter_id",None)!=adapter_id: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"adapter_mismatch","reachable":False}
        if getattr(handle,"effector_id",None)!=effector_id: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"effector_mismatch","reachable":False}
        if getattr(handle,"operation_id",None)!=self.OPERATION_ID: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"operation_mismatch","reachable":False}
        if getattr(handle,"target_binding",None)!=target: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"target_mismatch","reachable":False}
        if getattr(handle,"ambient_authority",True) is not False: return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"ambient_authority_forbidden","reachable":False}
        if getattr(handle,"transferable",True) is not False or getattr(handle,"child_inheritance",True) is not False:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"inheritance_or_transfer_forbidden","reachable":False}
        try: result=self._transport(host=str(host),port=int(port),timeout_seconds=float(timeout_seconds))
        except TimeoutError: return {"status":"EFFECT_FAILED_CONFIRMED","reason":"tcp_connect_timeout","reachable":False,"target":target}
        except OSError as exc: return {"status":"EFFECT_FAILED_CONFIRMED","reason":"tcp_connect_failed","reachable":False,"target":target,"exception_type":type(exc).__name__}
        except Exception as exc: return {"status":"EFFECT_STATE_INDETERMINATE","reason":"tcp_probe_transport_exception","reachable":False,"target":target,"retry_allowed":False,"exception_type":type(exc).__name__}
        return {"status":"EFFECT_CONFIRMED","reason":None,"reachable":bool((result or {}).get("connected")),"target":target,"retry_allowed":True}
