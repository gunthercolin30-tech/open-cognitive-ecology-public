from validation import p159_occ1k_genesis_g0_resolution_assessment_v1 as a
def D():return a.build()
def test_id():assert D()["canonical_id"]=="GENESIS.G0"
def test_human_judgment():assert D()["assessment"]["human_governed_semantic_decision_required"]
def test_no_machine_formalization():assert not D()["assessment"]["machine_formalization_claimed"]
def test_no_source_proven_ccad():assert not D()["assessment"]["ccad_binding_proven_by_source"]
def test_no_automatic_binding():assert not D()["assessment"]["consumer_binding_derivable_automatically"]
def test_fail_closed_default():assert D()["default_decision"]=="KEEP_GENESIS_G0_UNRESOLVED"
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["runtime_binding_created"] and not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
