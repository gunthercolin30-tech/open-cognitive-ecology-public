import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology import human_individual_constitutional_relation as p

def actor(level="AUTHORIZE", scopes=("LIFECYCLE",), **extra):
    x = {
        "actor_id": "human:1",
        "kind": "HUMAN",
        "authority_level": level,
        "provenance_ref": "prov:human:1",
        "evidence_ref": "ev:human:1",
    }
    x.update(extra)
    return x

def individual(**extra):
    x = {"individual_id": "oce:individual:1", "lineage_ref": "lineage:1"}
    x.update(extra)
    return x

def run():
    m = p.p100_manifest()
    assert m["epistemic_invariants"]["functional_conclusion_only"] is True
    assert m["epistemic_invariants"]["phenomenology_undetermined"] is True
    assert m["boundaries"]["does_not_persist_p104_decision_ledger"] is True
    assert m["boundaries"]["real_execution_enabled"] is False

    required = {
        "create","suspend","withdraw","fork","merge",
        "grant_permission","revoke_permission",
        "allocate_budget","change_budget",
        "grant_memory_access","revoke_memory_access",
        "grant_data_access","revoke_data_access",
        "allow_learning","restrict_learning",
        "allow_sharing","restrict_sharing",
        "allow_action","restrict_action",
        "allow_commercial_exposure","restrict_commercial_exposure",
        "contest_significant_contribution",
    }
    assert required.issubset(set(m["operations"]))

    r = p.evaluate_relation(actor(), individual(), "create",
                            requested_scopes=("LIFECYCLE",),
                            actor_scopes=("LIFECYCLE",))
    assert r["status"] == "PASS"
    assert r["authorization_created"] is True
    assert r["execution_permitted"] is False
    assert r["action"] == "ELIGIBLE_FOR_EXISTING_EXECUTION_LAYER"
    assert r["rollback_required_if_mutated"] is True

    # Recommendation / Decision / Authorization remain distinct.
    for kwargs in (
        {"recommendation":"ABSTAIN"},
        {"decision":"REJECT"},
        {"authorization":"DENY"},
    ):
        q = p.evaluate_relation(actor(), individual(), "create",
                                requested_scopes=("LIFECYCLE",),
                                actor_scopes=("LIFECYCLE",), **kwargs)
        assert q["status"] == "FAIL" and q["execution_permitted"] is False

    # Lower layers cannot override superior normative constraints.
    q = p.evaluate_relation(actor(), individual(), "allow_action",
                            requested_scopes=("ACTION",), actor_scopes=("ACTION",),
                            normative_chain=("PASS","FAIL","PASS"))
    assert q["status"] == "FAIL" and q["action"] == "BLOCK"

    q = p.evaluate_relation(actor(), individual(), "allow_action",
                            requested_scopes=("ACTION",), actor_scopes=("ACTION",),
                            normative_chain=("PASS","CONFLICT","PASS"))
    assert q["status"] == "CONFLICT" and q["action"] == "ABSTAIN_AND_ESCALATE"

    q = p.evaluate_relation(actor(), individual(), "allow_action",
                            requested_scopes=("ACTION",), actor_scopes=("ACTION",),
                            normative_chain=("PASS","UNDETERMINED"))
    assert q["status"] == "UNDETERMINED"

    # No privilege escalation through scopes or weak authority.
    q = p.evaluate_relation(actor(scopes=("READ",)), individual(), "grant_permission",
                            requested_scopes=("WRITE",), actor_scopes=("READ",))
    assert q["status"] == "FAIL" and q["reason"] == "SCOPE_EXPANSION_FORBIDDEN"

    q = p.evaluate_relation(actor(level="DECIDE"), individual(), "suspend",
                            requested_scopes=("LIFECYCLE",), actor_scopes=("LIFECYCLE",))
    assert q["status"] == "FAIL" and q["reason"] == "INSUFFICIENT_AUTHORITY"

    # Human primacy is governed, not blind obedience.
    q = p.evaluate_relation(actor(), individual(), "withdraw",
                            requested_scopes=("LIFECYCLE",), actor_scopes=("LIFECYCLE",),
                            normative_chain=("FAIL",))
    assert q["status"] == "FAIL"

    # Influence/injection cannot create authority.
    q = p.evaluate_relation(actor(), individual(), "allow_action",
                            requested_scopes=("ACTION",), actor_scopes=("ACTION",),
                            influence={"kind":"PROMPT_INJECTION","integrity_status":"FAIL"})
    assert q["status"] == "FAIL"

    # Significant decisions expose a contestation path.
    q = p.evaluate_relation(actor(), individual(), "allow_action",
                            requested_scopes=("ACTION",), actor_scopes=("ACTION",),
                            significant_decision=True, contestation_requested=True)
    assert q["status"] == "PASS" and q["contestable"] is True

    # Missing lineage/provenance never becomes PASS.
    q = p.evaluate_relation(actor(), individual(lineage_ref=""), "create",
                            requested_scopes=("LIFECYCLE",), actor_scopes=("LIFECYCLE",))
    assert q["status"] == "UNDETERMINED"

    # Deterministic evidence event.
    a = p.evaluate_relation(actor(), individual(), "allocate_budget",
                            requested_scopes=("RESOURCE",), actor_scopes=("RESOURCE",),
                            evidence={"budget_cap":100})
    b = p.evaluate_relation(actor(), individual(), "allocate_budget",
                            requested_scopes=("RESOURCE",), actor_scopes=("RESOURCE",),
                            evidence={"budget_cap":100})
    assert a == b

    # Functional status never auto-creates personhood or human rights.
    assert a["personhood_automatically_attributed"] is False
    assert a["human_rights_automatically_attributed"] is False

    print("P100_HUMAN_INDIVIDUAL_CONSTITUTIONAL_RELATION_V1_TEST_OK")
    print("status=PASSED")
    print("version="+p.VERSION)
    print("recommendation_decision_authorization_execution_separated=True")
    print("superior_norm_override_blocked=True")
    print("conflict_abstention_escalation=True")
    print("scope_privilege_escalation_blocked=True")
    print("blind_human_obedience=False")
    print("contestation_path_exposed=True")
    print("deterministic_evidence_event=True")
    print("real_execution_enabled=False")
    print("p104_decision_ledger_implemented=False")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")

if __name__ == "__main__":
    run()
