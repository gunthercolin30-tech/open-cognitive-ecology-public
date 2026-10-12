from concurrent.futures import ThreadPoolExecutor
from ontology.budget_reservation_manager import *
def b(scope="PER_CIVILIZATION",key="civilization",maxv=10): return SharedBudgetState("B",scope,key,maxv)
def req(scope="PER_CIVILIZATION",key="civilization",delta=1,ver=0): return {"budget_id":"B","scope":scope,"scope_key":key,"delta":delta,"expected_state_version":ver}
def rr(delta=1,ver=0): return {"resource_id":"R","delta":delta,"expected_state_version":ver}
def test_seven_scopes(): assert len(BUDGET_SCOPES)==7 and "PER_CIVILIZATION" in BUDGET_SCOPES
def test_budget_bound():
 m=BudgetResourceReservationManager();m.put_budget(SharedBudgetState("B","PER_TOKEN","T",5,2,1));assert m.reserve(reservation_id="r1",idempotency_key="k1",budget_requests=[req("PER_TOKEN","T",2)])["status"]=="RESERVATION_COMMITTED";assert m.reserve(reservation_id="r2",idempotency_key="k2",budget_requests=[req("PER_TOKEN","T",1,1)])["status"]=="RESERVATION_BUDGET_INSUFFICIENT"
def test_civilization_budget_not_multiplied():
 m=BudgetResourceReservationManager();m.put_budget(b(maxv=1))
 with ThreadPoolExecutor(max_workers=8) as x: out=list(x.map(lambda i:m.reserve(reservation_id=f"r{i}",idempotency_key=f"k{i}",budget_requests=[req()]),range(20)))
 assert sum(z["status"]=="RESERVATION_COMMITTED" for z in out)==1
def test_resource_availability_not_right():
 m=BudgetResourceReservationManager();m.put_budget(b(maxv=0));m.put_resource(TechnicalResourceState("R",1000));z=m.reserve(reservation_id="r",idempotency_key="k",budget_requests=[req()],resource_requests=[rr(500)]);assert z["status"]=="RESERVATION_BUDGET_INSUFFICIENT" and m.resource_state("R").reserved==0
def test_resource_failure_no_budget_hold():
 m=BudgetResourceReservationManager();m.put_budget(b());m.put_resource(TechnicalResourceState("R",1));z=m.reserve(reservation_id="r",idempotency_key="k",budget_requests=[req(delta=2)],resource_requests=[rr(2)]);assert z["status"]=="RESOURCE_SCOPE_INSUFFICIENT" and m.budget_state("B","PER_CIVILIZATION","civilization").reserved==0
def test_stale_budget_no_resource_hold():
 m=BudgetResourceReservationManager();m.put_budget(b());m.put_resource(TechnicalResourceState("R",10));z=m.reserve(reservation_id="r",idempotency_key="k",budget_requests=[req(ver=9)],resource_requests=[rr()]);assert z["status"]=="RESERVATION_REVALIDATION_REQUIRED" and m.resource_state("R").reserved==0
def test_stale_resource_no_budget_hold():
 m=BudgetResourceReservationManager();m.put_budget(b());m.put_resource(TechnicalResourceState("R",10));z=m.reserve(reservation_id="r",idempotency_key="k",budget_requests=[req()],resource_requests=[rr(ver=9)]);assert z["status"]=="RESERVATION_REVALIDATION_REQUIRED" and m.budget_state("B","PER_CIVILIZATION","civilization").reserved==0
def test_idempotent_retry():
 m=BudgetResourceReservationManager();m.put_budget(b());a=m.reserve(reservation_id="r",idempotency_key="k",budget_requests=[req()]);z=m.reserve(reservation_id="different",idempotency_key="k",budget_requests=[req()]);assert a==z and m.budget_state("B","PER_CIVILIZATION","civilization").reserved==1
def test_concurrent_same_snapshot_compare_and_reserve_allows_only_one_commit():
 m=BudgetResourceReservationManager();m.put_budget(b(maxv=4))
 with ThreadPoolExecutor(max_workers=12) as x:
  out=list(x.map(lambda i:m.reserve(reservation_id=f"r{i}",idempotency_key=f"k{i}",budget_requests=[req(ver=0)]),range(40)))
 assert sum(z["status"]=="RESERVATION_COMMITTED" for z in out)==1
 assert sum(z["status"]=="RESERVATION_REVALIDATION_REQUIRED" for z in out)==39
 assert m.budget_state("B","PER_CIVILIZATION","civilization").reserved==1

def test_revalidated_requests_fill_budget_but_never_double_spend():
 m=BudgetResourceReservationManager();m.put_budget(b(maxv=4))
 out=[]
 for i in range(8):
  st=m.budget_state("B","PER_CIVILIZATION","civilization")
  out.append(m.reserve(reservation_id=f"r{i}",idempotency_key=f"k{i}",budget_requests=[req(ver=st.state_version)]))
 assert sum(z["status"]=="RESERVATION_COMMITTED" for z in out)==4
 assert sum(z["status"]=="RESERVATION_BUDGET_INSUFFICIENT" for z in out)==4
 st=m.budget_state("B","PER_CIVILIZATION","civilization")
 assert st.committed+st.reserved==4
 assert st.reserved==4
def test_non_effecting():
 m=BudgetResourceReservationManager();m.put_budget(b());z=m.reserve(reservation_id="r",idempotency_key="k",budget_requests=[req()]);assert z["authorization_created"] is False and z["capability_accessed"] is False and z["execution_performed"] is False and not hasattr(m,"execute")
