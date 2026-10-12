from ontology.p161_authorization_token_lifecycle import *
def tok(policy="SINGLE_USE"):
 b={"token_id":"AT1","use_policy":policy,"validity":{"not_before":"2026-10-01T10:00:00Z","not_after":"2026-10-01T12:00:00Z"}}
 return {"body":b,"token_hash":"TH"}
def current(policy="SINGLE_USE",max_uses=None):
 return refresh(initialize_lifecycle(tok(policy),max_uses=max_uses),tok(policy),now="2026-10-01T11:00:00Z")
def test_positive_current():assert current()["state"]=="CURRENT"
def test_not_yet_valid():assert refresh(initialize_lifecycle(tok()),tok(),now="2026-10-01T09:00:00Z")["state"]=="NOT_YET_VALID"
def test_expiry_terminal():assert refresh(initialize_lifecycle(tok()),tok(),now="2026-10-01T12:00:00Z")["state"]=="EXPIRED"
def test_revoke_terminal():assert revoke(current(),now="2026-10-01T11:01:00Z",reason="WITHDRAWN")["state"]=="REVOKED"
def test_terminal_no_resurrection():
 x=revoke(current(),now="2026-10-01T11:01:00Z",reason="X");assert refresh(x,tok(),now="2026-10-01T11:02:00Z")["state"]=="REVOKED"
def test_single_use():
 x=current();r=reserve_for_use(x,tok(),now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash="TH")
 assert r["status"]=="RESERVED";c=consume_reserved(r["lifecycle"],now="2026-10-01T11:02:00Z",reservation_id="R1");assert c["lifecycle"]["state"]=="CONSUMED"
def test_single_use_no_second_use():
 x=current();r=reserve_for_use(x,tok(),now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash="TH")
 c=consume_reserved(r["lifecycle"],now="2026-10-01T11:02:00Z",reservation_id="R1")
 assert reserve_for_use(c["lifecycle"],tok(),now="2026-10-01T11:03:00Z",reservation_id="R2",current_token_hash="TH")["status"]=="REFUSED"
def test_bounded_multi_use():
 t=tok("BOUNDED_MULTI_USE");x=refresh(initialize_lifecycle(t,max_uses=2),t,now="2026-10-01T11:00:00Z")
 r=reserve_for_use(x,t,now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash="TH");c=consume_reserved(r["lifecycle"],now="2026-10-01T11:02:00Z",reservation_id="R1")
 assert c["lifecycle"]["state"]=="CURRENT" and c["lifecycle"]["consumed_uses"]==1
 r2=reserve_for_use(c["lifecycle"],t,now="2026-10-01T11:03:00Z",reservation_id="R2",current_token_hash="TH");c2=consume_reserved(r2["lifecycle"],now="2026-10-01T11:04:00Z",reservation_id="R2")
 assert c2["lifecycle"]["state"]=="CONSUMED"
def test_bounded_requires_limit():assert initialize_lifecycle(tok("BOUNDED_MULTI_USE"))["state"]=="INVALIDATED"
def test_revalidate_each_use_required():
 t=tok("REVALIDATE_EACH_USE");x=current("REVALIDATE_EACH_USE")
 assert reserve_for_use(x,t,now="2026-10-01T11:01:00Z",reservation_id="R",current_token_hash="TH")["reason"]=="REVALIDATION_REQUIRED"
def test_revalidate_each_use_positive():
 t=tok("REVALIDATE_EACH_USE");x=current("REVALIDATE_EACH_USE")
 assert reserve_for_use(x,t,now="2026-10-01T11:01:00Z",reservation_id="R",current_token_hash="TH",revalidation_passed=True)["status"]=="RESERVED"
def test_hash_drift_refuses():assert reserve_for_use(current(),tok(),now="2026-10-01T11:01:00Z",reservation_id="R",current_token_hash="OTHER")["reason"]=="TOKEN_HASH_DRIFT"
def test_double_reservation_refuses():
 r=reserve_for_use(current(),tok(),now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash="TH")
 assert reserve_for_use(r["lifecycle"],tok(),now="2026-10-01T11:02:00Z",reservation_id="R2",current_token_hash="TH")["status"]=="REFUSED"
def test_wrong_consumption_refuses():
 r=reserve_for_use(current(),tok(),now="2026-10-01T11:01:00Z",reservation_id="R1",current_token_hash="TH")
 assert consume_reserved(r["lifecycle"],now="2026-10-01T11:02:00Z",reservation_id="WRONG")["status"]=="REFUSED"
def test_no_execution_or_p162():
 r=reserve_for_use(current(),tok(),now="2026-10-01T11:01:00Z",reservation_id="R",current_token_hash="TH")
 assert r["execution_performed"] is False and r["p162_opened"] is False
def test_manifest_boundaries():
 m=manifest();assert m["capability_created"] is False and m["execution_performed"] is False and m["p162_opened"] is False
