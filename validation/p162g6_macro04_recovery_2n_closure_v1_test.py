from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import json
from ontology.failure_recovery_orchestrator import FailureRecoveryOrchestrator, _sha_payload
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
 state={"civilizational_identity":"oce","memory_anchor_count":4,"active_node_count":2}
 with TemporaryDirectory() as td:
  root=Path(td)
  with patch("ontology.failure_recovery_orchestrator._ssd_continuity_root",return_value=None):
   engine=FailureRecoveryOrchestrator(root=root)
  try:engine._create_snapshot("R1",state,{});raise AssertionError("ambient snapshot write accepted")
  except RuntimeError as e:assert "provider_required" in str(e)
  assert not list(engine.snapshot_root.glob("*.json"))
  missing=engine._create_snapshot("R1",state,{"snapshot_missing":True})
  assert not missing["snapshot_created"]
 print("DEGRADATION_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);provider,contexts=provider_factory(root)
  with patch("ontology.failure_recovery_orchestrator._ssd_continuity_root",return_value=None):
   engine=FailureRecoveryOrchestrator(root=root,filesystem_effect_context_provider=provider)
  snapshot=engine._create_snapshot("R2",state,{"snapshot_id":"SAFE-R2"})
  assert snapshot["snapshot_created"] and snapshot["snapshot_checksum"]==_sha_payload(state)
  payload=json.loads(Path(snapshot["snapshot_path"]).read_text())
  assert payload["snapshot_checksum"]==_sha_payload(payload["state"])
  restoration=engine._restore_snapshot(snapshot,{"restoration_target_node":"node-2"})
  assert restoration["snapshot_restored"] and restoration["snapshot_integrity_validated"]
  restored=json.loads(Path(restoration["restoration_path"]).read_text())
  assert restored["restored_checksum"]==_sha_payload(state)
  assert len(contexts)==2 and all(sum(c.remaining().values())==0 for c in contexts)
  corrupted=engine._restore_snapshot(snapshot,{"snapshot_corruption":True})
  assert not corrupted["snapshot_restored"] and not corrupted["snapshot_integrity_validated"]
  unavailable=engine._restore_snapshot({"snapshot_available":False},{})
  assert unavailable["restoration_error"]=="snapshot_unavailable"
  assert len(contexts)==3 and all(sum(c.remaining().values())==0 for c in contexts)
 print("FUNCTIONAL_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK");print("DEGRADATION_RESTORATION_TEST_OK")
 print("NON_REGRESSION_TEST_OK");print("P162G6_MACRO04_RECOVERY_2N_TEST_OK")
if __name__=="__main__":main()
