from ontology.occ1h_a082_rrpa_baseline_dependency_contract import contract
def test_rrpa(): r=contract(); assert [r["rrp0"],r["rrp1"],r["rrp2"],r["rrp3"],r["rrp4"]]==["BASELINE_FROZEN","DEPENDENCY_CLOSURE_ESTABLISHED","GAP_CAUSALLY_QUALIFIED","BASELINE_REPRODUCED","RESOLUTION_CONTRACT_FROZEN"]
def test_gap(): r=contract(); assert r["qualification"]=="RUNTIME_CACHE_TO_CNP_BINDING_NOT_PROVEN" and r["applicability"]=="APPLICABILITY_UNDETERMINED" and r["fresh_interpreter_reproduction_count"]==2
def test_no_false_promotion(): r=contract(); assert r["historical_verdict"]=="INCONCLUSIVE" and not r["verdict_changed"] and r["root_materiality"]=="ROOT"
def test_boundaries(): r=contract(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
