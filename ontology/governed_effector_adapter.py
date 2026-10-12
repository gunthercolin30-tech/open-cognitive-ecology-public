"""P162-G5 Governed Effector Mediation.

Reference causal boundary. No ambient filesystem/network/subprocess/database primitive
is imported here. A concrete effector must be explicitly injected and registered.
"""
from dataclasses import dataclass
from threading import RLock
from hashlib import sha256
import json

@dataclass(frozen=True)
class EffectAttemptRecord:
    attempt_id:str
    lease_id:str
    reservation_id:str
    claim_hash:str
    handle_id:str
    broker_use_id:str
    adapter_id:str
    effector_id:str
    operation_id:str
    target_binding:object
    status:str
    started_at:str
    idempotency_key:str
    attempt_hash:str

@dataclass(frozen=True)
class ExecutionReceipt:
    execution_id:str
    reservation_id:str
    lease_id:str
    adapter_id:str
    adapter_version:str
    capability_id:str
    capability_version:str
    operation:str
    effective_target:object
    effect_class:str
    effect_status:str
    uncertainty:bool
    idempotency_reference:str
    external_receipts:object
    resource_usage:object
    receipt_hash:str

class GovernedEffectorAdapter:
    """Only mediated entry point for an explicitly injected effector."""
    def __init__(self, *, adapter_id, adapter_version, adapter_hash, effector_id,
                 effector_callable, allowed_effect_classes):
        if not callable(effector_callable): raise TypeError("effector_callable_required")
        self.adapter_id=adapter_id; self.adapter_version=adapter_version
        self.adapter_hash=adapter_hash; self.effector_id=effector_id
        self._effector=effector_callable
        self.allowed_effect_classes=frozenset(allowed_effect_classes)
        self._lock=RLock(); self._attempted=set()

    def execute(self, *, claim, handle, brokered_use, registry_entry,
                capability_id, capability_version, effect_class,
                final_state, idempotency_key, now_iso):
        # Binding chain G2 -> G3 -> G4 -> registered adapter/effector.
        if claim is None or handle is None or brokered_use is None:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"incomplete_mediation_chain","receipt":None}
        checks=[
          (claim.adapter_id==self.adapter_id,"claim_adapter_mismatch"),
          (handle.claim_hash==claim.claim_hash,"handle_claim_mismatch"),
          (handle.adapter_id==self.adapter_id,"handle_adapter_mismatch"),
          (handle.effector_id==self.effector_id,"handle_effector_mismatch"),
          (brokered_use.handle_id==handle.handle_id,"credential_handle_mismatch"),
          (brokered_use.adapter_id==self.adapter_id,"credential_adapter_mismatch"),
          (brokered_use.effector_id==self.effector_id,"credential_effector_mismatch"),
          (brokered_use.allowed_operation==handle.operation_id,"credential_operation_mismatch"),
          (brokered_use.target_binding==handle.target_binding,"credential_target_mismatch"),
          (registry_entry.get("status")=="ACTIVE","adapter_not_active"),
          (registry_entry.get("adapter_id")==self.adapter_id,"registry_adapter_mismatch"),
          (registry_entry.get("adapter_hash")==self.adapter_hash,"adapter_identity_drift"),
          (registry_entry.get("effector_id")==self.effector_id,"registry_effector_mismatch"),
          (effect_class in self.allowed_effect_classes,"effect_class_not_allowed"),
          (final_state.get("lease_current") is True,"lease_not_current"),
          (final_state.get("reservation_current") is True,"reservation_not_current"),
          (final_state.get("revoked") is not True,"last_second_revocation"),
          (final_state.get("target_current") is True,"target_not_current"),
          (final_state.get("critical_preconditions_satisfied") is True,"critical_precondition_failed"),
          (final_state.get("security_state")=="VERIFIED","security_not_verified"),
          (final_state.get("adapter_attestation")==self.adapter_hash,"adapter_attestation_mismatch"),
        ]
        for ok,reason in checks:
            if not ok:return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":reason,"receipt":None}
        if not idempotency_key:
            return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"idempotency_key_required","receipt":None}
        attempt_key=(claim.lease_id,claim.reservation_id,idempotency_key)
        with self._lock:
            if attempt_key in self._attempted:
                return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"effect_attempt_replay","receipt":None}
            self._attempted.add(attempt_key)
        payload={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"claim_hash":claim.claim_hash,
                 "handle_id":handle.handle_id,"broker_use_id":brokered_use.broker_use_id,
                 "adapter_id":self.adapter_id,"effector_id":self.effector_id,"operation_id":handle.operation_id,
                 "target_binding":handle.target_binding,"started_at":now_iso,"idempotency_key":idempotency_key}
        ah=sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        attempt=EffectAttemptRecord(attempt_id=ah,attempt_hash=ah,status="EXECUTION_STARTED",**payload)
        try:
            outcome=self._effector(operation=handle.operation_id,target=handle.target_binding,
                                   credential_ref=brokered_use.credential_ref,
                                   idempotency_key=idempotency_key)
        except TimeoutError:
            return {"status":"EFFECT_STATE_INDETERMINATE","reason":"timeout_after_possible_dispatch",
                    "attempt":attempt,"receipt":None,"blind_retry_allowed":False}
        except Exception as exc:
            # Exception does not prove that a non-idempotent external effect did not occur.
            return {"status":"EFFECT_STATE_INDETERMINATE","reason":"effector_exception",
                    "attempt":attempt,"receipt":None,"blind_retry_allowed":False,
                    "exception_type":type(exc).__name__}
        if not isinstance(outcome,dict) or outcome.get("effect_status") not in {
            "EFFECT_CONFIRMED","EFFECT_PARTIAL","EFFECT_FAILED_CONFIRMED","EFFECT_NOT_REACHED"}:
            return {"status":"EFFECT_STATE_INDETERMINATE","reason":"unverifiable_effector_outcome",
                    "attempt":attempt,"receipt":None,"blind_retry_allowed":False}
        status=outcome["effect_status"]; uncertainty=False
        rp={"execution_id":ah,"reservation_id":claim.reservation_id,"lease_id":claim.lease_id,
            "adapter_id":self.adapter_id,"adapter_version":self.adapter_version,
            "capability_id":capability_id,"capability_version":capability_version,
            "operation":handle.operation_id,"effective_target":handle.target_binding,
            "effect_class":effect_class,"effect_status":status,"uncertainty":uncertainty,
            "idempotency_reference":idempotency_key,"external_receipts":outcome.get("external_receipts",[]),
            "resource_usage":outcome.get("resource_usage",{})}
        rh=sha256(json.dumps(rp,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        receipt=ExecutionReceipt(receipt_hash=rh,**rp)
        return {"status":status,"reason":None,"attempt":attempt,"receipt":receipt,
                "blind_retry_allowed": status in {"EFFECT_FAILED_CONFIRMED","EFFECT_NOT_REACHED"}}
