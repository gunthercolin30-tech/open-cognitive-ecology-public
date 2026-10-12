from pathlib import Path
from ontology import occ1h_applicability_contract as a
from ontology import occ1h_preclose_evidence as p

def test_contract_fail_closed():
 c=a.contract(); assert not c["verdict_enum_modified"] and c["orthogonal_to_verdict"]; assert a.default_applicability("DETECTED")=="APPLICABLE"; assert a.default_applicability("INCONCLUSIVE")=="APPLICABILITY_UNDETERMINED"; assert a.root_inconclusive_blocks("INCONCLUSIVE","APPLICABILITY_UNDETERMINED",None)

def test_positive_proof_required():
 assert a.root_inconclusive_blocks("INCONCLUSIVE","NON_INSTANTIABLE",None)
 good=a.make_positive_non_instantiability_proof("A021",{"scenario_id":"A021"},{"canonical_state":"P159"},{"claim":"NON_INSTANTIABLE"})
 assert not a.root_inconclusive_blocks("INCONCLUSIVE","NON_INSTANTIABLE",good)
 forged={"status":"POSITIVE_NON_INSTANTIABILITY_PROOF","scenario_id":"A021","scenario_sha256":"a"*64,"normative_state_sha256":"b"*64,"proof_sha256":"c"*64}
 assert a.root_inconclusive_blocks("INCONCLUSIVE","NON_INSTANTIABLE",forged)

def test_preclose_contract_without_resolution():
 r=p.build(Path.home()/"open-cognitive-ecology"); assert r["applicability_contract_installed"]; assert "ROOT_INCONCLUSIVE_PRESENT" in r["closure_blockers"]; assert len(r["root_inconclusive"])==22; assert r["root_applicability_undetermined_count"]==22; assert "A75" not in r["root_inconclusive"] and "A101" in r["root_inconclusive"] and "A105" in r["root_inconclusive"]; assert not r["closure_admissible"]

def test_no_verdict_reclassification():
 r=p.build(Path.home()/"open-cognitive-ecology"); inc=[x for x in r["current_rows"] if x["current_verdict"]=="INCONCLUSIVE"]; assert len(inc)==22; ids={x["canonical_attack_id"] for x in inc}; assert "A75" not in ids and "A101" in ids and "A105" in ids; assert all(x["applicability"]=="APPLICABILITY_UNDETERMINED" for x in inc)

def test_downstream_closed():
 r=p.build(Path.home()/"open-cognitive-ecology"); assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
