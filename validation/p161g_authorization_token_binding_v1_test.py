from ontology.p161_authorization_token_binding import *
REQ={"authorization_request_id":"AR1","request_hash":"RQH","normative_decision_id":"ND1","action_digest":"AD",
"runtime_context_fingerprint":"RF","constitutional_snapshot_hash":"CS","compiled_profile_hash":"CP"}
ND={"decision_id":"ND1","artifact_hash":"NDH"}
AU={"status":"VALID","receipt_hash":"AUH"}
EV={"status":"SATISFIED","evidence_bundle_hash":"EVH"}
HI={"status":"SATISFIED","receipt_hash":"HIH"}
SE={"status":"CONSTRUCTED","authorization_request_id":"AR1","normative_decision_id":"ND1","scope":{"r":["FR"]},
"capabilities":["C"],"target":"T","purpose":"P","validity":{"not_before":"A","not_after":"B"},
"requested_use_policy":"SINGLE_USE","scope_envelope_hash":"SEH"}
KEY=b"test-only-p161g-key"
def vec():return dependency_vector(REQ,ND,AU,EV,HI,SE)
def issue(**kw):return issue_authorization_token(kw.get("req",REQ),kw.get("nd",ND),kw.get("au",AU),
kw.get("ev",EV),kw.get("hi",HI),kw.get("se",SE),current_dependency_vector=kw.get("cur",vec()),
signer_id="ISSUER-1",signing_key=KEY,issued_at="2026-10-01T10:00:00Z")
def test_positive_token_commit():
 x=issue();assert x["status"]=="TOKEN_COMMITTED" and x["authorization_token_created"] is True
 assert x["execution_performed"] is False and x["capability_created"] is False and x["p162_opened"] is False
def test_integrity_verifies():
 x=issue();v=verify_token_integrity(x["token"],KEY);assert v["status"]=="PASS"
 assert v["authority_validity_proven"] is False and v["execution_permission_proven"] is False
def test_deterministic_same_inputs():assert issue()["token"]["token_hash"]==issue()["token"]["token_hash"]
def test_scope_tamper_breaks_signature():
 x=issue();x["token"]["body"]["scope"]={"r":["WORLD"]};assert verify_token_integrity(x["token"],KEY)["status"]=="FAIL"
def test_signature_wrong_key():assert verify_token_integrity(issue()["token"],b"wrong")["status"]=="FAIL"
def test_final_compare_drift_refuses():
 c=vec();c["authority_receipt_hash"]="NEW";x=issue(cur=c);assert x["status"]=="REFUSED" and x["authorization_token_created"] is False
def test_authority_invalid_refuses():
 a=dict(AU,status="REVOKED");x=issue(au=a);assert x["status"]=="REFUSED"
def test_scope_not_constructed_refuses():
 s=dict(SE,status="UNKNOWN");assert issue(se=s)["status"]=="REFUSED"
def test_evidence_not_satisfied_refuses():
 e=dict(EV,status="UNKNOWN");assert issue(ev=e)["status"]=="REFUSED"
def test_human_unknown_refuses():
 h=dict(HI,status="UNKNOWN");assert issue(hi=h)["status"]=="REFUSED"
def test_request_binding_refuses():
 s=dict(SE,authorization_request_id="OTHER");assert issue(se=s)["status"]=="REFUSED"
def test_decision_binding_refuses():
 s=dict(SE,normative_decision_id="OTHER");assert issue(se=s)["status"]=="REFUSED"
def test_precommit_stages_unusable():
 x=issue();assert all(not s["usable"] for s in x["transaction_stages"][:-1]);assert x["transaction_stages"][-1]=={"stage":"COMMIT","usable":True}
def test_signature_is_non_sovereign():
 x=issue();s=x["token"]["signature"];assert s["proves_authority"] is False and s["proves_execution_right"] is False
def test_manifest_boundaries():
 m=manifest();assert m["execution_performed"] is False and m["capability_created"] is False and m["p162_opened"] is False
