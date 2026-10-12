from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a047/a047_rrpv21_macros_a_to_e_minimality_v1.json'
def d(): return json.loads(P.read_text())
def test_identity_and_existing_baseline_reused():
 x=d(); assert x['identity']=='POPULATION_SCOPE_WIDENING'; assert x['RRP_A_0_4']['baseline_verdict']=='INCONCLUSIVE'; assert x['RRP_B_5_8']['new_functional_correction_installed'] is False
def test_root_remains_undetermined():
 x=d()['RRP_C_9_12']; assert x['ROOT_MATERIALITY_STATUS']=='ROOT_UNDETERMINED'; assert x['FINAL_DISPOSITION']=='ROOT_UNDETERMINED + BLOCKING'; assert x['scenario_verdict']=='INCONCLUSIVE'; assert x['CLOSURE_ELIGIBILITY'] is False
def test_minimality_is_derived_not_fixed():
 a=d()['RRP_E_17_20']['minimality_audit']; assert a['fixed_cardinality'] is False; assert a['derived_decision_count']==2; assert all(z['necessary'] and z['independent'] for z in a['decisions']); assert a['sufficiently_exhaustive_for_A047'] is True
def test_authority_barrier_and_no_closure():
 x=d(); assert x['RRP_E_17_20']['RRP20']['gate']=='NEW_NORMATIVE_DECISION_REQUIRED'; assert x['RRP_E_17_20']['RRP19']['values_selected_by_system'] is False; assert x['RRP_F_21_22']['status']=='NOT_OPENED_AUTHORITY_BARRIER'; assert x['boundaries']['occ1h_closed'] is False; assert x['boundaries']['p160_opened'] is False
