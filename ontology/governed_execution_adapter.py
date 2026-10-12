"""P162-G1 governed execution boundary foundation -- non-causal."""
from dataclasses import dataclass
from hashlib import sha256
import json
EXECUTION_STATUSES=("EXECUTION_NOT_STARTED","EXECUTION_BLOCKED_AT_FINAL_RECHECK","EXECUTION_STARTED","EFFECT_NOT_REACHED","EFFECT_DISPATCHED","EFFECT_CONFIRMED","EFFECT_PARTIAL","EFFECT_FAILED_CONFIRMED","EFFECT_STATE_INDETERMINATE","EXECUTION_INTERRUPTED","EXECUTION_ABORTED")
@dataclass(frozen=True)
class BoundaryAssessment:
    status:str
    binding_hash:str
    execution_claim_created:bool=False
    scoped_handle_issued:bool=False
    credential_disclosed:bool=False
    effector_called:bool=False
    real_world_effect_performed:bool=False
def assess_execution_boundary(*,lease,registry_entry,executor_instance_id,capability_instance_id,capability_id,operation_id,invocation_request_hash,effective_execution_scope_hash,now_iso):
    reason=None
    checks=[
      (registry_entry.get("status")=="ACTIVE","adapter_not_active"),
      (lease.get("executor_id")==executor_instance_id,"wrong_executor"),
      (lease.get("capability_instance_id")==capability_instance_id,"wrong_capability_instance"),
      (capability_id in registry_entry.get("capability_ids",[]),"unsupported_capability"),
      (operation_id in registry_entry.get("operation_ids",[]),"unsupported_operation"),
      (lease.get("operation_id")==operation_id,"operation_mismatch"),
      (lease.get("invocation_request_hash")==invocation_request_hash,"invocation_hash_mismatch"),
      (lease.get("effective_execution_scope_hash")==effective_execution_scope_hash,"scope_hash_mismatch"),
      (lease.get("audience")==registry_entry.get("adapter_id"),"wrong_adapter_audience"),
      (lease.get("reservation_status") in ("RESERVED","RESERVATION_COMMITTED"),"reservation_not_current"),
      (lease.get("used") is not True,"lease_replay"),
      (lease.get("revoked") is not True,"lease_revoked"),
      (bool(lease.get("expires_at")) and str(lease["expires_at"])>str(now_iso),"lease_expired")]
    for ok,msg in checks:
        if not ok: reason=msg; break
    payload={"lease_id":lease.get("lease_id"),"reservation_id":lease.get("reservation_id"),"adapter_id":registry_entry.get("adapter_id"),"effector_id":registry_entry.get("effector_id"),"executor":executor_instance_id,"capability_instance":capability_instance_id,"capability_id":capability_id,"operation_id":operation_id,"invocation_hash":invocation_request_hash,"scope_hash":effective_execution_scope_hash,"reason":reason}
    h=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return BoundaryAssessment("EXECUTION_NOT_STARTED" if reason is None else "EXECUTION_BLOCKED_AT_FINAL_RECHECK",h)

# P162-G2
from threading import RLock
from dataclasses import dataclass
from hashlib import sha256
import json
@dataclass(frozen=True)
class PointOfEffectSnapshot:
    data: dict
    snapshot_hash: str
@dataclass(frozen=True)
class ExecutionClaim:
    reservation_id:str; lease_id:str; adapter_id:str; executor_instance_id:str; claimed_at:str; state_version:int; claim_hash:str
class ExecutionClaimManager:
    def __init__(self):
        self._lock=RLock(); self._claims={}; self._version=0
    def claim(self,*,lease,registry_entry,executor_instance_id,capability_instance_id,capability_id,operation_id,invocation_request_hash,effective_execution_scope_hash,point_of_effect_state,now_iso):
        b=assess_execution_boundary(lease=lease,registry_entry=registry_entry,executor_instance_id=executor_instance_id,capability_instance_id=capability_instance_id,capability_id=capability_id,operation_id=operation_id,invocation_request_hash=invocation_request_hash,effective_execution_scope_hash=effective_execution_scope_hash,now_iso=now_iso)
        if b.status!="EXECUTION_NOT_STARTED": return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"boundary_binding_failed","claim":None}
        req=("lease_state_version","reservation_state_version","token_state_version","target_state_version","capability_runtime_attestation","adapter_attestation","critical_precondition_snapshot","security_state")
        if any(k not in point_of_effect_state for k in req): return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"snapshot_incomplete","claim":None}
        checks=[(point_of_effect_state.get("revoked") is not True,"last_second_revocation"),(point_of_effect_state.get("target_current") is True,"target_not_current"),(point_of_effect_state.get("critical_preconditions_satisfied") is True,"critical_precondition_failed"),(point_of_effect_state.get("security_state")=="VERIFIED","security_not_verified"),(point_of_effect_state.get("adapter_attestation")==registry_entry.get("adapter_hash"),"adapter_attestation_mismatch"),(point_of_effect_state.get("capability_runtime_attestation") not in (None,"","UNKNOWN","UNDETERMINED"),"capability_attestation_undetermined"),(point_of_effect_state.get("credential_identity_verified") is True,"credential_identity_not_verified")]
        for ok,reason in checks:
            if not ok:return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":reason,"claim":None}
        d={k:point_of_effect_state[k] for k in req};d["checked_at"]=now_iso
        sh=sha256(json.dumps(d,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest(); snap=PointOfEffectSnapshot(d,sh)
        key=(str(lease.get("lease_id")),str(lease.get("reservation_id")))
        with self._lock:
            if key in self._claims:return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"execution_claim_already_exists","claim":self._claims[key],"snapshot":snap}
            self._version+=1
            cp={"reservation_id":key[1],"lease_id":key[0],"adapter_id":str(registry_entry.get("adapter_id")),"executor_instance_id":str(executor_instance_id),"claimed_at":now_iso,"state_version":self._version,"snapshot_hash":sh}
            ch=sha256(json.dumps(cp,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            c=ExecutionClaim(key[1],key[0],cp["adapter_id"],cp["executor_instance_id"],now_iso,self._version,ch);self._claims[key]=c
            return {"status":"EXECUTION_STARTED","reason":None,"claim":c,"snapshot":snap,"scoped_handle_issued":False,"credential_disclosed":False,"effector_called":False,"real_world_effect_performed":False}
