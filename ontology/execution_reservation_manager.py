"""P162-F atomic reservation foundation. Non-effecting."""
from dataclasses import dataclass
from threading import RLock
from hashlib import sha256
import json
STATUSES=("PREPARED","COMMITTING","RESERVED","EXECUTION_STARTED","EXECUTION_CONFIRMED","COMMITTED","RELEASED","ABORTED","EXPIRED","INDETERMINATE","INVALIDATED","RESERVATION_COMMITTED","RESERVATION_REVALIDATION_REQUIRED","RESERVATION_BUDGET_INSUFFICIENT","RESERVATION_ATOMICITY_UNAVAILABLE","RESERVATION_UNDETERMINED")
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return sha256(_canon(x).encode()).hexdigest()
@dataclass(frozen=True)
class AuthorizationUseState:
    token_id:str; max_uses:int; committed_uses:int=0; reserved_uses:int=0; state_version:int=0
    revoked:bool=False; expired:bool=False; indeterminate:bool=False
class AtomicReservationManager:
    """F1 reference semantics: reserve authorization use; never execute capability."""
    def __init__(self):
        self._lock=RLock(); self._states={}; self._reservations={}; self._idempotency={}
    def put_authorization_state(self,state):
        if state.max_uses<1 or min(state.committed_uses,state.reserved_uses,state.state_version)<0: raise ValueError("invalid state")
        if state.committed_uses+state.reserved_uses>state.max_uses: raise ValueError("overcommitted state")
        with self._lock: self._states[state.token_id]=state
    def reserve(self,*,idempotency_key,invocation_request_id,token_id,effective_scope_hash,executor_id,capability_id,operation_id,target_binding,expected_state_version,use_count=1):
        if use_count<1: raise ValueError("use_count")
        with self._lock:
            if idempotency_key in self._idempotency: return dict(self._reservations[self._idempotency[idempotency_key]])
            st=self._states.get(token_id)
            fail={"status":"RESERVATION_REVALIDATION_REQUIRED","authorization_created":False,"capability_accessed":False,"execution_performed":False}
            if st is None or st.revoked or st.expired or st.indeterminate or st.state_version!=expected_state_version: return fail
            if st.committed_uses+st.reserved_uses+use_count>st.max_uses:
                return {"status":"RESERVATION_BUDGET_INSUFFICIENT","authorization_created":False,"capability_accessed":False,"execution_performed":False}
            rid="res_"+_hash({"key":idempotency_key,"invocation":invocation_request_id,"token":token_id,"scope":effective_scope_hash,"executor":executor_id,"capability":capability_id,"operation":operation_id,"target":target_binding})[:32]
            nxt=AuthorizationUseState(st.token_id,st.max_uses,st.committed_uses,st.reserved_uses+use_count,st.state_version+1,st.revoked,st.expired,st.indeterminate)
            rec={"reservation_id":rid,"invocation_request_id":invocation_request_id,"authorization_token_id":token_id,"effective_execution_scope_hash":effective_scope_hash,"executor_id":executor_id,"capability_id":capability_id,"operation_id":operation_id,"target_binding":target_binding,"reserved_use_count":use_count,"state_version_before":st.state_version,"state_version_after":nxt.state_version,"status":"RESERVED","authorization_created":False,"capability_accessed":False,"execution_performed":False}
            rec["reservation_hash"]=_hash(rec); self._states[token_id]=nxt; self._reservations[rid]=rec; self._idempotency[idempotency_key]=rid
            return dict(rec)
    def rollback_reserved_use(self,token_id,use_count,expected_state_version):
        with self._lock:
            st=self._states.get(token_id)
            if st is None or st.state_version!=expected_state_version or use_count<1 or st.reserved_uses<use_count: return False
            self._states[token_id]=AuthorizationUseState(st.token_id,st.max_uses,st.committed_uses,st.reserved_uses-use_count,st.state_version+1,st.revoked,st.expired,st.indeterminate)
            return True

    def state(self,token_id):
        with self._lock: return self._states.get(token_id)
