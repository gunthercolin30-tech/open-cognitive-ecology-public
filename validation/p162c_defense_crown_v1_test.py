from copy import deepcopy
import ast, inspect
import pytest
import validation.p162c_token_point_of_use_verification_v1_test as base
import ontology.token_point_of_use_verifier as impl

def run(x): return impl.verify_at_point_of_use(**x)
def blocked(x): return run(x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

# C-1..C-18 — invariants
def test_c01_schema_and_version_are_explicit():
 r=run(base.fx()); assert r["verification"]["schema"].startswith("oce.p162c."); assert r["receipt"]["version"]=="P162-C-v1"
def test_c02_integrity_required():
 x=base.fx(); x["token"]["token_hash"]="0"*64; assert blocked(x)
def test_c03_signature_alone_is_insufficient():
 x=base.fx(); x["registry_snapshot"]["continuity_status"]="UNKNOWN"; assert blocked(x)
def test_c04_issuer_and_committed_issuance_required():
 x=base.fx(); x["issuance_event"]["issuer_id"]="OTHER"; assert blocked(x)
 x=base.fx(); x["issuance_event"]["status"]="PENDING"; assert blocked(x)
def test_c05_registry_journal_uncertainty_blocks():
 x=base.fx(); x["registry_snapshot"]["continuity_status"]="CONFLICT"; assert blocked(x)
def test_c06_terminal_states_are_final():
 for state in ("CONSUMED","REVOKED","EXPIRED","INVALIDATED"):
  x=base.fx(); x["lifecycle"]["state"]=state; assert blocked(x)
def test_c07_temporal_uncertainty_blocks():
 for k in ("clock_uncertain","clock_rollback"):
  x=base.fx(); x[k]=True; assert blocked(x)
def test_c08_revocation_freshness_required():
 x=base.fx(); x["revocation_snapshot"]["stale"]=True; assert blocked(x)
def test_c09_executor_binding_exact():
 x=base.fx(); x["invocation_binding_manifest"]["executor"]["executor_instance_id"]="OTHER"; assert blocked(x)
def test_c10_capability_operation_exact():
 x=base.fx(); x["invocation_binding_manifest"]["operation"]["operation_id"]="other"; assert blocked(x)
def test_c11_target_exact():
 x=base.fx(); x["invocation_request"]["target_binding"]={"id":"OTHER"}; assert blocked(x)
def test_c12_purpose_exact():
 x=base.fx(); x["invocation_request"]["purpose_id"]="OTHER"; assert blocked(x)
def test_c13_environment_exact():
 x=base.fx(); x["invocation_request"]["environment"]="PRODUCTION"; assert blocked(x)
def test_c14_arguments_exact():
 x=base.fx(); x["invocation_binding_manifest"]["arguments"]["digest"]="DRIFT"; assert blocked(x)
def test_c15_capability_set_expansion_blocks():
 x=base.fx(); x["invocation_request"]["capability_id"]="cap.extra"; assert blocked(x)
def test_c16_unknown_critical_state_never_grants():
 for mutate in (
  lambda x:x["registry_snapshot"].update(version="UNKNOWN"),
  lambda x:x["revocation_snapshot"].update(status="UNKNOWN"),
  lambda x:x["authority_snapshot"].update(status="UNKNOWN"),
  lambda x:x["approval_consent_quorum_snapshot"].update(status="UNKNOWN"),
  lambda x:x["budget_snapshot"].update(status="UNKNOWN"),
 ):
  x=base.fx(); mutate(x); assert blocked(x)
def test_c17_verification_does_not_consume_or_reserve():
 x=base.fx(); before=deepcopy(x); r=run(x); assert x==before
 assert r["reservation_created"] is False and r["token_consumed"] is False
def test_c18_verification_does_not_execute_or_access_capability():
 r=run(base.fx()); assert r["capability_accessed"] is False and r["execution_performed"] is False and r["p162d_opened"] is False

# C-01..C-19 — defensive cases
def test_d01_malformed_token():
 x=base.fx(); x["token"]={}; assert blocked(x)
def test_d02_algorithm_downgrade():
 x=base.fx(); x["token"]["signature"]["algorithm"]="NONE"; assert blocked(x)
def test_d03_ghost_uncommitted_token():
 x=base.fx(); x["issuance_event"]={}; assert blocked(x)
def test_d04_clock_rollback():
 x=base.fx(); x["clock_rollback"]=True; assert blocked(x)
def test_d05_stale_revocation_cache():
 x=base.fx(); x["revocation_snapshot"]["stale"]=True; assert blocked(x)
def test_d06_consumed_replay():
 x=base.fx(); x["lifecycle"]["state"]="CONSUMED"; x["lifecycle"]["consumed_uses"]=1; assert blocked(x)
def test_d07_executor_substitution():
 x=base.fx(); x["invocation_request"]["executor_id"]="OTHER"; assert blocked(x)
def test_d08_capability_substitution():
 x=base.fx(); x["invocation_request"]["capability_id"]="other"; assert blocked(x)
def test_d09_operation_substitution():
 x=base.fx(); x["invocation_request"]["operation_id"]="other"; assert blocked(x)
def test_d10_target_substitution():
 x=base.fx(); x["invocation_request"]["target_binding"]={"id":"X"}; assert blocked(x)
def test_d11_purpose_substitution():
 x=base.fx(); x["invocation_request"]["purpose_id"]="X"; assert blocked(x)
def test_d12_shadow_prod_laundering():
 x=base.fx(); x["invocation_request"]["environment"]="PRODUCTION"; assert blocked(x)
def test_d13_argument_default_drift():
 x=base.fx(); x["invocation_request"]["arguments_digest"]="DEFAULT-DRIFT"; assert blocked(x)
def test_d14_authority_revocation_dependency():
 x=base.fx(); x["revocation_snapshot"]["dependency_revoked"]=True; assert blocked(x)
def test_d15_approval_consent_quorum_revocation():
 x=base.fx(); x["approval_consent_quorum_snapshot"]["status"]="REVOKED"; assert blocked(x)
def test_d16_emergency_end_or_authority_loss():
 x=base.fx(); x["authority_snapshot"]["status"]="EXPIRED"; assert blocked(x)
def test_d17_budget_race_snapshot():
 x=base.fx(); x["budget_snapshot"]["available_budget"]["cpu"]=0; assert blocked(x)
def test_d18_capability_binding_stale_or_mismatch():
 x=base.fx(); x["capability_binding_receipt"]["verification_status"]="REVERIFY_REQUIRED"; assert blocked(x)
def test_d19_unknown_critical_extension():
 x=base.fx(); x["capability_binding_receipt"]["binding_receipt_hash"]="UNKNOWN"; assert blocked(x)

# ROOT-C1..C8
def test_root_c1_signature_only_path_cannot_pass():
 x=base.fx(); x["issuance_event"]["status"]="PENDING"; x["registry_snapshot"]["continuity_status"]="UNKNOWN"; assert blocked(x)
def test_root_c2_terminal_resurrection_cannot_pass():
 x=base.fx(); x["lifecycle"]["state"]="REVOKED"; assert blocked(x)
def test_root_c3_revocation_blindness_cannot_pass():
 x=base.fx(); x["revocation_snapshot"]["token_revoked"]=True; assert blocked(x)
def test_root_c4_binding_substitution_cannot_pass():
 x=base.fx(); x["invocation_binding_manifest"]["capability"]["capability_id"]="OTHER"; assert blocked(x)
def test_root_c5_dependency_drift_cannot_pass():
 x=base.fx(); x["current_dependency_vector"]["scope_envelope_hash"]="OTHER"; assert blocked(x)
def test_root_c6_registry_conflict_cannot_pass():
 x=base.fx(); x["registry_snapshot"]["continuity_status"]="CONFLICT"; assert blocked(x)
def test_root_c7_stale_snapshot_cannot_pass():
 x=base.fx(); x["revocation_snapshot"]["stale"]=True; assert blocked(x)
def test_root_c8_unknown_cannot_be_promoted():
 x=base.fx(); x["budget_snapshot"]["snapshot_hash"]="UNKNOWN"; assert blocked(x)

# Nine canonical mutation-equivalent tests
@pytest.mark.parametrize("mutation",[
 lambda x:x["signing_key"].__class__(b"wrong"),
])
def test_mut01_signature_check_is_effective(mutation):
 x=base.fx(); x["signing_key"]=b"wrong"; assert blocked(x)
def test_mut02_committed_event_check_is_effective():
 x=base.fx(); x["issuance_event"]["status"]="PENDING"; assert blocked(x)
def test_mut03_terminal_state_check_is_effective():
 x=base.fx(); x["lifecycle"]["state"]="INVALIDATED"; assert blocked(x)
def test_mut04_revocation_check_is_effective():
 x=base.fx(); x["revocation_snapshot"]["token_revoked"]=True; assert blocked(x)
def test_mut05_state_conflict_cannot_become_current():
 x=base.fx(); x["registry_snapshot"]["continuity_status"]="CONFLICT"; assert blocked(x)
def test_mut06_binding_checks_are_effective():
 x=base.fx(); x["invocation_request"]["action_digest"]="OTHER"; assert blocked(x)
def test_mut07_dependency_drift_check_is_effective():
 x=base.fx(); x["current_dependency_vector"]["evidence_bundle_hash"]="OTHER"; assert blocked(x)
def test_mut08_unknown_cannot_become_current():
 x=base.fx(); x["authority_snapshot"]["status"]="UNKNOWN"; assert blocked(x)
def test_mut09_stale_cache_cannot_be_accepted():
 x=base.fx(); x["revocation_snapshot"]["stale"]=True; assert blocked(x)

# Meta-properties / non-amplification
def test_meta_deterministic_receipt():
 x=base.fx(); a=run(deepcopy(x)); b=run(deepcopy(x)); assert a["receipt"]["receipt_hash"]==b["receipt"]["receipt_hash"]
def test_meta_all_inputs_unchanged():
 x=base.fx(); before=deepcopy(x); run(x); assert x==before
def test_meta_no_reservation_consumption_calls_in_verifier():
 src=inspect.getsource(impl); tree=ast.parse(src)
 forbidden={"reserve_for_use","consume_reserved","revoke","append","execute","subprocess","system","popen"}
 calls=set()
 for n in ast.walk(tree):
  if isinstance(n,ast.Call):
   f=n.func
   if isinstance(f,ast.Name): calls.add(f.id)
   elif isinstance(f,ast.Attribute):
    if f.attr in {"reserve_for_use","consume_reserved","revoke","execute","subprocess","system","popen"}:
     calls.add(f.attr)
 assert not (calls & forbidden), sorted(calls & forbidden)
def test_meta_positive_receipt_is_not_execution_authority():
 r=run(base.fx())
 assert r["status"]=="TOKEN_USABLE_FOR_GATE"
 assert r["receipt"]["status"]=="TOKEN_USABLE_FOR_GATE"
 for k in ("authorization_created","reservation_created","token_consumed","capability_accessed","execution_performed","p162d_opened"):
  assert r["receipt"][k] is False
def test_meta_revalidate_after_is_mandatory_and_future():
 x=base.fx(); x["revalidate_after"]=x["now"]; assert blocked(x)
def test_meta_capability_binding_receipt_hash_required():
 x=base.fx(); x["capability_binding_receipt"]["binding_receipt_hash"]=None; assert blocked(x)

def test_gap_human_integrity_unknown_never_grants():
 x=base.fx(); x["human_integrity_snapshot"].update(required=True,status="UNKNOWN"); assert blocked(x)
def test_gap_profile_unknown_never_grants():
 x=base.fx(); x["profile_snapshot"]["status"]="UNKNOWN"; assert blocked(x)
def test_gap_target_state_stale_or_mismatch_never_grants():
 x=base.fx(); x["target_state_snapshot"]["status"]="STALE"; assert blocked(x)
 x=base.fx(); x["target_state_snapshot"]["target_binding"]={"id":"OTHER"}; assert blocked(x)
def test_gap_pending_composition_unknown_or_conflict_never_grants():
 x=base.fx(); x["pending_composition_snapshot"]["status"]="UNKNOWN"; assert blocked(x)
 x=base.fx(); x["pending_composition_snapshot"]["has_conflicting_pending_composition"]=True; assert blocked(x)
def test_gap_b_receipt_substitution_never_grants():
 for field in ("capability_id","capability_version","implementation_identity","invocation_request_id"):
  x=base.fx(); x["capability_binding_receipt"][field]="OTHER"; assert blocked(x)
