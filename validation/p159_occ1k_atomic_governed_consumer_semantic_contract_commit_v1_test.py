from validation import p159_occ1k_atomic_governed_consumer_semantic_contract_commit_v1 as a
import pytest
def test_contract_six_consumers(): assert len(a.build_contract()["responsibilities"])==6
def test_contract_scope_is_semantic_only():
 s=a.build_contract()["scope"]; assert s["semantic_responsibility_contract_only"] and not s["rule_bindings_modified"] and not s["runtime_reachability_claimed"]
def test_wrong_confirmation_rejected():
 with pytest.raises(RuntimeError,match="EXPLICIT_CONFIRMATION_REQUIRED"): a.commit("WRONG")
def test_no_execution_or_authorization():
 s=a.build_contract()["scope"]; assert not s["authorization_created"] and not s["execution_performed"]
def test_dossier_hash_bound(): assert a.build_contract()["source_dossier_sha256"]==a.sha_file(a.DOSSIER)
def test_deterministic_contract(): assert a.build_contract()==a.build_contract()
