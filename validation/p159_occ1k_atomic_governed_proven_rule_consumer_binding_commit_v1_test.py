from validation import p159_occ1k_atomic_governed_proven_rule_consumer_binding_commit_v1 as a
import pytest
def L():return a.build_layer()
def test_partition_24_23_1():
 c=L()["counts"];assert (c["rules"],c["fully_resolved_adopted"],c["partial_preserved"],c["unresolved_preserved"])==(48,24,23,1)
def test_partial_not_promoted():
 assert all(x["unresolved_reasons_preserved"] for x in L()["rules"] if x["binding_state_at_adoption"]=="PARTIAL_KEEP_UNRESOLVED")
def test_unresolved_gets_no_binding():
 assert all(not x["adopted_consumers"] for x in L()["rules"] if x["binding_state_at_adoption"]=="UNRESOLVED_NO_BINDING_PROPOSED")
def test_candidates_not_adopted_implicitly():
 assert all(set(x["adopted_consumers"]).isdisjoint(set(x["candidate_not_adopted_consumers"])) for x in L()["rules"])
def test_wrong_confirmation_rejected():
 with pytest.raises(RuntimeError,match="EXPLICIT_CONFIRMATION_REQUIRED"):a.commit("WRONG")
def test_no_runtime_claim():
 s=L()["semantics"];assert not s["runtime_reachability_claimed"] and not s["runtime_enforcement_proven"]
def test_dossier_hash_bound():assert L()["source_dossier_sha256"]==a.sha(a.DOSSIER)
def test_deterministic():assert L()==L()
