from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a050/a050_rrpv21_macros_a_to_e_existing_authority_v1.json'
def d(): return json.loads(P.read_text())
def test_identity_and_baseline():
 x=d(); assert x['scenario']=='A050'; assert x['identity']=='ROLE_RENAME_LAUNDERING'; assert x['baseline']['historical_verdict']=='INCONCLUSIVE'
def test_existing_authority_and_minimality():
 x=d()['RRP_E_17_20']; assert x['minimality_audit']['derived_new_normative_decision_count']==0; assert x['RRP20']['gate']=='EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT'; assert x['RRP20']['new_human_normative_decision_required'] is False
def test_rrpf_not_opened():
 x=d(); assert x['RRP_F_21_22']['status']=='NOT_OPENED'; assert x['RRP_B_5_8']['correction_installed'] is False
def test_boundaries():
 assert d()['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
