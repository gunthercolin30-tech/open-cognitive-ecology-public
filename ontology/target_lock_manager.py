"""P162-F3 target locks, concurrency slots, dependency reservations. Non-effecting."""
from dataclasses import dataclass
from threading import RLock

LOCK_MODES=("READ_SHARED","WRITE_EXCLUSIVE","DELETE_EXCLUSIVE","CUSTOM")

@dataclass(frozen=True)
class ConcurrencySlotState:
    slot_key:str
    capacity:int
    reserved:int=0
    state_version:int=0

@dataclass(frozen=True)
class DependencyReservationState:
    dependency_key:str
    capacity:int
    reserved:int=0
    state_version:int=0

class TargetConcurrencyDependencyManager:
    """Atomic reference semantics for F3. Canonical acquisition: target -> slot -> dependency."""
    def __init__(self):
        self._lock=RLock()
        self._targets={}
        self._slots={}
        self._deps={}
        self._holds={}
        self._idem={}

    @staticmethod
    def _compatible(existing,new_mode):
        if not existing: return True
        if new_mode=="READ_SHARED":
            return all(x["mode"]=="READ_SHARED" for x in existing)
        return False

    def put_slot(self,s):
        if s.capacity<1 or s.reserved<0 or s.reserved>s.capacity or s.state_version<0: raise ValueError("slot state")
        with self._lock: self._slots[s.slot_key]=s

    def put_dependency(self,s):
        if s.capacity<1 or s.reserved<0 or s.reserved>s.capacity or s.state_version<0: raise ValueError("dependency state")
        with self._lock: self._deps[s.dependency_key]=s

    def reserve(self,*,reservation_id,idempotency_key,target_requests=(),slot_requests=(),dependency_requests=()):
        with self._lock:
            if idempotency_key in self._idem:
                return dict(self._holds[self._idem[idempotency_key]])

            # Validate all dimensions first; mutate none until every check passes.
            target_plan=[]
            for q in sorted(target_requests,key=lambda z:(z["target_key"],z["lock_mode"])):
                mode=q["lock_mode"]
                if mode not in LOCK_MODES: return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                existing=self._targets.get(q["target_key"],[])
                if not self._compatible(existing,mode): return self._fail("TARGET_LOCK_CONFLICT")
                target_plan.append((q["target_key"],mode))

            slot_plan=[]
            for q in sorted(slot_requests,key=lambda z:z["slot_key"]):
                s=self._slots.get(q["slot_key"]); delta=int(q.get("delta",1))
                if s is None or delta<1 or s.state_version!=q["expected_state_version"]:
                    return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                if s.reserved+delta>s.capacity: return self._fail("CONCURRENCY_SLOT_UNAVAILABLE")
                slot_plan.append((s,delta))

            dep_plan=[]
            for q in sorted(dependency_requests,key=lambda z:z["dependency_key"]):
                s=self._deps.get(q["dependency_key"]); delta=int(q.get("delta",1))
                if s is None or delta<1 or s.state_version!=q["expected_state_version"]:
                    return self._fail("RESERVATION_REVALIDATION_REQUIRED")
                if s.reserved+delta>s.capacity: return self._fail("DEPENDENCY_RESERVATION_UNAVAILABLE")
                dep_plan.append((s,delta))

            # Commit in canonical order only after complete validation.
            for key,mode in target_plan:
                self._targets.setdefault(key,[]).append({"reservation_id":reservation_id,"mode":mode})
            for s,d in slot_plan:
                self._slots[s.slot_key]=ConcurrencySlotState(s.slot_key,s.capacity,s.reserved+d,s.state_version+1)
            for s,d in dep_plan:
                self._deps[s.dependency_key]=DependencyReservationState(s.dependency_key,s.capacity,s.reserved+d,s.state_version+1)

            rec={"reservation_id":reservation_id,"status":"RESERVATION_COMMITTED",
                 "target_holds":[{"target_key":k,"lock_mode":m} for k,m in target_plan],
                 "slot_holds":[{"slot_key":s.slot_key,"delta":d} for s,d in slot_plan],
                 "dependency_holds":[{"dependency_key":s.dependency_key,"delta":d} for s,d in dep_plan],
                 "acquisition_order":["TARGET","CONCURRENCY_SLOT","DEPENDENCY"],
                 "authorization_created":False,"capability_accessed":False,
                 "execution_lease_issued":False,"execution_performed":False}
            self._holds[reservation_id]=rec; self._idem[idempotency_key]=reservation_id
            return dict(rec)

    @staticmethod
    def _fail(status):
        return {"status":status,"authorization_created":False,"capability_accessed":False,
                "execution_lease_issued":False,"execution_performed":False}

    def target_holds(self,key):
        with self._lock: return tuple(dict(x) for x in self._targets.get(key,()))
    def slot_state(self,key):
        with self._lock: return self._slots.get(key)
    def dependency_state(self,key):
        with self._lock: return self._deps.get(key)
