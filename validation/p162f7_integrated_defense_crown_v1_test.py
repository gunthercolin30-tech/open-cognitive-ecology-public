"""P162-F7 integrated defense crown: F-01..F-20 and ROOT-F1..ROOT-F10."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
from ontology.execution_reservation_manager import AtomicReservationManager,AuthorizationUseState
from ontology.budget_reservation_manager import BudgetResourceReservationManager,SharedBudgetState,TechnicalResourceState
from ontology.target_lock_manager import TargetConcurrencyDependencyManager,ConcurrencySlotState,DependencyReservationState
from ontology.integrated_reservation_coordinator import IntegratedReservationCoordinator
from ontology.execution_lease_issuer import ExecutionLeaseIssuer
from ontology.reservation_recovery_manager import ReservationRecoveryJournal

NOW=datetime(2030,1,1,tzinfo=timezone.utc)
H="a"*64

def env(tmp_path=None,max_uses=2,budget=10,slot=1,dep=1):
 u=AtomicReservationManager();u.put_authorization_state(AuthorizationUseState("tok",max_uses))
 b=BudgetResourceReservationManager();b.put_budget(SharedBudgetState("money","PER_CIVILIZATION","civil",budget));b.put_resource(TechnicalResourceState("cpu",2))
 t=TargetConcurrencyDependencyManager();t.put_slot(ConcurrencySlotState("slot",slot));t.put_dependency(DependencyReservationState("dep",dep))
 j=ReservationRecoveryJournal(tmp_path/"j") if tmp_path else None
 return u,b,t,IntegratedReservationCoordinator(u,b,t,j)

def reserve(c,key="k",tx="tx",ver=0,use=1,bdelta=1,target=True,slot=True,dep=True,atomicity="SINGLE_PROCESS_SHARED_MEMORY"):
 return c.reserve(transaction_id=tx,idempotency_key=key,invocation_request_id="inv-"+key,token_id="tok",
  effective_scope_hash=H,executor_id="e",capability_id="c",operation_id="op",target_binding={"id":"T"},
  expected_token_version=ver,use_count=use,
  budget_requests=[{"budget_id":"money","scope":"PER_CIVILIZATION","scope_key":"civil","delta":bdelta,"expected_state_version":ver}] if bdelta else [],
  resource_requests=[],target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}] if target else [],
  slot_requests=[{"slot_key":"slot","delta":1,"expected_state_version":ver}] if slot else [],
  dependency_requests=[{"dependency_key":"dep","delta":1,"expected_state_version":ver}] if dep else [],
  requested_atomicity_scope=atomicity)

def lease_res(r):
 return {"reservation_id":r["reservation_id"],"status":"RESERVATION_COMMITTED",
  "effective_execution_scope_hash":r["effective_execution_scope_hash"],"executor_id":r["executor_id"],
  "operation_id":r["operation_id"],"target_binding":r["target_binding"]}

# F-01 / ROOT-F1: double reserve single-use
def test_F01_ROOTF1_double_reserve_single_use():
 u,b,t,c=env(max_uses=1,slot=2,dep=2)
 def go(i): return reserve(c,key=f"k{i}",tx=f"t{i}",target=False,slot=False,dep=False)
 with ThreadPoolExecutor(max_workers=16) as ex: rs=list(ex.map(go,range(32)))
 assert sum(r["status"]=="RESERVATION_COMMITTED" for r in rs)==1 and u.state("tok").reserved_uses==1

# F-02 / ROOT-F3: bounded-use oversubscription
def test_F02_ROOTF3_multi_use_oversubscription():
 u,b,t,c=env(max_uses=3,slot=4,dep=4)
 rs=[reserve(c,key=f"k{i}",tx=f"t{i}",ver=i,target=False,slot=False,dep=False,bdelta=0) for i in range(5)]
 assert sum(r["status"]=="RESERVATION_COMMITTED" for r in rs)==3 and u.state("tok").reserved_uses==3

# F-03 / ROOT-F2: civilization budget cannot double spend
def test_F03_ROOTF2_budget_double_spend():
 u,b,t,c=env(max_uses=10,budget=2,slot=10,dep=10)
 rs=[reserve(c,key=f"k{i}",tx=f"t{i}",ver=i,target=False,slot=False,dep=False,bdelta=1) for i in range(4)]
 assert sum(r["status"]=="RESERVATION_COMMITTED" for r in rs)==2
 assert b.budget_state("money","PER_CIVILIZATION","civil").reserved==2

# F-04: pending reservations count against authorization
def test_F04_pending_reservation_not_ignored():
 u,b,t,c=env(max_uses=1);assert reserve(c,target=False,slot=False,dep=False,bdelta=0)["status"]=="RESERVATION_COMMITTED"
 assert reserve(c,key="k2",tx="t2",ver=1,target=False,slot=False,dep=False,bdelta=0)["status"]=="RESERVATION_BUDGET_INSUFFICIENT"

# F-05: target race
def test_F05_target_lock_race():
 u,b,t,c=env(max_uses=10,slot=10,dep=10)
 def go(i): return reserve(c,key=f"k{i}",tx=f"t{i}",target=True,slot=False,dep=False,bdelta=0)
 with ThreadPoolExecutor(max_workers=12) as ex: rs=list(ex.map(go,range(12)))
 assert sum(r["status"]=="RESERVATION_COMMITTED" for r in rs)==1 and len(t.target_holds("T"))==1

# F-06: concurrency slot race
def test_F06_concurrency_slot_race():
 u,b,t,c=env(max_uses=10,slot=1,dep=10)
 def go(i): return reserve(c,key=f"k{i}",tx=f"t{i}",target=False,slot=True,dep=False,bdelta=0)
 with ThreadPoolExecutor(max_workers=12) as ex: rs=list(ex.map(go,range(12)))
 assert sum(r["status"]=="RESERVATION_COMMITTED" for r in rs)==1 and t.slot_state("slot").reserved==1

# F-07: revocation before commit
def test_F07_revocation_between_C_and_F():
 u,b,t,c=env();s=u.state("tok");u.put_authorization_state(AuthorizationUseState("tok",s.max_uses,s.committed_uses,s.reserved_uses,s.state_version,True,False,False))
 assert reserve(c,target=False,slot=False,dep=False)["status"]=="RESERVATION_REVALIDATION_REQUIRED"

# F-08 / ROOT-F4: stale state
def test_F08_ROOTF4_stale_state_commit_blocked():
 u,b,t,c=env();assert reserve(c,target=False,slot=False,dep=False)["status"]=="RESERVATION_COMMITTED"
 assert reserve(c,key="k2",tx="t2",ver=0,target=False,slot=False,dep=False)["status"]=="RESERVATION_REVALIDATION_REQUIRED"

# F-09: crash/restart journal preserves reservation
def test_F09_crash_after_commit_recovery(tmp_path):
 u,b,t,c=env(tmp_path);r=reserve(c,target=False,slot=False,dep=False,bdelta=0)
 rr=ReservationRecoveryJournal(tmp_path/"j").reconstruct(r["reservation_id"])
 assert rr["state"]=="RESERVED" and rr["assessment"]=="INDETERMINATE"

# F-10 / ROOT-F5: retry same idempotency key
def test_F10_ROOTF5_retry_no_second_reservation():
 u,b,t,c=env();a=reserve(c,target=False,slot=False,dep=False);z=reserve(c,target=False,slot=False,dep=False)
 assert a==z and u.state("tok").reserved_uses==1

# F-11 / ROOT-F10: lease replay
def test_F11_ROOTF10_lease_replay():
 u,b,t,c=env();r=reserve(c,target=False,slot=False,dep=False,bdelta=0)
 i=ExecutionLeaseIssuer();z=i.issue(idempotency_key="lease",reservation=lease_res(r),invocation_request_hash="b"*64,
 capability_instance_id="ci",audience="p162-g",issued_at=NOW,requested_expires_at=NOW+timedelta(seconds=10),
 token_expires_at=NOW+timedelta(seconds=10),reservation_expires_at=NOW+timedelta(seconds=10))
 args=dict(audience="p162-g",executor_id="e",capability_instance_id="ci",operation_id="op",target_binding={"id":"T"},now=NOW)
 assert i.validate_for_handoff(z,**args)=="LEASE_CURRENT_FOR_HANDOFF";assert i.mark_handoff_once(z["lease_id"])
 assert i.validate_for_handoff(z,**args)=="LEASE_REPLAY"

# F-12: fork/audience transfer
def test_F12_forked_or_transferred_lease_rejected():
 u,b,t,c=env();r=reserve(c,target=False,slot=False,dep=False,bdelta=0);i=ExecutionLeaseIssuer()
 z=i.issue(idempotency_key="lease",reservation=lease_res(r),invocation_request_hash="b"*64,capability_instance_id="ci",
 audience="runtime-A",issued_at=NOW,requested_expires_at=NOW+timedelta(seconds=10),token_expires_at=NOW+timedelta(seconds=10),reservation_expires_at=NOW+timedelta(seconds=10))
 assert i.validate_for_handoff(z,audience="runtime-B",executor_id="e",capability_instance_id="ci",operation_id="op",target_binding={"id":"T"},now=NOW)=="LEASE_BINDING_MISMATCH"

# F-13 / ROOT-F6: old backup cannot resurrect
def test_F13_ROOTF6_old_backup_resurrection(tmp_path):
 j=ReservationRecoveryJournal(tmp_path/"j");j.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});j.append({"type":"EXECUTION_CONFIRMED","reservation_id":"r"})
 assert j.reconstruct("r",{"state":"AVAILABLE"})["state"]=="CONSUMED"

# F-14 / ROOT-F7: possible effect cannot expire to unused
def test_F14_ROOTF7_expiry_after_possible_effect_is_not_unused(tmp_path):
 j=ReservationRecoveryJournal(tmp_path/"j");j.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});j.append({"type":"EXECUTION_STARTED","reservation_id":"r"})
 assert j.reconstruct("r")["assessment"]=="LIKELY_USED_REVIEW_REQUIRED"

# F-15: unsupported exactly-once is not claimed
def test_F15_exactly_once_not_claimed():
 _,_,_,c=env()
 assert not hasattr(c,"exactly_once") and c.ATOMICITY_SCOPE=="SINGLE_PROCESS_SHARED_MEMORY"

# F-16 / ROOT-F8: distributed/split-brain atomicity unavailable
def test_F16_F17_ROOTF8_distributed_partial_not_called_atomic():
 u,b,t,c=env();r=reserve(c,atomicity="DISTRIBUTED_MULTI_PROCESS")
 assert r["status"]=="RESERVATION_ATOMICITY_UNAVAILABLE" and u.state("tok").reserved_uses==0

# F-18: emergency label cannot bypass budget
def test_F18_emergency_cannot_bypass_budget():
 u,b,t,c=env(max_uses=5,budget=0)
 r=reserve(c,key="EMERGENCY",tx="EMERGENCY",target=False,slot=False,dep=False,bdelta=1)
 assert r["status"]=="RESERVATION_BUDGET_INSUFFICIENT"

# F-19 / ROOT-F9: civilization budget remains shared across executors
def test_F19_ROOTF9_civilization_budget_not_per_agent():
 u,b,t,c=env(max_uses=10,budget=1)
 a=reserve(c,key="a",tx="a",target=False,slot=False,dep=False,bdelta=1)
 # same coordinator, different executor request still shares PER_CIVILIZATION budget
 z=c.reserve(transaction_id="b",idempotency_key="b",invocation_request_id="b",token_id="tok",effective_scope_hash=H,
 executor_id="other",capability_id="c",operation_id="op",target_binding={"id":"T"},expected_token_version=1,use_count=1,
 budget_requests=[{"budget_id":"money","scope":"PER_CIVILIZATION","scope_key":"civil","delta":1,"expected_state_version":1}],
 resource_requests=[],target_requests=[],slot_requests=[],dependency_requests=[])
 assert a["status"]=="RESERVATION_COMMITTED" and z["status"]=="RESERVATION_BUDGET_INSUFFICIENT"

# F-20: cancellation after possible effect preserves causal history
def test_F20_cancellation_after_possible_effect(tmp_path):
 j=ReservationRecoveryJournal(tmp_path/"j");j.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});j.append({"type":"CANCEL_AFTER_POSSIBLE_EFFECT","reservation_id":"r"})
 assert j.reconstruct("r")["state"]=="INDETERMINATE"

def test_ROOT_summary_non_effecting_boundary():
 _,_,_,c=env();r=reserve(c,target=False,slot=False,dep=False,bdelta=0)
 assert r["authorization_created"] is False and r["capability_accessed"] is False and r["execution_performed"] is False and r["p162g_opened"] is False
