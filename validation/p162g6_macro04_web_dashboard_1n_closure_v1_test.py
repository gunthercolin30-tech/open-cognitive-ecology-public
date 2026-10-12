from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from types import SimpleNamespace
from ontology.civilizational_web_dashboard import CivilizationalWebDashboard
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
SLOT="macro04_civilizational_web_dashboard"
class FakePersistence:
 def load(self):return {"state":{"a":"<script>","b":7}}
def factory(root):
 contexts=[]
 def provider(op,target,slot):
  assert op=="FS_WRITE_REPLACE_BYTES" and slot==SLOT
  broker=ScopedHandleBroker();eff=GovernedFilesystemEffector(root_registry={"R":str(root)},handle_broker=broker)
  binding=eff.canonical_target("R",Path(target).resolve().relative_to(root.resolve()).as_posix())
  lease={"lease_id":"lease-"+str(len(contexts)),"reservation_id":"reservation-"+str(len(contexts)),"operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
  claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id="A",claim_hash="c"+str(len(contexts)))
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
  issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":"A","effector_id":"E"},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience="A",now_iso="2026-10-08T00:00:00+00:00")
  assert issued["status"]=="HANDLE_ISSUED"
  ctx=GovernedFilesystemEffectContext(slots={slot:[issued["handle"]]},effector=eff,root_id="R",root_path=root,adapter_id="A",effector_id="E")
  contexts.append(ctx);return ctx
 return provider,contexts
def main():
 with TemporaryDirectory() as td:
  root=Path(td);p=root/"dashboard.html"
  with patch("ontology.civilizational_web_dashboard.CivilizationalStatePersistence",FakePersistence):
   obj=CivilizationalWebDashboard(output_path=str(p))
  try:obj.step();raise AssertionError("ambient_write_accepted")
  except RuntimeError as e:assert "provider_required" in str(e)
  assert not p.exists();print("DEGRADATION_TEST_OK")
  provider,contexts=factory(root)
  with patch("ontology.civilizational_web_dashboard.CivilizationalStatePersistence",FakePersistence):
   obj=CivilizationalWebDashboard(output_path=str(p),filesystem_effect_context_provider=provider)
  result=obj.step();actual=p.read_bytes()
  assert result["success"] is True and result["metrics_exported"]==2
  assert b"&lt;script&gt;" in actual and b"<script>" not in actual and b"<td>7</td>" in actual
  assert len(contexts)==1 and all(not any(c.remaining().values()) for c in contexts)
  p.write_bytes(b"old")
  obj.step();assert b"old" not in p.read_bytes()
  assert len(contexts)==2 and all(not any(c.remaining().values()) for c in contexts)
  print("FUNCTIONAL_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK")
  print("NON_REGRESSION_TEST_OK");print("P162G6_MACRO04_WEB_DASHBOARD_1N_TEST_OK")
if __name__=="__main__":main()
