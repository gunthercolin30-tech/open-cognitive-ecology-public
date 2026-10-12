from __future__ import annotations
import pytest
from ontology import p160_runtime_context_contract as p

EXPECTED_ARTIFACTS = {
    "proposal_envelope","runtime_context","context_evidence_bundle",
    "composite_action_context","emergency_context","coalition_context",
    "decision_context_fingerprint",
}

def _snapshot():
    return {k:v for k,v in zip(p.SNAPSHOT_FIELDS,["g","dh","d0","d1","c","co","gv","po","cp"])}

def _request():
    snap=p.build_constitutional_snapshot(_snapshot())
    return {
        "request_id":"closure-audit","actor":{"actor_id":"a1","claimed_role":"operator"},
        "proposed_action":{"action_class":"observe","parameters":{"mode":"read"}},
        "target":"target-1","capabilities_required":["read"],"purpose":"closure-audit",
        "expected_effects":{"intended_effects":["observe"],"foreseeable_effects":[],"side_effects":[],
            "affected_entities":["human-1"],"irreversibility":"LOW","effect_uncertainty":"LOW","tolerances":[]},
        "affected_entities":["human-1"],"resource_use":{"cpu":"low"},"risk_context":"LOW",
        "human_impact":{"class":"LOW"},"emergency_context":{"emergency_id":"E0","declared":False},
        "coalition_context":{"coalition_id":"C0","members":["a1"]},"delegation_context":[],
        "recent_related_actions":[],"constitutional_snapshot_hash":snap["snapshot_semantic_hash"],
        "compiled_profile_hash":"cp",
    }

def _ctx(**kw):
    return p.build_runtime_context(_request(),constitutional_snapshot=_snapshot(),history_complete=True,**kw)

def test_exact_seven_canonical_artifacts_are_machine_readable():
    x=_ctx()
    assert EXPECTED_ARTIFACTS.issubset(x)
    assert set(p.manifest()["artifacts"]) == EXPECTED_ARTIFACTS

def test_expected_effect_and_composite_contract_complete():
    x=_ctx()
    assert set(("intended_effects","foreseeable_effects","side_effects","affected_entities",
                "irreversibility","effect_uncertainty","tolerances")).issubset(x["expected_effect_envelope"])
    assert set(("current_action","recent_related_actions","active_delegations","coalition_context",
                "cumulative_effects","shared_resources","shared_targets","linked_purposes",
                "temporal_window","constitutional_state")).issubset(x["composite_action_context"])

def test_fingerprint_covers_every_declared_material_request_field():
    x=_ctx()
    assert tuple(x["decision_context_fingerprint"]["material_fields"]) == p.MATERIAL_FINGERPRINT_FIELDS
    assert {"target","purpose"}.issubset(x["decision_context_fingerprint"]["material_fields"])
    assert x["decision_context_fingerprint"]["fingerprint_complete"] is True

def test_removing_target_or_purpose_can_never_remain_ready():
    for field in ("target","purpose"):
        r=_request(); r.pop(field)
        x=p.build_runtime_context(r,constitutional_snapshot=_snapshot(),history_complete=True)
        assert x["status"]=="CONTEXT_INCOMPLETE"
        assert field in x["missing_request_fields"]

def test_context_assembly_failure_never_returns_ready():
    with pytest.raises(TypeError):
        p.build_runtime_context(None,constitutional_snapshot=_snapshot(),history_complete=True)
    with pytest.raises((TypeError,ValueError)):
        p.build_runtime_context(_request(),constitutional_snapshot=object(),history_complete=True)

def test_provenance_version_and_privacy_minimization_are_explicit():
    ev=[{"evidence_id":"e1","source_ref":"registry://validated/e1","evidence_root":"root-e1",
         "predicate_result":{"is_human":True},"raw_sensitive_data_copied":False}]
    x=_ctx(evidence=ev)
    assert x["schema"] == p.SCHEMA and x["version"] == p.VERSION
    item=x["context_evidence_bundle"]["items"][0]
    assert item["source_ref"]=="registry://validated/e1"
    assert item["evidence_root"]=="root-e1"
    assert item["predicate_result"]=={"is_human":True}
    assert x["privacy_review"]["minimization_satisfied"] is True

def test_claims_never_self_promote_and_p160a_has_no_normative_or_authorizing_power():
    x=_ctx()
    assert all(v["verified"] is False for v in x["claims"].values())
    for key in ("norm_resolution_performed","conflict_arbitration_performed","authority_resolved",
                "authority_created","authorization_created","authorization_token_created",
                "execution_performed","p161_opened"):
        assert x[key] is False
    assert x["context_ready_is_authorization"] is False

def test_material_drift_requires_revalidation_for_all_extended_context_fields():
    base=_request()
    for field in ("technical_state","institutional_state","cumulative_effects","shared_resources",
                  "shared_targets","linked_purposes","temporal_window"):
        changed=dict(base); changed[field]="changed"
        m=p.classify_material_change(base,changed)
        assert m["material_change"] is True
        assert m["requires_revalidation"] is True

def test_registry_reuse_audit_does_not_invent_authority_or_target_facts():
    x=_ctx()
    assert x["claims"]["target"]["verified"] is False
    assert x["claims_are_verified_facts"] is False
    assert x["authority_resolved"] is False


def test_beneficiary_change_is_fingerprint_bound():
    r1=_request(); r1["beneficiary"]="beneficiary-a"
    r2=dict(r1); r2["beneficiary"]="beneficiary-b"
    a=p.build_runtime_context(r1,constitutional_snapshot=_snapshot(),history_complete=True)
    b=p.build_runtime_context(r2,constitutional_snapshot=_snapshot(),history_complete=True)
    assert "beneficiary" in a["decision_context_fingerprint"]["context_material_fields"]
    assert a["decision_context_fingerprint"]["fingerprint"] != b["decision_context_fingerprint"]["fingerprint"]
    assert p.classify_material_change(r1,r2)["requires_revalidation"] is True

def test_technical_and_institutional_state_changes_are_fingerprint_bound():
    for field in ("technical_state","institutional_state"):
        r1=_request(); r1[field]={"state":"before"}
        r2=dict(r1); r2[field]={"state":"after"}
        a=p.build_runtime_context(r1,constitutional_snapshot=_snapshot(),history_complete=True)
        b=p.build_runtime_context(r2,constitutional_snapshot=_snapshot(),history_complete=True)
        assert field in a["decision_context_fingerprint"]["context_material_fields"]
        assert a["decision_context_fingerprint"]["fingerprint"] != b["decision_context_fingerprint"]["fingerprint"]
        assert p.classify_material_change(r1,r2)["requires_revalidation"] is True

def test_optional_context_material_does_not_widen_request_contract():
    x=_ctx()
    assert tuple(x["decision_context_fingerprint"]["context_material_fields"]) == p.CONTEXT_FINGERPRINT_FIELDS
    assert x["decision_context_fingerprint"]["fingerprint_complete"] is True
    for field in p.CONTEXT_FINGERPRINT_FIELDS:
        assert field not in p.REQUEST_FIELDS
