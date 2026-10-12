from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from ontology.corpus_simulation_engine import CorpusSimulationEngine
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";NOW="2026-10-07T00:00:00+00:00"
def factory(root):
 contexts=[]
 def provider(op,target,slot):
  assert op=="FS_WRITE_REPLACE_BYTES" and slot=="macro04_corpus_simulation_report"
  target=Path(target);broker=ScopedHandleBroker()
  eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
  binding=eff.canonical_target(RID,target.resolve().relative_to(root.resolve()).as_posix())
  lease={"lease_id":"l-"+slot,"reservation_id":"r-"+slot,"operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
  claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash="c-"+slot)
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
  issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=NOW)
  assert issued["status"]=="HANDLE_ISSUED"
  ctx=GovernedFilesystemEffectContext(slots={slot:[issued["handle"]]},effector=eff,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
  contexts.append(ctx);return ctx
 return provider,contexts

def main():
 with TemporaryDirectory() as td:
  root=Path(td);path=root/"report.txt"
  engine=CorpusSimulationEngine(max_steps=7)
  try:engine.save_report(str(path));raise AssertionError("ambient write accepted")
  except RuntimeError as e:assert "provider_required" in str(e)
  assert not path.exists()
  print("DEGRADATION_TEST_OK")
  provider,contexts=factory(root)
  engine=CorpusSimulationEngine(max_steps=7,filesystem_effect_context_provider=provider)
  engine.diagnostics={"rounds":3};engine.errors=[{"stage":"test","source":"unit","message":"sample"}]
  engine.save_report(str(path));actual=path.read_bytes()
  assert actual.startswith(b"CORPUS SIMULATION REPORT\n") and b"rounds: 3" in actual and b"[test] unit : sample" in actual
  assert len(contexts)==1 and all(not any(c.remaining().values()) for c in contexts)
  assert b"\r\n" not in actual and actual.endswith(b"\n")
  path.write_bytes(b"old report")
  engine.errors=[];engine.diagnostics={}
  engine.save_report(str(path))
  assert b"old report" not in path.read_bytes() and b"None" in path.read_bytes()
  assert len(contexts)==2 and all(not any(c.remaining().values()) for c in contexts)
  print("FUNCTIONAL_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK")
  print("NON_REGRESSION_TEST_OK");print("P162G6_MACRO04_CORPUS_REPORT_1N_TEST_OK")
if __name__=="__main__":main()
