from pathlib import Path
import ast, pytest
from ontology.closed_embodied_feedback_validation_loop import ClosedEmbodiedFeedbackValidationLoop
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision, ALLOW
class C:
 root_id="r1"
 def __init__(self,root): self.root_path=Path(root); self.r={"history_append":1,"latest_write":1,"index_write":1}; self.calls=[]; self.b=False
 def begin(self):
  if self.b: raise RuntimeError("replay")
  self.b=True
 def execute_path(self,**kw):
  if not self.b or self.r.get(kw["slot"],0)!=1: raise RuntimeError("no preissued handle")
  self.r[kw["slot"]]=0; self.calls.append(kw); return {"status":"EFFECT_CONFIRMED"}
 def remaining(self): return dict(self.r)
def d(): return EvidenceEffectDecision(decision_id="d1",decision=ALLOW,evidence_role="EVIDENCE_REPORT_EXPORT",operation_id="FS_APPEND_BYTES",target_binding="filesystem://r1/closed_embodied_feedback_validation/closed_embodied_feedback_validation_loop_history.jsonl",rationale="bounded",provenance="test")
def test_read_only(tmp_path): assert ClosedEmbodiedFeedbackValidationLoop(root=tmp_path).step(persist=False)["success"] is True
def test_no_context(tmp_path):
 with pytest.raises(RuntimeError,match="context_required"): ClosedEmbodiedFeedbackValidationLoop(root=tmp_path).step()
def test_no_decision(tmp_path):
 c=C(tmp_path)
 with pytest.raises(RuntimeError,match="evidence_decision_required"): ClosedEmbodiedFeedbackValidationLoop(root=tmp_path).step(filesystem_context=c)
 assert c.calls==[]
def test_exact(tmp_path):
 c=C(tmp_path); r=ClosedEmbodiedFeedbackValidationLoop(root=tmp_path).step(filesystem_context=c,evidence_decisions={"history_append":d()})
 assert r["success"] is True and [x["operation_id"] for x in c.calls]==["FS_APPEND_BYTES","FS_WRITE_REPLACE_BYTES","FS_WRITE_REPLACE_BYTES"] and not any(c.remaining().values())
def test_no_direct_bypass():
 import ontology.closed_embodied_feedback_validation_loop as m
 tr=ast.parse(Path(m.__file__).read_text()); bad=[]
 for n in ast.walk(tr):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {"write_text","write_bytes","open","mkdir","replace","rename","unlink"}: bad.append((n.lineno,n.func.attr))
 assert bad==[]
