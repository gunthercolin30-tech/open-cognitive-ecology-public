from ontology.scope_intersection_engine import *
def test_e10_quantitative_limits_remain_target_effect_bound():
 read_x=make_tuple("exec","cap","READ","X","p","prod",resource_constraints={"bytes":{"max":10}},effect_constraints={"read_bytes":{"max":10}})
 write_y=make_tuple("exec","cap","WRITE","Y","p","prod",resource_constraints={"bytes":{"max":2}},effect_constraints={"write_bytes":{"max":2}})
 out=relational_intersection([read_x,write_y],[read_x,write_y],[read_x,write_y],[read_x,write_y],[read_x,write_y])
 proof=quantitative_binding_proof(out)
 by={(b["target"],b["operation"]):b for b in proof["bindings"]}
 assert by[("X","READ")]["resource_constraints"]["bytes"]["max"]==10
 assert by[("X","READ")]["effect_constraints"]["read_bytes"]["max"]==10
 assert by[("Y","WRITE")]["resource_constraints"]["bytes"]["max"]==2
 assert by[("Y","WRITE")]["effect_constraints"]["write_bytes"]["max"]==2
 assert ("X","WRITE") not in by and ("Y","READ") not in by
def test_e10_narrowing_preserves_quantitative_binding():
 read_x=make_tuple("exec","cap","READ","X","p","prod",resource_constraints={"bytes":{"max":10}},effect_constraints={"read_bytes":{"max":10}})
 write_y=make_tuple("exec","cap","WRITE","Y","p","prod",resource_constraints={"bytes":{"max":2}},effect_constraints={"write_bytes":{"max":2}})
 out=relational_intersection([read_x,write_y],[read_x,write_y],[read_x],[read_x,write_y],[read_x,write_y])
 proof=quantitative_binding_proof(out)
 assert len(proof["bindings"])==1
 b=proof["bindings"][0]
 assert (b["target"],b["operation"])==("X","READ")
 assert b["resource_constraints"]=={"bytes":{"max":10}}
 assert b["effect_constraints"]=={"read_bytes":{"max":10}}
def test_e10_envelope_persists_tuple_bound_constraints():
 t=make_tuple("exec","cap","READ","X","p","prod",resource_constraints={"bytes":{"max":7}},effect_constraints={"read_bytes":{"max":7}})
 tr={"resolved_targets":["X"],"status":"RESOLVED_WITHIN_SCOPE","escape_detected":False}
 kw=dict(envelope_id="e10",authorization_relation=[t],capability_relation=[t],invocation_relation=[t],runtime_relation=[t],preconditions_relation=[t],receipts={},source_scope_hashes=["0"*64],target_resolution=tr,resources=[],effect_scope=effective_effect_scope(["read"],["read"],["read"]),enforceability_profiles=[],credential_scope={},dependency_composition_envelope={},temporal_bounds={},precondition_recheck_plan={},postconditions_rollback={},budget_reservation_requirements={},state_versions={})
 env,proof=derive_effective_envelope(**kw)
 assert env["constraint_tuples"]==[t]
 q=quantitative_binding_proof(env["constraint_tuples"])
 assert q["bindings"][0]["target"]=="X"
 assert q["bindings"][0]["operation"]=="READ"
 assert q["bindings"][0]["resource_constraints"]["bytes"]["max"]==7
 assert q["bindings"][0]["effect_constraints"]["read_bytes"]["max"]==7
 assert proof["constraint_tuples"]==env["constraint_tuples"]
def test_e10_deterministic_binding_proof():
 t=make_tuple("exec","cap","READ","X","p","prod",resource_constraints={"n":{"max":3}},effect_constraints={"e":{"max":3}})
 assert quantitative_binding_proof([t])==quantitative_binding_proof([t])
