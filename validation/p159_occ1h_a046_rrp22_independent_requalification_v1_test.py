from ontology.occ1h_a046_rrp22_independent_requalification import independent_oracle,requalify
def test_independent_requalification(): r=requalify(); assert r["status"]=="PASSED_BOUNDED" and r["candidate_verdict"]=="RESISTED" and r["imports_rrp21"] is False
def test_degradation(): assert independent_oracle("FR",None)=="FAIL_CLOSED" and independent_oracle("FR","")=="FAIL_CLOSED"
def test_ungoverned_vs_governed(): assert independent_oracle("FR-ARA-74","FR-ARA",False)=="RESISTED" and independent_oracle("FR-ARA-74","FR-ARA",True)=="GOVERNED_CHANGE"
def test_no_self_certification_or_closure(): r=requalify(); assert r["final_disposition_required"] and not r["criticality_changed"] and r["historical_inconclusive_preserved"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
