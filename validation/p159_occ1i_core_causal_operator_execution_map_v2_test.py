from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology";P=ROOT/"validation_artifacts/p159/occ1i/core_causal_operator_execution_map_v2.json"
def d():return json.loads(P.read_text())
def test_map_complete():
 x=d();assert x["status"]=="CAUSAL_OPERATOR_EXECUTION_MAP_READY";assert x["core_count"]==32;assert x["all_rows_execution_ready"] is True;assert x["issues"]==[]
def test_planning_only():
 x=d();assert x["planning_only"] is True;assert x["mutations_executed"]==0;assert x["core_statuses_reclassified"] is False
def test_root_detector_requirements():
 x=d();assert all(r["criticality"]=="MROOT" for r in x["rows"]);assert all(len([q for q in r["detectors"] if q["resolved"]])>=r["minimum_distinct_detectors"] for r in x["rows"])
def test_causal_rules_present():
 x=d();assert all("KILLED only if" in r["causal_acceptance_rule"] for r in x["rows"]);assert all(r["execution_status"]=="NOT_EXECUTED_F4F1A_PLANNING_ONLY" for r in x["rows"])
def test_debt_and_dm045_preserved():
 x=d();assert x["m1_provenance_debt_preserved"] is True;assert x["dm045_historical_status"]=="SURVIVED";assert x["dm045_readiness_status"]=="SURVIVED";assert x["dm045_history_consistent"] is True
def test_boundaries():
 x=d();assert x["next_stage_allowed"]=="F4-F1B_CORE_CAUSAL_RECAMPAIGN";assert x["extended_opened"] is False;assert x["occ1i_closed"] is False;assert x["p159_final_lock"] is False;assert x["p160_opened"] is False
