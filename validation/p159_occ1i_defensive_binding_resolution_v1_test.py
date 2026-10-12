from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/defensive_binding_resolution_v1.json"
def load(): return json.loads(P.read_text())
def test_no_empirical_reclassification():
 d=load(); assert d["f4b_statuses_not_reclassified"] is True; assert d["empirical_kill_claims_created"]==0; assert d["binding_is_not_detector_evidence"] is True
def test_accounting():
 d=load(); assert d["input_unresolved_count"]==11; assert d["structurally_bound_count"]+d["semantic_target_unresolved_count"]==11
def test_provenance_debt_preserved():
 d=load(); assert set(["DM002","DM003","DM005"]).issubset(set(d["provenance_debt_ids"])); assert d["provenance_debt_blocks_empirical_upgrade"] is True
def test_dm045_and_boundaries():
 d=load(); assert d["dm045_survived_retained"] is True; assert d["dm045_status"]=="SURVIVED"; assert d["extended_opened"] is False; assert d["occ1i_closed"] is False; assert d["p159_final_lock"] is False; assert d["p160_opened"] is False
def test_bound_bindings_have_real_hashes_and_hits():
 d=load()
 for b in d["bindings"]:
  if b["state"]=="STRUCTURALLY_BOUND":
   assert len(b["target_sha256"])==64; assert b["anchor_hit_count"]>0
  elif b["state"]=="STRUCTURALLY_BOUND_WITH_PROVENANCE_DEBT":
   assert b["candidate_count"]>0
