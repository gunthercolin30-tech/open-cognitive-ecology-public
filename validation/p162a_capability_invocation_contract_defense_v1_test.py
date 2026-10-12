from copy import deepcopy
from ontology.capability_invocation_request_builder import *
from validation.p162a_capability_invocation_contract_v1_test import kw
def test_root_a1_identity_substitution():
 r=build_invocation_request(**kw())["request"];x=deepcopy(r);x["executor_id"]="SUB";assert assert_requested_immutable(r,x)["status"]=="FAIL"
def test_root_a2_dependency_no_authority():
 k=kw();k["requested_resources"]={"network":True,"cpu":999};r=build_invocation_request(**k);assert not r["authorization_verified"] and not r["execution_performed"]
def test_root_a3_functional_equivalence_no_authorization_equivalence():
 r=build_invocation_request(**kw());assert not r["binding_manifest"]["capability"]["functional_equivalence_is_authorization_equivalence"]
def test_root_a4_pure_claim_no_effector_bypass():
 k=kw();k["effect_class_claim"]="PURE";r=build_invocation_request(**k);assert not r["effect_binding"]["pure_claim_is_gate_bypass"] and r["effect_binding"]["registry_verification_deferred_to"]=="P162-B"
def test_no_execution_libraries_in_builder():
 import inspect,ontology.capability_invocation_request_builder as m
 s=inspect.getsource(m);assert "subprocess" not in s and "requests." not in s and "os.system" not in s
