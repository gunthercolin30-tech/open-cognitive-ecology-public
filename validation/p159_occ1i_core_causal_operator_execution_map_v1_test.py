from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
A=ROOT/"validation_artifacts/p159/occ1i/core_causal_operator_execution_map_v1.json"
B=ROOT/"validation_artifacts/p159/occ1i/core_causal_operator_execution_map_v2.json"
def load(p): return json.loads(p.read_text())
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def test_v1_historical_artifact_is_immutable():
 assert sh(A)=="d4860399181c6cb34b600dbc413851dae45e0b96a101600bded66e056e9b884d"
def test_v1_preserves_historical_readout_defect():
 assert load(A)["dm045_historical_status"] is None
def test_v1_did_not_execute_or_reclassify_mutations():
 x=load(A);assert x["planning_only"] is True;assert x["mutations_executed"]==0;assert x["core_statuses_reclassified"] is False
def test_v1_other_structural_results_are_preserved():
 x=load(A);assert x["core_count"]==32;assert x["issues"]==[];assert x["m1_provenance_debt_preserved"] is True
def test_v2_resolves_dm045_readout_without_rewriting_v1():
 x=load(B);assert x["dm045_historical_status"]=="SURVIVED";assert x["dm045_readiness_status"]=="SURVIVED";assert x["dm045_history_consistent"] is True
def test_boundaries_remain_closed_in_v1():
 x=load(A);assert x["extended_opened"] is False;assert x["occ1i_closed"] is False;assert x["p159_final_lock"] is False;assert x["p160_opened"] is False
