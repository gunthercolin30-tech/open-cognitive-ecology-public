from ontology.p161_authorization_scope_construction import *

REQ={"authorization_request_id":"AR1","normative_decision_id":"ND1","action_digest":"AD","target":"T","purpose":"P",
 "requested_scope":{"region":["FR"],"mode":["READ"]},"requested_capabilities":["CAP_A"],
 "requested_validity":{"not_before":"2026-10-01T10:00:00Z","not_after":"2026-10-01T11:00:00Z"},
 "requested_use_policy":"SINGLE_USE"}
ND={"decision_id":"ND1","action_digest":"AD","target":"T","purpose":"P","lifecycle":"SEALED","transaction_state":"COMMITTED",
 "eligible_scope":{"region":["FR","CH"],"mode":["READ","WRITE"]},"eligible_capabilities":["CAP_A","CAP_B"],"artifact_hash":"NDH"}
AUTH={"status":"VALID","effective_scope":{"region":["FR"],"mode":["READ","WRITE"]},
 "effective_capabilities":["CAP_A"],"effective_temporal_bounds":{"not_before":"2026-10-01T09:00:00Z","not_after":"2026-10-01T12:00:00Z"},"receipt_hash":"ARH"}
EV={"status":"SATISFIED","approved_scope":{"region":["FR"],"mode":["READ"]},"evidence_bundle_hash":"EBH"}
HI={"status":"SATISFIED","receipt_hash":"HIH"}

def call(**kw):
 return construct_authorization_scope(kw.get("request",REQ),kw.get("nd",ND),kw.get("auth",AUTH),
  kw.get("ev",EV),kw.get("hi",HI),human_required=kw.get("human_required",True))

def test_manifest_non_sovereign():
 m=manifest(); assert all(m[k] is False for k in ("authorization_created","authorization_token_created","capability_created","execution_performed","p162_opened"))
def test_positive_intersection():
 x=call();assert x["status"]=="CONSTRUCTED";assert x["scope"]=={"mode":["READ"],"region":["FR"]};assert x["capabilities"]==["CAP_A"]
def test_deterministic(): assert call()["scope_envelope_hash"]==call()["scope_envelope_hash"]
def test_request_cannot_widen():
 r=dict(REQ);r["requested_scope"]={"region":["FR","US"],"mode":["READ"]}
 x=call(request=r);assert x["status"]=="CONSTRUCTED" and x["scope"]["region"]==["FR"]
def test_authority_cannot_be_widened():
 a=dict(AUTH);a["effective_scope"]={"region":["CH"],"mode":["READ"]}
 assert call(auth=a)["status"]=="UNSATISFIED"
def test_approval_cannot_be_widened():
 e=dict(EV);e["approved_scope"]={"region":["CH"],"mode":["READ"]}
 assert call(ev=e)["status"]=="UNSATISFIED"
def test_unknown_dimension_not_unlimited():
 r=dict(REQ);r["requested_scope"]={"region":["FR"],"mode":"UNKNOWN"}
 assert call(request=r)["status"]=="UNKNOWN"
def test_missing_approval_scope_unknown():
 e=dict(EV);e.pop("approved_scope")
 assert call(ev=e)["status"]=="UNKNOWN"
def test_capability_intersection():
 r=dict(REQ);r["requested_capabilities"]=["CAP_B"]
 assert call(request=r)["status"]=="UNSATISFIED"
def test_target_exact():
 r=dict(REQ);r["target"]="OTHER";assert call(request=r)["status"]=="UNSATISFIED"
def test_purpose_exact():
 r=dict(REQ);r["purpose"]="OTHER";assert call(request=r)["status"]=="UNSATISFIED"
def test_validity_narrowing():
 r=dict(REQ);r["requested_validity"]={"not_before":"2026-10-01T08:00:00Z","not_after":"2026-10-01T11:00:00Z"}
 assert call(request=r)["status"]=="UNSATISFIED"
def test_authority_required():
 a=dict(AUTH,status="EXPIRED");assert call(auth=a)["status"]=="UNSATISFIED"
def test_d_required():
 e=dict(EV,status="UNKNOWN");assert call(ev=e)["status"]=="UNSATISFIED"
def test_e_required_when_human():
 h=dict(HI,status="UNKNOWN");assert call(hi=h)["status"]=="UNSATISFIED"
def test_e_not_required_path():
 h={"status":"NOT_REQUIRED","receipt_hash":"HIH"};assert call(hi=h,human_required=False)["status"]=="CONSTRUCTED"
def test_decision_binding():
 r=dict(REQ,normative_decision_id="OTHER");assert call(request=r)["status"]=="UNSATISFIED"
def test_action_digest_binding():
 r=dict(REQ,action_digest="OTHER");assert call(request=r)["status"]=="UNSATISFIED"
def test_no_token_execution():
 x=call();assert x["authorization_created"] is False and x["authorization_token_created"] is False and x["execution_performed"] is False
