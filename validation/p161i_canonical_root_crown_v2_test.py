from validation.p161i_authorization_defensive_crown_v1 import ROOT_IDS,run_canonical_root_crown
def test_root_ids(): assert ROOT_IDS==tuple(f"ROOT-C{i:02d}" for i in range(1,26))
def test_crown():
 r=run_canonical_root_crown();assert r["positive_pass"]==r["positive_total"]==10;assert r["root_pass"]==r["root_total"]==25;assert r["root_violated"]==r["root_inconclusive"]==r["root_skipped"]==0;assert r["status"]=="PASS"
