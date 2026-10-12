from ontology.governed_execution_adapter import ExecutionClaim
from ontology.scoped_handle_broker import ScopedHandleBroker
def claim():return ExecutionClaim("R1","L1","A1","EX1","2026",1,"CH")
def lease(**k):
 d={"lease_id":"L1","reservation_id":"R1","operation_id":"WRITE","expires_at":"2999-01-01T00:00:00+00:00"};d.update(k);return d
def reg():return {"adapter_id":"A1","effector_id":"FS1"}
def allowed():return {"path":"/tmp/exact","operations":["WRITE"],"ambient_authority":False,"child_inheritance":False,"transferable":False}
def issue(b,req=None,**k):return b.issue(claim=k.get("claim",claim()),lease=k.get("lease",lease()),registry_entry=k.get("registry_entry",reg()),requested_scope=req or allowed(),authorized_scope=k.get("authorized_scope",allowed()),target_binding={"path":"/tmp/exact"},audience=k.get("audience","A1"),now_iso="2026-10-01T16:00:00+00:00")
def test_issue_is_noncausal():
 x=issue(ScopedHandleBroker());assert x["status"]=="HANDLE_ISSUED";h=x["handle"];assert h.single_use and not h.transferable and not h.child_inheritance and not h.ambient_authority;assert not x["credential_disclosed"] and not x["effector_called"] and not x["real_world_effect_performed"]
def test_missing_claim():assert issue(ScopedHandleBroker(),claim=None)["reason"]=="missing_execution_claim"
def test_scope_widening_path():assert issue(ScopedHandleBroker(),{"path":"/tmp/other","operations":["WRITE"],"ambient_authority":False,"child_inheritance":False,"transferable":False})["reason"]=="scope_widening"
def test_scope_widening_operation():assert issue(ScopedHandleBroker(),{"path":"/tmp/exact","operations":["WRITE","DELETE"],"ambient_authority":False,"child_inheritance":False,"transferable":False})["reason"]=="scope_widening"
def test_ambient_authority(): 
 a=allowed();a["ambient_authority"]=True;assert issue(ScopedHandleBroker(),a,authorized_scope=a)["reason"]=="ambient_authority_forbidden"
def test_child_inheritance():
 a=allowed();a["child_inheritance"]=True;assert issue(ScopedHandleBroker(),a,authorized_scope=a)["reason"]=="child_inheritance_forbidden"
def test_transfer():
 a=allowed();a["transferable"]=True;assert issue(ScopedHandleBroker(),a,authorized_scope=a)["reason"]=="transfer_forbidden"
def test_wrong_audience():assert issue(ScopedHandleBroker(),audience="OTHER")["reason"]=="wrong_audience"
def test_expired():assert issue(ScopedHandleBroker(),lease=lease(expires_at="2020-01-01T00:00:00+00:00"))["reason"]=="lease_expired"
def test_duplicate_issue_blocked():
 b=ScopedHandleBroker();assert issue(b)["status"]=="HANDLE_ISSUED";assert issue(b)["reason"]=="duplicate_handle_request"
def test_single_use_consumption():
 b=ScopedHandleBroker();h=issue(b)["handle"];assert b.consume_once(h.handle_id) is True;assert b.consume_once(h.handle_id) is False
def test_unknown_handle_cannot_consume():assert ScopedHandleBroker().consume_once("UNKNOWN") is False
