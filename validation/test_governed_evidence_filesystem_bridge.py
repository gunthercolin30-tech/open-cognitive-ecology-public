import pytest
from ontology.governed_evidence_effect_policy import GovernedEvidenceEffectPolicy,EvidenceEffectDecision,ALLOW,DENY
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
class C:
    root_id="r1"
    def __init__(self,fail=False): self.calls=[]; self.fail=fail
    def execute_path(self,**kw):
        self.calls.append(kw)
        if self.fail: raise RuntimeError("no_preissued_handle")
        return {"status":"EFFECT_CONFIRMED"}
def d(**kw):
    x=dict(decision_id="d1",decision=ALLOW,evidence_role="EVIDENCE_REPORT_EXPORT",operation_id="FS_APPEND_BYTES",
      target_binding="filesystem://r1/evidence/log.jsonl",rationale="bounded",provenance="test")
    x.update(kw); return EvidenceEffectDecision(**x)
def test_allow_composes_only():
    c=C(); b=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),c)
    r=b.execute_path(decision=d(),evidence_role="EVIDENCE_REPORT_EXPORT",slot="append",
      operation_id="FS_APPEND_BYTES",path="evidence/log.jsonl",payload=b"x")
    assert r["status"]=="EVIDENCE_EFFECT_CONFIRMED" and r["authorization_created"] is False and b.authority_minting is False
def test_deny_no_effect():
    c=C(); b=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),c); x=d(decision=DENY)
    r=b.execute_path(decision=x,evidence_role=x.evidence_role,slot="append",operation_id=x.operation_id,path="evidence/log.jsonl")
    assert r["status"]=="DENIED" and c.calls==[]
@pytest.mark.parametrize("field,value",[("evidence_role","OTHER"),("operation_id","FS_REMOVE_FILE"),("path","other.jsonl")])
def test_mismatch(field,value):
    c=C(); b=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),c)
    kw=dict(evidence_role="EVIDENCE_REPORT_EXPORT",operation_id="FS_APPEND_BYTES",path="evidence/log.jsonl"); kw[field]=value
    with pytest.raises(RuntimeError): b.execute_path(decision=d(),slot="append",payload=b"x",**kw)
    assert c.calls==[]
def test_missing_preissued_handle():
    c=C(True); b=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),c)
    with pytest.raises(RuntimeError,match="no_preissued_handle"):
        b.execute_path(decision=d(),evidence_role="EVIDENCE_REPORT_EXPORT",slot="append",operation_id="FS_APPEND_BYTES",path="evidence/log.jsonl")
@pytest.mark.parametrize("path",["/abs","../x","a/../x"])
def test_unsafe_path(path):
    c=C(); b=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),c)
    with pytest.raises(RuntimeError,match="unsafe_relative_path"):
        b.execute_path(decision=d(),evidence_role="EVIDENCE_REPORT_EXPORT",slot="append",operation_id="FS_APPEND_BYTES",path=path)
    assert c.calls==[]
