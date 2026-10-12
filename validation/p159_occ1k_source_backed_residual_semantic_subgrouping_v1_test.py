from validation import p159_occ1k_source_backed_residual_semantic_subgrouping_v1 as a
def D():return a.build()
def test_24_rules_preserved():assert D()["rules"]==24
def test_no_duplicate_or_loss():
 ids=[r for g in D()["subgroups"] for r in g["rule_ids"]];assert len(ids)==24 and len(set(ids))==24
def test_subgroups_have_one_signature():assert all(g["source_semantic_signature"] for g in D()["subgroups"])
def test_no_binding_derived():assert D()["counts"]["consumer_bindings_derived"]==0
def test_no_candidates_invented():assert all(not g["consumer_binding_candidates"] for g in D()["subgroups"])
def test_signature_not_binding():assert D()["policy"]["subgroup_signature_is_not_consumer_binding"]
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
