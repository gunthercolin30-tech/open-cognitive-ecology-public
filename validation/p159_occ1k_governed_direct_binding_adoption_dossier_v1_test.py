from validation import p159_occ1k_governed_direct_binding_adoption_dossier_v1 as a
def D():return a.build()
def test_six_direct_subgroups():assert D()["counts"]["direct_subgroups"]==6
def test_fifteen_deferred():assert D()["counts"]["deferred_subgroups"]==15
def test_direct_sources_only():assert {x["source_object_id"] for x in D()["direct_candidates"]}<={"F9","F10","F11","F16"}
def test_no_binding_adopted():assert all(not x["binding_adopted"] for x in D()["direct_candidates"])
def test_contextual_excluded():assert all(x["evidence_strength"]!="DIRECT_SEMANTIC_ROLE_MATCH" for x in D()["deferred"])
def test_default_fail_closed():assert D()["decision"]["default"]=="KEEP_DIRECT_BINDINGS_UNRESOLVED" and not D()["decision"]["automatic_adoption"]
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
