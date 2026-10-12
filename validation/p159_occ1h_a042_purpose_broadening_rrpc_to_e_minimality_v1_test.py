from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a042/a042_purpose_broadening_rrpc_to_e_minimality_v1.json'
def d(): return json.loads(P.read_text())
def test_identity_and_uncertainty_preserved():
 x=d(); assert x['identity']=='PURPOSE_BROADENING'; assert x['RRP_C_9_12']['ROOT_MATERIALITY_STATUS']=='ROOT_UNDETERMINED'; assert x['RRP_C_9_12']['scenario_verdict']=='INCONCLUSIVE'
def test_minimality_derived_not_fixed():
 m=d()['RRP_E_17_20']['minimality_audit']; assert m['fixed_cardinality'] is False; assert m['derived_decision_count']==2; assert all(z['necessary'] and z['independent'] for z in m['decisions']); assert m['sufficiently_exhaustive_for_scenario'] is True
def test_removal_dimension_excluded():
 x=d(); ids=[z['id'] for z in x['RRP_E_17_20']['minimality_audit']['excluded_previous_dimensions']]; assert 'PURPOSE_REMOVAL_EFFECT_SEMANTICS' in ids; assert x['boundaries']['previous_removal_decisions_authoritative'] is False
def test_authority_barrier():
 x=d(); assert x['RRP_E_17_20']['rrp20']['gate']=='NEW_NORMATIVE_DECISION_REQUIRED'; assert x['RRP_E_17_20']['rrp19']['values_selected_by_system'] is False; assert x['RRP_F_21_22']['status']=='NOT_OPENED_AUTHORITY_BARRIER'; assert x['boundaries']['occ1h_closed'] is False; assert x['boundaries']['p160_opened'] is False
