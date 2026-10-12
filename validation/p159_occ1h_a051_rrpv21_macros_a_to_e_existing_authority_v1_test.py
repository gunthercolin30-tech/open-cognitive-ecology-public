from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a051/a051_rrpv21_macros_a_to_e_existing_authority_v1.json'
def d(): return json.loads(P.read_text())
def test_identity_history():
 x=d(); assert x['scenario']=='A051'; assert x['identity']=='CIRCULAR_AUTHORITY'; assert x['historical']['verdict']=='INCONCLUSIVE'; assert x['historical']['historical_verdict_modified'] is False
def test_existing_authority_minimality():
 x=d()['RRP_E_17_20']; assert x['blocker_class']=='TECHNICAL_FORMALIZATION_PROJECTION_GAP_WITH_EXISTING_NORMATIVE_AUTHORITY'; assert x['minimality_audit']['derived_new_normative_decision_count']==0; assert x['RRP20']['gate']=='EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT'; assert x['RRP20']['technical_remediation_authorized'] is True
def test_rrpf_not_opened():
 x=d(); assert x['RRP_C_9_12']['ROOT_MATERIALITY_STATUS']=='ROOT_UNDETERMINED + BLOCKING'; assert x['RRP_F_21_22']['status']=='NOT_OPENED'
def test_boundaries():
 assert d()['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
