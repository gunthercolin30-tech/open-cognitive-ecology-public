from copy import deepcopy
from ontology.p161_authority_revalidation import revalidate_authority, manifest

def fx():
 req={"authorization_request_id":"AR1","requested_scope":{"action_class":["A"]},"purpose":"govern"}
 ver={"status":"VERIFIED","verification_hash":"V"}
 h={"holder_id":"H1","kind":"HUMAN","status":"ACTIVE","authority_classes":["GOVERNANCE"],"scope":{"action_class":["A"]},"purposes":["govern"],"roles":["APPROVER"],"valid_from":"2026-01-01T00:00:00Z","valid_until":"2027-01-01T00:00:00Z"}
 res={"authority_status":"VALID","resolution_hash":"R","authority_context_fingerprint":"CTX","required_authority":{"authority_class":"GOVERNANCE"},"candidate_holders":[{"holder_id":"H1"}],"human_reserved":False,"temporal_bounds":{"valid_from":"2026-01-01T00:00:00Z","expires_at":"2027-01-01T00:00:00Z"},"separation_of_duties":{"forbidden_role_pairs":[]},"quorum":{"n":1,"required_roles":["APPROVER"]}}
 live={"authority_context_fingerprint":"CTX","holders":[h]}
 return req,ver,res,live

def call(*,mut=None):
 req,ver,res,live=fx()
 if mut: mut(req,ver,res,live)
 return revalidate_authority(req,ver,res,live_authority_context=live,now="2026-10-01T08:00:00Z")

def test_valid(): assert call()["status"]=="VALID"
def test_deterministic(): assert call()["receipt_hash"]==call()["receipt_hash"]
def test_non_sovereign():
 x=call(); assert x["effect"]=="EVIDENCE_ONLY_NOT_APPROVAL_OR_AUTHORIZATION"
 for k in ("authorization_created","authorization_token_created","capability_created","execution_performed","p162_opened"): assert x[k] is False
 assert manifest()["authority_created"] is False

def test_requires_b(): assert call(mut=lambda r,v,a,l:v.update(status="UNRESOLVED"))["status"]=="RETURN_TO_P160"
def test_context_drift(): assert call(mut=lambda r,v,a,l:l.update(authority_context_fingerprint="NEW"))["status"]=="RETURN_TO_P160"
def test_class(): assert call(mut=lambda r,v,a,l:l["holders"][0].update(authority_classes=["OPERATIONAL"]))["status"]=="CLASS_INSUFFICIENT"
def test_scope(): assert call(mut=lambda r,v,a,l:r.update(requested_scope={"action_class":["A","B"]}))["status"]=="SCOPE_INSUFFICIENT"
def test_purpose(): assert call(mut=lambda r,v,a,l:r.update(purpose="other"))["status"]=="PURPOSE_INSUFFICIENT"
def test_expired_holder(): assert call(mut=lambda r,v,a,l:l["holders"][0].update(valid_until="2026-09-01T00:00:00Z"))["status"]=="EXPIRED"
def test_revoked_unavailable(): assert call(mut=lambda r,v,a,l:l["holders"][0].update(status="REVOKED"))["status"]=="UNAVAILABLE"
def test_quorum(): assert call(mut=lambda r,v,a,l:a.update(quorum={"n":2,"required_roles":["APPROVER"]}))["status"]=="QUORUM_INCOMPLETE"
def test_sod():
 def m(r,v,a,l): a.update(separation_of_duties={"forbidden_role_pairs":[["APPROVER","EXECUTOR"]]}); l["holders"][0]["roles"]=["APPROVER","EXECUTOR"]
 assert call(mut=m)["status"]=="SEPARATION_OF_DUTIES_VIOLATION"
def test_human_reserved_no_substitution():
 def m(r,v,a,l): a["human_reserved"]=True; l["holders"][0]["kind"]="AI"; l["succession_rule"]={"preexisting":False,"valid":False}
 assert call(mut=m)["status"]=="HUMAN_RESERVED_UNAVAILABLE"
def test_delegation_amplification():
 def m(r,v,a,l):
  l["holders"][0]["parent_authority_id"]="P"; l["holders"].append({"holder_id":"P","kind":"HUMAN","status":"ACTIVE","authority_classes":["GOVERNANCE"],"scope":{"action_class":["X"]},"purposes":["govern"],"roles":[]})
 assert call(mut=m)["status"]=="INVALID"
