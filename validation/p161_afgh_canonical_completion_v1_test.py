from ontology.p161_authorization_request import validate_canonical_request_constraints
from ontology.p161_authorization_scope_construction import intersect_constraint_tuples,validate_active_authorization_composition
from ontology.p161_authorization_token_binding import canonical_signed_authorization_constraints,authorization_event
from ontology.p161_authorization_token_lifecycle import token_tombstone,validate_lifecycle_temporal_context,propagate_dependency_revocation
from ontology.p161_authorization_token_persistence import classify_consumption_recovery
def test_a():
    assert validate_canonical_request_constraints({"environment":"prod","related_requests":[],"break_glass":False,"max_uses":2,"max_resource":10,"max_targets":1,"max_duration":60,"max_concurrent_uses":1})["status"]=="SATISFIED"
    assert validate_canonical_request_constraints({"environment":"prod","related_requests":[],"break_glass":False,"max_uses":-1})["status"]=="UNSATISFIED"
def test_f_tuple():
    assert intersect_constraint_tuples([{"target":"A","mode":"R"},{"target":"B","mode":"W"}],[{"target":"A","mode":"R"},{"target":"B","mode":"R"}])==[{"mode":"R","target":"A"}]
def test_f_composition():
    c={"environment":"prod","target":"A","budget":{"max_uses":1},"reservation":"R","constraint_tuples":[{"target":"A","mode":"R"}]}
    assert validate_active_authorization_composition(c,[dict(c)])["status"]=="UNSATISFIED"
def test_g():
    x=canonical_signed_authorization_constraints({"environment":"prod","budget":{"max_uses":2},"max_uses":2})
    assert x["max_uses"]==2
    assert authorization_event("T","H","S","ISS",{"ISS":{"environments":["prod"]}},"prod")["status"]=="COMMITTED"
def test_h():
    assert token_tombstone("T","H","REVOKED","X","now")["resurrectable"] is False
    assert validate_lifecycle_temporal_context(clock_rollback=True)["status"]=="UNKNOWN"
    assert propagate_dependency_revocation({"state":"CURRENT"},dependency_revoked=True)["state"]=="REVOKED"
    assert classify_consumption_recovery(commit_known=False,effect_known=False)["retry_allowed"] is False
