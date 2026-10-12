from ontology.execution_reservation_manager import AtomicReservationManager,AuthorizationUseState,STATUSES
from ontology.budget_reservation_manager import BudgetResourceReservationManager,SharedBudgetState,TechnicalResourceState
from ontology.target_lock_manager import TargetConcurrencyDependencyManager,ConcurrencySlotState,DependencyReservationState
from ontology.integrated_reservation_coordinator import IntegratedReservationCoordinator
from ontology.reservation_recovery_manager import ReservationRecoveryJournal

def setup(tmp_path=None):
 u=AtomicReservationManager();u.put_authorization_state(AuthorizationUseState("tok",2))
 b=BudgetResourceReservationManager();b.put_budget(SharedBudgetState("money","PER_CIVILIZATION","civil",10));b.put_resource(TechnicalResourceState("cpu",2))
 t=TargetConcurrencyDependencyManager();t.put_slot(ConcurrencySlotState("slot",1));t.put_dependency(DependencyReservationState("dep",1))
 j=ReservationRecoveryJournal(tmp_path/"j") if tmp_path else None
 return u,b,t,IntegratedReservationCoordinator(u,b,t,j)

def req(c,**x):
 q=dict(transaction_id="tx1",idempotency_key="idem1",invocation_request_id="inv",token_id="tok",
 effective_scope_hash="a"*64,executor_id="e",capability_id="c",operation_id="op",target_binding={"id":"T"},
 expected_token_version=0,use_count=1,
 budget_requests=[{"budget_id":"money","scope":"PER_CIVILIZATION","scope_key":"civil","delta":3,"expected_state_version":0}],
 resource_requests=[{"resource_id":"cpu","delta":1,"expected_state_version":0}],
 target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}],
 slot_requests=[{"slot_key":"slot","delta":1,"expected_state_version":0}],
 dependency_requests=[{"dependency_key":"dep","delta":1,"expected_state_version":0}])
 q.update(x);return c.reserve(**q)

def test_canonical_missing_status_is_fixed():
 assert "RESERVATION_UNDETERMINED" in STATUSES and len(STATUSES)==16

def test_integrated_commit_all_dimensions(tmp_path):
 u,b,t,c=setup(tmp_path);r=req(c)
 assert r["status"]=="RESERVATION_COMMITTED" and r["atomicity_scope"]=="SINGLE_PROCESS_SHARED_MEMORY"
 assert u.state("tok").reserved_uses==1
 assert b.budget_state("money","PER_CIVILIZATION","civil").reserved==3
 assert b.resource_state("cpu").reserved==1
 assert len(t.target_holds("T"))==1 and t.slot_state("slot").reserved==1 and t.dependency_state("dep").reserved==1
 assert ReservationRecoveryJournal(tmp_path/"j").reconstruct(r["reservation_id"])["state"]=="RESERVED"

def test_late_dependency_failure_mutates_nothing():
 u,b,t,c=setup()
 r=req(c,dependency_requests=[{"dependency_key":"dep","delta":2,"expected_state_version":0}])
 assert r["status"]=="DEPENDENCY_RESERVATION_UNAVAILABLE"
 assert u.state("tok").reserved_uses==0 and b.budget_state("money","PER_CIVILIZATION","civil").reserved==0
 assert b.resource_state("cpu").reserved==0 and t.target_holds("T")==() and t.slot_state("slot").reserved==0 and t.dependency_state("dep").reserved==0

def test_late_slot_failure_mutates_nothing():
 u,b,t,c=setup();r=req(c,slot_requests=[{"slot_key":"slot","delta":2,"expected_state_version":0}])
 assert r["status"]=="CONCURRENCY_SLOT_UNAVAILABLE"
 assert u.state("tok").reserved_uses==0 and b.budget_state("money","PER_CIVILIZATION","civil").reserved==0 and t.target_holds("T")==()

def test_budget_failure_mutates_nothing():
 u,b,t,c=setup();r=req(c,budget_requests=[{"budget_id":"money","scope":"PER_CIVILIZATION","scope_key":"civil","delta":11,"expected_state_version":0}])
 assert r["status"]=="RESERVATION_BUDGET_INSUFFICIENT" and u.state("tok").reserved_uses==0 and t.target_holds("T")==()

def test_stale_token_mutates_nothing():
 u,b,t,c=setup();r=req(c,expected_token_version=9)
 assert r["status"]=="RESERVATION_REVALIDATION_REQUIRED" and b.budget_state("money","PER_CIVILIZATION","civil").reserved==0

def test_retry_is_idempotent_no_double_spend():
 u,b,t,c=setup();a=req(c);z=req(c)
 assert a==z and u.state("tok").reserved_uses==1 and b.budget_state("money","PER_CIVILIZATION","civil").reserved==3 and len(t.target_holds("T"))==1

def test_distributed_atomicity_not_claimed():
 u,b,t,c=setup();r=req(c,requested_atomicity_scope="DISTRIBUTED_MULTI_PROCESS")
 assert r["status"]=="RESERVATION_ATOMICITY_UNAVAILABLE"
 assert u.state("tok").reserved_uses==0 and b.budget_state("money","PER_CIVILIZATION","civil").reserved==0

def test_no_lease_or_effect_at_f6():
 u,b,t,c=setup();r=req(c)
 assert r["lease_issued"] is False and r["authorization_created"] is False and r["capability_accessed"] is False and r["execution_performed"] is False and r["p162g_opened"] is False
 assert not hasattr(c,"execute") and not hasattr(c,"dispatch")

def test_target_conflict_is_all_or_none():
 u,b,t,c=setup();assert req(c)["status"]=="RESERVATION_COMMITTED"
 # fresh authorization/budget versions, but target remains exclusively held
 r=c.reserve(transaction_id="tx2",idempotency_key="idem2",invocation_request_id="inv2",token_id="tok",
 effective_scope_hash="a"*64,executor_id="e",capability_id="c",operation_id="op",target_binding={"id":"T"},
 expected_token_version=1,use_count=1,budget_requests=[{"budget_id":"money","scope":"PER_CIVILIZATION","scope_key":"civil","delta":1,"expected_state_version":1}],
 resource_requests=[],target_requests=[{"target_key":"T","lock_mode":"WRITE_EXCLUSIVE"}],slot_requests=[],dependency_requests=[])
 assert r["status"]=="TARGET_LOCK_CONFLICT" and u.state("tok").reserved_uses==1 and b.budget_state("money","PER_CIVILIZATION","civil").reserved==3
