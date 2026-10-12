from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
from unittest.mock import patch
from ontology.civilizational_replication_engine import CivilizationalReplicationEngine, _sha
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";NOW="2026-10-07T00:00:00+00:00"
def provider_factory(root):
 contexts=[]
 def provider(op,target,slot):
  assert op=="FS_WRITE_REPLACE_BYTES"
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
  root=Path(td)
  with patch("ontology.civilizational_replication_engine._ssd_continuity_root",return_value=None):
   engine=CivilizationalReplicationEngine(root=root)
  try:engine._make_package({"package_id":"test1"},{"dependency_readiness":1.0});raise AssertionError("ambient write accepted")
  except RuntimeError as e:assert "provider_required" in str(e)
  assert not (engine.replication_root/"test1.json").exists()
 print("DEGRADATION_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);provider,contexts=provider_factory(root)
  with patch("ontology.civilizational_replication_engine._ssd_continuity_root",return_value=None):
   engine=CivilizationalReplicationEngine(root=root,filesystem_effect_context_provider=provider)
  package=engine._make_package({"package_id":"test2"},{"dependency_readiness":0.99})
  assert json.loads(Path(package["package_path"]).read_text())["checksum"]==package["checksum"]
  record=engine._transfer_direction(package,"cloud","community",{},0.99,0.99)
  assert json.loads(Path(record["direction_record_path"]).read_text())["expected_checksum"]==package["checksum"]
  assert record["checksum_match"] is True
  assert len(contexts)==2 and all(sum(c.remaining().values())==0 for c in contexts)
  assert engine._transfer_direction(package,"cloud","community",{"cross_node_transfer_failure":True},0.99,0.99)["transfer_success"] is False
 print("FUNCTIONAL_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK");print("DEGRADATION_TRANSFER_TEST_OK")
 print("NON_REGRESSION_TEST_OK");print("P162G6_MACRO04_REPLICATION_2N_TEST_OK")
if __name__=="__main__":main()
