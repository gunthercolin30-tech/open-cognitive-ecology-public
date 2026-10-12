from __future__ import annotations
import hashlib,hmac,json
from copy import deepcopy
from typing import Any,Mapping

PRIMITIVE="p161_authorization_token_binding";VERSION="P161-G-v1"
SCHEMA="oce.p161g.authorization_token.v1"
def _canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x):return hashlib.sha256(_canon(x).encode()).hexdigest()
def _m(x):return x if isinstance(x,Mapping) else {}

def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,
 "laws":["VALID_SIGNATURE!=VALID_AUTHORITY","VALID_SIGNATURE!=VALID_AUTHORIZATION",
 "AUTHORIZATION_TOKEN!=CAPABILITY","AUTHORIZATION_TOKEN!=EXECUTION",
 "FINAL_COMPARE_AND_AUTHORIZE_REQUIRED_AT_COMMIT"],
 "execution_performed":False,"capability_created":False,"p162_opened":False,
 "functional_only":True,"phenomenology_undetermined":True}

def dependency_vector(request,decision,authority,evidence,human,scope):
 return {"request_hash":request.get("request_hash"),
 "normative_decision_hash":decision.get("artifact_hash"),
 "authority_receipt_hash":authority.get("receipt_hash"),
 "approval_evidence_bundle_hash":evidence.get("evidence_bundle_hash"),
 "human_integrity_receipt_hash":human.get("receipt_hash"),
 "scope_envelope_hash":scope.get("scope_envelope_hash"),
 "runtime_context_fingerprint":request.get("runtime_context_fingerprint"),
 "constitutional_snapshot_hash":request.get("constitutional_snapshot_hash"),
 "compiled_profile_hash":request.get("compiled_profile_hash")}

def issue_authorization_token(request:Mapping[str,Any],decision:Mapping[str,Any],authority:Mapping[str,Any],
 evidence:Mapping[str,Any],human:Mapping[str,Any],scope:Mapping[str,Any],*,current_dependency_vector:Mapping[str,Any],
 signer_id:str,signing_key:bytes,issued_at:str):
 req,nd,au,ev,hi,se=[dict(_m(x)) for x in (request,decision,authority,evidence,human,scope)]
 stages=[];reasons=[]
 stages.append({"stage":"PREPARE","usable":False})
 if se.get("status")!="CONSTRUCTED":reasons.append("SCOPE_NOT_CONSTRUCTED")
 if au.get("status")!="VALID":reasons.append("AUTHORITY_NOT_VALID")
 if ev.get("status")!="SATISFIED":reasons.append("EVIDENCE_NOT_SATISFIED")
 if hi.get("status") not in ("SATISFIED","NOT_REQUIRED"):reasons.append("HUMAN_INTEGRITY_NOT_SATISFIED")
 if req.get("authorization_request_id")!=se.get("authorization_request_id"):reasons.append("REQUEST_SCOPE_BINDING_MISMATCH")
 if nd.get("decision_id")!=se.get("normative_decision_id"):reasons.append("DECISION_SCOPE_BINDING_MISMATCH")
 stages.append({"stage":"VALIDATE","usable":False})
 expected=dependency_vector(req,nd,au,ev,hi,se);current=dict(_m(current_dependency_vector))
 if expected!=current:reasons.append("FINAL_COMPARE_DEPENDENCY_DRIFT")
 stages.append({"stage":"FINAL_COMPARE","usable":False,"matched":expected==current})
 if reasons:
  return {"status":"REFUSED","reasons":sorted(set(reasons)),"transaction_stages":stages,
   "authorization_created":False,"authorization_token_created":False,"capability_created":False,
   "execution_performed":False,"p162_opened":False,"functional_only":True,"phenomenology_undetermined":True}
 body={"schema":SCHEMA,"version":VERSION,"authorization_request_id":req.get("authorization_request_id"),
  "normative_decision_id":nd.get("decision_id"),"action_digest":req.get("action_digest"),
  "scope":deepcopy(se.get("scope")),"capabilities":deepcopy(se.get("capabilities")),
  "target":se.get("target"),"purpose":se.get("purpose"),"validity":deepcopy(se.get("validity")),
  "use_policy":se.get("requested_use_policy"),"dependency_vector":expected,
  "signer_id":signer_id,"issued_at":issued_at,
  "non_sovereign":True,"grants_capability":False,"permits_execution":False}
 token_id="AT-"+_hash(body)[:24];body["token_id"]=token_id
 signature=hmac.new(signing_key,_canon(body).encode(),hashlib.sha256).hexdigest()
 stages.append({"stage":"SIGN","usable":False})
 token={"body":body,"signature":{"algorithm":"HMAC-SHA256","value":signature,
   "proves":["integrity","signer_key_possession"],"proves_authority":False,"proves_execution_right":False}}
 token["token_hash"]=_hash(token)
 stages.append({"stage":"COMMIT","usable":True})
 return {"status":"TOKEN_COMMITTED","token":token,"transaction_stages":stages,
  "authorization_created":True,"authorization_token_created":True,"capability_created":False,
  "execution_performed":False,"p162_opened":False,"functional_only":True,"phenomenology_undetermined":True}

def verify_token_integrity(token:Mapping[str,Any],signing_key:bytes):
 t=dict(_m(token));body=dict(_m(t.get("body")));sig=_m(t.get("signature"))
 expected=hmac.new(signing_key,_canon(body).encode(),hashlib.sha256).hexdigest()
 sigok=sig.get("algorithm")=="HMAC-SHA256" and hmac.compare_digest(str(sig.get("value","")),expected)
 x=dict(t);claimed=x.pop("token_hash",None);hashok=claimed==_hash(x)
 return {"status":"PASS" if sigok and hashok else "FAIL","signature_valid":sigok,"token_hash_valid":hashok,
  "authority_validity_proven":False,"execution_permission_proven":False}

# P161_CANONICAL_COMPLETION_AFGH_V1
UNCOMMITTED="UNCOMMITTED"
def canonical_signed_authorization_constraints(scope):
    return {"environment":scope.get("environment"),"budget":scope.get("budget",{}),"max_uses":scope.get("max_uses"),"constraint_tuples":scope.get("constraint_tuples",[]),"reservation":scope.get("reservation")}
def authorization_event(token_id,token_hash,semantic_slot,issuer_id,issuer_registry,environment):
    if issuer_id not in (issuer_registry or {}):return {"status":"REFUSED","reason":"ISSUER_NOT_IN_BOUNDED_REGISTRY","state":UNCOMMITTED}
    if environment not in issuer_registry[issuer_id].get("environments",[]):return {"status":"REFUSED","reason":"ISSUER_ENVIRONMENT_OUT_OF_BOUNDS","state":UNCOMMITTED}
    return {"type":"AuthorizationEvent","status":"COMMITTED","token_id":token_id,"token_hash":token_hash,"semantic_authorization_slot":semantic_slot,"issuer_id":issuer_id,"environment":environment,"authorization_created":False,"execution_performed":False}
