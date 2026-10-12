from validation.p162d_runtime_context_preconditions_gate_v1_test import fx
from ontology.runtime_precondition_evaluator import evaluate_runtime_preconditions
def ev(x): return evaluate_runtime_preconditions(**x)
def test_d01_stale_sensor():
 x=fx();x["preconditions"][0]["freshness"]="STALE";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d02_fake_conflicting_sensor():
 for k,v in [("health_status","UNHEALTHY"),("calibration_status","INVALID"),("provenance_status","UNKNOWN")]:
  x=fx();x["preconditions"][0]["evidence_metadata"][k]=v;assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d03_prediction_laundering():
 x=fx();x["preconditions"][0]["evidence_class"]="PREDICTION";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d04_missing_evidence():
 x=fx();del x["preconditions"][0]["evidence_metadata"];assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d05_stale_cache():
 x=fx();x["security_snapshot"]["freshness"]="STALE";assert ev(x)["status"]=="CONTEXT_STALE"
def test_d06_emergency_ended():
 x=fx();x["invocation_request"]["emergency_required"]=True;x["world_snapshot"]["emergency_status"]="ENDED";assert ev(x)["required_action"]=="RETURN_TO_P160"
def test_d07_security_context():
 for k,v in [("sandbox_status","INVALID"),("host_integrity","UNKNOWN"),("credential_broker_status","INVALID")]:
  x=fx();x["security_snapshot"][k]=v;assert ev(x)["required_action"]=="SAFE_MODE_REQUIRED"
def test_d08_rollback_impossible():
 x=fx();x["invocation_request"]["rollback_required"]=True;x["world_snapshot"]["rollback_status"]="IMPOSSIBLE";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d09_composition_constraints():
 for k,v in [("rolling_window_status","VIOLATED"),("mutual_exclusion_conflict",True),("shared_budget_status","VIOLATED")]:
  x=fx();x["composition_snapshot"][k]=v;assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d10_precondition_set_mutation():
 x=fx();x["invocation_request"]["expected_preconditions"]=["P1","P2"];assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d11_hard_soft_downgrade():
 x=fx();x["preconditions"][0]["mandatory"]=False;assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d12_wrong_environment():
 x=fx();x["runtime_snapshot"]["environment"]="PROD";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d13_clock_skew():
 x=fx();x["world_snapshot"]["clock_skew_status"]="UNBOUNDED";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d14_unknown_permissive():
 x=fx();x["preconditions"][0]["observed_state"]="UNKNOWN";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d15_continuous_to_once():
 x=fx();x["preconditions"][0]["minimum_recheck_stage"]="CONTINUOUSLY_MONITORED";x["preconditions"][0]["recheck_stage"]="CHECK_ONCE";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_d16_predicate_injection():
 x=fx();x["preconditions"][0]["predicate"]="PYTHON";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_root_d1_unknown(): test_d14_unknown_permissive()
def test_root_d2_target_drift():
 x=fx();x["target_snapshot"]["target_fingerprint"]="OTHER";assert ev(x)["status"]=="TARGET_STATE_DRIFTED"
def test_root_d3_prediction(): test_d03_prediction_laundering()
def test_root_d4_safety():
 x=fx();x["preconditions"][0].update(type="SAFETY",required_state="CLOSED",observed_state="OPEN");assert ev(x)["status"]=="SAFETY_INTERLOCK_FAILED"
def test_root_d5_stale(): test_d05_stale_cache()
def test_root_d6_upstream_removed(): test_d10_precondition_set_mutation()
def test_temporal_conflict():
 x=fx();x["target_snapshot"]["temporal_consistency"]="CONFLICTING";assert ev(x)["status"]!="PRECONDITIONS_SATISFIED"
def test_resource_nonreservation():
 x=fx();r=ev(x);assert r["reservation_created"] is False and x["resource_snapshot"]["reserved"] is False
def test_noncausal_paths():
 for x in (fx(),fx()):
  x["preconditions"][0]["observed_state"]="UNKNOWN"
  r=ev(x)
  for k in ("authorization_created","reservation_created","token_consumed","capability_accessed","execution_performed","p162e_opened"): assert r[k] is False
