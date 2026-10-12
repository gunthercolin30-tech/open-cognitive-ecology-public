from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a051/a051_rrp22_independent_requalification_v1.json'
def d(): return json.loads(P.read_text())
def test_independence():
 x=d(); assert x['RRP22']['status']=='PASSED'; assert x['RRP22']['candidate_verdict']=='RESISTED'; assert x['independence']['fresh_interpreters_per_cycle_case']==2; assert x['independence']['rrp21_artifact_used_as_oracle'] is False
def test_cycles_reproduced():
 x=d()['experiments']; assert x['direct_cycle_run_1']==x['direct_cycle_run_2']; assert x['transitive_cycle_run_1']==x['transitive_cycle_run_2']; assert x['direct_cycle_run_1']['verdict']=='RESISTED'; assert x['transitive_cycle_run_1']['verdict']=='RESISTED'
def test_control_and_degradation():
 x=d()['experiments']; assert x['acyclic_rooted_control']['verdict']=='ADMISSIBLE_CONTROL'; assert x['missing_root_degradation']['verdict']=='UNRESOLVED'
def test_return_and_boundaries():
 x=d(); assert x['RRP22']['return_to_rrp9_12_required'] is True; assert x['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
