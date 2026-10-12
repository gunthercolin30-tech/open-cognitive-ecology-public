import hashlib,json
from ontology.scope_intersection_engine import *
from ontology.target_scope_resolver import resolve_target_scope
def t(op,target):return make_tuple("exec","cap",op,target,"purpose","prod")
def hh(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def test_cartesian_amplification_blocked():
 a,b=t("READ","X"),t("WRITE","Y"); out=relational_intersection([a,b],[a,b],[a],[a,b],[a,b]); assert [tuple_key(x) for x in out]==[tuple_key(a)]; assert tuple_key(t("READ","Y")) not in {tuple_key(x) for x in out}
def test_technical_power_no_permission():
 a,x=t("READ","X"),t("DELETE","X");assert relational_intersection([a],[a,x],[a],[a],[a])==[a]
def test_request_narrowing():
 a,b=t("READ","X"),t("WRITE","Y");assert relational_intersection([a,b],[a,b],[a],[a,b],[a,b])==[a]
def test_target_escape_vs_unknown():
 e=resolve_target_scope("alias",["outside"],["inside"],["redirect"]);u=resolve_target_scope("alias",[],["inside"],[],True);assert e["status"]=="TARGET_SCOPE_INSUFFICIENT";assert u["status"]=="EFFECTIVE_SCOPE_UNDETERMINED"
def test_availability_no_budget_expansion():
 r=effective_resource_requirement("cpu","UP_TO",1,100,4,1000);assert r["effective_max"]==4
def test_minimum_cannot_expand_right():
 r=effective_resource_requirement("gpu","AT_LEAST",8,8,4,100);assert r["status"]=="RESOURCE_SCOPE_INSUFFICIENT"
def test_hidden_effect_not_permission():
 e=effective_effect_scope(["read"],["read","delete"],["read"]);assert e["effective_effects"]==["read"] and e["hidden_effects"]==["delete"]
def test_bounded_semantics():
 import pytest
 with pytest.raises(ValueError):effective_resource_requirement("cpu","PERMISSIVE",1,1,1,1)
def test_dependency_no_inheritance():
 a,c=t("READ","X"),t("WRITE","dependency");assert c not in relational_intersection([a],[a,c],[a,c],[a,c],[a,c])
def test_envelope_empty_noncausal_deterministic():
 a,b=t("READ","X"),t("WRITE","Y");tr=resolve_target_scope("X",["X"],["X"])
 kw=dict(envelope_id="e",authorization_relation=[a],capability_relation=[a],invocation_relation=[b],runtime_relation=[a],preconditions_relation=[a],receipts={},source_scope_hashes=[hh("a")],target_resolution=tr,resources=[],effect_scope=effective_effect_scope(["read"],["read"],["read"]),enforceability_profiles=[],credential_scope={},dependency_composition_envelope={"inherits_authorization":False},temporal_bounds={},precondition_recheck_plan={},postconditions_rollback={},budget_reservation_requirements={},state_versions={})
 e1,p1=derive_effective_envelope(**kw);e2,p2=derive_effective_envelope(**kw);assert e1==e2 and p1==p2;assert e1["overall_status"]=="EFFECTIVE_SCOPE_EMPTY";assert e1["constraint_tuples"]==[]
 for k in ("authorization_created","reservation_created","token_consumed","capability_accessed","execution_performed"):assert e1[k] is False
def test_critical_unenforceable_blocks():
 a=t("READ","X");tr=resolve_target_scope("X",["X"],["X"]);p=enforceability("c","sandbox","CRITICAL",True,False,"BLOCK")
 kw=dict(envelope_id="e",authorization_relation=[a],capability_relation=[a],invocation_relation=[a],runtime_relation=[a],preconditions_relation=[a],receipts={},source_scope_hashes=[hh("a")],target_resolution=tr,resources=[],effect_scope=effective_effect_scope(["read"],["read"],["read"]),enforceability_profiles=[p],credential_scope={},dependency_composition_envelope={},temporal_bounds={},precondition_recheck_plan={},postconditions_rollback={},budget_reservation_requirements={},state_versions={})
 e,_=derive_effective_envelope(**kw);assert e["overall_status"]=="TECHNICAL_CONTAINMENT_INSUFFICIENT"
