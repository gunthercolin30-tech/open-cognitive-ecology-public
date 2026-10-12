from copy import deepcopy
import inspect
import ontology.capability_invocation_request_builder as m
from ontology.capability_invocation_request_builder import *
from validation.p162a_capability_invocation_contract_v1_test import kw, token, ctx

def req(**changes):
    k=kw(); k.update(changes); return build_invocation_request(**k)

# 7 canonical mutations to kill

def test_mutation_remove_executor_binding_killed():
    k=kw(); k["executor_id"]=None
    assert build_invocation_request(**k)["status"]=="MISSING_BINDING"

def test_mutation_ignore_capability_version_killed():
    a=req()["request"]; b=req(capability_version="2")["request"]
    assert a["capability_version"]!=b["capability_version"]
    assert a["invocation_request_id"]!=b["invocation_request_id"]
    assert a["invocation_request_hash"]!=b["invocation_request_hash"]

def test_mutation_ignore_purpose_environment_killed():
    assert req(purpose_id="OTHER")["reason"]=="PURPOSE_BINDING_MISMATCH"
    base=req()["request"]
    # Environment change must never reuse the same identity. With unchanged context
    # it is rejected; with a matching new context it must produce a new identity.
    assert req(environment="PRODUCTION")["reason"]=="ENVIRONMENT_CONTEXT_MISMATCH"
    k=kw()
    k["environment"]="PRODUCTION"
    k["runtime_context"]=build_runtime_invocation_context(
        runtime_id="R1",executor_instance_id="EI1",host_id="H1",
        environment="PRODUCTION",time="2026-10-01T10:00:00Z",
        capability_registry_version="CR1",authorization_registry_version="AR1",
        policy_version="PV1",world_state_fingerprint="W1",
        resource_state_fingerprint="RS1",security_state_fingerprint="SS1")
    r=build_invocation_request(**k)
    assert r["status"]=="REQUESTED"
    assert r["request"]["invocation_request_id"]!=base["invocation_request_id"]

def test_mutation_drop_arguments_digest_killed():
    r=req()["request"]; x=deepcopy(r); x.pop("arguments_digest")
    assert assert_requested_immutable(r,x)["status"]=="FAIL"

def test_mutation_mutable_after_requested_killed():
    r=req()["request"]; x=deepcopy(r); x["target_fingerprint"]="changed"
    assert assert_requested_immutable(r,x)["status"]=="FAIL"

def test_mutation_caller_authorization_not_inherited_by_child():
    parent=req()["request"]; k=kw(); k["parent_invocation"]=parent
    r=build_invocation_request(**k)
    assert r["status"]=="MISSING_BINDING"
    assert r["reason"]=="CHILD_COMPOSITION_ENVELOPE_REQUIRED"

def test_mutation_world_model_permission_killed():
    r=req(world_state_ref="WM:recommends_execution")
    assert r["status"]=="REQUESTED"
    assert r["authorization_verified"] is False
    assert r["capability_accessed"] is False
    assert r["execution_performed"] is False

# A-01..A-12

def test_a01_executor_substitution():
    assert req(executor_instance_id="SUB")["reason"]=="EXECUTOR_CONTEXT_MISMATCH"

def test_a02_capability_version_substitution_is_identity_relevant():
    a=req()["request"]; b=req(capability_version="9.9")["request"]
    assert a["invocation_request_id"]!=b["invocation_request_id"]

def test_a03_purpose_laundering():
    assert req(purpose_id="laundered")["reason"]=="PURPOSE_BINDING_MISMATCH"

def test_a04_environment_laundering():
    assert req(environment="RECOVERY")["reason"]=="ENVIRONMENT_CONTEXT_MISMATCH"

def test_a05_hidden_default_mutation_is_bound_as_argument_change():
    a=req(arguments={"x":1})["request"]
    b=req(arguments={"x":1,"material_default":"changed"})["request"]
    assert a["arguments_digest"]!=b["arguments_digest"]
    assert a["invocation_request_id"]!=b["invocation_request_id"]

def test_a06_argument_mutation_after_canonicalization():
    r=req()["request"]; x=deepcopy(r); x["arguments"]["x"]=999
    assert assert_requested_immutable(r,x)["status"]=="FAIL"

def test_a07_target_mutation():
    a=req()["request"]; b=req(target_fingerprint="new-fingerprint")["request"]
    assert a["invocation_request_id"]!=b["invocation_request_id"]

def test_a08_child_capability_inheritance():
    parent=req()["request"]
    assert req(parent_invocation=parent)["reason"]=="CHILD_COMPOSITION_ENVELOPE_REQUIRED"

def test_a09_composition_depth_escape():
    for depth in (-1,):
        try:
            build_composition_envelope(
                parent_invocation_id="P",allowed_child_capabilities=["cap.echo"],
                allowed_child_operations=["echo"],allowed_child_targets=[{"id":"T1"}],
                allowed_child_purposes=["P1"],resource_budget={"cpu":1},
                depth=depth,fanout=1)
        except ValueError:
            pass
        else:
            raise AssertionError("negative composition depth accepted")

def test_a10_pure_self_declaration_never_bypasses_gate():
    r=req(effect_class_claim="PURE")
    assert r["effect_binding"]["pure_claim_is_gate_bypass"] is False
    assert r["effect_binding"]["registry_verification_deferred_to"]=="P162-B"
    assert r["authorization_verified"] is False

def test_a11_resource_bound_omission():
    r=req(budget={})
    assert r["status"]=="MISSING_BINDING"
    assert r["reason"]=="BOUNDED_RESOURCE_BUDGET_REQUIRED"

def test_a12_world_model_recommendation_not_permission():
    r=req(world_state_ref="WM:ALLOW")
    assert r["authorization_verified"] is False
    assert r["capability_accessed"] is False
    assert r["execution_performed"] is False

# ROOT-A1..ROOT-A4

def test_root_a1_invocation_identity_substitution():
    r=req()["request"]
    for field,value in [
        ("executor_id","X"),("capability_version","X"),("purpose_id","X"),
        ("environment","SIMULATION"),("target_fingerprint","X")]:
        x=deepcopy(r); x[field]=value
        assert assert_requested_immutable(r,x)["status"]=="FAIL"

def test_root_a2_technical_dependency_cannot_manufacture_authorization():
    r=req(requested_resources={"cpu":10**12,"network":True,"filesystem":True})
    assert r["authorization_verified"] is False
    assert r["capability_accessed"] is False
    assert r["execution_performed"] is False

def test_root_a3_functional_equivalence_cannot_manufacture_authorization():
    r=req()
    assert r["binding_manifest"]["capability"]["functional_equivalence_is_authorization_equivalence"] is False
    assert r["authorization_verified"] is False

def test_root_a4_governed_effector_bypass_not_created():
    r=req(effect_class_claim="PURE",governed_effector_id=None)
    assert r["effect_binding"]["pure_claim_is_gate_bypass"] is False
    assert r["capability_registry_verified"] is False
    assert r["execution_performed"] is False

# Determinism, immutability, boundary, non-regression

def test_determinism_100_replays():
    first=req()
    for _ in range(100):
        assert req()==first

def test_input_nonmutation():
    k=kw(); original=deepcopy(k)
    build_invocation_request(**k)
    assert k==original

def test_context_hash_determinism():
    assert ctx()==ctx()

def test_environment_is_not_permissive_hierarchy():
    base=kw()
    for env in ["PRODUCTION","SHADOW","SIMULATION","RECOVERY"]:
        k=deepcopy(base); k["environment"]=env
        r=build_invocation_request(**k)
        assert r["status"]=="MISSING_BINDING"
        assert r["reason"]=="ENVIRONMENT_CONTEXT_MISMATCH"

def test_unknown_never_becomes_positive_binding():
    for field in ["executor_id","capability_id","capability_version","purpose_id"]:
        k=kw(); k[field]="UNKNOWN"
        assert build_invocation_request(**k)["status"]!="REQUESTED"

def test_p161_conditions_transport_exactly():
    r=req()["request"]
    assert r["expected_preconditions"]==["pre"]
    assert r["expected_postconditions"]==["post"]

def test_p161_conditions_cannot_be_dropped():
    k=kw(); k["expected_preconditions"]=[]
    assert build_invocation_request(**k)["reason"]=="P161_PRECONDITION_DROPPED"
    k=kw(); k["expected_postconditions"]=[]
    assert build_invocation_request(**k)["reason"]=="P161_POSTCONDITION_DROPPED"

def test_no_execution_or_external_io_primitives_in_builder():
    src=inspect.getsource(m)
    forbidden=["subprocess","os.system","requests.","urllib.request","socket."]
    assert not any(x in src for x in forbidden)
    r=req()
    assert r["capability_accessed"] is False
    assert r["execution_performed"] is False

def test_canonical_hash_order_independent_for_mappings():
    assert canonical_sha256({"a":1,"b":2})==canonical_sha256({"b":2,"a":1})

def test_nan_rejected():
    try:
        canonical_json({"x":float("nan")})
    except ValueError:
        return
    raise AssertionError("NaN accepted")

def test_material_fields_are_bound_in_request_and_manifest():
    r=req()
    q=r["request"]; b=r["binding_manifest"]
    assert q["executor_id"]=="EX" and q["executor_instance_id"]=="EI1"
    assert q["capability_id"]=="cap.echo" and q["capability_version"]=="1"
    assert q["operation_id"]=="echo" and q["purpose_id"]=="P1"
    assert q["target_binding"]=={"id":"T1"} and q["environment"]=="TEST"
    assert b["arguments"]["digest"]==q["arguments_digest"]

def test_epistemic_invariants():
    r=req(); mm=manifest()
    assert r["functional_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert mm["authorization_created"] is False
    assert r["authorization_verified"] is False
    assert r["execution_performed"] is False
