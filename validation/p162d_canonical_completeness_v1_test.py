import json
from pathlib import Path
import jsonschema
from validation.p162d_runtime_context_preconditions_gate_v1_test import fx
from ontology.runtime_precondition_evaluator import evaluate_runtime_preconditions,predicate_registry
ROOT=Path(__file__).resolve().parents[1]
def schema(n): return json.loads((ROOT/"ontology"/n).read_text())
def test_four_schemas_strict():
 for n in ("runtime_precondition_assessment.schema.json","precondition_result.schema.json","runtime_context_snapshot.schema.json","precondition_predicate_registry.schema.json"): assert schema(n)["additionalProperties"] is False
def test_positive_assessment_schema_and_uncertainty():
 r=evaluate_runtime_preconditions(**fx());a=r["assessment"];jsonschema.validate(a,schema("runtime_precondition_assessment.schema.json"));assert len(a["uncertainty_results"])==len(a["precondition_results"])
def test_result_and_snapshot_schemas():
 x=fx();a=evaluate_runtime_preconditions(**x)["assessment"];jsonschema.validate(a["precondition_results"][0],schema("precondition_result.schema.json"));jsonschema.validate(x["runtime_snapshot"],schema("runtime_context_snapshot.schema.json"))
def test_predicate_registry_schema():
 r=predicate_registry();jsonschema.validate({k:r[k] for k in ("schema","version","predicates")},schema("precondition_predicate_registry.schema.json"));assert len(r["predicates"])==10
def test_explicit_bounded_routing():
 x=fx();x["token_verification_receipt"]["status"]="INVALID";assert evaluate_runtime_preconditions(**x)["required_action"]=="RETURN_TO_P161"
 x=fx();x["world_snapshot"]["evidence_class"]="PREDICTION";assert evaluate_runtime_preconditions(**x)["status"]=="WORLD_STATE_UNDETERMINED"
 x=fx();x["resource_snapshot"]["status"]="INSUFFICIENT";assert evaluate_runtime_preconditions(**x)["status"]=="RESOURCE_STATE_INSUFFICIENT"
 x=fx();x["world_snapshot"]["clock_skew_status"]="UNBOUNDED";assert evaluate_runtime_preconditions(**x)["status"]=="CONTEXT_CONFLICTING"
def test_noncausal():
 r=evaluate_runtime_preconditions(**fx())
 for k in ("authorization_created","reservation_created","token_consumed","capability_accessed","execution_performed","p162e_opened"): assert r[k] is False
