import pytest
from ontology.governed_evidence_effect_policy import GovernedEvidenceEffectPolicy,EvidenceEffectDecision,ALLOW,DENY
def d(**kw):
    x=dict(decision_id="d1",decision=ALLOW,evidence_role="EVIDENCE_REPORT_EXPORT",operation_id="FS_APPEND_BYTES",target_binding="filesystem://r/evidence/log.jsonl",rationale="explicit bounded evidence persistence decision",provenance="test-governance")
    x.update(kw); return EvidenceEffectDecision(**x)
def test_exact_allow_is_decision_only():
    p=GovernedEvidenceEffectPolicy(); x=d(); r=p.evaluate(decision=x,evidence_role=x.evidence_role,operation_id=x.operation_id,target_binding=x.target_binding)
    assert r["status"]=="EXPLICIT_BOUNDARY_DECISION_CONFIRMED" and r["authorization_created"] is False and r["implementation_authorized"] is False and r["execution_performed"] is False
    assert p.authority_minting is False and p.execution_performed is False
def test_implementation_authorized_forbidden():
    with pytest.raises(ValueError,match="implementation_authorized"): d(implementation_authorized=True).validate()
def test_authorization_inference_forbidden():
    with pytest.raises(ValueError,match="authorization_inference"): d(authorization_inference=True).validate()
@pytest.mark.parametrize("field,value,match",[("evidence_role","OTHER","evidence_role_mismatch"),("operation_id","FS_REMOVE_FILE","operation_mismatch"),("target_binding","filesystem://r/other","target_mismatch")])
def test_exact_binding(field,value,match):
    p=GovernedEvidenceEffectPolicy(); x=d(); vals=dict(evidence_role=x.evidence_role,operation_id=x.operation_id,target_binding=x.target_binding); vals[field]=value
    with pytest.raises(RuntimeError,match=match): p.evaluate(decision=x,**vals)
def test_replay_forbidden():
    p=GovernedEvidenceEffectPolicy(); x=d(); vals=dict(evidence_role=x.evidence_role,operation_id=x.operation_id,target_binding=x.target_binding); p.evaluate(decision=x,**vals)
    with pytest.raises(RuntimeError,match="replay"): p.evaluate(decision=x,**vals)
def test_explicit_deny_nonexecuting():
    p=GovernedEvidenceEffectPolicy(); x=d(decision=DENY); r=p.evaluate(decision=x,evidence_role=x.evidence_role,operation_id=x.operation_id,target_binding=x.target_binding)
    assert r=={"status":"DENIED","decision_id":"d1","authorization_created":False,"execution_performed":False}
def test_non_filesystem_target_rejected():
    with pytest.raises(ValueError,match="filesystem_target"): d(target_binding="https://example.invalid/x").validate()
