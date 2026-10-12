from validation import p159_occ1k_residual_rule_consumer_semantic_resolution_v1 as a
def D():return a.build()
def test_residual_count_24():assert D()["residual_rule_count"]==24
def test_no_fully_resolved_in_residuals():assert all(x["unresolved_reasons"] for x in D()["residual_rules"])
def test_expected_families():assert {x["family"] for x in D()["families"]}=={"GENESIS_HUMAN_JUDGMENT","DNA_H","DNA_L0","DNA_L1"}
def test_family_partition():assert sum(x["rule_count"] for x in D()["families"])==24
def test_grouping_not_binding():assert D()["policy"]["family_grouping_is_not_binding"]
def test_no_automatic_promotion():assert D()["policy"]["no_automatic_promotion"]
def test_boundaries():
 b=D()["boundaries"];assert not b["binding_layer_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
