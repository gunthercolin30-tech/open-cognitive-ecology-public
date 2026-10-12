from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]; P=R/'validation_artifacts/p159/occ1h/a041/a041_rrpf_v1.json'
def d(): return json.loads(P.read_text())
def test_rrp21_boundary():
 x=d()['RRP_F']['RRP21']; assert x['cases']=={'after':False,'at':False,'before':True,'ungoverned_before':False}; assert x['status']=='REMEDIATION_IMPLEMENTED_AND_EXPERIMENTALLY_DISCRIMINATED'
def test_rrp21_degradation():
 x=d()['RRP_F']['RRP21']['degradation']; assert x['missing_subject_id']=='FAIL_CLOSED'; assert x['unresolved_clock_inconsistency']=='FAIL_CLOSED'; assert x['historical_pre_sunset_record']=='PRESERVED'
