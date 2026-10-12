"""P162-F2 shared normative budget and technical resource reservation."""
from dataclasses import dataclass
from threading import RLock
BUDGET_SCOPES=("PER_TOKEN","PER_EXECUTOR","PER_TARGET","PER_CAPABILITY","PER_PURPOSE","PER_GROUP","PER_CIVILIZATION")
@dataclass(frozen=True)
class SharedBudgetState:
    budget_id:str; scope:str; scope_key:str; max_authorized:float
    committed:float=0.0; reserved:float=0.0; state_version:int=0
@dataclass(frozen=True)
class TechnicalResourceState:
    resource_id:str; capacity:float; committed:float=0.0; reserved:float=0.0; state_version:int=0
class BudgetResourceReservationManager:
    def __init__(self):
        self._lock=RLock(); self._budgets={}; self._resources={}; self._holds={}; self._idem={}
    def put_budget(self,s):
        if s.scope not in BUDGET_SCOPES or min(s.max_authorized,s.committed,s.reserved,s.state_version)<0: raise ValueError("budget state")
        if s.committed+s.reserved>s.max_authorized: raise ValueError("budget overcommitted")
        with self._lock: self._budgets[(s.budget_id,s.scope,s.scope_key)]=s
    def put_resource(self,s):
        if min(s.capacity,s.committed,s.reserved,s.state_version)<0: raise ValueError("resource state")
        if s.committed+s.reserved>s.capacity: raise ValueError("resource overcommitted")
        with self._lock: self._resources[s.resource_id]=s
    def reserve(self,*,reservation_id,idempotency_key,budget_requests=(),resource_requests=()):
        with self._lock:
            if idempotency_key in self._idem: return dict(self._holds[self._idem[idempotency_key]])
            bn=[]; rn=[]
            for q in budget_requests:
                key=(q["budget_id"],q["scope"],q["scope_key"]); s=self._budgets.get(key); d=float(q["delta"])
                if s is None or d<0 or s.state_version!=q["expected_state_version"]: return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                if s.committed+s.reserved+d>s.max_authorized: return self._fail("RESERVATION_BUDGET_INSUFFICIENT")
                bn.append((key,SharedBudgetState(s.budget_id,s.scope,s.scope_key,s.max_authorized,s.committed,s.reserved+d,s.state_version+1),d))
            for q in resource_requests:
                s=self._resources.get(q["resource_id"]); d=float(q["delta"])
                if s is None or d<0 or s.state_version!=q["expected_state_version"]: return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                if s.committed+s.reserved+d>s.capacity: return self._fail("RESOURCE_SCOPE_INSUFFICIENT")
                rn.append((s.resource_id,TechnicalResourceState(s.resource_id,s.capacity,s.committed,s.reserved+d,s.state_version+1),d))
            for k,n,_ in bn: self._budgets[k]=n
            for k,n,_ in rn: self._resources[k]=n
            rec={"reservation_id":reservation_id,"status":"RESERVATION_COMMITTED","budget_holds":[{"key":list(k),"delta":d} for k,_,d in bn],"resource_holds":[{"resource_id":k,"delta":d} for k,_,d in rn],"authorization_created":False,"capability_accessed":False,"execution_performed":False}
            self._holds[reservation_id]=rec; self._idem[idempotency_key]=reservation_id; return dict(rec)
    @staticmethod
    def _fail(status): return {"status":status,"authorization_created":False,"capability_accessed":False,"execution_performed":False}
    def budget_state(self,budget_id,scope,scope_key):
        with self._lock: return self._budgets.get((budget_id,scope,scope_key))
    def resource_state(self,resource_id):
        with self._lock: return self._resources.get(resource_id)
