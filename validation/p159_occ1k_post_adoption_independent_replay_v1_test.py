from validation import p159_occ1k_post_adoption_independent_replay_v1 as a
def test_exact_binding_set(): r=a.build();assert r["binding_count"]==8 and sum(map(len,r["phase_bindings"].values()))==8
def test_s7_materialized(): assert a.build()["s7"]["status"]=="PASS"
def test_s8_materialized(): assert a.build()["s8"]["status"]=="PASS"
def test_s10_not_overpromoted(): r=a.build();assert r["s10"]["status"]=="PARTIAL" and not r["runtime_enforcement_proven"]
def test_flb3_stays_blocked(): r=a.build();assert r["fl_b3"].startswith("BLOCKED") and not r["lock_ready"] and not r["lock_granted"] and not r["p160b_opened"]
def test_no_authorization_execution(): r=a.build();assert not r["authorization_created"] and not r["execution_performed"]
def test_deterministic(): assert a.build()==a.build()

def test_canonical_target_phase_labels_are_normalized():
 r=a.build()
 assert len(r["phase_bindings"]["S7"])==3
 assert len(r["phase_bindings"]["S8"])==3
 assert len(r["phase_bindings"]["S10"])==2
