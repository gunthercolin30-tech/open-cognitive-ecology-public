from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
from ontology import constitution_registry, constitution_operational, dna_fundamental, normative_hierarchy

PRIMITIVE="operational_constitutional_invariants"
VERSION="P093-v1"
SCHEMA_VERSION="oce.p093.operational_constitutional_invariants.v1"
SCOPE="P093_ONLY"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
EXECUTION_DEPENDENCIES=("P092_CONSTITUTION_REGISTRY","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENTIALS={"doctrines":("R20","R21"),"artifacts":("A-CANON",),"canonical_non_loss":("4B","4C","4D","4E"),"world_models_dependency":None}
CORE_INVARIANTS=("authority","identity","permissions","action_separation","recourse","provenance","resources","evolution")
CIVILIZATIONAL_INVARIANTS=("non_self_sovereignty","concentration_control","human_exit_capacity","viable_human_alternatives","organizational_reversibility","no_self_justifying_growth")
MANDATORY_INVARIANTS=CORE_INVARIANTS+CIVILIZATIONAL_INVARIANTS
REUSE_MAP={
"authority":("constitution_operational","dna_fundamental"),
"identity":("representative_identity_registry","constitution_operational"),
"permissions":("constitution_operational",),
"action_separation":("constitution_operational","dna_fundamental"),
"recourse":("constitution_operational","constitution_registry"),
"provenance":("constitution_operational","constitution_registry"),
"resources":("resource_allocation","autonomous_resource_manager"),
"evolution":("constitutional_evolution_gate","constitutional_self_modification_protocol"),
"non_self_sovereignty":("dna_fundamental","constitution_operational"),
"concentration_control":("constitutional_compliance_check",),
"human_exit_capacity":("human_non_replacement","indispensability_regulation_controller"),
"viable_human_alternatives":("human_non_replacement","future_openness"),
"organizational_reversibility":("trajectory_reversibility","constitution_operational"),
"no_self_justifying_growth":("indispensability_index","indispensability_regulation_controller")}
BOUNDARIES={
"all_invariants_non_optional":True,"unknown_is_not_pass":True,
"ambiguous_authority_does_not_expand_power":True,"superior_intelligence_does_not_create_authority":True,
"performance_or_resource_gain_cannot_bypass_higher_constraints":True,"human_primacy_is_not_blind_obedience":True,
"does_not_implement_p094_act_authorities":True,"does_not_create_p095_human_reserved_authority_registry":True,
"does_not_resolve_p098_normative_conflicts":True,"does_not_implement_p099_non_circumvention":True,
"does_not_persist_p104_decision_ledger":True,"does_not_claim_p155_p166_ccad_runtime_enforcement":True,
"does_not_grant_execution_authority":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def invariant_specification():
    return tuple(deepcopy({"invariant_id":"P093:"+n.upper(),"name":n,"mandatory":True,"status":UNDETERMINED,
      "runtime_enforcement_proven":False,"execution_authority_granted":False,"reuse_candidates":tuple(REUSE_MAP[n]),
      "exception_policy":"NO_IMPLICIT_EXCEPTION","authority":"G2_DNA_FUNDAMENTAL","version":VERSION,
      "provenance":"P093_CANONICAL_PLAN_AND_ANNEX"}) for n in MANDATORY_INVARIANTS)

def find_invariant(name):
    key=str(name or "").strip().lower()
    for row in invariant_specification():
        if row["name"]==key: return deepcopy(row)
    return None

def evaluate_invariant(name,evidence_status=UNDETERMINED):
    spec=find_invariant(name)
    if spec is None:
        return {"status":UNDETERMINED,"invariant_known":False,"satisfied":False,"authorized":False,"required_response":"ABSTAIN"}
    normalized=str(evidence_status or UNDETERMINED).strip().upper()
    status=normalized if normalized in (PASS,FAIL,CONFLICT) else UNDETERMINED
    return {"status":status,"invariant_known":True,"satisfied":status==PASS,"mandatory":True,"authorized":False,
      "required_response":"CONTINUE_REVIEW" if status==PASS else ("ESCALATE" if status==CONFLICT else "ABSTAIN")}

def evaluate_invariant_set(evidence):
    if not isinstance(evidence,Mapping):
        return {"status":FAIL,"all_mandatory_satisfied":False,"authorized":False,"missing":MANDATORY_INVARIANTS}
    results={n:evaluate_invariant(n,evidence.get(n,UNDETERMINED)) for n in MANDATORY_INVARIANTS}
    missing=tuple(n for n,r in results.items() if r["status"]!=PASS)
    if any(r["status"]==CONFLICT for r in results.values()): status=CONFLICT
    elif any(r["status"]==FAIL for r in results.values()): status=FAIL
    elif missing: status=UNDETERMINED
    else: status=PASS
    return {"status":status,"all_mandatory_satisfied":status==PASS,"authorized":False,"missing":missing,
      "results":deepcopy(results),"required_response":"CONTINUE_AUTHORIZED_REVIEW" if status==PASS else ("ESCALATE" if status==CONFLICT else "ABSTAIN")}

def validate_p093_contract():
    p092=constitution_registry.validate_registry()
    p091=constitution_operational.validate_operational_contract()
    p087=normative_hierarchy.validate_hierarchy()
    dna=dna_fundamental.fundamental_manifest()
    specs=invariant_specification(); names=tuple(r["name"] for r in specs)
    unique=len(names)==len(set(names))==len(MANDATORY_INVARIANTS)
    fields_ok=all(r["mandatory"] is True and r["status"]==UNDETERMINED and
      r["runtime_enforcement_proven"] is False and r["execution_authority_granted"] is False and
      r["exception_policy"]=="NO_IMPLICIT_EXCEPTION" and bool(r["reuse_candidates"]) for r in specs)
    deps_ok=p092.get("status")==PASS and p091.get("status")==PASS and p087.get("status")==PASS and dna.get("primitive")=="dna_fundamental"
    valid=bool(unique and fields_ok and deps_ok and all(BOUNDARIES.values()))
    return {"status":PASS if valid else FAIL,"valid":valid,"primitive":PRIMITIVE,"version":VERSION,"scope":SCOPE,
      "invariant_count":len(specs),"core_count":len(CORE_INVARIANTS),"civilizational_count":len(CIVILIZATIONAL_INVARIANTS),
      "unique_invariants":unique,"dependencies_valid":deps_ok,"unknown_promoted_to_pass":False,
      "runtime_enforcement_proven":False,"execution_authority_proven":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}

def p093_manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,
      "execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_referentials":deepcopy(TRANSVERSAL_REFERENTIALS),
      "core_invariants":CORE_INVARIANTS,"civilizational_invariants":CIVILIZATIONAL_INVARIANTS,
      "boundaries":deepcopy(BOUNDARIES),"invariants":invariant_specification()}
