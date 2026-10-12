from concurrent.futures import ThreadPoolExecutor
from ontology.target_lock_manager import *

def test_lock_modes_canonical():
 assert set(LOCK_MODES)=={"READ_SHARED","WRITE_EXCLUSIVE","DELETE_EXCLUSIVE","CUSTOM"}

def test_shared_reads_compatible():
 m=TargetConcurrencyDependencyManager()
 assert m.reserve(reservation_id="a",idempotency_key="a",target_requests=[{"target_key":"T","lock_mode":"READ_SHARED"}])["status"]=="RESERVATION_COMMITTED"
 assert m.reserve(reservation_id="b",idempotency_key="b",target_requests=[{"target_key":"T","lock_mode":"READ_SHARED"}])["status"]=="RESERVATION_COMMITTED"

def test_write_conflicts_with_read():
 m=TargetConcurrencyDependencyManager()
 m.reserve(reservation_id="a",idempotency_key="a",target_requests=[{"target_key":"T","lock_mode":"READ_SHARED"}])
 z=m.reserve(reservation_id="b",idempotency_key="b",target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}])
 assert z["status"]=="TARGET_LOCK_CONFLICT" and len(m.target_holds("T"))==1

def test_concurrent_writes_at_most_one():
 m=TargetConcurrencyDependencyManager()
 def f(i): return m.reserve(reservation_id=f"r{i}",idempotency_key=f"k{i}",target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}])
 with ThreadPoolExecutor(max_workers=12) as x: out=list(x.map(f,range(40)))
 assert sum(z["status"]=="RESERVATION_COMMITTED" for z in out)==1 and len(m.target_holds("T"))==1

def test_slot_same_snapshot_only_one_commit():
 m=TargetConcurrencyDependencyManager();m.put_slot(ConcurrencySlotState("S",4))
 def f(i): return m.reserve(reservation_id=f"r{i}",idempotency_key=f"k{i}",slot_requests=[{"slot_key":"S","delta":1,"expected_state_version":0}])
 with ThreadPoolExecutor(max_workers=8) as x: out=list(x.map(f,range(20)))
 assert sum(z["status"]=="RESERVATION_COMMITTED" for z in out)==1
 assert m.slot_state("S").reserved==1

def test_revalidated_slot_fills_capacity():
 m=TargetConcurrencyDependencyManager();m.put_slot(ConcurrencySlotState("S",3))
 for i in range(3):
  s=m.slot_state("S")
  assert m.reserve(reservation_id=f"r{i}",idempotency_key=f"k{i}",slot_requests=[{"slot_key":"S","delta":1,"expected_state_version":s.state_version}])["status"]=="RESERVATION_COMMITTED"
 s=m.slot_state("S")
 assert m.reserve(reservation_id="r4",idempotency_key="k4",slot_requests=[{"slot_key":"S","delta":1,"expected_state_version":s.state_version}])["status"]=="CONCURRENCY_SLOT_UNAVAILABLE"

def test_dependency_failure_leaves_no_target_or_slot_hold():
 m=TargetConcurrencyDependencyManager();m.put_slot(ConcurrencySlotState("S",1));m.put_dependency(DependencyReservationState("D",1,reserved=1))
 z=m.reserve(reservation_id="r",idempotency_key="k",
  target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}],
  slot_requests=[{"slot_key":"S","delta":1,"expected_state_version":0}],
  dependency_requests=[{"dependency_key":"D","delta":1,"expected_state_version":0}])
 assert z["status"]=="DEPENDENCY_RESERVATION_UNAVAILABLE"
 assert m.target_holds("T")==() and m.slot_state("S").reserved==0

def test_stale_dependency_leaves_no_earlier_hold():
 m=TargetConcurrencyDependencyManager();m.put_slot(ConcurrencySlotState("S",1));m.put_dependency(DependencyReservationState("D",1))
 z=m.reserve(reservation_id="r",idempotency_key="k",
  target_requests=[{"target_key":"T","lock_mode":"DELETE_EXCLUSIVE"}],
  slot_requests=[{"slot_key":"S","delta":1,"expected_state_version":0}],
  dependency_requests=[{"dependency_key":"D","delta":1,"expected_state_version":9}])
 assert z["status"]=="RESERVATION_REVALIDATION_REQUIRED"
 assert m.target_holds("T")==() and m.slot_state("S").reserved==0 and m.dependency_state("D").reserved==0

def test_canonical_acquisition_order_recorded():
 m=TargetConcurrencyDependencyManager();m.put_slot(ConcurrencySlotState("S",1));m.put_dependency(DependencyReservationState("D",1))
 z=m.reserve(reservation_id="r",idempotency_key="k",
  target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}],
  slot_requests=[{"slot_key":"S","delta":1,"expected_state_version":0}],
  dependency_requests=[{"dependency_key":"D","delta":1,"expected_state_version":0}])
 assert z["acquisition_order"]==["TARGET","CONCURRENCY_SLOT","DEPENDENCY"]

def test_retry_idempotent_no_duplicate_holds():
 m=TargetConcurrencyDependencyManager()
 a=m.reserve(reservation_id="r",idempotency_key="k",target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}])
 b=m.reserve(reservation_id="other",idempotency_key="k",target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}])
 assert a==b and len(m.target_holds("T"))==1

def test_non_effecting_boundary():
 m=TargetConcurrencyDependencyManager()
 z=m.reserve(reservation_id="r",idempotency_key="k")
 assert z["authorization_created"] is False and z["capability_accessed"] is False
 assert z["execution_lease_issued"] is False and z["execution_performed"] is False
 assert not hasattr(m,"execute") and not hasattr(m,"dispatch")
