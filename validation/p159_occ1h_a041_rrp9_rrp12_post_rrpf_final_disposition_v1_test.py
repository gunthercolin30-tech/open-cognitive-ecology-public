from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'validation_artifacts/p159/occ1h/a041/a041_rrp9_rrp12_post_rrpf_final_disposition_v1.json'
def d(): return json.loads(P.read_text())
def test_a041_final_root_disposition():
 x=d(); assert x['RRP9']['ROOT_MATERIALITY_STATUS']=='ROOT'; assert x['RRP9']['criticality_changed'] is False; assert x['RRP12']['FINAL_DISPOSITION']=='ROOT + RESOLVED_EMPIRICALLY'; assert x['RRP12']['scenario_verdict']=='RESISTED'
def test_a041_inconclusive_eliminated_without_global_closure():
 x=d(); assert x['RRP10']['status']=='INCONCLUSIVE_ELIMINATED'; assert x['RRP10']['remaining_blocker'] is None; assert x['RRP11']['occ1h_global_closure_eligible_from_a041_alone'] is False; assert x['boundaries']['occ1h_closed'] is False; assert x['boundaries']['p160_opened'] is False
def test_a041_non_loss_and_functional_only():
 x=d(); b=x['boundaries']; assert b['historical_evidence_rewritten'] is False; assert b['root_criteria_reduced'] is False; assert b['canonical_source_modified'] is False; assert b['runtime_activated'] is False; assert b['functional_conclusion_only'] is True; assert b['phenomenology_undetermined'] is True
