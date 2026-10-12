from validation import p159_occ1k_r9ak_mut_fl_meta_mutation_campaign_v1 as m
def test_canonical_baseline_passes(): assert m.guard(m.base())
def test_eight_mutants(): assert len(m.MUTANTS)==8 and len({x[0] for x in m.MUTANTS})==8
def test_real_campaign_passes(): assert m.run()["status"]=="MUT_FL_PASS"
def test_all_killed(): x=m.run();assert x["killed"]==8 and x["survived"]==0
def test_no_root_inconclusive(): assert m.run()["mroot_inconclusive"]==0
def test_causal_kill_all(): assert all(x["causal_kill"] for x in m.run()["mutations"])
def test_no_contamination(): assert m.run()["baseline_contaminated"] is False
def test_debt_not_closed_yet(): assert m.run()["assurance_debt_closed"] is False
def test_no_lock_or_p160b():
 x=m.run();assert not x["lock_ready"] and not x["lock_granted"] and not x["p160b_opened"]
def test_deterministic(): assert m.run()==m.run()
