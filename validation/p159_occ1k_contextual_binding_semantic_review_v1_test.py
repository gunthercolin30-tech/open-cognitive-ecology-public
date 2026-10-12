from validation import p159_occ1k_contextual_binding_semantic_review_v1 as a
def D():return a.build()
def test_15_residual():assert D()["counts"]["residual_subgroups"]==15
def test_14_contextual():assert D()["counts"]["contextual"]==14
def test_one_unresolved():assert D()["counts"]["unresolved"]==1
def test_no_new_binding():assert D()["counts"]["new_bindings_adopted"]==0 and all(not x["binding_adopted"] for x in D()["residual_subgroups"])
def test_direct_not_precedent():assert D()["conclusion"]["r9w_direct_bindings_not_reused_as_precedent"]
def test_keyword_mapping_forbidden():assert D()["conclusion"]["keyword_mapping_forbidden"]
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["runtime_binding_created"] and not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
