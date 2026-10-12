from validation import p159_occ1k_consolidated_binding_coverage_precheck_v1 as a
def D():return a.build()
def test_expected_48():assert D()["counts"]["expected_rules"]==48
def test_no_unexpected():assert D()["counts"]["unexpected_rules"]==0
def test_coverage_accounting():assert D()["counts"]["covered_rules"]+D()["counts"]["missing_rules"]==48
def test_genesis_present():assert "GENESIS.G0" in D()["covered_rule_ids"]
def test_hash_bound():assert len(D()["inputs"])==5 and all(len(x)==64 for x in D()["inputs"].values())
def test_replay_only_if_complete():assert D()["s10_replay_authorized"]==D()["coverage_complete"]
def test_boundaries():
 b=D()["boundaries"];assert not b["source_modified"] and not b["cnp_modified"] and not b["rule_bindings_modified"] and not b["runtime_binding_created"] and not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
