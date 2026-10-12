from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping
from ontology import normative_hierarchy, normative_conflict_resolution
from ontology import constitutional_non_circumvention, constitution_registry
from ontology import constitutional_epistemic_pluralism

PRIMITIVE="constitutional_emergency_context"
VERSION="1.0.0-p102"
SCHEMA_VERSION="oce.p102.constitutional_emergency_context.v1"
SCOPE="P102_ONLY"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
EXECUTION_DEPENDENCIES=("P101","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENCES=("R20","R21","A-CANON","4B","4C","4D","4E")
REUSED_PRIMITIVES=("normative_hierarchy","normative_conflict_resolution","constitutional_non_circumvention","constitution_registry","constitution_operational","human_reserved_authority_registry","human_individual_constitutional_relation","constitutional_epistemic_pluralism")
REQUIRED_FIELDS=("emergency_id","reason","trigger","authority_ref","scope","start","end","affected_rules","actions","evidence_ref","post_event_review_ref")
FORBIDDEN_AFFECTED_RULES=("GENESIS","DNA_H","DNA_L0","DNA_FUNDAMENTAL")
FORBIDDEN_AUTHORITY_BASES=("EMERGENCY","URGENCY","INTELLIGENCE","PERFORMANCE","WEALTH","REPUTATION","MAJORITY")

def _present(v):
    return v is not None and str(v).strip().upper() not in ("","UNKNOWN","NONE")

def _dt(v):
    try:
        s=str(v).strip()
        if s.endswith("Z"): s=s[:-1]+"+00:00"
        d=datetime.fromisoformat(s)
        if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None

def _result(status,reason,action,ctx=None,**extra):
    r={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,"action":action,
       "authorization_created":False,"execution_permitted":False,
       "p103_appeal_override_implemented":False,"p104_decision_ledger_persisted":False,
       "runtime_enforcement_p155_p166_proven":False,"real_execution_enabled":False,
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    if isinstance(ctx,Mapping):
        stable={k:ctx.get(k) for k in REQUIRED_FIELDS if k in ctx}
        r["evidence_event_id"]="p102:"+sha256(json.dumps(stable,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:24]
    r.update(extra); return r

def validate_context(ctx,*,now=None,normative_status=PASS,influence_status=PASS,
                     recommendation="ACTIVATE_EMERGENCY_CONTEXT",decision="APPROVE",authorization="GRANT"):
    if not isinstance(ctx,Mapping): return _result(UNDETERMINED,"EMERGENCY_CONTEXT_NOT_MAPPING","ABSTAIN_AND_ESCALATE")
    missing=tuple(k for k in REQUIRED_FIELDS if k not in ctx)
    if missing: return _result(UNDETERMINED,"REQUIRED_FIELDS_MISSING","ABSTAIN_AND_ESCALATE",ctx,missing_fields=missing)
    unknown=tuple(k for k in REQUIRED_FIELDS if not _present(ctx.get(k)))
    if unknown: return _result(UNDETERMINED,"REQUIRED_FIELDS_UNKNOWN","ABSTAIN_AND_ESCALATE",ctx,unknown_fields=unknown)
    if not isinstance(ctx.get("affected_rules"),(list,tuple)) or not isinstance(ctx.get("actions"),(list,tuple)):
        return _result(UNDETERMINED,"RULES_OR_ACTIONS_NOT_SEQUENCE","ABSTAIN_AND_ESCALATE",ctx)
    if not ctx["affected_rules"] or not ctx["actions"]:
        return _result(UNDETERMINED,"RULES_OR_ACTIONS_EMPTY","ABSTAIN_AND_ESCALATE",ctx)
    start,end=_dt(ctx["start"]),_dt(ctx["end"]); current=_dt(now) if now is not None else start
    if start is None or end is None or current is None: return _result(UNDETERMINED,"INVALID_TIME_BOUNDARY","ABSTAIN_AND_ESCALATE",ctx)
    if end<=start: return _result(FAIL,"NON_POSITIVE_EMERGENCY_DURATION","BLOCK",ctx)
    if current<start: return _result(UNDETERMINED,"EMERGENCY_NOT_YET_ACTIVE","ABSTAIN_AND_ESCALATE",ctx)
    if current>=end: return _result(FAIL,"EMERGENCY_EXPIRED","EXPIRE_AND_BLOCK",ctx,expired=True)
    affected={str(x).strip().upper().replace("-","_") for x in ctx["affected_rules"]}
    if affected.intersection(FORBIDDEN_AFFECTED_RULES):
        return _result(FAIL,"DNA_FUNDAMENTAL_OR_CONSTITUTIVE_RULE_CANNOT_BE_ERASED","BLOCK",ctx)
    basis=str(ctx.get("authority_basis","EXISTING_CONSTITUTIONAL_AUTHORITY")).strip().upper()
    if basis in FORBIDDEN_AUTHORITY_BASES: return _result(FAIL,"EMERGENCY_CANNOT_CREATE_AUTHORITY","BLOCK",ctx)
    ns=str(normative_status).upper()
    if ns==CONFLICT: return _result(CONFLICT,"UNRESOLVED_NORMATIVE_CONFLICT","ABSTAIN_AND_ESCALATE",ctx)
    if ns!=PASS: return _result(UNDETERMINED,"NORMATIVE_STATUS_NOT_PROVEN","ABSTAIN_AND_ESCALATE",ctx)
    if str(influence_status).upper()!=PASS: return _result(FAIL,"INFLUENCE_CANNOT_EXPAND_EMERGENCY_AUTHORITY","BLOCK",ctx)
    if recommendation!="ACTIVATE_EMERGENCY_CONTEXT": return _result(FAIL,"RECOMMENDATION_NOT_ACTIVATE","BLOCK",ctx)
    if decision!="APPROVE": return _result(FAIL,"DECISION_NOT_APPROVED","BLOCK",ctx)
    if authorization!="GRANT": return _result(FAIL,"AUTHORIZATION_NOT_GRANTED","BLOCK",ctx)
    renewal=int(ctx.get("renewal_count",0) or 0)
    if renewal>0 and (not _present(ctx.get("renewal_authorization_ref")) or not _present(ctx.get("renewal_justification"))):
        return _result(FAIL,"RENEWAL_REQUIRES_NEW_AUTHORIZATION_AND_JUSTIFICATION","BLOCK",ctx)
    return _result(PASS,"BOUNDED_EMERGENCY_CONTEXT_ELIGIBLE","EMERGENCY_CONTEXT_ACTIVE",ctx,
      active=True,expired=False,start=start.isoformat(),end=end.isoformat(),expiration_mandatory=True,
      renewal_requires_new_authorization=True,dna_fundamental_preserved=True,
      post_event_review_required=True,audit_required=True,rollback_required_if_mutated=True)

def validate_reuse_contract():
    h=normative_hierarchy.validate_hierarchy(); n=normative_conflict_resolution.validate_contract()
    c=constitutional_non_circumvention.validate_contract(); r=constitution_registry.validate_registry()
    p=constitutional_epistemic_pluralism.p101_manifest()
    ok=(h.get("status")==PASS and n.get("status")==PASS and c.get("status")==PASS and r.get("status")==PASS
        and p.get("boundaries",{}).get("does_not_implement_p102") is True)
    return {"status":PASS if ok else FAIL,"p101_boundary_reused":p.get("boundaries",{}).get("does_not_implement_p102") is True,
      "authorization_created":False,"execution_permitted":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def p102_manifest():
    return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,
      "execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_references":TRANSVERSAL_REFERENCES,
      "reused_primitives":REUSED_PRIMITIVES,"required_fields":REQUIRED_FIELDS,
      "rules":{"expiration_mandatory":True,"permanent_emergency_forbidden":True,"dna_fundamental_cannot_be_erased":True,
       "renewal_requires_new_authorization_and_justification":True,"recommendation_decision_authorization_execution_separated":True,
       "emergency_does_not_create_authority":True,"post_event_review_required":True},
      "boundaries":{"does_not_implement_p103_appeal_override":True,"does_not_persist_p104_decision_ledger":True,
       "does_not_prove_runtime_enforcement_p155_p166":True,"real_execution_enabled":False},
      "functional_conclusion_only":True,"phenomenology_undetermined":True})
