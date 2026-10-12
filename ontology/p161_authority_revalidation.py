from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping

PRIMITIVE="p161_authority_revalidation"
VERSION="P161-C-v1"
SCHEMA="oce.p161c.authority_revalidation_receipt.v1"
STATUSES=("VALID","INVALID","EXPIRED","REVOKED","UNAVAILABLE","UNDETERMINED","CONFLICTING","SCOPE_INSUFFICIENT","PURPOSE_INSUFFICIENT","CLASS_INSUFFICIENT","SEPARATION_OF_DUTIES_VIOLATION","QUORUM_INCOMPLETE","HUMAN_RESERVED_UNAVAILABLE","SUCCESSION_INVALID","RETURN_TO_P160")
BOUNDARIES={"authority_created":False,"approval_created":False,"authorization_created":False,"authorization_token_created":False,"capability_created":False,"execution_performed":False,"p162_opened":False}
FUNCTIONAL={"functional_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}

def _m(v): return dict(v) if isinstance(v,Mapping) else {}
def _l(v): return list(v) if isinstance(v,(list,tuple,set)) else []
def _present(v): return v not in (None,"",[],{},"UNKNOWN","UNRESOLVED","INCONCLUSIVE")
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_sha256(v): return sha256(_canon(v).encode()).hexdigest()
def _utc(v):
    if not isinstance(v,str) or not v: return None
    try:
        s=v[:-1]+"+00:00" if v.endswith("Z") else v
        d=datetime.fromisoformat(s)
        if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception: return None

def _subset(child,parent):
    c,p=_m(child),_m(parent)
    for k,v in c.items():
        if k not in p: return False
        a=p[k]
        if isinstance(v,(list,tuple,set)) and isinstance(a,(list,tuple,set)):
            if not set(v).issubset(set(a)): return False
        elif v!=a: return False
    return True

def _receipt(status,reasons,req,verification,resolution,checks,holders=()):
    x={"schema":SCHEMA,"version":VERSION,"status":status,"reasons":sorted(set(reasons)),"authorization_request_id":req.get("authorization_request_id"),"normative_decision_verification_hash":verification.get("verification_hash"),"p160_authority_resolution_hash":resolution.get("resolution_hash"),"authority_context_fingerprint":resolution.get("authority_context_fingerprint"),"effective_holders":deepcopy(list(holders)),"checks":deepcopy(checks),"effect":"EVIDENCE_ONLY_NOT_APPROVAL_OR_AUTHORIZATION",**BOUNDARIES,**FUNCTIONAL}
    x["receipt_hash"]=canonical_sha256(x); x["receipt_id"]="p161c-"+x["receipt_hash"][:24]
    return x

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"statuses":STATUSES,"scope":"P161-C_ONLY","reuses":["P160-F authority dimensionality","P095 human mandate windows/delegation semantics"],"doctrines":["AUTHORITY != APPROVAL != AUTHORIZATION","INTERSECTION_NEVER_UNION","HUMAN_ABSENCE_NEVER_CREATES_ARTIFICIAL_SUCCESSION","UNKNOWN_NEVER_SATISFIES_POSITIVE_PRECONDITION"],**BOUNDARIES,**FUNCTIONAL}

def revalidate_authority(authorization_request:Mapping[str,Any], normative_verification:Mapping[str,Any], p160_authority_resolution:Mapping[str,Any], *, live_authority_context:Mapping[str,Any], now:str):
    req=_m(authorization_request); ver=_m(normative_verification); res=_m(p160_authority_resolution); live=_m(live_authority_context); checks={}; reasons=[]
    if ver.get("status")!="VERIFIED": return _receipt("RETURN_TO_P160",["NORMATIVE_DECISION_NOT_VERIFIED"],req,ver,res,checks)
    if res.get("authority_status")!="VALID": return _receipt("RETURN_TO_P160",["P160_AUTHORITY_RESOLUTION_NOT_VALID"],req,ver,res,checks)
    expected=res.get("authority_context_fingerprint"); actual=live.get("authority_context_fingerprint")
    checks["authority_context_exact"]=_present(expected) and expected==actual
    if not _present(expected) or not _present(actual): return _receipt("UNDETERMINED",["AUTHORITY_CONTEXT_UNRESOLVED"],req,ver,res,checks)
    if expected!=actual: return _receipt("RETURN_TO_P160",["AUTHORITY_CONTEXT_DRIFT"],req,ver,res,checks)
    required=_m(res.get("required_authority")); holders=[_m(x) for x in _l(live.get("holders"))]; byid={h.get("holder_id"):h for h in holders if h.get("holder_id")}
    candidates=[]
    for old in _l(res.get("candidate_holders")):
        oid=_m(old).get("holder_id"); h=byid.get(oid)
        if not h: continue
        st=h.get("status","UNKNOWN")
        if st=="REVOKED" or h.get("revoked") is True: continue
        if st=="EXPIRED" or h.get("expired") is True: continue
        if st!="ACTIVE": continue
        candidates.append(h)
    if not candidates:
        if res.get("human_reserved") is True: return _receipt("HUMAN_RESERVED_UNAVAILABLE",["NO_CURRENT_HUMAN_RESERVED_HOLDER"],req,ver,res,checks)
        return _receipt("UNAVAILABLE",["NO_CURRENT_ELIGIBLE_HOLDER"],req,ver,res,checks)
    cls=required.get("authority_class")
    class_ok=[h for h in candidates if cls in set(_l(h.get("authority_classes")))]
    if not class_ok: return _receipt("CLASS_INSUFFICIENT",["REQUIRED_AUTHORITY_CLASS_MISSING"],req,ver,res,checks,candidates)
    scope=_m(req.get("requested_scope")); scoped=[h for h in class_ok if _subset(scope,_m(h.get("scope")))]
    if not scoped: return _receipt("SCOPE_INSUFFICIENT",["REQUEST_SCOPE_OUTSIDE_CURRENT_AUTHORITY"],req,ver,res,checks,class_ok)
    purpose=req.get("purpose") or required.get("purpose")
    purposed=[h for h in scoped if not purpose or purpose in set(_l(h.get("purposes")))]
    if not purposed: return _receipt("PURPOSE_INSUFFICIENT",["REQUEST_PURPOSE_OUTSIDE_CURRENT_AUTHORITY"],req,ver,res,checks,scoped)
    t=_utc(now)
    if t is None: return _receipt("UNDETERMINED",["CURRENT_TIME_UNRESOLVED"],req,ver,res,checks,purposed)
    temporal=_m(res.get("temporal_bounds")); vf=_utc(temporal.get("valid_from")); ex=_utc(temporal.get("expires_at"))
    if temporal.get("valid_from") and vf is None or temporal.get("expires_at") and ex is None: return _receipt("UNDETERMINED",["AUTHORITY_TIME_BOUND_UNRESOLVED"],req,ver,res,checks,purposed)
    if vf and t<vf: return _receipt("UNAVAILABLE",["AUTHORITY_NOT_YET_VALID"],req,ver,res,checks,purposed)
    if ex and t>=ex: return _receipt("EXPIRED",["AUTHORITY_EXPIRED"],req,ver,res,checks,purposed)
    current=[]
    for h in purposed:
        hvf=_utc(h.get("valid_from")); hexp=_utc(h.get("expires_at") or h.get("valid_until"))
        if h.get("valid_from") and hvf is None or (h.get("expires_at") or h.get("valid_until")) and hexp is None: continue
        if hvf and t<hvf: continue
        if hexp and t>=hexp: continue
        current.append(h)
    if not current: return _receipt("EXPIRED",["ALL_HOLDER_MANDATES_OUTSIDE_CURRENT_WINDOW"],req,ver,res,checks,purposed)
    if res.get("human_reserved") is True:
        current=[h for h in current if h.get("kind")=="HUMAN"]
        if not current:
            return _receipt("HUMAN_RESERVED_UNAVAILABLE",["NO_CURRENT_HUMAN_RESERVED_HOLDER"],req,ver,res,checks)
    # delegation may only narrow parent class/scope/time; unknown parent is not accepted
    for h in current:
        pid=h.get("parent_authority_id")
        if pid:
            parent=byid.get(pid)
            if not parent: return _receipt("UNDETERMINED",["DELEGATION_PARENT_UNRESOLVED"],req,ver,res,checks,current)
            if not set(_l(h.get("authority_classes"))).issubset(set(_l(parent.get("authority_classes")))) or not _subset(_m(h.get("scope")),_m(parent.get("scope"))): return _receipt("INVALID",["DELEGATION_AMPLIFICATION"],req,ver,res,checks,current)
    sod=_m(res.get("separation_of_duties")); pairs=_l(sod.get("forbidden_role_pairs"))
    for h in current:
        roles=set(_l(h.get("roles")))
        for pair in pairs:
            if isinstance(pair,(list,tuple)) and len(pair)==2 and pair[0] in roles and pair[1] in roles: return _receipt("SEPARATION_OF_DUTIES_VIOLATION",["FORBIDDEN_ROLE_PAIR"],req,ver,res,checks,current)
    q=_m(res.get("quorum")); n=q.get("n",1); required_roles=set(_l(q.get("required_roles"))); have=set().union(*(set(_l(h.get("roles"))) for h in current)) if current else set()
    if isinstance(n,bool) or not isinstance(n,int) or n<1: return _receipt("UNDETERMINED",["QUORUM_RULE_UNRESOLVED"],req,ver,res,checks,current)
    if len({h.get("holder_id") for h in current})<n or not required_roles.issubset(have): return _receipt("QUORUM_INCOMPLETE",["CURRENT_QUORUM_OR_ROLE_INCOMPLETE"],req,ver,res,checks,current)
    checks.update({"class":True,"scope":True,"purpose":True,"time":True,"delegation":True,"separation_of_duties":True,"quorum":True,"human_reserved":True})
    return _receipt("VALID",[],req,ver,res,checks,current)
