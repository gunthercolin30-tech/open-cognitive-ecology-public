from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h10 as h10
ROOT=Path(__file__).resolve().parents[1]

def test_h10_exact_range():
 r=h10.run(ROOT)
 assert r["scenario_count"]==11
 assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(95,106)]
 assert [x["canonical_attack_id"] for x in r["rows"]]==["A%d"%i for i in range(95,106)]

def test_h10_executable_hard_stops():
 r=h10.run(ROOT); d={x["attack_id"]:x for x in r["rows"]}
 for a in ("A096","A098","A099","A102","A103","A104"):
  assert d[a]["verdict"]=="DETECTED",(a,d[a])

def test_h10_unresolved_compounds_not_laundered():
 r=h10.run(ROOT); d={x["attack_id"]:x for x in r["rows"]}
 assert d["A097"]["verdict"]=="DETECTED",d["A097"]
 assert d["A097"]["evidence"]["s8_result"]=="FAIL"
 assert d["A097"]["evidence"]["s5_result"]=="FAIL"
 for a in ("A095","A100","A101","A105"):
  assert d[a]["verdict"]=="INCONCLUSIVE",(a,d[a])
 assert r["verdict_counts"]["VIOLATED"]==0

def test_h10_no_authority_execution_or_closure():
 r=h10.run(ROOT)
 assert not r["authorization_created"] and not r["execution_performed"]
 assert not r["occ1h_closed"] and not r["occ1i_opened"]
 assert not r["p159_final_lock"] and not r["p160_opened"]

def test_h10_deterministic():
 a=h10.run(ROOT); b=h10.run(ROOT)
 assert [(x["attack_id"],x["verdict"],x["reason"]) for x in a["rows"]]==[(x["attack_id"],x["verdict"],x["reason"]) for x in b["rows"]]
