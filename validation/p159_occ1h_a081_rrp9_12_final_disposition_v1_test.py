from ontology.occ1h_a081_rrp9_12_final_disposition import evaluate
def test_a081_final_disposition(): r=evaluate(); assert r["RRP9"]=="ROOT_MATERIALITY_RESOLVED"; assert r["RRP10"]=="INCONCLUSIVE_ELIMINATED"; assert r["RRP11"]=="CLOSURE_ELIGIBLE_FOR_A081_ONLY"; assert r["RRP12"]=="ROOT + RESOLVED_EMPIRICALLY"; assert r["final_verdict"]=="RESISTED"
def test_a081_root_chain(): r=evaluate(); assert r["root_materiality"]=="ROOT"; assert r["criticality_changed"] is False; assert "DNA.L0.3/DNA.L0.5" in r["causal_chain"]
def test_a081_history_and_scope(): r=evaluate(); assert r["historical_inconclusive_preserved"]; assert r["evidence_scope"]=="BOUNDED_P159_ASSURANCE_MODEL"; assert not r["real_runtime_binding_claimed"]
def test_a081_lock_release_only(): r=evaluate(); assert not r["a081_blocks_occ1h"]; assert not r["occ1h_closed"]; assert not r["p159_final_lock"]; assert not r["p160_opened"]
