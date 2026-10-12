import json
from pathlib import Path
from ontology.scope_intersection_engine import make_tuple,derive_effective_envelope,effective_effect_scope,attenuate_credential,intersect_temporal_windows
from ontology.target_scope_resolver import resolve_target_scope
ROOT=Path(__file__).resolve().parents[1]
STATUSES={"EFFECTIVE_SCOPE_CONSTRUCTED","EFFECTIVE_SCOPE_REDUCED","EFFECTIVE_SCOPE_EMPTY","EFFECTIVE_SCOPE_UNDETERMINED","EFFECTIVE_SCOPE_CONFLICTING","RESOURCE_SCOPE_INSUFFICIENT","CAPABILITY_SCOPE_INSUFFICIENT","TARGET_SCOPE_INSUFFICIENT","DEPENDENCY_SCOPE_INSUFFICIENT","COMPOSITION_SCOPE_CONFLICT","TECHNICAL_CONTAINMENT_INSUFFICIENT","CREDENTIAL_ATTENUATION_UNAVAILABLE","REAUTHORIZATION_REQUIRED","REPLAN_REQUIRED"}
ARTIFACTS=["effective_execution_scope.schema.json","execution_constraint_tuple.schema.json","cross_dimension_constraint_set.schema.json","resolved_target_scope.schema.json","effective_resource_scope.schema.json","resource_requirement.schema.json","effective_effect_scope.schema.json","enforceability_profile.schema.json","scope_derivation_proof.schema.json","scope_intersection_engine.py","target_scope_resolver.py"]
FLAGS=("authorization_created","reservation_created","credential_reserved","resource_reserved","token_consumed","execution_lease_created","capability_accessed","execution_performed","p162f_opened")
def t(op,target): return make_tuple("exec","cap",op,target,"purpose","prod",resource_constraints={"units":{"max":1}},effect_constraints={op.lower():{"max":1}})
def kw(a,c,i,r,p):
 tr=resolve_target_scope("X",["X"],["X"],[{"kind":"direct"}])
 return dict(envelope_id="zg",authorization_relation=a,capability_relation=c,invocation_relation=i,runtime_relation=r,preconditions_relation=p,receipts={},source_scope_hashes=["0"*64,"1"*64,"2"*64,"3"*64,"4"*64],target_resolution=tr,resources=[],effect_scope=effective_effect_scope(["read"],["read"],["read"]),enforceability_profiles=[],credential_scope=attenuate_credential(["read"],["read"],["read"],True),dependency_composition_envelope={"status":"EFFECTIVE_SCOPE_CONSTRUCTED","authorization_inherited":False},temporal_bounds=intersect_temporal_windows([{"start":1,"end":10},{"start":2,"end":9}]),precondition_recheck_plan={"stage":"RECHECK_AT_RESERVATION"},postconditions_rollback={"required":True},budget_reservation_requirements={"atomic_components":["authorization_use","resource_budget","concurrency","target_dependency_locks"]},state_versions={"token":1})
def test_strict_integrated_reduction_closure_criterion():
 a,b=t("READ","X"),t("WRITE","Y"); k=kw([a,b],[a,b],[a],[a,b],[a,b]); e,p=derive_effective_envelope(**k)
 assert e["overall_status"]=="EFFECTIVE_SCOPE_REDUCED" and e["constraint_tuples"]==[a]
 assert len(e["constraint_tuples"])<len(k["authorization_relation"]) and p["excluded_elements"] and p["reduction_reasons"]
 assert all(e[f] is False for f in FLAGS)
def test_effective_scope_subset_authorized():
 a,b=t("READ","X"),t("WRITE","Y"); k=kw([a],[a,b],[a,b],[a,b],[a,b]); e,_=derive_effective_envelope(**k)
 assert {x["tuple_hash"] for x in e["constraint_tuples"]}<={x["tuple_hash"] for x in k["authorization_relation"]}
def test_all_canonical_statuses_representable():
 s=json.loads((ROOT/"ontology/effective_execution_scope.schema.json").read_text()); assert set(s["properties"]["overall_status"]["enum"])==STATUSES
def test_all_11_artifacts_exist_and_registered():
 inv=(ROOT/"ontology_inventory.txt").read_text()
 for n in ARTIFACTS:
  assert (ROOT/"ontology"/n).is_file()
  assert n in inv or ("ontology."+n[:-3]) in inv
def test_noncausal_boundary_schema_enforced():
 s=json.loads((ROOT/"ontology/effective_execution_scope.schema.json").read_text())
 for f in FLAGS: assert f in s["required"] and s["properties"][f]["const"] is False
def test_catalog_counts():
 assert len(STATUSES)==14 and len(ARTIFACTS)==11 and len(FLAGS)==9
