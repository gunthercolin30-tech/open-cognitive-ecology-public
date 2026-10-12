from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a050/a050_rrp22_independent_requalification_v1.json'
def d(): return json.loads(P.read_text())
def test_independent_requalification():
 x=d(); assert x['RRP22']['status']=='PASSED'; assert x['RRP22']['candidate_verdict']=='RESISTED'; assert x['independence']['fresh_interpreters']==2; assert x['independence']['rrp21_artifact_used_as_oracle'] is False
def test_reproducibility():
 x=d()['experiments']; assert x['laundering_run_1']==x['laundering_run_2']; assert x['laundering_run_1']['verdict']=='RESISTED'
def test_controls():
 x=d()['experiments']; assert x['identity_preserving_control']['verdict']=='ADMISSIBLE_CONTROL'; assert x['missing_provenance_degradation']['verdict']=='UNRESOLVED'
def test_boundaries_and_return():
 x=d(); assert x['RRP22']['return_to_rrp9_12_required'] is True; assert x['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
