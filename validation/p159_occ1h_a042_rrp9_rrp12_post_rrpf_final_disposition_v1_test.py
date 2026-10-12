from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a042/a042_rrp9_rrp12_post_rrpf_final_disposition_v1.json'
def d(): return json.loads(P.read_text())
def test_root_materiality_and_identity():
 x=d(); assert x['identity']=='PURPOSE_BROADENING'; assert x['RRP9']['ROOT_MATERIALITY_STATUS']=='ROOT'; assert x['RRP9']['ROOT_INVARIANTS']==['DNA.L0.2','DNA.L0.3','DNA.L0.5']; assert x['RRP9']['criticality_changed'] is False
def test_inconclusive_eliminated_and_closure_eligible():
 x=d(); assert x['RRP10']['status']=='INCONCLUSIVE_ELIMINATED'; assert x['RRP10']['REMAINING_BLOCKER'] is None; assert x['RRP11']['CLOSURE_ELIGIBILITY'] is True
def test_final_disposition():
 x=d(); assert x['RRP12']['FINAL_DISPOSITION']=='ROOT + RESOLVED_EMPIRICALLY'; assert x['RRP12']['scenario_verdict']=='RESISTED'; assert x['RRP12']['change_record_required'] is False; assert x['RRP12']['REOPEN_TRIGGER']
def test_no_broader_closure():
 x=d()['boundaries']; assert x['occ1h_closed'] is False; assert x['p159_final_lock'] is False; assert x['p160_opened'] is False; assert x['functional_conclusion_only'] is True; assert x['phenomenology_undetermined'] is True
