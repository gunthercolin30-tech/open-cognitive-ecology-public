from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Any,Mapping

PRIMITIVE="p161_human_decision_integrity"
VERSION="P161-E-v1"
SCHEMA="oce.p161e.human_decision_integrity_receipt.v1"
BOUNDARIES={"authority_created":False,"approval_created":False,"authorization_created":False,
"authorization_token_created":False,"capability_created":False,"execution_performed":False,"p162_opened":False}

def _m(x): return x if isinstance(x,Mapping) else {}
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return hashlib.sha256(_canon(x).encode()).hexdigest()
def _known(x): return x not in (None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE")

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,
      "distinctions":["HUMAN_IDENTITY!=HUMAN_AUTHORITY","HUMAN_APPROVAL!=HUMAN_DECISION_INTEGRITY",
      "SIGNATURE!=MEANINGFUL_HUMAN_DECISION","HUMAN_DECISION_INTEGRITY!=AUTHORIZATION",
      "HUMAN_DECISION_INTEGRITY!=EXECUTION"],**deepcopy(BOUNDARIES),
      "functional_only":True,"phenomenology_undetermined":True}

def build_human_decision_evidence(**kwargs):
    p=dict(kwargs);p["evidence_hash"]=_hash(p);return p

def evaluate_human_decision_integrity(request:Mapping[str,Any], authority_receipt:Mapping[str,Any],
 evidence_bundle:Mapping[str,Any], human_evidence:Mapping[str,Any], *,
 human_required:bool, expected_human_roles=()):
    req=dict(_m(request));auth=dict(_m(authority_receipt));bundle=dict(_m(evidence_bundle));h=dict(_m(human_evidence))
    checks={};fail=[];unknown=[]

    if not human_required:
        checks["human_required"]=False
        return _receipt("NOT_REQUIRED",[],req,auth,bundle,checks)

    checks["human_required"]=True
    if auth.get("status")!="VALID": fail.append("AUTHORITY_NOT_VALID")
    if bundle.get("status")!="SATISFIED": fail.append("APPROVAL_CONSENT_QUORUM_NOT_SATISFIED")

    required=("evidence_id","human_id","human_role","authorization_request_id","normative_decision_id",
      "action_digest","purpose","target","presentation_hash","decision","decided_at","nonce","evidence_hash")
    if any(not _known(h.get(k)) for k in required):
        unknown.append("HUMAN_DECISION_EVIDENCE_INCOMPLETE")
    else:
        base=dict(h);claimed=base.pop("evidence_hash",None)
        if _hash(base)!=claimed: fail.append("HUMAN_DECISION_EVIDENCE_HASH_INVALID")

    if h.get("actor_kind")!="HUMAN": fail.append("ARTIFICIAL_SUBSTITUTION_FORBIDDEN")
    if expected_human_roles and h.get("human_role") not in set(expected_human_roles):
        fail.append("HUMAN_ROLE_MISMATCH")

    bindings=(("authorization_request_id","authorization_request_id"),
              ("normative_decision_id","normative_decision_id"),
              ("action_digest","action_digest"),("purpose","purpose"),("target","target"))
    for hk,rk in bindings:
        if _known(h.get(hk)) and h.get(hk)!=req.get(rk): fail.append("HUMAN_DECISION_BINDING_MISMATCH")

    bp=bundle.get("checks",{}).get("presentation_hash")
    if bp is None:
        bp=h.get("approval_presentation_hash")
    if not _known(bp): unknown.append("APPROVAL_PRESENTATION_HASH_UNRESOLVED")
    elif _known(h.get("presentation_hash")) and h.get("presentation_hash")!=bp:
        fail.append("PRESENTATION_DRIFT")

    decision=h.get("decision")
    if decision not in ("APPROVE","REJECT"):
        unknown.append("HUMAN_DECISION_NOT_EXPLICIT")
    if h.get("withdrawn") is True: fail.append("HUMAN_DECISION_WITHDRAWN")
    if h.get("identity_verified") is not True: unknown.append("HUMAN_IDENTITY_NOT_VERIFIED")
    if h.get("role_verified") is not True: unknown.append("HUMAN_ROLE_NOT_VERIFIED")
    if h.get("canonical_summary_presented") is not True: unknown.append("CANONICAL_SUMMARY_NOT_CONFIRMED")
    if h.get("material_risks_presented") is not True: unknown.append("MATERIAL_RISKS_NOT_CONFIRMED")
    if h.get("material_objections_presented") is not True: unknown.append("MATERIAL_OBJECTIONS_NOT_CONFIRMED")
    if h.get("alternatives_presented") is not True: unknown.append("ALTERNATIVES_NOT_CONFIRMED")
    if h.get("consequences_understood") is not True: unknown.append("UNDERSTANDING_NOT_CONFIRMED")
    if h.get("ability_to_refuse") is not True: unknown.append("ABILITY_TO_REFUSE_NOT_CONFIRMED")
    if h.get("specific_confirmation") is not True: unknown.append("SPECIFIC_CONFIRMATION_MISSING")
    if h.get("ui_or_model_decided_for_human") is True: fail.append("HUMAN_DECISION_SUBSTITUTED")
    if h.get("material_information_hidden") is True: fail.append("MATERIAL_INFORMATION_HIDDEN")

    status="UNSATISFIED" if fail else ("UNKNOWN" if unknown else "SATISFIED")
    return _receipt(status,fail+unknown,req,auth,bundle,checks)

def _receipt(status,reasons,req,auth,bundle,checks):
    p={"schema":SCHEMA,"version":VERSION,"status":status,"reasons":sorted(set(reasons)),
       "checks":checks,"authorization_request_id":req.get("authorization_request_id"),
       "authority_revalidation_receipt_hash":auth.get("receipt_hash"),
       "approval_evidence_bundle_hash":bundle.get("evidence_bundle_hash"),
       **deepcopy(BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True}
    p["receipt_hash"]=_hash(p);return p
