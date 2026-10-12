from __future__ import annotations
import hashlib, json
from copy import deepcopy
from typing import Any, Mapping, Sequence

PRIMITIVE="p161_approval_consent_quorum_evidence"
VERSION="P161-D-v1"
SCHEMA="oce.p161d.approval_consent_quorum_evidence.v1"

BOUNDARIES={"authority_created":False,"authorization_created":False,
"authorization_token_created":False,"capability_created":False,
"execution_performed":False,"p162_opened":False}

VALID_REQ={"SATISFIED","UNSATISFIED","UNKNOWN","NOT_APPLICABLE","REVOKED","EXPIRED"}
VALID_CONSENT={"EXPLICIT","INFORMED","DELEGATED","WITHDRAWN","NOT_REQUIRED"}

def _m(x): return x if isinstance(x,Mapping) else {}
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return hashlib.sha256(_canon(x).encode()).hexdigest()
def _present(x): return x not in (None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE")

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,
      "distinctions":["AUTHORITY!=APPROVAL","APPROVAL!=CONSENT","CONSENT!=QUORUM",
      "QUORUM!=SIGNATURE","SIGNATURE!=TOKEN"],
      **deepcopy(BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True}

def _result(status,reasons,request,authority,checks):
    p={"schema":SCHEMA,"version":VERSION,"status":status,
       "reasons":sorted(set(reasons)),"checks":checks,
       "authorization_request_id":request.get("authorization_request_id"),
       "authority_revalidation_receipt_hash":authority.get("receipt_hash"),
       **deepcopy(BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True}
    p["evidence_bundle_hash"]=_hash(p); return p

def validate_evidence(request:Mapping[str,Any], authority_receipt:Mapping[str,Any],
                      approval_evidence:Sequence[Mapping[str,Any]], *,
                      requirements:Sequence[Mapping[str,Any]],
                      eligible_participants:Sequence[str]=(),
                      quorum_rule:Mapping[str,Any]|None=None,
                      consent_requirement:Mapping[str,Any]|None=None):
    req=dict(_m(request)); auth=dict(_m(authority_receipt))
    checks={}; fail=[]; unknown=[]

    checks["authority_revalidated"]=auth.get("status")=="VALID"
    if not checks["authority_revalidated"]: fail.append("AUTHORITY_NOT_CURRENTLY_VALID")

    approvals=[]
    seen=set()
    for raw in approval_evidence:
        e=dict(_m(raw)); eid=e.get("evidence_id")
        needed=("evidence_id","participant_id","authorization_request_id","normative_decision_id",
                "action_digest","purpose","target","scope","presentation_hash","expression",
                "expressed_at","nonce","evidence_hash")
        if any(not _present(e.get(k)) for k in needed):
            unknown.append("APPROVAL_EVIDENCE_INCOMPLETE"); continue
        base=dict(e); claimed=base.pop("evidence_hash",None)
        if _hash(base)!=claimed:
            fail.append("APPROVAL_EVIDENCE_HASH_INVALID"); continue
        if e["authorization_request_id"]!=req.get("authorization_request_id") or            e["normative_decision_id"]!=req.get("normative_decision_id") or            e["action_digest"]!=req.get("action_digest") or e["purpose"]!=req.get("purpose") or            e["target"]!=req.get("target"):
            fail.append("APPROVAL_BINDING_MISMATCH"); continue
        if e.get("revoked") is True:
            fail.append("APPROVAL_REVOKED"); continue
        if e.get("expired") is True:
            fail.append("APPROVAL_EXPIRED"); continue
        if eid in seen:
            fail.append("DUPLICATE_APPROVAL_EVIDENCE"); continue
        seen.add(eid); approvals.append(e)

    checks["approval_evidence_count"]=len(approvals)

    # Requirements do not compensate for one another.
    states={}
    for r in requirements:
        rid=r.get("requirement_id"); state=r.get("state","UNKNOWN")
        if state not in VALID_REQ: state="UNKNOWN"
        states[rid]=state
        if state in ("UNSATISFIED","REVOKED","EXPIRED"): fail.append("REQUIREMENT_"+state)
        elif state=="UNKNOWN": unknown.append("REQUIREMENT_UNKNOWN")
    checks["requirement_states"]=states

    cr=dict(_m(consent_requirement))
    if cr:
        cstate=cr.get("state","UNKNOWN")
        checks["consent_state"]=cstate
        if cstate not in VALID_CONSENT: unknown.append("CONSENT_UNKNOWN")
        elif cstate=="WITHDRAWN": fail.append("CONSENT_WITHDRAWN")
        elif cstate not in ("EXPLICIT","INFORMED","DELEGATED","NOT_REQUIRED"):
            unknown.append("CONSENT_UNKNOWN")
        if cstate=="DELEGATED" and cr.get("delegation_valid") is not True:
            fail.append("CONSENT_DELEGATION_INVALID")
    else:
        checks["consent_state"]="UNKNOWN"
        unknown.append("CONSENT_REQUIREMENT_UNRESOLVED")

    qr=dict(_m(quorum_rule))
    if qr:
        qtype=qr.get("type")
        needed=int(qr.get("required",0) or 0)
        elig=set(eligible_participants)
        counted=[]
        aliases=set()
        veto=False
        presentation=None
        for e in approvals:
            pid=e.get("participant_id")
            if pid not in elig: continue
            alias=e.get("participant_alias") or pid
            if alias in aliases: continue
            aliases.add(alias)
            if presentation is None: presentation=e.get("presentation_hash")
            if e.get("presentation_hash")!=presentation:
                fail.append("QUORUM_PRESENTATION_MISMATCH"); continue
            if e.get("separation_of_duties_ok") is not True:
                fail.append("SEPARATION_OF_DUTIES_VIOLATION"); continue
            if e.get("veto") is True and qr.get("veto_defined") is True: veto=True
            if e.get("expression")=="APPROVE": counted.append(pid)
        checks["quorum_count"]=len(counted)
        checks["quorum_required"]=needed
        if qtype not in ("N_OF_M","UNANIMOUS","SINGLE_APPROVER"):
            unknown.append("QUORUM_RULE_UNKNOWN")
        elif veto: fail.append("DEFINED_VETO_PRESENT")
        elif len(counted)<needed: fail.append("QUORUM_INCOMPLETE")
    else:
        checks["quorum_count"]=None
        unknown.append("QUORUM_RULE_UNRESOLVED")

    if fail: return _result("UNSATISFIED",fail+unknown,req,auth,checks)
    if unknown: return _result("UNKNOWN",unknown,req,auth,checks)
    return _result("SATISFIED",[],req,auth,checks)

def build_approval_evidence(**kwargs):
    p=dict(kwargs); p["evidence_hash"]=_hash(p); return p
