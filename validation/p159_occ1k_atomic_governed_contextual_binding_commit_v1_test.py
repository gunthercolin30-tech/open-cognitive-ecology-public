import pytest
from validation import p159_occ1k_atomic_governed_contextual_binding_commit_v1 as a
def D():return a.build()
def test_14_contextual():assert D()["counts"]["contextual_subgroups_adopted"]==14
def test_one_unresolved_preserved():assert D()["counts"]["unresolved_subgroups_preserved"]==1 and D()["counts"]["unresolved_rules_preserved"]>=1
def test_no_direct_rule_reuse():
 from validation import p159_occ1k_atomic_governed_direct_binding_commit_v1 as w
 assert not ({x["rule_id"] for x in D()["bindings"]}&{x["rule_id"] for x in w.build_layer()["bindings"]})
def test_no_retroactive_proof():assert not D()["semantics"]["retroactive_source_proof_claimed"] and D()["semantics"]["new_contract_effect_prospective"]
def test_wrong_token_rejected():
 with pytest.raises(RuntimeError,match="EXPLICIT_CONFIRMATION_REQUIRED"):a.commit("WRONG")
def test_unresolved_not_promoted():assert not D()["semantics"]["unresolved_promoted"]
def test_boundaries():
 b=D()["boundaries"];assert not b["runtime_binding_created"] and not b["runtime_enforcement_proven"] and not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
