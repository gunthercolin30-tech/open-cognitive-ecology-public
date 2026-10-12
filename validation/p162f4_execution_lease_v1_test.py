from datetime import datetime,timezone,timedelta
from ontology.execution_lease_issuer import ExecutionLeaseIssuer
H="a"*64
NOW=datetime(2030,1,1,tzinfo=timezone.utc)
def reservation(status="RESERVED"):
 return {"reservation_id":"r1","status":status,"effective_execution_scope_hash":H,
         "executor_id":"e1","operation_id":"read","target_binding":{"id":"T"}}
def issue(i,r=None,**over):
 kw=dict(idempotency_key="k",reservation=r or reservation(),invocation_request_hash="b"*64,
  capability_instance_id="ci1",audience="p162-g",issued_at=NOW,
  requested_expires_at=NOW+timedelta(seconds=30),token_expires_at=NOW+timedelta(seconds=20),
  reservation_expires_at=NOW+timedelta(seconds=10))
 kw.update(over); return i.issue(**kw)

def test_requires_current_reservation():
 for s in ("ABORTED","EXPIRED","INDETERMINATE","INVALIDATED","RELEASED"):
  assert issue(ExecutionLeaseIssuer(),reservation(s))["status"]=="LEASE_RESERVATION_NOT_CURRENT"

def test_expiry_is_strict_intersection():
 z=issue(ExecutionLeaseIssuer())
 assert z["expires_at"]==(NOW+timedelta(seconds=10)).isoformat()

def test_cannot_outlive_token():
 z=issue(ExecutionLeaseIssuer(),token_expires_at=NOW+timedelta(seconds=5),reservation_expires_at=NOW+timedelta(seconds=50))
 assert z["expires_at"]==(NOW+timedelta(seconds=5)).isoformat()

def test_empty_or_expired_window_rejected():
 z=issue(ExecutionLeaseIssuer(),reservation_expires_at=NOW)
 assert z["status"]=="LEASE_EXPIRED_OR_EMPTY"

def test_exact_bindings_and_nontransferability():
 z=issue(ExecutionLeaseIssuer())
 assert z["executor_id"]=="e1" and z["capability_instance_id"]=="ci1" and z["operation_id"]=="read"
 assert z["target_binding"]=={"id":"T"} and z["audience"]=="p162-g" and z["transferable"] is False

def test_retry_idempotent_same_lease():
 i=ExecutionLeaseIssuer(); a=issue(i); b=issue(i)
 assert a==b and a["lease_id"]==b["lease_id"]

def test_handoff_binding_mismatch_fails():
 i=ExecutionLeaseIssuer(); z=issue(i)
 assert i.validate_for_handoff(z,audience="other",executor_id="e1",capability_instance_id="ci1",operation_id="read",target_binding={"id":"T"},now=NOW)=="LEASE_BINDING_MISMATCH"

def test_handoff_expiry_fails():
 i=ExecutionLeaseIssuer(); z=issue(i)
 assert i.validate_for_handoff(z,audience="p162-g",executor_id="e1",capability_instance_id="ci1",operation_id="read",target_binding={"id":"T"},now=NOW+timedelta(seconds=11))=="LEASE_EXPIRED"

def test_single_use_handoff_replay_blocked():
 i=ExecutionLeaseIssuer(); z=issue(i)
 args=dict(audience="p162-g",executor_id="e1",capability_instance_id="ci1",operation_id="read",target_binding={"id":"T"},now=NOW)
 assert i.validate_for_handoff(z,**args)=="LEASE_CURRENT_FOR_HANDOFF"
 assert i.mark_handoff_once(z["lease_id"]) is True
 assert i.mark_handoff_once(z["lease_id"]) is False
 assert i.validate_for_handoff(z,**args)=="LEASE_REPLAY"

def test_deterministic_fresh_issuer():
 a=issue(ExecutionLeaseIssuer()); b=issue(ExecutionLeaseIssuer())
 assert a["lease_id"]==b["lease_id"] and a["lease_nonce"]==b["lease_nonce"] and a["lease_hash"]==b["lease_hash"]

def test_non_effecting_boundary_and_g_closed():
 i=ExecutionLeaseIssuer(); z=issue(i)
 assert z["capability_accessed"] is False and z["effect_performed"] is False and z["p162g_opened"] is False
 assert z["use_policy"]["point_of_effect_recheck_required"] is True
 assert not hasattr(i,"execute") and not hasattr(i,"dispatch") and not hasattr(i,"invoke")
