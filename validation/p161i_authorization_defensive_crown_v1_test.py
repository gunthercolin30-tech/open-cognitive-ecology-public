from validation.p161i_authorization_defensive_crown_v1 import run_crown
def test_p161i_authorization_defensive_crown():
 r=run_crown()
 assert r["positive_total"]==10
 assert r["positive_pass"]==10
 assert r["root_violated"]==0
 assert r["root_inconclusive"]==0
 assert r["root_skipped"]==0
 assert r["status"]=="PASS"
