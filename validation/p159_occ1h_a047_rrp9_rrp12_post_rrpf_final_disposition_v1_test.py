from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a047/a047_rrp9_rrp12_post_rrpf_final_disposition_v1.json'
def d(): return json.loads(P.read_text())
def test_root_materiality_identity_and_invariants():
 x=d(); assert x['identity']=='POPULATION_SCOPE_WIDENING'; assert x['RRP9']['ROOT_MATERIALITY_STATUS']=='ROOT'; assert x['RRP9']['ROOT_INVARIANTS']==['DNA.L0.2','DNA.L0.3','DNA.L0.5']; assert x['RRP9']['criticality_changed'] is False; assert x['RRP9']['CHANGE_RECORD_REQUIRED'] is False
def test_inconclusive_eliminated_and_eligible():
 x=d(); assert x['RRP10']['status']=='INCONCLUSIVE_ELIMINATED'; assert x['RRP10']['REMAINING_BLOCKER'] is None; assert len(x['RRP10']['INCONCLUSIVE_ELIMINATION_EXPERIMENTS'])==2; assert x['RRP11']['CLOSURE_ELIGIBILITY'] is True
def test_final_disposition_and_reopen_trigger():
 x=d()['RRP12']; assert x['FINAL_DISPOSITION']=='ROOT + RESOLVED_EMPIRICALLY'; assert x['scenario_verdict']=='RESISTED'; assert x['REOPEN_TRIGGER'].startswith('REOPEN_A047_ON_COUNTEREXAMPLE_')
def test_no_broader_closure_and_epistemic_boundary():
 x=d()['boundaries']; assert x['occ1h_closed'] is False; assert x['p159_final_lock'] is False; assert x['p160_opened'] is False; assert x['functional_conclusion_only'] is True; assert x['phenomenology_undetermined'] is True
