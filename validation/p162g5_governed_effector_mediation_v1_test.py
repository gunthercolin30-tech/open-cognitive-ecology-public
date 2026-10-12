from ontology.governed_execution_adapter import ExecutionClaim
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.credential_broker import CredentialBroker
from ontology.governed_effector_adapter import GovernedEffectorAdapter
CALLS=[]
def effector(**kw):
 CALLS.append(kw);return {"effect_status":"EFFECT_CONFIRMED","external_receipts":["X"],"resource_usage":{"units":1}}
def timeout_effector(**kw): raise TimeoutError()
def claim():return ExecutionClaim("R1","L1","A1","EX1","2026",1,"CH")
def lease():return {"lease_id":"L1","reservation_id":"R1","operation_id":"WRITE","expires_at":"2999-01-01T00:00:00+00:00"}
def reg(**k):
 d={"adapter_id":"A1","adapter_version":"1","adapter_hash":"AH","effector_id":"EF1","status":"ACTIVE"};d.update(k);return d
def scope():return {"path":"/tmp/exact","operations":["WRITE"],"ambient_authority":False,"child_inheritance":False,"transferable":False}
def chain():
 hb=ScopedHandleBroker();h=hb.issue(claim=claim(),lease=lease(),registry_entry=reg(),requested_scope=scope(),authorized_scope=scope(),target_binding={"path":"/tmp/exact"},audience="A1",now_iso="2026")["handle"]
 cb=CredentialBroker();c={"credential_ref":"vault://1","status":"ACTIVE","expires_at":"2999-01-01T00:00:00+00:00","allowed_operations":["WRITE"],"allowed_targets":[{"path":"/tmp/exact"}],"ambient_authority":False,"transferable":False,"child_inheritance":False}
 u=cb.authorize_use(handle=h,credential_record=c,requested_operation="WRITE",requested_target={"path":"/tmp/exact"},audience="A1",now_iso="2026")["use"]
 return h,u
def state(**k):
 d={"lease_current":True,"reservation_current":True,"revoked":False,"target_current":True,"critical_preconditions_satisfied":True,"security_state":"VERIFIED","adapter_attestation":"AH"};d.update(k);return d
def adapter(fn=effector):return GovernedEffectorAdapter(adapter_id="A1",adapter_version="1",adapter_hash="AH",effector_id="EF1",effector_callable=fn,allowed_effect_classes=["FILESYSTEM"])
def run(a=None,r=None,s=None,key="K1"):
 h,u=chain();return (a or adapter()).execute(claim=claim(),handle=h,brokered_use=u,registry_entry=r or reg(),capability_id="C1",capability_version="1",effect_class="FILESYSTEM",final_state=s or state(),idempotency_key=key,now_iso="2026")
def test_confirmed_effect_crosses_only_injected_effector():
 CALLS.clear();x=run();assert x["status"]=="EFFECT_CONFIRMED";assert len(CALLS)==1;assert CALLS[0]["target"]=={"path":"/tmp/exact"};assert "credential_ref" in CALLS[0] and "raw_secret" not in CALLS[0]
def test_last_second_revocation_blocks_before_effector():
 CALLS.clear();x=run(s=state(revoked=True));assert x["reason"]=="last_second_revocation";assert not CALLS
def test_adapter_identity_drift_blocks():
 CALLS.clear();x=run(r=reg(adapter_hash="OTHER"));assert x["reason"]=="adapter_identity_drift";assert not CALLS
def test_target_drift_blocks():
 CALLS.clear();x=run(s=state(target_current=False));assert x["reason"]=="target_not_current";assert not CALLS
def test_security_unknown_blocks():
 CALLS.clear();x=run(s=state(security_state="UNKNOWN"));assert x["reason"]=="security_not_verified";assert not CALLS
def test_replay_attempt_blocked():
 CALLS.clear();a=adapter();assert run(a=a,key="K")["status"]=="EFFECT_CONFIRMED";assert run(a=a,key="K")["reason"]=="effect_attempt_replay";assert len(CALLS)==1
def test_timeout_is_indeterminate_and_no_blind_retry():
 x=run(a=adapter(timeout_effector));assert x["status"]=="EFFECT_STATE_INDETERMINATE";assert x["blind_retry_allowed"] is False
def test_missing_idempotency_key_blocks():
 CALLS.clear();x=run(key="");assert x["reason"]=="idempotency_key_required";assert not CALLS
def test_partial_effect_is_explicit():
 def partial(**kw):return {"effect_status":"EFFECT_PARTIAL","resource_usage":{"units":2}}
 x=run(a=adapter(partial));assert x["status"]=="EFFECT_PARTIAL";assert x["receipt"].effect_status=="EFFECT_PARTIAL"
def test_unverifiable_outcome_is_indeterminate():
 def bad(**kw):return {"ok":True}
 x=run(a=adapter(bad));assert x["status"]=="EFFECT_STATE_INDETERMINATE";assert x["blind_retry_allowed"] is False
