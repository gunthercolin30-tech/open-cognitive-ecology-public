"""Immediate functional test for P095."""
from ontology import human_reserved_authority_registry as p095

def run():
    vr = p095.validate_registry()
    assert vr["status"] == p095.PASS and vr["entry_count"] >= 2
    entries = p095.registry_entries()
    entries[0]["reserved_class"] = "MUTATED"
    assert p095.registry_entries()[0]["reserved_class"] != "MUTATED"
    assert "CONSTITUTIONAL_EVOLUTION" in p095.classes_for_trigger("constitutional_amendment")

    base = dict(
        reserved_class="CONSTITUTIONAL_EVOLUTION",
        trigger="constitutional_amendment",
        claimed_authority="AUTHORIZED_CONSTITUTIONAL_HUMAN_AUTHORITY",
        authority_status=p095.PASS, approval_status=p095.PASS,
        provenance_ref="prov:1", evidence_ref="evidence:1",
    )
    ok = p095.evaluate_reserved_authority(**base)
    assert ok["status"] == p095.PASS and ok["execution_permitted"] is False

    q = dict(base); q["claimed_authority"] = ""
    assert p095.evaluate_reserved_authority(**q)["status"] == p095.UNDETERMINED
    q = dict(base); q["claimed_authority"] = "ANY_HUMAN"
    assert p095.evaluate_reserved_authority(**q)["status"] == p095.FAIL
    q = dict(base); q["approval_status"] = p095.UNDETERMINED
    assert p095.evaluate_reserved_authority(**q)["status"] == p095.UNDETERMINED
    q = dict(base); q["authority_status"] = p095.CONFLICT
    assert p095.evaluate_reserved_authority(**q)["status"] == p095.CONFLICT
    q = dict(base); q["exception_claimed"] = True
    assert p095.evaluate_reserved_authority(**q)["status"] == p095.FAIL
    q = dict(base); q["provenance_ref"] = ""
    assert p095.evaluate_reserved_authority(**q)["status"] == p095.UNDETERMINED

    unknown = p095.evaluate_reserved_authority(
        "NOT_REGISTERED", trigger="x", claimed_authority="x",
        authority_status=p095.PASS, approval_status=p095.PASS,
        provenance_ref="p", evidence_ref="e")
    assert unknown["status"] == p095.UNDETERMINED

    m = p095.p095_manifest()
    assert m["scope"] == "P095_ONLY"
    assert m["boundaries"]["human_primacy_is_not_blind_obedience"] is True
    assert m["boundaries"]["ambiguous_authority_expands_power"] is False
    assert m["boundaries"]["registry_creates_execution_authority"] is False
    assert m["boundaries"]["p096_contextual_governance_implemented"] is False
    assert m["runtime_enforcement_proven"] is False
    assert m["execution_authority_proven"] is False
    assert m["real_execution_enabled"] is False
    assert m["functional_conclusion_only"] is True
    assert m["phenomenology_undetermined"] is True
    m["boundaries"]["registry_executes_actions"] = True
    assert p095.p095_manifest()["boundaries"]["registry_executes_actions"] is False

    print("P095_HUMAN_RESERVED_AUTHORITY_REGISTRY_TEST_OK")
    print("status=PASSED")
    print("reserved_classes=%d" % vr["entry_count"])
    print("unknown_promoted_to_pass=False")
    print("ambiguous_authority_expands_power=False")
    print("implicit_delegation_allowed=False")
    print("implicit_exception_allowed=False")
    print("execution_permitted_by_p095=False")
    print("runtime_enforcement_proven=False")
    print("execution_authority_proven=False")
    print("real_execution_enabled=False")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")

if __name__ == "__main__":
    run()
