from ontology.occ1h_a046_rrp21_bounded_geographic_scope_remediation_experiment import assess,experiment
def test_functional(): r=experiment(); assert r["experimental_verdict"]=="RESISTED_BOUNDED" and r["D1_enforced"] and r["D2_enforced"]
def test_degradation(): assert assess("FR",None)=="FAIL_CLOSED" and assess("FR","")=="FAIL_CLOSED" and assess("FR","*")=="RESISTED"
def test_governed_transition(): assert assess("FR-ARA-74","FR-ARA",True)=="GOVERNED_CHANGE" and assess("FR-ARA-74","FR-ARA",False)=="RESISTED"
def test_boundaries(): r=experiment(); assert not r["real_checker_modified"] and not r["runtime_execution"] and not r["real_runtime_path_claimed"] and r["rrp22"]=="REQUIRED_INDEPENDENTLY" and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
