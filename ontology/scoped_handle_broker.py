"""P162-G3 ScopedEffectHandle broker — non-causal least-effective-capability reference."""
from dataclasses import dataclass
from hashlib import sha256
from threading import RLock
import json
@dataclass(frozen=True)
class ScopedEffectHandle:
    handle_id:str; lease_id:str; reservation_id:str; claim_hash:str; adapter_id:str; effector_id:str
    operation_id:str; target_binding:object; scope_hash:str; audience:str; expires_at:str
    single_use:bool=True; transferable:bool=False; child_inheritance:bool=False; ambient_authority:bool=False
class ScopedHandleBroker:
    def __init__(self):
        self._lock=RLock();self._issued={};self._used=set()
    @staticmethod
    def _subset(requested,allowed):
        if not isinstance(requested,dict) or not isinstance(allowed,dict): return False
        for k,v in requested.items():
            if k not in allowed:return False
            a=allowed[k]
            if isinstance(v,list):
                if not isinstance(a,list) or not set(v).issubset(set(a)):return False
            elif isinstance(v,dict):
                if not ScopedHandleBroker._subset(v,a):return False
            elif v!=a:return False
        return True
    def issue(self,*,claim,lease,registry_entry,requested_scope,authorized_scope,target_binding,audience,now_iso):
        if claim is None:return {"status":"HANDLE_BLOCKED","reason":"missing_execution_claim","handle":None}
        if claim.lease_id!=str(lease.get("lease_id")) or claim.reservation_id!=str(lease.get("reservation_id")):
            return {"status":"HANDLE_BLOCKED","reason":"claim_lease_binding_mismatch","handle":None}
        if claim.adapter_id!=str(registry_entry.get("adapter_id")):return {"status":"HANDLE_BLOCKED","reason":"wrong_adapter","handle":None}
        if audience!=claim.adapter_id:return {"status":"HANDLE_BLOCKED","reason":"wrong_audience","handle":None}
        if str(lease.get("expires_at",""))<=str(now_iso):return {"status":"HANDLE_BLOCKED","reason":"lease_expired","handle":None}
        if not self._subset(requested_scope,authorized_scope):return {"status":"HANDLE_BLOCKED","reason":"scope_widening","handle":None}
        if requested_scope.get("ambient_authority") is True:return {"status":"HANDLE_BLOCKED","reason":"ambient_authority_forbidden","handle":None}
        if requested_scope.get("child_inheritance") is True:return {"status":"HANDLE_BLOCKED","reason":"child_inheritance_forbidden","handle":None}
        if requested_scope.get("transferable") is True:return {"status":"HANDLE_BLOCKED","reason":"transfer_forbidden","handle":None}
        key=(claim.claim_hash,json.dumps(requested_scope,sort_keys=True,separators=(",",":")),json.dumps(target_binding,sort_keys=True,default=str))
        with self._lock:
            if key in self._issued:return {"status":"HANDLE_BLOCKED","reason":"duplicate_handle_request","handle":self._issued[key]}
            payload={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"claim_hash":claim.claim_hash,"adapter_id":claim.adapter_id,"effector_id":registry_entry.get("effector_id"),"operation_id":lease.get("operation_id"),"target_binding":target_binding,"scope":requested_scope,"audience":audience,"expires_at":lease.get("expires_at")}
            hid=sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
            h=ScopedEffectHandle(hid,claim.lease_id,claim.reservation_id,claim.claim_hash,claim.adapter_id,str(registry_entry.get("effector_id")),str(lease.get("operation_id")),target_binding,sha256(json.dumps(requested_scope,sort_keys=True,separators=(",",":")).encode()).hexdigest(),audience,str(lease.get("expires_at")))
            self._issued[key]=h;return {"status":"HANDLE_ISSUED","reason":None,"handle":h,"credential_disclosed":False,"effector_called":False,"real_world_effect_performed":False}
    def consume_once(self,handle_id):
        with self._lock:
            if handle_id in self._used:return False
            if not any(h.handle_id==handle_id for h in self._issued.values()):return False
            self._used.add(handle_id);return True
