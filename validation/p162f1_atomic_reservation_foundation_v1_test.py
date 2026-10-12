from concurrent.futures import ThreadPoolExecutor
from ontology.execution_reservation_manager import AtomicReservationManager,AuthorizationUseState,STATUSES
H="a"*64
def kw(k="K",v=0):
 return dict(idempotency_key=k,invocation_request_id="inv-1",token_id="tok-1",effective_scope_hash=H,executor_id="exec-1",capability_id="cap-1",operation_id="read",target_binding={"id":"X"},expected_state_version=v,use_count=1)
def test_status_catalog_canonical_16():
    expected = {
        "PREPARED","COMMITTING","RESERVED","EXECUTION_STARTED","EXECUTION_CONFIRMED",
        "COMMITTED","RELEASED","ABORTED","EXPIRED","INDETERMINATE","INVALIDATED",
        "RESERVATION_COMMITTED","RESERVATION_REVALIDATION_REQUIRED",
        "RESERVATION_BUDGET_INSUFFICIENT","RESERVATION_ATOMICITY_UNAVAILABLE",
        "RESERVATION_UNDETERMINED",
    }
    assert len(STATUSES) == 16
    assert set(STATUSES) == expected

def test_single_use_retry_same_right():
 m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",1)); a=m.reserve(**kw()); b=m.reserve(**kw())
 assert a["status"]=="RESERVED" and a["reservation_id"]==b["reservation_id"] and m.state("tok-1").reserved_uses==1
def test_distinct_second_reservation_refused():
 m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",1)); assert m.reserve(**kw("A"))["status"]=="RESERVED"; assert m.reserve(**kw("B",1))["status"]=="RESERVATION_BUDGET_INSUFFICIENT"
def test_bounded_multi_use():
 m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",3,committed_uses=1)); assert m.reserve(**kw("A"))["status"]=="RESERVED"; assert m.reserve(**kw("B",1))["status"]=="RESERVED"; assert m.reserve(**kw("C",2))["status"]=="RESERVATION_BUDGET_INSUFFICIENT"; assert m.state("tok-1").committed_uses+m.state("tok-1").reserved_uses==3
def test_stale_compare_fails():
 m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",2)); assert m.reserve(**kw("A"))["status"]=="RESERVED"; assert m.reserve(**kw("B",0))["status"]=="RESERVATION_REVALIDATION_REQUIRED"
def test_lifecycle_fail_closed():
 for f in ("revoked","expired","indeterminate"):
  m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",1,**{f:True})); assert m.reserve(**kw())["status"]=="RESERVATION_REVALIDATION_REQUIRED"
def test_concurrent_single_use():
 m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",1))
 with ThreadPoolExecutor(max_workers=8) as x: out=list(x.map(lambda i:m.reserve(**kw(str(i),0)),range(32)))
 assert sum(r["status"]=="RESERVED" for r in out)==1 and m.state("tok-1").reserved_uses==1
def test_non_effecting():
 m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",1)); r=m.reserve(**kw())
 assert r["authorization_created"] is False and r["capability_accessed"] is False and r["execution_performed"] is False
def test_deterministic_identity():
 ids=[]
 for _ in range(2):
  m=AtomicReservationManager(); m.put_authorization_state(AuthorizationUseState("tok-1",1)); ids.append(m.reserve(**kw())["reservation_id"])
 assert ids[0]==ids[1]
def test_no_execution_api():
 assert not hasattr(AtomicReservationManager,"execute") and not hasattr(AtomicReservationManager,"dispatch")
