from validation.p161j_race_final_compare_crown_v1 import run_crown
def test_p161j_race_final_compare_crown():
 r=run_crown()
 assert r["total"]>=14
 assert r["fail"]==0
 assert r["inconclusive"]==0
 assert r["pass"]==r["total"]
 assert r["status"]=="PASS"
