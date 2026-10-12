"P161-B — NormativeDecision Verification. Functional-only; verification is not authorization."
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping
from ontology.p160_normative_decision_sealing import verify_normative_decision

PRIMITIVE="p161_normative_decision_verification"
VERSION="P161-B-v1"
SCHEMA="oce.p161b.normative_decision_verification.v1"
BOUNDARIES={"authority_created":False,"authorization_created":False,"authorization_token_created":False,"capability_created":False,"execution_performed":False,"p162_opened":False}
FUNCTIONAL_ONLY={"functional_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_sha256(v): return sha256(_canon(v).encode()).hexdigest()
def _map(v): return v if isinstance(v,Mapping) else {}
def _present(v): return v not in (None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE")

def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"scope":"P161-B_ONLY","doctrines":["VERIFICATION != AUTHORIZATION","STALE_DECISION_IS_NOT_REPAIRED_HERE","UNKNOWN_NEVER_SATISFIES_POSITIVE_PRECONDITION"],**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}

def _result(status,reasons,checks,decision,request):
 x={"schema":SCHEMA,"version":VERSION,"status":status,"reasons":sorted(set(reasons)),"checks":deepcopy(checks),"normative_decision_id":decision.get("decision_id"),"normative_decision_hash":decision.get("artifact_hash"),"authorization_request_id":request.get("authorization_request_id"),**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
 x["verification_hash"]=canonical_sha256(x); return x

def _scope_narrowing(req,decision):
 rs=_map(req.get("requested_scope")); ds=_map(decision.get("authority_scope"))
 if not rs:return False
 for k,v in rs.items():
  a=ds.get(k)
  if a is None:return False
  if isinstance(v,list) and isinstance(a,list):
   if not set(v).issubset(set(a)):return False
  elif v!=a:return False
 return True

def verify_for_authorization(authorization_request,normative_decision,*,current_state,persisted_state=None):
 request=deepcopy(dict(_map(authorization_request))); decision=deepcopy(dict(_map(normative_decision))); state=deepcopy(dict(_map(current_state))); persisted=deepcopy(dict(_map(persisted_state)))
 checks={}; reject=[]; revalidate=[]; unresolved=[]
 base=verify_normative_decision(decision); checks["p160_verifier"]=base.get("status")
 if base.get("status")!="PASS":reject.append("P160_ARTIFACT_OR_SEAL_INVALID")
 checks["sealed_committed"]=decision.get("lifecycle")=="SEALED" and decision.get("transaction_state")=="COMMITTED"
 if not checks["sealed_committed"]:reject.append("DECISION_NOT_SEALED_COMMITTED")
 if decision.get("usable_by_p161") is not True:reject.append("DECISION_NOT_USABLE_BY_P161")
 if decision.get("normative_eligibility")!="ELIGIBLE_CANDIDATE":reject.append("DECISION_NOT_ELIGIBLE_CANDIDATE")
 b=_map(decision.get("bindings")); policy=_map(decision.get("decision_freshness_policy")); required=_map(policy.get("required_state_hashes"))
 exact={"decision_id":(request.get("normative_decision_id"),decision.get("decision_id")),"decision_hash":(request.get("normative_decision_hash"),decision.get("artifact_hash")),"action_digest":(request.get("action_digest"),_map(decision.get("action_digest")).get("semantic_hash")),"constitutional_snapshot_hash":(request.get("constitutional_snapshot_hash"),b.get("constitutional_snapshot_hash")),"compiled_profile_hash":(request.get("compiled_profile_hash"),b.get("compiled_profile_hash")),"runtime_context_fingerprint":(request.get("runtime_context_fingerprint"),b.get("runtime_context_fingerprint")),"authority_context_ref":(request.get("authority_context_ref"),required.get("authority_context_fingerprint"))}
 for name,(left,right) in exact.items():
  if not _present(left) or not _present(right):unresolved.append("BINDING_UNRESOLVED:"+name)
  elif left!=right:reject.append("BINDING_MISMATCH:"+name)
 if not policy:unresolved.append("DECISION_FRESHNESS_POLICY_MISSING")
 if not required:unresolved.append("FRESHNESS_REQUIRED_STATE_HASHES_MISSING")
 for k,expected in required.items():
  actual=state.get(k)
  if not _present(expected) or not _present(actual):unresolved.append("CURRENT_STATE_UNRESOLVED:"+k)
  elif actual!=expected:revalidate.append("MATERIAL_STATE_DRIFT:"+k)
 if not _present(policy.get("max_age")):unresolved.append("DECISION_MAX_AGE_UNRESOLVED")
 if not persisted:unresolved.append("PERSISTED_STATE_REQUIRED")
 else:
  ps=persisted.get("status"); ph=persisted.get("artifact_hash")
  if not _present(ps) or not _present(ph):unresolved.append("PERSISTED_STATE_UNRESOLVED")
  elif ph!=decision.get("artifact_hash"):reject.append("PERSISTED_ARTIFACT_HASH_MISMATCH")
  elif ps in ("STALE","SUPERSEDED","INVALIDATED","EXPIRED","REVOKED"):revalidate.append("PERSISTED_STATE_NOT_CURRENT:"+str(ps))
  elif ps not in ("SEALED","COMMITTED"):unresolved.append("PERSISTED_STATE_UNKNOWN:"+str(ps))
 if not _scope_narrowing(request,decision):reject.append("REQUEST_SCOPE_NOT_PROVEN_NARROWING")
 if not isinstance(decision.get("normative_preconditions"),list):unresolved.append("PRECONDITIONS_UNRESOLVED")
 if not isinstance(decision.get("normative_postconditions"),list):unresolved.append("POSTCONDITIONS_UNRESOLVED")
 if reject:return _result("REJECTED",reject+revalidate+unresolved,checks,decision,request)
 if revalidate:return _result("RETURN_TO_P160",revalidate+unresolved,checks,decision,request)
 if unresolved:return _result("UNRESOLVED",unresolved,checks,decision,request)
 x=_result("VERIFIED",[],checks,decision,request); x["verification_effect"]="EVIDENCE_ONLY_NOT_AUTHORIZATION"; x.pop("verification_hash"); x["verification_hash"]=canonical_sha256(x); return x
