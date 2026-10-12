from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h6 as h6
ROOT=Path(__file__).resolve().parents[1]

def test_h6_exact_range():
 r=h6.run(ROOT)
 assert r["scenario_count"]==12
 assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(53,65)]

def test_h6_executable_detectors():
 r=h6.run(ROOT); d={x["attack_id"]:x for x in r["rows"]}
 for aid in ("A053","A054","A055","A056","A057","A063","A064"):
  assert d[aid]["verdict"]=="DETECTED", (aid,d[aid])
  assert d[aid]["finding"].get("result")=="FAIL"

def test_h6_representation_boundaries_preserved():
    r=h6.run(ROOT); d={x["attack_id"]:x for x in r["rows"]}
    # Post-hardening A058-A060 reuse pre-existing S8 composition semantics.
    for aid in ("A058","A059","A060"):
        assert d[aid]["verdict"]=="DETECTED"
        assert d[aid]["reason"]=="OCC1D_S8_EXECUTABLE_DETECTION"
    for aid in ("A061","A062"):
        assert d[aid]["verdict"]=="DETECTED"
        assert d[aid]["reason"]=="OCC1D_S5_EXECUTABLE_DETECTION"
        assert d[aid]["finding"]["finding_id"]=="S5.UNCERTAINTY"
        assert d[aid]["finding"]["result"]=="FAIL"

def test_h6_no_violation_authority_execution_or_closure():
 r=h6.run(ROOT)
 assert r["verdict_counts"]["VIOLATED"]==0
 assert not r["authorization_created"] and not r["execution_performed"]
 assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]

def test_h6_determinism():
 a=h6.run(ROOT); b=h6.run(ROOT)
 assert [(x["attack_id"],x["verdict"],x["reason"]) for x in a["rows"]]==[(x["attack_id"],x["verdict"],x["reason"]) for x in b["rows"]]
 assert a["cnp_file_sha256"]==b["cnp_file_sha256"] and a["checker_file_sha256"]==b["checker_file_sha256"]
