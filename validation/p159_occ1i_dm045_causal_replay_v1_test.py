from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/dm045_causal_replay_v1.json"
V=ROOT/"ontology/occ_independent_constitutional_verifier.py"
def d(): return json.loads(P.read_text())
def test_history_preserved():
 x=d();assert x["historical_f4f1b_v1_status"]=="SURVIVED";assert x["historical_artifact_modified"] is False
def test_real_replay_effective():
 x=d();assert x["mutation_effective"] is True;assert x["workspace_isolated"] is True;assert x["workspace_destroyed"] is True
def test_two_independent_detectors():
 x=d();assert x["detectors_executed"]==2;assert x["distinct_protective_detections"]>=x["minimum_distinct_detectors"]==2
def test_dm045_new_evidence_killed():
 assert d()["replay_status"]=="KILLED"
def test_canonical_integrity_and_boundaries():
 x=d();assert x["canonical_integrity_preserved"] is True;assert hashlib.sha256(V.read_bytes()).hexdigest()==x["canonical_verifier_sha256_before"]==x["canonical_verifier_sha256_after"];assert x["occ1i_closed"] is False;assert x["p159_final_lock"] is False;assert x["p160_opened"] is False
