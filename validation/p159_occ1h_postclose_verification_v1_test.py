import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/"validation_artifacts/p159/occ1h"
P=ART/"postclose_verification_v1.json"; C=ART/"governed_closure_v1.json"; E=ART/"global_consolidation_eligibility_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def test_occ1h_postclose_functional():
 x=load(P); assert x["status"]=="POST_CLOSE_VERIFIED"; assert x["occ1h_closed"] is True and x["post_close_verified"] is True
 assert x["h1_h10_covered"] and x["scenarios_accounted"]==105 and x["root_total"]==29
 assert x["active_root_violated_count"]==0 and x["active_root_inconclusive_count"]==0 and x["root_undetermined_count"]==0
def test_occ1h_postclose_independent_binding():
 x=load(P); c=load(C); assert x["verification_mode"]=="INDEPENDENT_READ_ONLY_FAIL_CLOSED"
 assert x["closure_artifact_sha256"]==sha(C); assert x["closure_identity_sha256"]==c["closure_identity_sha256"]
 assert x["eligibility_artifact_sha256"]==sha(E); assert x["bound_source_hashes"]==c["bound_source_hashes"]
def test_occ1h_postclose_non_regression():
 x=load(P); e=load(E); assert x["historical_states_preserved"] and x["root_non_compensatory"]
 assert x["no_scope_reduction_for_closure"] and x["no_production_grand_chain_claim"]
 assert e["historical_inconclusive_preserved"] and e["historical_violations_preserved"]; assert len(e["active_root_states"])==29
 assert all(v["active_verdict"] in {"RESISTED","DETECTED"} for v in e["active_root_states"].values())
def test_occ1h_postclose_boundaries():
 x=load(P); c=load(C); assert c["post_close_verified"] is False and x["post_close_verified"] is True
 assert x["p159_final_lock"] is False and x["p160_opened"] is False
 assert x["authorization_created"] is False and x["execution_performed"] is False
 assert x["functional_conclusion_only"] and x["phenomenology_undetermined"]
 assert not x["consciousness_proven"] and not x["subjectivity_proven"] and not x["qualia_proven"] and not x["phenomenology_proven"]
