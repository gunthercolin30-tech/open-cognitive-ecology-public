from concurrent.futures import ThreadPoolExecutor
from ontology.governed_execution_adapter import ExecutionClaimManager
def L(**k):
 d={"lease_id":"L1","reservation_id":"R1","executor_id":"EX1","capability_instance_id":"CI1","operation_id":"OP1","invocation_request_hash":"IH","effective_execution_scope_hash":"SH","audience":"A1","reservation_status":"RESERVED","used":False,"revoked":False,"expires_at":"2999-01-01T00:00:00+00:00"};d.update(k);return d
def R(**k):
 d={"adapter_id":"A1","adapter_hash":"AH","effector_id":"EF1","capability_ids":["C1"],"operation_ids":["OP1"],"status":"ACTIVE"};d.update(k);return d
def S(**k):
 d={"lease_state_version":1,"reservation_state_version":2,"token_state_version":3,"target_state_version":4,"capability_runtime_attestation":"CAP","adapter_attestation":"AH","critical_precondition_snapshot":{"ok":True},"security_state":"VERIFIED","revoked":False,"target_current":True,"critical_preconditions_satisfied":True,"credential_identity_verified":True};d.update(k);return d
def C(m,s=None,**k):
 return m.claim(lease=k.get("lease",L()),registry_entry=k.get("registry_entry",R()),executor_instance_id=k.get("executor_instance_id","EX1"),capability_instance_id="CI1",capability_id="C1",operation_id="OP1",invocation_request_hash="IH",effective_execution_scope_hash="SH",point_of_effect_state=s or S(),now_iso="2026-10-01T16:00:00+00:00")
def test_noncausal_claim():
 x=C(ExecutionClaimManager());assert x["status"]=="EXECUTION_STARTED";assert not any((x["scoped_handle_issued"],x["credential_disclosed"],x["effector_called"],x["real_world_effect_performed"]))
def test_replay():m=ExecutionClaimManager();assert C(m)["status"]=="EXECUTION_STARTED";assert C(m)["reason"]=="execution_claim_already_exists"
def test_concurrency():
 m=ExecutionClaimManager()
 with ThreadPoolExecutor(max_workers=8) as e:o=list(e.map(lambda _:C(m),range(20)))
 assert sum(x["status"]=="EXECUTION_STARTED" for x in o)==1
def test_revocation():assert C(ExecutionClaimManager(),S(revoked=True))["reason"]=="last_second_revocation"
def test_target():assert C(ExecutionClaimManager(),S(target_current=False))["reason"]=="target_not_current"
def test_precondition():assert C(ExecutionClaimManager(),S(critical_preconditions_satisfied=False))["reason"]=="critical_precondition_failed"
def test_security():assert C(ExecutionClaimManager(),S(security_state="UNKNOWN"))["reason"]=="security_not_verified"
def test_adapter_swap():assert C(ExecutionClaimManager(),S(adapter_attestation="X"))["reason"]=="adapter_attestation_mismatch"
def test_capability_unknown():assert C(ExecutionClaimManager(),S(capability_runtime_attestation="UNKNOWN"))["reason"]=="capability_attestation_undetermined"
def test_credential_identity():assert C(ExecutionClaimManager(),S(credential_identity_verified=False))["reason"]=="credential_identity_not_verified"
def test_incomplete():
 s=S();del s["target_state_version"];assert C(ExecutionClaimManager(),s)["reason"]=="snapshot_incomplete"
