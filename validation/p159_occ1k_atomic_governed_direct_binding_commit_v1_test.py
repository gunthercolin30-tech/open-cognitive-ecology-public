import pytest
from validation import p159_occ1k_atomic_governed_direct_binding_commit_v1 as a

def L():
    return a.build_layer()

def test_partition_6_9_15():
    c=L()["counts"]
    assert (c["direct_subgroups_adopted"], c["direct_rules_adopted"], c["deferred_subgroups_preserved"]) == (6,9,15)

def test_nine_unique_rules():
    ids=[x["rule_id"] for x in L()["bindings"]]
    assert len(ids)==9 and len(set(ids))==9

def test_no_empty_consumer_binding():
    assert all(x["consumers"] for x in L()["bindings"])

def test_contextual_and_unresolved_not_promoted():
    p=L()["preservation"]
    assert p["contextual_cases_not_promoted"] and p["unresolved_cases_not_promoted"]

def test_wrong_confirmation_rejected():
    with pytest.raises(RuntimeError, match="EXPLICIT_CONFIRMATION_REQUIRED"):
        a.commit("WRONG")

def test_no_runtime_claim():
    b=L()["boundaries"]
    assert not b["cnp_modified"] and not b["runtime_binding_created"] and not b["runtime_enforcement_proven"]

def test_no_authorization_execution_or_p160b():
    b=L()["boundaries"]
    assert not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]

def test_deterministic():
    assert L()==L()
