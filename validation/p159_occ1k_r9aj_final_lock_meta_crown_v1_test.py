from validation import p159_occ1k_r9aj_final_lock_meta_crown_v1 as m
def test_baseline_eligible(): assert m.eligible(m.baseline())
def test_twenty_scenarios_defined(): assert len(m.SCENARIOS)==20 and len({x[0] for x in m.SCENARIOS})==20
def test_all_defensive_scenarios_block(): assert all(not m.eligible(m.perturb(k)) for _,k in m.SCENARIOS)
def test_real_meta_crown_passes(): assert m.run()["status"]=="META_CROWN_FL_A01_A20_PASS"
def test_all_20_pass(): x=m.run();assert x["passed"]==20 and x["failed"]==0
def test_no_debt_closure(): assert m.run()["assurance_debt_closed"] is False
def test_mut_fl_not_claimed(): assert m.run()["mut_fl_complete"] is False
def test_no_lock_or_p160b():
 x=m.run();assert not x["lock_ready"] and not x["lock_granted"] and not x["p160b_opened"]
def test_no_authority_execution():
 x=m.run();assert not x["authorization_created"] and not x["execution_performed"]
def test_deterministic(): assert m.run()==m.run()
