from ontology.occ1h_a021_rrpv21_macros_a_to_e_may_permits_authority_gate import evaluate
def test_gate():
 r=evaluate(); assert r["RRP_E"]["rrp20"]=="NEW_NORMATIVE_DECISION_REQUIRED"; assert r["rrp_f"]=="BLOCKED_PENDING_HUMAN_GOVERNANCE"
def test_no_silent_equivalence():
 r=evaluate(); assert r["evidence"]["MAY_equals_PERMITS_not_proven_by_existing_evidence"]; assert r["RRP_E"]["new_normative_degrees_of_freedom"]==1
def test_fail_closed():
 r=evaluate(); assert r["root_status"]=="ROOT + BLOCKING_INCONCLUSIVE"; assert not r["builder_repair_authorized"]; assert not r["semantic_extension_authorized"]
def test_boundaries():
 r=evaluate(); assert r["historical_inconclusive_preserved"]; assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
