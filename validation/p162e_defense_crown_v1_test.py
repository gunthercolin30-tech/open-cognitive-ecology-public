from ontology.scope_intersection_engine import *
from ontology.target_scope_resolver import resolve_alias_chain
def t(op,target,p="p",env="prod",cap="cap"):return make_tuple("exec",cap,op,target,p,env)
def test_e01():
 a,b=t("READ","X"),t("WRITE","Y");assert relational_intersection([a,b],[a,b],[a],[a,b],[a,b])==[a]
def test_e02():
 a,x=t("READ","X",cap="c1"),t("READ","X",cap="c2");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_e03():
 a,x=t("READ","X","p1"),t("READ","X","p2");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_e04():
 a,x=t("READ","X",env="sandbox"),t("READ","X",env="prod");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_e05():
 a,x=t("READ","X"),t("DELETE","X");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_e06():
 assert effective_resource_requirement("r","UP_TO",1,50,3,100)["effective_max"]==3
def test_e07():
 a,b=t("READ","X"),t("WRITE","Y");assert relational_intersection([a,b],[a,b],[a],[a,b],[a,b])==[a]
def test_e08():
 assert resolve_alias_chain("link",["outside"],["inside"])["status"]=="TARGET_SCOPE_INSUFFICIENT"
def test_e09():
 assert resolve_alias_chain("url",["redirected"],["authorized"])["escape_detected"]
def test_e10():
 a,x=t("READ","X",cap="c1"),t("READ","X",cap="c2");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_e11():
 assert dependency_scope([],t("WRITE","D"))["status"]=="DEPENDENCY_SCOPE_INSUFFICIENT"
def test_e12():
 assert effective_resource_requirement("gpu","AT_LEAST",8,8,4,100)["status"]=="RESOURCE_SCOPE_INSUFFICIENT"
def test_e13():
 assert semantic_narrow(9,"EXACT",10)["status"]=="EFFECTIVE_SCOPE_CONFLICTING"
def test_e14():
 assert effective_resource_requirement("cost","UP_TO",1,100,10,100)["effective_max"]==10
def test_e15():
 r=attenuate_credential(["read","admin"],["read"],["read"]);assert r["effective_permissions"]==["read"] and not r["credential_acquired"]
def test_e16():
 e=effective_effect_scope(["read"],["read","delete"],["read"]);assert e["hidden_effects"]==["delete"]
def test_e17():
 assert enforceability("x","none","CRITICAL",False,False,"BLOCK")["status"]=="UNENFORCEABLE"
def test_e18():
 r=intersect_temporal_windows([{"start":1,"end":4},{"start":3,"end":6}]);assert (r["start"],r["end"])==(3,4)
def test_e19():
 r=composition_budget_scope(10,8,10,4,1);assert r["effective_max"]==5 and r["status"]=="COMPOSITION_SCOPE_CONFLICT"
def test_e20():
 assert validate_atomicity_requirements({"atomic_components":["authorization_use"]})["status"]=="TECHNICAL_CONTAINMENT_INSUFFICIENT"
def test_root_e1():
 a,b=t("READ","X"),t("WRITE","Y");assert len(relational_intersection([a,b],[a,b],[a],[a,b],[a,b]))==1
def test_root_e2():
 a,x=t("READ","X"),t("DELETE","X");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_root_e3():
 assert resolve_alias_chain("a",["X","OUT"],["X"])["escape_detected"]
def test_root_e4():
 assert effective_resource_requirement("r","UP_TO",1,99,2,99)["effective_max"]==2
def test_root_e5():
 assert enforceability("c","none","CRITICAL",False,False,"FAIL_CLOSED")["status"]!="ENFORCEABLE"
def test_root_e6():
 assert dependency_scope([],t("WRITE","D"))["authorization_inherited"] is False
def test_root_e7():
 assert composition_budget_scope(5,5,5,3,2)["effective_max"]==0
def test_root_e8():
 a,x=t("READ","X"),t("WRITE","X");assert x not in relational_intersection([a],[a,x],[a,x],[a,x],[a,x])
def test_credential_unavailable():
 assert attenuate_credential(["read","admin"],["read"],["read"],False)["status"]=="CREDENTIAL_ATTENUATION_UNAVAILABLE"
def test_temporal_disjoint():
 assert intersect_temporal_windows([{"start":1,"end":2},{"start":3,"end":4}])["status"]=="EFFECTIVE_SCOPE_EMPTY"
def test_temporal_unknown():
 assert intersect_temporal_windows([{"start":None,"end":2}])["status"]=="EFFECTIVE_SCOPE_UNDETERMINED"
def test_alias_hop_limit():
 assert resolve_alias_chain("a",list(map(str,range(20))),["19"],3)["status"]=="EFFECTIVE_SCOPE_UNDETERMINED"
def test_distinct_dependency_auth():
 d=t("WRITE","D");assert dependency_scope([],d,[tuple_key(d)])["status"]=="EFFECTIVE_SCOPE_CONSTRUCTED"
def test_atomicity_complete_nonreservation():
 r=validate_atomicity_requirements({"atomic_components":["authorization_use","resource_budget","concurrency","target_dependency_locks"]});assert r["status"]=="EFFECTIVE_SCOPE_CONSTRUCTED" and not r["reservation_created"]

def test_e09_authorized_nominal_redirects_outside_must_fail():
 # The nominal URL is authorized, but its resolved redirect target is not.
 r=resolve_alias_chain("authorized",["outside"],["authorized"])
 assert r["status"]=="TARGET_SCOPE_INSUFFICIENT"
 assert r["escape_detected"] is True
 assert r["resolved_targets"]==["outside"]

def test_e15_required_permission_outside_authorized_scope_must_fail():
 # Technical credential has both permissions, but normative authorization has only read.
 r=attenuate_credential(["read","admin"],["admin"],["read"],True)
 assert r["status"]=="CREDENTIAL_ATTENUATION_UNAVAILABLE"
 assert r["effective_permissions"]==[]
 assert r["credential_acquired"] is False
