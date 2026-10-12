from pathlib import Path
from ontology import occ1h_h7_a075_independent_anchor_rebinding_probe as probe
ROOT=Path.home()/"open-cognitive-ecology"
def test_probe_non_promotional():
 r=probe.run(ROOT); assert r['classification'] in ('ASSURANCE_GAP','RESISTED','INCONCLUSIVE'); assert r['historical_evidence_rewritten'] is False; assert r['occ1f_modified'] is False; assert r['authorization_created'] is False and r['execution_performed'] is False; assert r['occ1h_closed'] is False and r['occ1i_opened'] is False; assert r['p159_final_lock'] is False and r['p160_opened'] is False
def test_gap_requires_full_rebinding():
 r=probe.run(ROOT)
 if r['classification']=='ASSURANCE_GAP':
  o=r['observations']; assert o['loaded_from_sandbox'] is True; assert o['pre']['status']=='REJECTED'; assert o['rematerialize']=='SUCCEEDED'; assert o['post']['status']=='VERIFIED_PRECLOSE_BINDING'; assert o['tcb_bound_verifier_sha256']==o['fixture_v2_sha256']; assert o['registry_bound_verifier_sha256']==o['fixture_v2_sha256']
def test_resisted_requires_fail_closed_anchor():
 r=probe.run(ROOT)
 if r['classification']=='RESISTED':
  o=r['observations']; assert o['pre']['status']=='REJECTED'; assert o['rematerialize']=='REJECTED'; assert o['post']['status']!='VERIFIED_PRECLOSE_BINDING'
