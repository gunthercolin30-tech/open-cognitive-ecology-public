import json,hashlib
from pathlib import Path
from ontology.governed_execution_adapter import assess_execution_boundary,EXECUTION_STATUSES
ROOT=Path(__file__).resolve().parents[1]
def L(**k):
 d={"lease_id":"L1","reservation_id":"R1","executor_id":"EX1","capability_instance_id":"CI1","operation_id":"OP1","invocation_request_hash":"IH","effective_execution_scope_hash":"SH","audience":"A1","reservation_status":"RESERVED","used":False,"revoked":False,"expires_at":"2999-01-01T00:00:00+00:00"};d.update(k);return d
def R(**k):
 d={"adapter_id":"A1","adapter_version":"1","adapter_hash":"AH","effector_id":"EF1","capability_ids":["C1"],"operation_ids":["OP1"],"status":"ACTIVE","effect_boundary_definition":"immediately before governed effect"};d.update(k);return d
def C(l=None,r=None,**k):
 return assess_execution_boundary(lease=l or L(),registry_entry=r or R(),executor_instance_id=k.get("executor_instance_id","EX1"),capability_instance_id=k.get("capability_instance_id","CI1"),capability_id=k.get("capability_id","C1"),operation_id=k.get("operation_id","OP1"),invocation_request_hash=k.get("invocation_request_hash","IH"),effective_execution_scope_hash=k.get("effective_execution_scope_hash","SH"),now_iso="2026-10-01T00:00:00+00:00")
def test_statuses(): assert len(EXECUTION_STATUSES)==11
def test_valid_is_still_noncausal():
 x=C(); assert x.status=="EXECUTION_NOT_STARTED"; assert not any((x.execution_claim_created,x.scoped_handle_issued,x.credential_disclosed,x.effector_called,x.real_world_effect_performed))
def test_wrong_executor(): assert C(executor_instance_id="X").status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_wrong_audience(): assert C(l=L(audience="X")).status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_expired(): assert C(l=L(expires_at="2020-01-01T00:00:00+00:00")).status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_replay(): assert C(l=L(used=True)).status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_revoked(): assert C(l=L(revoked=True)).status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_inactive_adapter(): assert C(r=R(status="SUSPENDED")).status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_wrong_capability_instance(): assert C(capability_instance_id="X").status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_wrong_operation(): assert C(operation_id="X").status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_invocation_drift(): assert C(invocation_request_hash="X").status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_scope_drift(): assert C(effective_execution_scope_hash="X").status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_f_manifest_still_matches():
 m=json.loads((ROOT/"validation_artifacts/p162/p162f/protected_manifest.json").read_text())
 for rel,h in m["files"].items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
def test_nine_schemas_parse():
 for n in ["governed_execution_adapter","execution_adapter_registry_entry","point_of_effect_snapshot","execution_claim","scoped_effect_handle","brokered_credential_use","effect_attempt_record","execution_receipt","execution_sandbox_profile"]: json.loads((ROOT/"ontology"/(n+".schema.json")).read_text())
