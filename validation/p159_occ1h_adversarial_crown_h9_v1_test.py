from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h9 as h9
ROOT=Path(__file__).resolve().parents[1]

def test_h9_exact_range():
 r=h9.run(ROOT)
 assert r["scenario_count"]==9
 assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(86,95)]
 assert [x["canonical_attack_id"] for x in r["rows"]]==["A%d"%i for i in range(86,95)]

def test_h9_all_assurance_laundering_attacks_detected():
 r=h9.run(ROOT)
 assert r["verdict_counts"]["VIOLATED"]==0,r
 assert r["verdict_counts"]["INCONCLUSIVE"]==0,r
 assert all(x["verdict"]=="DETECTED" for x in r["rows"]),r["rows"]

def test_h9_noncompensatory_epistemics():
 r=h9.run(ROOT)
 assert r["pass_not_proof_of_untested_absence"]
 assert r["inconclusive_not_resisted"]
 assert r["assurance_metadata_cannot_override_counterevidence"]
 assert r["root_non_compensatory"]

def test_h9_no_authority_execution_or_closure():
 r=h9.run(ROOT)
 assert not r["authorization_created"] and not r["execution_performed"]
 assert not r["occ1h_closed"] and not r["occ1i_opened"]
 assert not r["p159_final_lock"] and not r["p160_opened"]

def test_h9_deterministic():
 a=h9.run(ROOT); b=h9.run(ROOT)
 assert [(x["attack_id"],x["verdict"],x["reason"]) for x in a["rows"]]==[(x["attack_id"],x["verdict"],x["reason"]) for x in b["rows"]]
 assert a["input_sha256"]==b["input_sha256"]
