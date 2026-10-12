from dataclasses import dataclass
from typing import Any
from ontology.governed_evidence_effect_policy import GovernedEvidenceEffectPolicy, EvidenceEffectDecision
@dataclass
class GovernedEvidenceFilesystemBridge:
    policy: GovernedEvidenceEffectPolicy
    filesystem_context: Any
    @property
    def authority_minting(self): return False
    def execute_path(self, *, decision, evidence_role, slot, operation_id, path, payload=None):
        if not isinstance(decision,EvidenceEffectDecision): raise TypeError("EvidenceEffectDecision_required")
        root_id=getattr(self.filesystem_context,"root_id",None)
        if not isinstance(root_id,str) or not root_id: raise RuntimeError("filesystem_context_root_id_required")
        rel=str(path)
        if rel.startswith("/") or ".." in rel.split("/"): raise RuntimeError("unsafe_relative_path")
        target="filesystem://%s/%s"%(root_id,rel.lstrip("/"))
        gate=self.policy.evaluate(decision=decision,evidence_role=evidence_role,operation_id=operation_id,target_binding=target)
        if gate.get("status")!="EXPLICIT_BOUNDARY_DECISION_CONFIRMED":
            return {"status":"DENIED","decision_id":decision.decision_id,"authorization_created":False,"execution_performed":False}
        result=self.filesystem_context.execute_path(slot=slot,operation_id=operation_id,path=path,payload=payload)
        return {"status":"EVIDENCE_EFFECT_CONFIRMED","decision_id":decision.decision_id,
          "authorization_created":False,"authorization_inference":False,
          "implementation_authorized":False,"execution_performed":True,"effect_result":result}
