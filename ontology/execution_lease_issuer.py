"""P162-F4 bounded ExecutionLease issuer. Non-effecting; P162-G remains closed."""
from hashlib import sha256
from threading import RLock
from datetime import datetime, timezone
import json

def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return sha256(_canon(x).encode()).hexdigest()
def _ts(x):
    if isinstance(x,datetime): d=x
    else: d=datetime.fromisoformat(str(x).replace("Z","+00:00"))
    if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)

class ExecutionLeaseIssuer:
    """Issues bounded ephemeral artifacts; never executes or accesses a capability."""
    def __init__(self):
        self._lock=RLock(); self._by_key={}; self._leases={}; self._used_nonces=set()

    def issue(self,*,idempotency_key,reservation,invocation_request_hash,capability_instance_id,
              audience,issued_at,requested_expires_at,token_expires_at,reservation_expires_at):
        with self._lock:
            if idempotency_key in self._by_key:
                return dict(self._leases[self._by_key[idempotency_key]])
            if reservation.get("status") not in ("RESERVED","RESERVATION_COMMITTED"):
                return self._fail("LEASE_RESERVATION_NOT_CURRENT")
            required=("reservation_id","effective_execution_scope_hash","executor_id","operation_id","target_binding")
            if any(k not in reservation for k in required):
                return self._fail("LEASE_BINDING_INCOMPLETE")
            if not audience or not capability_instance_id:
                return self._fail("LEASE_BINDING_INCOMPLETE")
            now=_ts(issued_at); req=_ts(requested_expires_at); tok=_ts(token_expires_at); res=_ts(reservation_expires_at)
            expiry=min(req,tok,res)
            if expiry<=now: return self._fail("LEASE_EXPIRED_OR_EMPTY")
            basis={"reservation_id":reservation["reservation_id"],"invocation_request_hash":invocation_request_hash,
                   "effective_execution_scope_hash":reservation["effective_execution_scope_hash"],
                   "executor_id":reservation["executor_id"],"capability_instance_id":capability_instance_id,
                   "operation_id":reservation["operation_id"],"target_binding":reservation["target_binding"],
                   "issued_at":now.isoformat(),"expires_at":expiry.isoformat(),"audience":audience}
            nonce="ln_"+_hash({"key":idempotency_key,"basis":basis})[:32]
            lease_id="lease_"+_hash({"nonce":nonce,"reservation":reservation["reservation_id"]})[:32]
            lease={**basis,"lease_id":lease_id,"lease_nonce":nonce,
                   "use_policy":{"single_use":True,"point_of_effect_recheck_required":True},
                   "transferable":False,"capability_accessed":False,"effect_performed":False,
                   "p162g_opened":False}
            lease["lease_hash"]=_hash(lease)
            self._leases[lease_id]=lease; self._by_key[idempotency_key]=lease_id
            return dict(lease)

    def validate_for_handoff(self,lease,*,audience,executor_id,capability_instance_id,operation_id,target_binding,now):
        """F-only handoff validation; does not authorize or perform a governed effect."""
        if lease.get("lease_id") not in self._leases: return "LEASE_UNKNOWN"
        if lease.get("transferable") is not False: return "LEASE_TRANSFER_FORBIDDEN"
        if _ts(now)>=_ts(lease["expires_at"]): return "LEASE_EXPIRED"
        checks=((lease["audience"],audience),(lease["executor_id"],executor_id),
                (lease["capability_instance_id"],capability_instance_id),(lease["operation_id"],operation_id),
                (lease["target_binding"],target_binding))
        if any(a!=b for a,b in checks): return "LEASE_BINDING_MISMATCH"
        if lease["lease_nonce"] in self._used_nonces: return "LEASE_REPLAY"
        return "LEASE_CURRENT_FOR_HANDOFF"

    def mark_handoff_once(self,lease_id):
        """Consumes F-side handoff nonce only; still no capability access/effect."""
        with self._lock:
            lease=self._leases.get(lease_id)
            if lease is None: return False
            n=lease["lease_nonce"]
            if n in self._used_nonces: return False
            self._used_nonces.add(n); return True

    @staticmethod
    def _fail(status):
        return {"status":status,"authorization_created":False,"capability_accessed":False,
                "effect_performed":False,"p162g_opened":False}
