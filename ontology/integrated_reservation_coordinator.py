"""P162-F6 integrated local compare-and-reserve transaction. Non-effecting."""
from hashlib import sha256
import json
from ontology.execution_reservation_manager import AuthorizationUseState
from ontology.budget_reservation_manager import SharedBudgetState,TechnicalResourceState
from ontology.target_lock_manager import ConcurrencySlotState,DependencyReservationState

def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return sha256(_canon(x).encode()).hexdigest()

class IntegratedReservationCoordinator:
    """Local-runtime atomic coordinator. Never claims distributed atomicity."""
    ATOMICITY_SCOPE="SINGLE_PROCESS_SHARED_MEMORY"
    def __init__(self,use_manager,budget_manager,target_manager,journal=None):
        self.u=use_manager; self.b=budget_manager; self.t=target_manager; self.journal=journal
        self._idem={}

    def reserve(self,*,transaction_id,idempotency_key,invocation_request_id,token_id,
                effective_scope_hash,executor_id,capability_id,operation_id,target_binding,
                expected_token_version,use_count=1,budget_requests=(),resource_requests=(),
                target_requests=(),slot_requests=(),dependency_requests=(),
                requested_atomicity_scope="SINGLE_PROCESS_SHARED_MEMORY"):
        if requested_atomicity_scope != self.ATOMICITY_SCOPE:
            return self._fail("RESERVATION_ATOMICITY_UNAVAILABLE")
        # Fixed global lock order prevents coordinator deadlock.
        with self.u._lock:
          with self.b._lock:
            with self.t._lock:
              if idempotency_key in self._idem: return dict(self._idem[idempotency_key])
              # ----- validate every dimension; mutate nothing -----
              st=self.u._states.get(token_id)
              if (st is None or st.revoked or st.expired or st.indeterminate or
                  st.state_version!=expected_token_version):
                  return self._fail("RESERVATION_REVALIDATION_REQUIRED")
              if use_count<1 or st.committed_uses+st.reserved_uses+use_count>st.max_uses:
                  return self._fail("RESERVATION_BUDGET_INSUFFICIENT")

              bp=[]; rp=[]
              for q in budget_requests:
                  key=(q["budget_id"],q["scope"],q["scope_key"]); s=self.b._budgets.get(key); d=float(q["delta"])
                  if s is None or d<0 or s.state_version!=q["expected_state_version"]:
                      return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                  if s.committed+s.reserved+d>s.max_authorized:
                      return self._fail("RESERVATION_BUDGET_INSUFFICIENT")
                  bp.append((key,s,d))
              for q in resource_requests:
                  s=self.b._resources.get(q["resource_id"]); d=float(q["delta"])
                  if s is None or d<0 or s.state_version!=q["expected_state_version"]:
                      return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                  if s.committed+s.reserved+d>s.capacity:
                      return self._fail("RESOURCE_SCOPE_INSUFFICIENT")
                  rp.append((s,d))

              tp=[]
              for q in sorted(target_requests,key=lambda z:(z["target_key"],z["lock_mode"])):
                  mode=q["lock_mode"]; existing=self.t._targets.get(q["target_key"],[])
                  if mode not in ("READ_SHARED","WRITE_EXCLUSIVE","DELETE_EXCLUSIVE","CUSTOM") or not self.t._compatible(existing,mode):
                      return self._fail("TARGET_LOCK_CONFLICT")
                  tp.append((q["target_key"],mode))
              sp=[]
              for q in sorted(slot_requests,key=lambda z:z["slot_key"]):
                  s=self.t._slots.get(q["slot_key"]); d=int(q.get("delta",1))
                  if s is None or d<1 or s.state_version!=q["expected_state_version"]:
                      return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                  if s.reserved+d>s.capacity: return self._fail("CONCURRENCY_SLOT_UNAVAILABLE")
                  sp.append((s,d))
              dp=[]
              for q in sorted(dependency_requests,key=lambda z:z["dependency_key"]):
                  s=self.t._deps.get(q["dependency_key"]); d=int(q.get("delta",1))
                  if s is None or d<1 or s.state_version!=q["expected_state_version"]:
                      return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                  if s.reserved+d>s.capacity: return self._fail("DEPENDENCY_RESERVATION_UNAVAILABLE")
                  dp.append((s,d))

              rid="res_"+_hash({"transaction":transaction_id,"key":idempotency_key,"invocation":invocation_request_id})[:32]
              # ----- commit all dimensions while every manager lock remains held -----
              self.u._states[token_id]=AuthorizationUseState(st.token_id,st.max_uses,st.committed_uses,
                  st.reserved_uses+use_count,st.state_version+1,st.revoked,st.expired,st.indeterminate)
              for key,s,d in bp:
                  self.b._budgets[key]=SharedBudgetState(s.budget_id,s.scope,s.scope_key,s.max_authorized,s.committed,s.reserved+d,s.state_version+1)
              for s,d in rp:
                  self.b._resources[s.resource_id]=TechnicalResourceState(s.resource_id,s.capacity,s.committed,s.reserved+d,s.state_version+1)
              for key,mode in tp: self.t._targets.setdefault(key,[]).append({"reservation_id":rid,"mode":mode})
              for s,d in sp: self.t._slots[s.slot_key]=ConcurrencySlotState(s.slot_key,s.capacity,s.reserved+d,s.state_version+1)
              for s,d in dp: self.t._deps[s.dependency_key]=DependencyReservationState(s.dependency_key,s.capacity,s.reserved+d,s.state_version+1)

              rec={"transaction_id":transaction_id,"reservation_id":rid,"status":"RESERVATION_COMMITTED",
                   "atomicity_scope":self.ATOMICITY_SCOPE,"invocation_request_id":invocation_request_id,
                   "authorization_token_id":token_id,"effective_execution_scope_hash":effective_scope_hash,
                   "executor_id":executor_id,"capability_id":capability_id,"operation_id":operation_id,
                   "target_binding":target_binding,"reserved_use_count":use_count,
                   "budget_holds":[{"key":list(k),"delta":d} for k,_,d in bp],
                   "resource_holds":[{"resource_id":s.resource_id,"delta":d} for s,d in rp],
                   "target_holds":[{"target_key":k,"lock_mode":m} for k,m in tp],
                   "slot_holds":[{"slot_key":s.slot_key,"delta":d} for s,d in sp],
                   "dependency_holds":[{"dependency_key":s.dependency_key,"delta":d} for s,d in dp],
                   "lease_issued":False,"authorization_created":False,"capability_accessed":False,
                   "execution_performed":False,"p162g_opened":False}
              rec["reservation_hash"]=_hash(rec)
              self._idem[idempotency_key]=rec
              if self.journal is not None:
                  self.journal.append({"type":"RESERVATION_COMMITTED","reservation_id":rid,
                                       "transaction_id":transaction_id,"reservation_hash":rec["reservation_hash"]})
              return dict(rec)

    @staticmethod
    def _fail(status):
        return {"status":status,"authorization_created":False,"capability_accessed":False,
                "execution_performed":False,"lease_issued":False,"p162g_opened":False}
