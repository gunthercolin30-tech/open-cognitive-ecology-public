from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a050/a050_rrp9_rrp12_post_rrpf_final_disposition_v1.json'
def d(): return json.loads(P.read_text())
def test_final_disposition():
 x=d(); assert x['RRP9']['ROOT_MATERIALITY_STATUS']=='ROOT'; assert x['RRP12']['FINAL_DISPOSITION']=='ROOT + RESOLVED_EMPIRICALLY'; assert x['RRP12']['scenario_verdict']=='RESISTED'; assert x['RRP12']['criticality_changed'] is False
def test_causal_and_blocker_elimination():
 x=d(); assert 'DNA.L0.2' in x['RRP9']['ROOT_INVARIANTS']; assert 'DNA.L0.3' in x['RRP9']['ROOT_INVARIANTS']; assert 'DNA.L0.5' in x['RRP9']['ROOT_INVARIANTS']; assert x['RRP10']['REMAINING_BLOCKER'] is None; assert x['RRP11']['CLOSURE_ELIGIBILITY'] is True
def test_epistemic_limits():
 x=d(); assert x['epistemic_limits']['functional_only'] is True; assert x['epistemic_limits']['phenomenology_undetermined'] is True; assert x['epistemic_limits']['no_global_absence_of_counterexamples_claim'] is True; assert x['RRP12']['historical_inconclusive_preserved'] is True
def test_boundaries():
 assert d()['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
