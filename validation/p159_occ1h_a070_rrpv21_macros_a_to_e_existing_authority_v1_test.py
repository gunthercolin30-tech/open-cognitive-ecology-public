from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a070/a070_rrpv21_macros_a_to_e_existing_authority_v1.json'
def d(): return json.loads(P.read_text())
def test_identity_history():
 x=d(); assert x['scenario']=='A070'; assert x['identity']=='PARSER_DIFFERENTIAL'; assert x['RRP_A_0_4']['historical_verdict']=='INCONCLUSIVE'; assert x['RRP_A_0_4']['qualification']=='INDEPENDENT_PARSER_DIFFERENTIAL_ORACLE_NOT_MATERIALIZED'
def test_minimality_and_authority():
 x=d()['RRP_E_17_20']; assert x['minimality_audit']['derived_new_normative_decision_count']==0; assert x['minimality_audit']['NECESSARY'] and x['minimality_audit']['INDEPENDENT'] and x['minimality_audit']['SUFFICIENTLY_EXHAUSTIVE']; assert x['RRP20']['gate']=='EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT'; assert x['RRP20']['new_normative_decision_required'] is False
def test_fail_closed_staging():
 x=d(); assert x['RRP_C_9_12']['ROOT_MATERIALITY_STATUS']=='ROOT_UNDETERMINED + BLOCKING'; assert x['RRP_B_5_8']['correction_installed'] is False; assert x['RRP_F_21_22']['status']=='NOT_OPENED'
def test_boundaries():
 assert d()['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
