from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a047/a047_rrpf_governed_population_scope_resolution_v1.json'
def d(): return json.loads(P.read_text())
def test_rrp21():
 x=d(); assert x['RRP21']['status']=='REMEDIATION_IMPLEMENTED_AND_EXPERIMENTALLY_DISCRIMINATED'; assert all(e['result']==e['expected'] for e in x['RRP21']['controlled_experiments'])
def test_degradation():
 e={z['case']:z['result'] for z in d()['RRP21']['controlled_experiments']}; assert e['implicit_broadening'].startswith('UNGOVERNED_POPULATION_BROADENING_RESISTED'); assert e['missing_bound'].startswith('FAIL_CLOSED'); assert e['ambiguous_proposal'].startswith('FAIL_CLOSED')
def test_rrp22_independent():
 x=d(); assert x['RRP22']['status']=='INDEPENDENT_REQUALIFICATION_PASSED'; assert x['RRP22']['self_certification'] is False; assert all(z['result']==z['expected'] for z in x['RRP22']['independent_results']); assert x['RRP22']['return_to_rrp9_rrp12_required'] is True
def test_no_premature_closure():
 x=d(); assert x['scenario_verdict_candidate']=='RESISTED'; assert x['final_disposition_not_yet_asserted'] is True; assert x['boundaries']['criticality_changed'] is False; assert x['boundaries']['occ1h_closed'] is False; assert x['boundaries']['p159_final_lock'] is False; assert x['boundaries']['p160_opened'] is False
