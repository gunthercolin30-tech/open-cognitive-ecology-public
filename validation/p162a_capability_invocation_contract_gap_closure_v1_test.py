from ontology.capability_invocation_request_builder import *
from validation.p162a_capability_invocation_contract_v1_test import kw

def test_requester_executor_distinct():
    k=kw(); k["requester"]=k["executor_id"]; r=build_invocation_request(**k)
    assert r["status"]=="MISSING_BINDING" and r["reason"]=="REQUESTER_EXECUTOR_NOT_DISTINCT"

def test_implementation_explicit_bound_and_identity_relevant():
    a=build_invocation_request(**kw())
    assert a["request"]["capability_implementation_id"]=="impl.echo.v1"
    assert a["binding_manifest"]["capability"]["implementation_id"]=="impl.echo.v1"
    k=kw(); k["capability_implementation_id"]="impl.echo.v2"; b=build_invocation_request(**k)
    assert b["status"]=="REQUESTED"
    assert b["request"]["invocation_request_id"]!=a["request"]["invocation_request_id"]
    assert b["request"]["invocation_request_hash"]!=a["request"]["invocation_request_hash"]

def test_implementation_unknown_rejected():
    for v in (None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE"):
        k=kw(); k["capability_implementation_id"]=v
        assert build_invocation_request(**k)["status"]=="MISSING_BINDING"

def test_material_defaults_resolution_required_and_bound():
    for v in (None,False):
        k=kw(); k["material_defaults_resolved"]=v; r=build_invocation_request(**k)
        assert r["status"]=="MISSING_BINDING" and r["reason"]=="MATERIAL_DEFAULTS_NOT_RESOLVED"
    r=build_invocation_request(**kw())
    assert r["request"]["material_defaults_resolved"] is True

def test_gap_closure_preserves_non_authority_non_execution():
    r=build_invocation_request(**kw())
    assert r["authorization_verified"] is False
    assert r["capability_registry_verified"] is False
    assert r["capability_accessed"] is False
    assert r["execution_performed"] is False
    assert r["functional_only"] is True and r["phenomenology_undetermined"] is True
