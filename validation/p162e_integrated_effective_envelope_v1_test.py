import json
from pathlib import Path
from ontology.scope_intersection_engine import make_tuple,derive_effective_envelope,effective_effect_scope,attenuate_credential,dependency_scope,composition_budget_scope,intersect_temporal_windows
from ontology.target_scope_resolver import resolve_target_scope

def base():
 t=make_tuple("exec","cap","read","T","purpose","prod")
 tr=resolve_target_scope("T",["T"],["T"],[{"kind":"direct","from":"T","to":"T"}])
 return dict(envelope_id="integrated-e",authorization_relation=[t],capability_relation=[t],invocation_relation=[t],runtime_relation=[t],preconditions_relation=[t],receipts={},source_scope_hashes=["0"*64],target_resolution=tr,resources=[],effect_scope=effective_effect_scope(["read"],["read"],["read"]),enforceability_profiles=[],credential_scope=attenuate_credential(["read"],["read"],["read"],True),dependency_composition_envelope={"status":"EFFECTIVE_SCOPE_CONSTRUCTED","authorization_inherited":False},temporal_bounds=intersect_temporal_windows([{"start":1,"end":9},{"start":2,"end":8}]),precondition_recheck_plan={},postconditions_rollback={},budget_reservation_requirements={"atomic_components":["authorization_use","resource_budget","concurrency","target_dependency_locks"]},state_versions={})

def test_positive_integrated_envelope_is_constructed_and_noncausal():
 e,_=derive_effective_envelope(**base()); assert e["overall_status"]=="EFFECTIVE_SCOPE_CONSTRUCTED"
 for k in ("authorization_created","reservation_created","credential_reserved","resource_reserved","token_consumed","execution_lease_created","capability_accessed","execution_performed","p162f_opened"): assert e[k] is False

def test_effect_empty_blocks_integrated_envelope():
 k=base(); k["effect_scope"]=effective_effect_scope(["read"],["delete"],["read"]); e,_=derive_effective_envelope(**k); assert e["overall_status"]=="EFFECTIVE_SCOPE_EMPTY"

def test_credential_failure_blocks_integrated_envelope():
 k=base(); k["credential_scope"]=attenuate_credential(["read","admin"],["admin"],["read"],True); e,_=derive_effective_envelope(**k); assert e["overall_status"]=="CREDENTIAL_ATTENUATION_UNAVAILABLE"

def test_dependency_failure_blocks_integrated_envelope():
 k=base(); t=k["authorization_relation"][0]; k["dependency_composition_envelope"]=dependency_scope([],t,[]); e,_=derive_effective_envelope(**k); assert e["overall_status"]=="DEPENDENCY_SCOPE_INSUFFICIENT"

def test_composition_conflict_blocks_integrated_envelope():
 k=base(); k["dependency_composition_envelope"]=composition_budget_scope(10,8,10,3,2); e,_=derive_effective_envelope(**k); assert e["overall_status"]=="COMPOSITION_SCOPE_CONFLICT"

def test_empty_temporal_intersection_blocks_integrated_envelope():
 k=base(); k["temporal_bounds"]=intersect_temporal_windows([{"start":1,"end":2},{"start":3,"end":4}]); e,_=derive_effective_envelope(**k); assert e["overall_status"]=="EFFECTIVE_SCOPE_EMPTY"

def test_unknown_from_each_integrated_dimension_fails_closed():
 for field,status in (("effect_scope","EFFECT_SCOPE_UNDETERMINED"),("credential_scope","EFFECTIVE_SCOPE_UNDETERMINED"),("dependency_composition_envelope","EFFECTIVE_SCOPE_UNDETERMINED"),("temporal_bounds","EFFECTIVE_SCOPE_UNDETERMINED")):
  k=base(); k[field]={"status":status}; e,p=derive_effective_envelope(**k); assert e["overall_status"]=="EFFECTIVE_SCOPE_UNDETERMINED"; assert p["unknowns"]

def test_effective_execution_schema_requires_all_noncausal_boundary_flags():
 root=Path(__file__).resolve().parents[1]; s=json.loads((root/"ontology/effective_execution_scope.schema.json").read_text())
 for k in ("authorization_created","reservation_created","credential_reserved","resource_reserved","token_consumed","execution_lease_created","capability_accessed","execution_performed","p162f_opened"): assert s["properties"][k]["const"] is False and k in s["required"]

def test_inventory_registers_all_11_canonical_artifacts():
 root=Path(__file__).resolve().parents[1]; txt=(root/"ontology_inventory.txt").read_text()
 expected=["execution_constraint_tuple.schema.json","cross_dimension_constraint_set.schema.json","resolved_target_scope.schema.json","resource_requirement.schema.json","effective_resource_scope.schema.json","effective_effect_scope.schema.json","enforceability_profile.schema.json","scope_derivation_proof.schema.json","effective_execution_scope.schema.json","ontology.scope_intersection_engine","ontology.target_scope_resolver"]
 assert all(x in txt for x in expected); assert "status=IMPLEMENTED_NOT_FINAL_LOCKED" in txt

def test_integration_is_deterministic():
 k=base(); assert derive_effective_envelope(**k)==derive_effective_envelope(**k)
