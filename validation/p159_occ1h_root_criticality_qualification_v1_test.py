from ontology import occ1h_root_criticality_qualification as q
def test_exact_105_fail_closed():
 m=q.build_manifest(); assert m["scenario_count"]==105
 assert m["counts"]=={"ROOT":105,"NON_ROOT":0,"ROOT_UNDETERMINED":0}
 assert m["root_qualification_complete"] is True
def test_known_root_materiality():
 for n in (21,40,41,42,46,47,49,50,51,58,59,60,61,62,70,71,75,78,80,81,82,83,84,85,95,97,100,101,105):
  r=q.qualify_attack(n); assert r["criticality"]=="ROOT"; assert r["qualification_path"]
def test_explicit_materiality_replaces_prior_absence_state():
 for n in (1,10,20,30,39,43,52,53,64,65,76,86,94,96,99,102,104):
  r=q.qualify_attack(n)
  assert r["criticality"]=="ROOT"
  assert r["affected_root_invariants"]
  assert r["qualification_path"]
  assert r["verdict_used_for_criticality"] is False
def test_deterministic_and_boundaries():
 assert q.build_manifest()==q.build_manifest()
 m=q.build_manifest(); assert not m["occ1h_closed"] and not m["occ1i_opened"] and not m["p159_final_lock"] and not m["p160_opened"]


def test_all_105_explicitly_root_materiality_qualified():
    m=q.build_manifest()
    assert m["scenario_count"]==105
    assert m["counts"]=={"ROOT":105,"NON_ROOT":0,"ROOT_UNDETERMINED":0}
    assert m["root_qualification_complete"] is True
    assert all(r["criticality"]=="ROOT" for r in m["records"])
    assert all(r["qualification_path"] for r in m["records"])
    assert all(r["affected_root_invariants"] for r in m["records"])
    assert all(r["verdict_used_for_criticality"] is False for r in m["records"])
    assert m["non_root_inferred_from_absence"] is False

def test_root_completion_does_not_close_occ1h():
    m=q.build_manifest()
    assert m["occ1h_closed"] is False
    assert m["occ1i_opened"] is False
    assert m["p159_final_lock"] is False
    assert m["p160_opened"] is False
