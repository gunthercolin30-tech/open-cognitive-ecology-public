from copy import deepcopy
from pathlib import Path
from ontology import occ1h_root_blocker_resolution_matrix as m

def _r(): return m.build(Path.home()/"open-cognitive-ecology")
def test_exact_29_complete_unique():
 r=_r(); ids=[x["scenario_id"] for x in r["rows"]]
 assert len(ids)==29 and len(set(ids))==29 and r["classified_root_inconclusive"]==29
 assert r["unmapped"]==0
def test_groups_and_dependencies():
 r=_r(); assert r["independent_structural_groups"]==7 and r["derived_structural_groups"]==1
 d=r["dependency_edges"]; assert d["A097"]==["A060","A062"]; assert d["A101"]==["A075"]
 assert d["A105"]==["A095","A097","A100","A101"]
def test_g1_fail_closed():
 q={x["scenario_id"]:x for x in _r()["rows"]}
 assert q["A040"]["resolution_category"]=="NORMATIVE_GAP"
 for a in ("A021","A041","A042"): assert q[a]["resolution_category"]=="POSITIVE_NON_INSTANTIABILITY_CANDIDATE"
 assert all(q[a]["proposed_next_state"]=="INCONCLUSIVE" for a in q)
def test_mechanism_and_boundary_partition():
 q={x["scenario_id"]:x for x in _r()["rows"]}
 for a in ("A046","A047","A049","A050","A051","A058","A059","A060","A061","A062","A070","A071","A075","A095","A100"):
  assert q[a]["resolution_category"]=="P159_MECHANISM_REQUIRED"
 for a in ("A078","A080","A081","A082","A083","A084","A085"):
  assert q[a]["resolution_category"]=="P160_BOUNDARY_CANDIDATE"
 for a in ("A097","A101","A105"): assert q[a]["resolution_category"]=="DEPENDENCY_BLOCKED"
def test_no_resolution_or_downstream_opening():
 r=_r(); assert not r["verdicts_modified"] and not r["applicability_reclassified"]
 assert r["root_inconclusive_resolved"]==0 and not r["occ1h_closed"]
 assert not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
 assert not r["authorization_created"] and not r["execution_created"] and not r["normative_auto_rewrite"]
def test_source_hash_drift_is_observable():
 r=_r(); assert len(r["source_hashes"])>=8
 assert all(len(v)==64 for v in r["source_hashes"].values())
def test_categories_are_exhaustive():
 r=_r(); assert sum(r["categories"].values())==29
 assert set(r["categories"])==set(m.CATEGORIES)
