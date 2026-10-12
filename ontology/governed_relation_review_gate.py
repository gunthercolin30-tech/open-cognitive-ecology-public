\
"""AY1-D1c — governed review of documentary relation candidates.

Validates explicit review decisions. It never persists validated relations.
"""
from __future__ import annotations
import hashlib, json, math, unicodedata
from dataclasses import dataclass
from typing import Any, Mapping

PRIMITIVE="GOVERNED_RELATION_REVIEW_GATE"
STATUS_READY="GOVERNED_RELATION_REVIEW_READY"
STATUS_DEGRADED="GOVERNED_RELATION_REVIEW_DEGRADED"
ALLOWED_DECISIONS={"approve","reject","request_revision","abstain"}
ALLOWED_RELATIONS={"supports","requires","extends","generalizes","specializes","contradicts"}
DEFAULT_ROLES={"human_reviewer","scientific_reviewer","theory_governance_reviewer","principal_investigator"}

def _canon(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v:Any)->str:return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _norm(v:Any)->str:return unicodedata.normalize("NFC",str(v or "")).strip()
def _confidence(v:Any)->float:
    try:n=float(v)
    except (TypeError,ValueError) as e:raise ValueError("candidate confidence must be numeric") from e
    if not math.isfinite(n) or not 0<=n<=1:raise ValueError("candidate confidence must be finite in [0,1]")
    return round(n,12)

def candidate_payload_hash(candidate:Mapping[str,Any])->str:
    core={k:candidate.get(k) for k in ("candidate_id","source","target","relation","confidence","evidence","requires_review","validated","auto_promotion_forbidden","provenance")}
    return _sha(core)

def evidence_payload_hash(evidence_records:list[Mapping[str,Any]])->str:
    normalized=sorted((dict(x) for x in evidence_records),key=lambda x:_canon(x))
    return _sha(normalized)

@dataclass
class GovernedRelationReviewGate:
    allowed_roles:set[str]|None=None
    def __post_init__(self):self.allowed_roles=set(self.allowed_roles or DEFAULT_ROLES)
    def step(self,inputs:Mapping[str,Any]|None=None,persist:bool=False)->dict[str,Any]:
        if persist: raise RuntimeError("AY1-D1c review gate never persists; use validated_relation_registry")
        supplied=dict(inputs or {})
        candidate=supplied.get("candidate")
        decision=supplied.get("decision")
        evidence=supplied.get("evidence_records",[])
        if not isinstance(candidate,Mapping):raise TypeError("candidate must be a mapping")
        if not isinstance(decision,Mapping):raise TypeError("decision must be a mapping")
        if not isinstance(evidence,list) or not all(isinstance(x,Mapping) for x in evidence):raise TypeError("evidence_records must be a list of mappings")
        cid=_norm(candidate.get("candidate_id")); source=_norm(candidate.get("source")); target=_norm(candidate.get("target")); relation=_norm(candidate.get("relation")).lower()
        if not cid or not source or not target:raise ValueError("candidate identity incomplete")
        if source==target:raise ValueError("self relation forbidden")
        if relation not in ALLOWED_RELATIONS:raise ValueError("unsupported relation")
        _confidence(candidate.get("confidence",0))
        if candidate.get("requires_review") is not True or candidate.get("validated") is not False or candidate.get("auto_promotion_forbidden") is not True:raise ValueError("candidate governance flags invalid")
        evidence_ids=sorted({_norm(x) for x in candidate.get("evidence",[]) if _norm(x)})
        supplied_ids=sorted({_norm(x.get("evidence_id")) for x in evidence if _norm(x.get("evidence_id"))})
        if not evidence_ids or not set(evidence_ids).issubset(set(supplied_ids)):raise ValueError("candidate evidence missing")
        d=_norm(decision.get("decision")).lower(); did=_norm(decision.get("decision_id")); reviewer=_norm(decision.get("reviewer_id")); role=_norm(decision.get("reviewer_role")); rationale=_norm(decision.get("rationale"))
        if d not in ALLOWED_DECISIONS:raise ValueError("unsupported decision")
        if not did or not reviewer or not rationale:raise ValueError("decision_id, reviewer_id and rationale are required")
        if role not in self.allowed_roles:raise PermissionError("reviewer role not authorized")
        if _norm(decision.get("candidate_id"))!=cid:raise ValueError("decision candidate mismatch")
        confirmed={"source":_norm(decision.get("confirmed_source")),"target":_norm(decision.get("confirmed_target")),"relation":_norm(decision.get("confirmed_relation")).lower()}
        if d=="approve" and confirmed!={"source":source,"target":target,"relation":relation}:raise ValueError("approval must explicitly confirm source, target and relation")
        expected_cph=candidate_payload_hash(candidate); expected_eph=evidence_payload_hash(evidence)
        if _norm(decision.get("candidate_payload_hash"))!=expected_cph:raise ValueError("candidate payload hash mismatch")
        if _norm(decision.get("evidence_payload_hash"))!=expected_eph:raise ValueError("evidence payload hash mismatch")
        core={"decision_id":did,"candidate_id":cid,"decision":d,"reviewer_id":reviewer,"reviewer_role":role,"rationale":rationale,"confirmed_source":confirmed["source"],"confirmed_target":confirmed["target"],"confirmed_relation":confirmed["relation"],"confirmed_evidence_ids":evidence_ids,"candidate_payload_hash":expected_cph,"evidence_payload_hash":expected_eph}
        record={**core,"decision_hash":_sha(core),"machine_actionable":True,"approved":d=="approve","functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
        return {"primitive":PRIMITIVE,"status":STATUS_READY,"review_record":record,"approval_authorized":d=="approve","registry_write_performed":False,"review_hash":record["decision_hash"],"functional_conclusion_only":True,"phenomenology_undetermined":True}
