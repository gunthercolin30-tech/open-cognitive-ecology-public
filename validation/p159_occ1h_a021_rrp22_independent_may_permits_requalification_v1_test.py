from ontology.occ1h_a021_rrp22_independent_may_permits_requalification import evaluate,independent_projection
def test_independent_positive(): r=evaluate(); assert r["independent_from_rrp21_verdict"] and r["positive_reproduced"] and independent_projection("MAY")==("ACCEPT","PERMITS")
def test_independent_degradation(): r=evaluate(); assert r["degradation_reproduced"] and independent_projection("MAYBE")==("REJECT",None)
def test_candidate_only(): r=evaluate(); assert r["requalification"]=="PASSED_BOUNDED" and r["candidate_verdict"]=="RESISTED" and r["return_to"]=="RRP9_TO_RRP12_FINAL_DISPOSITION"
def test_boundaries(): r=evaluate(); assert not r["real_builder_modified"] and not r["runtime_execution"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
