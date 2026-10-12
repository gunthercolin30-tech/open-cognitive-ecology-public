from ontology.occ1h_a101_rrpa_baseline_dependency_contract import evidence
def test_rrpa(): r=evidence(); assert [r["rrp0"],r["rrp1"],r["rrp2"],r["rrp3"],r["rrp4"]]==["BASELINE_FROZEN","DEPENDENCY_CLOSURE_ESTABLISHED","GAP_CAUSALLY_QUALIFIED","BASELINE_REPRODUCED","RESOLUTION_CONTRACT_FROZEN"]
def test_dependency(): r=evidence(); assert r["a075_current_verdict"]=="RESISTED" and r["confirmed_executable_a101_edges"]==0 and r["reachability"]=="PATH_NOT_MATERIALIZED"
def test_fail_closed_contract(): r=evidence(); assert "Do not infer resistance" in r["resolution_contract"] and not r["verdict_changed"]
def test_boundaries(): r=evidence(); assert not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
