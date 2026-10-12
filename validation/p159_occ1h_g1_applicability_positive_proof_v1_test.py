from ontology import occ1h_g1_applicability_positive_proof as q
from ontology import occ1h_applicability_contract as c

def test_g1_remains_fail_closed_without_positive_proof():
 e=q.qualification(); assert e["decision"]=="NO_POSITIVE_NON_INSTANTIABILITY_PROOF_YET"
 assert e["positive_non_instantiability_proof_count"]==0
 assert e["applicability_undetermined_count"]==4 and e["g1_root_inconclusive_resolved"]==0
 assert all(r["root_closure_blocking"] for r in e["records"].values())

def test_representation_boundary_not_promoted():
 e=q.qualification()
 for a in ("A021","A041","A042"):
  assert e["records"][a]["gap_classification"]=="REPRESENTATION_BOUNDARY"
  assert e["records"][a]["applicability"]=="APPLICABILITY_UNDETERMINED"
  assert not e["records"][a]["positive_non_instantiability_proof_valid"]

def test_normative_gap_not_laundered():
 r=q.qualification()["records"]["A040"]
 assert r["gap_classification"]=="NORMATIVE_GAP"
 assert r["applicability"]=="APPLICABILITY_UNDETERMINED"
 assert r["reason"]=="NORMATIVE_GAP_CANNOT_BE_LAUNDERED_AS_NON_INSTANTIABLE"

def test_contract_rejects_absence_as_positive_proof():
 assert not c.validate_positive_non_instantiability(None)
 assert not c.validate_positive_non_instantiability({})
 assert c.root_inconclusive_blocks("INCONCLUSIVE","NON_INSTANTIABLE",None)

def test_downstream_stays_closed():
 e=q.qualification()
 assert not e["occ1h_closed"] and not e["occ1i_opened"]
 assert not e["p159_final_lock"] and not e["p160_opened"]
 assert not e["historical_verdicts_modified"] and not e["canonical_sources_modified"]
