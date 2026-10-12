"""Governed evidence-effect decision policy. Decision-only: no execution, no authority minting."""
from dataclasses import dataclass, field
from typing import Set
PRIMITIVE="governed_evidence_effect_policy"
SCHEMA="oce.p162.g6.evidence_effect_decision.v1"
ALLOW="ALLOW_EXACT_EVIDENCE_EFFECT"
DENY="DENY_EVIDENCE_EFFECT"
@dataclass(frozen=True)
class EvidenceEffectDecision:
    decision_id: str
    decision: str
    evidence_role: str
    operation_id: str
    target_binding: str
    rationale: str
    provenance: str
    authorization_inference: bool=False
    implementation_authorized: bool=False
    def validate(self):
        for name in ("decision_id","evidence_role","operation_id","target_binding","rationale","provenance"):
            if not isinstance(getattr(self,name),str) or not getattr(self,name).strip(): raise ValueError("missing_or_invalid_"+name)
        if self.decision not in (ALLOW,DENY): raise ValueError("invalid_evidence_effect_decision")
        if self.authorization_inference is not False: raise ValueError("authorization_inference_forbidden")
        if self.implementation_authorized is not False: raise ValueError("implementation_authorized_must_remain_false")
        if not self.target_binding.startswith("filesystem://"): raise ValueError("filesystem_target_binding_required")
        return self
@dataclass
class GovernedEvidenceEffectPolicy:
    _used: Set[str]=field(default_factory=set,init=False,repr=False)
    @property
    def authority_minting(self): return False
    @property
    def execution_performed(self): return False
    def evaluate(self,*,decision,evidence_role,operation_id,target_binding):
        if not isinstance(decision,EvidenceEffectDecision): raise TypeError("EvidenceEffectDecision_required")
        decision.validate()
        if decision.decision_id in self._used: raise RuntimeError("evidence_effect_decision_replay")
        if decision.evidence_role!=evidence_role: raise RuntimeError("evidence_role_mismatch")
        if decision.operation_id!=operation_id: raise RuntimeError("operation_mismatch")
        if decision.target_binding!=target_binding: raise RuntimeError("target_mismatch")
        self._used.add(decision.decision_id)
        if decision.decision!=ALLOW:
            return {"status":"DENIED","decision_id":decision.decision_id,"authorization_created":False,"execution_performed":False}
        return {"status":"EXPLICIT_BOUNDARY_DECISION_CONFIRMED","schema":SCHEMA,"decision_id":decision.decision_id,
                "evidence_role":evidence_role,"operation_id":operation_id,"target_binding":target_binding,
                "authorization_created":False,"authorization_inference":False,"implementation_authorized":False,"execution_performed":False}
