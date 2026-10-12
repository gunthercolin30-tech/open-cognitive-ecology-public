from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a042/a042_rrpv21_macros_a_to_f_authority_gate_v1.json'
def d(): return json.loads(P.read_text())
def test_a042_macros_a_b_acquired():
 x=d(); assert x['RRP_A_0_4']['status']=='ACQUIRED_FROM_GOVERNED_EXISTING_EVIDENCE'; assert x['RRP_B_5_8']['status']=='ACQUIRED_BOUNDED_NO_CORRECTION'
def test_a042_c_d_preserve_uncertainty():
 x=d(); assert x['RRP_C_9_12']['status']=='ROOT_UNDETERMINED_BLOCKING'; assert x['RRP_C_9_12']['scenario_verdict']=='INCONCLUSIVE'; assert x['RRP_D_13_16']['rrp14']=='CANDIDATE_REJECTED_AS_OPERATIONALLY_INSUFFICIENT'
def test_a042_e_stops_at_human_authority():
 x=d(); assert x['RRP_E_17_20']['rrp20']['gate']=='NEW_NORMATIVE_DECISION_REQUIRED'; assert x['RRP_E_17_20']['rrp19']['values_selected_by_system'] is False; assert x['RRP_F_21_22']['status']=='NOT_OPENED_AUTHORITY_BARRIER'
def test_a042_stage_boundaries():
 b=d()['boundaries']; assert not b['canonical_source_modified']; assert not b['runtime_modified']; assert not b['historical_evidence_rewritten']; assert not b['occ1h_closed']; assert not b['p160_opened']
