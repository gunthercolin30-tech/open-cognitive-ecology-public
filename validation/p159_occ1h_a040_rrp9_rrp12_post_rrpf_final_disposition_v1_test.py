from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'validation_artifacts/p159/occ1h/a040/a040_rrp9_rrp12_post_rrpf_final_disposition_v1.json'
def test_a040_post_rrpf_disposition():
 d=json.loads(P.read_text(encoding='utf-8')); assert d['RRP9']['ROOT_MATERIALITY_STATUS']=='ROOT'; assert d['RRP12']['FINAL_DISPOSITION']=='ROOT + RESOLVED_EMPIRICALLY'; assert d['RRP12']['scenario_verdict']=='RESISTED'; assert d['RRP10']['REMAINING_BLOCKER'] is None; assert d['boundaries']['occ1h_closed'] is False; assert d['boundaries']['p160_opened'] is False
def test_a040_non_compensatory_boundaries():
 d=json.loads(P.read_text(encoding='utf-8')); assert d['RRP12']['criticality_changed'] is False; assert d['boundaries']['historical_evidence_modified'] is False; assert d['boundaries']['root_criteria_reduced'] is False; assert d['boundaries']['root_to_non_root_reclassification'] is False
