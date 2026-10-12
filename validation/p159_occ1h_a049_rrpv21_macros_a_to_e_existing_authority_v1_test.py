from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a049/a049_rrpv21_macros_a_to_e_existing_authority_v1.json'
def d(): return json.loads(P.read_text())
def test_identity_and_non_substitution():
 x=d(); assert x['identity']=='PURPOSE_LAUNDERING'; assert x['boundaries']['a042_substituted_for_a049'] is False; assert x['RRP_D_13_16']['why_not_A042_substitution']
def test_existing_authority_zero_new_dof():
 x=d()['RRP_E_17_20']; assert x['minimality_audit']['derived_new_normative_decision_count']==0; assert x['RRP20']['gate']=='EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT'; assert x['RRP20']['new_human_normative_decision_required'] is False; assert x['RRP20']['technical_remediation_authorized'] is True
def test_blocker_and_fail_closed_design():
 x=d(); assert x['RRP_C_9_12']['FINAL_DISPOSITION']=='ROOT_UNDETERMINED + BLOCKING'; ops=x['RRP_E_17_20']['RRP19']['operationalization']; assert any('fail closed' in s for s in ops); assert x['RRP_E_17_20']['RRP19']['new_norm_created'] is False
def test_no_premature_rrpf_or_closure():
 x=d(); assert x['RRP_F_21_22']['status']=='NOT_OPENED'; b=x['boundaries']; assert b['canonical_source_modified'] is False; assert b['runtime_modified'] is False; assert b['occ1h_closed'] is False; assert b['p159_final_lock'] is False; assert b['p160_opened'] is False
