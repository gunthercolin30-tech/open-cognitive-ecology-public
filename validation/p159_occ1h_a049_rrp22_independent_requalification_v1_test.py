from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a049/a049_rrp22_independent_requalification_v1.json'
def test_rrp22():
 x=json.loads(P.read_text()); assert x['RRP22']['status']=='PASSED'; assert x['RRP22']['candidate_verdict']=='RESISTED'; assert x['independence']['fresh_interpreters']==2; assert x['independence']['rrp21_artifact_used_as_oracle'] is False
def test_controls():
 x=json.loads(P.read_text())['experiments']; assert x['positive_1']==x['positive_2']; assert x['positive_1']['status']=='RESISTED'; assert x['admissible_control']['status']=='ADMISSIBLE_CONTROL'; assert x['degradation_control']['status']=='UNRESOLVED'
def test_boundaries():
 b=json.loads(P.read_text())['boundaries']; assert b=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
