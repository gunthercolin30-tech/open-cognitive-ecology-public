import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"validation_artifacts/p159/occ1i/defensive_core_empirical_campaign_v1.json"
def L(): return json.loads(P.read_text(encoding="utf-8"))
def test_f4b_accounting():
 x=L(); assert x["core_count"]==32 and len(x["results"])==32 and sum(x["status_counts"].values())==32
def test_f4b_root_non_compensation():
 x=L(); assert x["root_non_compensatory"] is True
 assert x["core_gate_pass"]==(x["status_counts"]["SURVIVED"]==0 and x["status_counts"]["INCONCLUSIVE"]==0)
def test_f4b_causal_contract():
 x=L()
 for r in x["results"]:
  if r["status"]=="KILLED": assert r["mutation_effective"] and r["distinct_detector_count"]>=2
  if r["status"]=="SURVIVED": assert r["mutation_effective"] and r["distinct_detector_count"]<2
def test_f4b_boundaries():
 x=L(); assert x["canonical_integrity_preserved"] and x["all_workspaces_destroyed"]
 assert not x["occ1i_closed"] and not x["occ1j_opened"] and not x["p159_final_lock"] and not x["p160_opened"]
