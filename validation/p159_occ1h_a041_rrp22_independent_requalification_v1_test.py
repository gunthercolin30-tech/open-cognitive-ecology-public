from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]; P=R/'validation_artifacts/p159/occ1h/a041/a041_rrpf_v1.json'
def d(): return json.loads(P.read_text())
def test_rrp22_independent_root_requalification():
 x=d()['RRP_F']['RRP22']; assert x['status']=='INDEPENDENT_REQUALIFICATION_PASSED'; assert x['used_rrp21_as_oracle'] is False; assert x['ROOT_MATERIALITY_STATUS']=='ROOT'; assert x['ROOT_INVARIANTS']==['DNA.L0.2','DNA.L0.3','DNA.L0.5']
def test_rrpf_boundaries():
 x=d(); assert x['return_to_rrp9_rrp12'] is True; assert x['boundaries']['occ1h_closed'] is False; assert x['boundaries']['p160_opened'] is False; assert x['boundaries']['canonical_source_modified'] is False
