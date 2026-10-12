from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/core_causal_recampaign_v1.json"
def d(): return json.loads(P.read_text())
def test_complete_core_accounting():
 x=d();assert x["core_count"]==32;assert len(x["results"])==32
def test_fail_closed_semantics():
 x=d();assert x["unsupported_recipe_is_inconclusive"] is True;assert x["killed_requires_causal_execution"] is True
def test_canonical_integrity():
 x=d();assert x["canonical_integrity_preserved"] is True;assert x["canonical_target_hashes_before"]==x["canonical_target_hashes_after"]
def test_isolation_and_boundaries():
 x=d();assert x["workspaces_isolated"] is True;assert x["workspaces_destroyed"] is True;assert x["extended_opened"] is False;assert x["occ1i_closed"] is False;assert x["occ1j_opened"] is False;assert x["p159_final_lock"] is False;assert x["p160_opened"] is False
def test_dm045_history_and_debt_preserved():
 x=d();assert x["dm045_historical_status"]=="SURVIVED";assert x["m1_provenance_debt_preserved"] is True
def test_no_false_killed():
 x=d()
 for r in x["results"]:
  if r["status"]=="KILLED":
   assert r["recipe_applicable"] is True and r["mutation_effective"] is True
   assert r["syntax_valid"] is True
   assert r["distinct_protective_detections"]>=r["minimum_distinct_detectors"]
