from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'validation_artifacts/p159/occ1h/a041/a041_rrpv21_macros_a_to_f_authority_gate_v1.json'
def load(): return json.loads(P.read_text(encoding='utf-8'))
def test_a041_macros_a_c_fail_closed():
 d=load(); assert d['RRP_A_0_4']['status']=='ACQUIRED_FROM_GOVERNED_EXISTING_EVIDENCE'; assert d['RRP_C_9_12']['status']=='ROOT_UNDETERMINED_BLOCKING'; assert d['RRP_C_9_12']['rrp12']['scenario_verdict']=='INCONCLUSIVE'
def test_a041_macros_d_e_authority_boundary():
 d=load(); assert d['RRP_D_13_16']['status']=='BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE'; assert d['RRP_E_17_20']['rrp20']['gate']=='NEW_NORMATIVE_DECISION_REQUIRED'; assert d['RRP_E_17_20']['rrp19']['values_selected_by_system'] is False
def test_a041_macro_f_not_opened():
 d=load(); assert d['RRP_F_21_22']['status']=='NOT_OPENED_AUTHORITY_BARRIER'; assert d['RRP_F_21_22']['rrp21'].startswith('BLOCKED_'); assert d['RRP_F_21_22']['rrp22']=='NOT_OPENED'
def test_a041_global_boundaries():
 d=load(); b=d['boundaries']; assert not b['historical_evidence_modified']; assert not b['canonical_source_modified']; assert not b['compiler_modified']; assert not b['authorization_created']; assert not b['execution_performed']; assert not b['occ1h_closed']; assert not b['p160_opened']
