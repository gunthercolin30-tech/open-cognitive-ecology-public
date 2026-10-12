from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Any,Mapping

PRIMITIVE="p161_authorization_scope_construction"
VERSION="P161-F-v1"
SCHEMA="oce.p161f.authorization_scope_envelope.v1"
BOUNDARIES={"authority_created":False,"approval_created":False,"authorization_created":False,
"authorization_token_created":False,"capability_created":False,"execution_performed":False,"p162_opened":False}

def _m(x): return x if isinstance(x,Mapping) else {}
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return hashlib.sha256(_canon(x).encode()).hexdigest()
def _known(x): return x not in (None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE")
def _set(x):
    if isinstance(x,(list,tuple,set)): return set(x)
    return {x} if _known(x) else set()

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,
      "laws":["TOKEN_SCOPE<=APPROVAL_SCOPE<=NORMATIVE_DECISION_ELIGIBLE_SCOPE",
      "AUTHORIZED_SCOPE=INTERSECTION_ONLY","UNKNOWN_DIMENSION!=UNLIMITED",
      "SCOPE_CONSTRUCTION!=AUTHORIZATION","SCOPE_CONSTRUCTION!=EXECUTION"],
      **deepcopy(BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True}

def construct_authorization_scope(request:Mapping[str,Any], normative_decision:Mapping[str,Any],
 authority_receipt:Mapping[str,Any], evidence_bundle:Mapping[str,Any],
 human_integrity:Mapping[str,Any], *, human_required:bool):
    req=dict(_m(request));nd=dict(_m(normative_decision));auth=dict(_m(authority_receipt))
    ev=dict(_m(evidence_bundle));hi=dict(_m(human_integrity));fail=[];unknown=[];checks={}

    if nd.get("lifecycle")!="SEALED" or nd.get("transaction_state")!="COMMITTED":
        fail.append("NORMATIVE_DECISION_NOT_USABLE")
    if auth.get("status")!="VALID": fail.append("AUTHORITY_NOT_VALID")
    if ev.get("status")!="SATISFIED": fail.append("APPROVAL_CONSENT_QUORUM_NOT_SATISFIED")
    expected_hi="SATISFIED" if human_required else "NOT_REQUIRED"
    if hi.get("status")!=expected_hi: fail.append("HUMAN_INTEGRITY_NOT_SATISFIED")

    if req.get("normative_decision_id")!=nd.get("decision_id"): fail.append("DECISION_ID_MISMATCH")
    if req.get("action_digest")!=nd.get("action_digest"): fail.append("ACTION_DIGEST_MISMATCH")

    requested=_m(req.get("requested_scope"))
    eligible=_m(nd.get("eligible_scope") or nd.get("scope") or _m(nd.get("action")).get("scope"))
    authority=_m(auth.get("effective_scope") or auth.get("scope"))
    approval=_m(ev.get("approved_scope") or ev.get("scope"))

    sources={"requested":requested,"eligible":eligible,"authority":authority,"approval":approval}
    for name,s in sources.items():
        if not s: unknown.append(name.upper()+"_SCOPE_UNRESOLVED")

    dims=sorted(set().union(*(set(s.keys()) for s in sources.values())))
    result={}
    for d in dims:
        vals=[]
        for name,s in sources.items():
            if d not in s or not _known(s.get(d)):
                unknown.append("SCOPE_DIMENSION_UNRESOLVED:"+d+":"+name); vals=[]; break
            vals.append(_set(s[d]))
        if not vals: continue
        inter=set.intersection(*vals)
        if not inter:
            fail.append("EMPTY_SCOPE_INTERSECTION:"+d); continue
        result[d]=sorted(inter)

    # Exact non-scope bindings must remain equal to the sealed decision.
    action=_m(nd.get("action"))
    for k in ("target","purpose"):
        rv=req.get(k); nv=nd.get(k,action.get(k))
        if not _known(rv) or not _known(nv): unknown.append(k.upper()+"_UNRESOLVED")
        elif rv!=nv: fail.append(k.upper()+"_MISMATCH")

    req_caps=_set(req.get("requested_capabilities"))
    nd_caps=_set(nd.get("eligible_capabilities") or action.get("capabilities"))
    auth_caps=_set(auth.get("effective_capabilities") or auth.get("capabilities"))
    if not req_caps or not nd_caps or not auth_caps:
        unknown.append("CAPABILITY_BOUND_UNRESOLVED"); caps=[]
    else:
        caps=sorted(req_caps & nd_caps & auth_caps)
        if not caps: fail.append("EMPTY_CAPABILITY_INTERSECTION")

    validity=_m(req.get("requested_validity"))
    temporal=_m(auth.get("effective_temporal_bounds") or auth.get("temporal_bounds"))
    if not validity or not temporal:
        unknown.append("TEMPORAL_BOUND_UNRESOLVED")
    else:
        vf=validity.get("not_before"); vu=validity.get("not_after")
        af=temporal.get("not_before"); au=temporal.get("not_after")
        if not all(_known(x) for x in (vf,vu,af,au)): unknown.append("TEMPORAL_BOUND_UNRESOLVED")
        elif vf<af or vu>au or vf>vu: fail.append("REQUESTED_VALIDITY_OUTSIDE_AUTHORITY")

    status="UNSATISFIED" if fail else ("UNKNOWN" if unknown else "CONSTRUCTED")
    p={"schema":SCHEMA,"version":VERSION,"status":status,"reasons":sorted(set(fail+unknown)),
       "authorization_request_id":req.get("authorization_request_id"),"normative_decision_id":nd.get("decision_id"),
       "scope":result if status=="CONSTRUCTED" else None,
       "capabilities":caps if status=="CONSTRUCTED" else None,
       "target":req.get("target") if status=="CONSTRUCTED" else None,
       "purpose":req.get("purpose") if status=="CONSTRUCTED" else None,
       "validity":validity if status=="CONSTRUCTED" else None,
       "requested_use_policy":req.get("requested_use_policy") if status=="CONSTRUCTED" else None,
       "source_hashes":{"normative_decision":nd.get("artifact_hash"),
         "authority_receipt":auth.get("receipt_hash"),"evidence_bundle":ev.get("evidence_bundle_hash"),
         "human_integrity":hi.get("receipt_hash")},
       "checks":checks,**deepcopy(BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True}
    p["scope_envelope_hash"]=_hash(p);return p

# P161_CANONICAL_COMPLETION_AFGH_V1
def intersect_constraint_tuples(*collections):
    if not collections:return []
    sets=[{tuple(sorted(x.items())) for x in col} for col in collections]
    common=set.intersection(*sets)
    return [dict(x) for x in sorted(common)]
def validate_active_authorization_composition(candidate,active_authorizations):
    if candidate.get("environment") is None:return {"status":"UNKNOWN","reason":"ENVIRONMENT_UNKNOWN"}
    if not candidate.get("constraint_tuples"):return {"status":"UNKNOWN","reason":"CONSTRAINT_TUPLE_UNKNOWN"}
    for a in active_authorizations or []:
        if a.get("environment")==candidate.get("environment") and a.get("target")==candidate.get("target") and a.get("reservation") and a.get("reservation")==candidate.get("reservation"):
            return {"status":"UNSATISFIED","reason":"ACTIVE_AUTHORIZATION_RESERVATION_COLLISION"}
    return {"status":"SATISFIED","budget":candidate.get("budget",{}),"reservation":candidate.get("reservation"),"environment":candidate["environment"]}
