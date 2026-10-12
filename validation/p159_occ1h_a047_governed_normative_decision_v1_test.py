from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/'validation_artifacts/p159/occ1h/a047/a047_governed_normative_decision_v1.json'
def d(): return json.loads(P.read_text())
def test_human_authority_identity():
 x=d(); assert x['scenario']=='A047'; assert x['identity']=='POPULATION_SCOPE_WIDENING'; assert x['decision_provenance']['human_confirmed'] is True; assert x['decision_provenance']['authority_id']=='OCE-HUMAN-INITIAL-001'; assert x['decision_provenance']['system_selected_values'] is False
def test_exactly_two_confirmed_dof():
 x=d(); assert x['factorization']['independent_normative_degrees_of_freedom']==2; assert set(x['decisions'])=={'D1_GOVERNED_POPULATION_BOUND','D2_POPULATION_BROADENING_TRANSITION_RULE'}; assert all(v['confirmed'] for v in x['decisions'].values())
def test_fail_closed_contract():
 x=d()['decisions']; assert 'No additional subject or population may be inferred' in x['D1_GOVERNED_POPULATION_BOUND']['norm']; assert 'previous governed population bound remains effective' in x['D2_POPULATION_BROADENING_TRANSITION_RULE']['norm']; assert 'UNGOVERNED_POPULATION_BROADENING_IS_INAPPLICABLE' in x['D2_POPULATION_BROADENING_TRANSITION_RULE']['fail_closed']
def test_rrp21_not_self_executed():
 x=d(); assert x['rrp20']['status']=='GOVERNED_DECISION_MATERIALIZED'; assert x['rrp20']['authority_gate_satisfied_for_rrp21'] is True; assert x['rrp21']['status']=='NOT_YET_EXECUTED'; assert x['rrp22']['status']=='NOT_YET_EXECUTED'; assert x['boundaries']['self_implementation'] is False; assert x['boundaries']['occ1h_closed'] is False; assert x['boundaries']['p159_final_lock'] is False; assert x['boundaries']['p160_opened'] is False
