from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from ontology import minimal_dna, dna_stack, dna_registry, dna_rule_contract
from ontology import dna_severity_model, dna_inheritance, dna_mutation_protocol
from ontology import dna_versioning_lineage, dna_fitness_suite, dna_adversarial_regression

PRIMITIVE="dna_fundamental"
DESCRIPTION="P088 thin provider-independent DNA Fundamental normative boundary; composes P015-P024 without defining P089/P090 or granting runtime authority."
DEPENDENCIES=["minimal_architectural_dna","dna_stack","dna_registry","dna_rule_contract","dna_severity_model","dna_inheritance","dna_mutation_protocol","dna_versioning_lineage","dna_fitness_suite","dna_adversarial_regression"]
P088_VERSION="P088-v1"
P088_SCHEMA_VERSION="oce.p088.dna_fundamental.v1"
P088_SCOPE="P088_ONLY"
PASS="PASS"; FAIL="FAIL"; CONFLICT="CONFLICT"; UNDETERMINED="UNDETERMINED"

NORMATIVE_ORDER=("GENESIS",("DNA-H","DNA-L0"),"DNA-L1","CCAD","CONSTITUTION","GOVERNANCE","POLICY_PROCEDURE")
FUNDAMENTAL_RELATION_DIMENSIONS=("human_dignity","human_normative_primacy","human_integrity","human_autonomy","human_freedoms","non_coercion","reserved_authority","privacy","equity","plurality","non_usurpation","contestability","recourse","traceability","proportionality","reversibility")
DISTINCT_ACTS=("RECOMMENDATION","DECISION","AUTHORIZATION","EXECUTION")
NON_AUTHORITY_SOURCES=("intelligence","performance","wealth","reputation","majority")

P088_BOUNDARIES={
"thin_composition_and_normative_boundary_only":True,
"provider_independent":True,"model_independent":True,"technology_independent":True,
"trans_jurisdictional_core_intent":True,
"does_not_encode_contextual_law_policy":True,
"contextual_rules_belong_to_governance_contextual":True,
"does_not_define_p089_values":True,"does_not_define_p090_meta_rules":True,
"does_not_implement_p061_p086":True,"p061_p086_are_downstream_integration_interfaces":True,
"does_not_replace_decision_ledger":True,"does_not_replace_governance_engines":True,
"does_not_replace_conflict_engines":True,"does_not_replace_action_execution":True,
"does_not_grant_runtime_authority":True,
"human_primacy_is_not_blind_obedience":True,
"superior_intelligence_is_not_superior_authority":True,
"optimization_never_bypasses_higher_constraints":True,
"unknown_authority_is_not_authorized":True,
"functional_conclusion_only":True,"phenomenology_undetermined":True}

TRANSVERSAL_REFERENTIALS={"doctrines":("R0","R5","R21"),"artifacts":("A-CANON","A-COHERENCE","A-DNA-ADV","A-NONLOSS","A-TRACE"),"world_models_dependency":None}
REUSE_ARTICULATIONS={
"external_influence_ledger":"canonical_external_influence_ledger",
"decision_record_extension":"external_decision_record_extension",
"decision_engine":"autonomous_decision_engine",
"action_proposal_queue":"external_action_proposal_queue",
"action_authorization":"action_safety_governor",
"governance_review":"governance_review",
"governance_amendment_gate":"external_governance_amendment_gate",
"distributed_governance":"distributed_governance_layer",
"civilizational_meta_governance":"civilizational_meta_governance",
"conflict_detection":"conflict_detector",
"internal_conflict_monitoring":"internal_conflict_monitoring",
"governed_execution_bridge":"governed_predictive_action_execution_bridge"}

def _rank_map()->Dict[str,int]:
    out={}
    for i,item in enumerate(NORMATIVE_ORDER):
        if isinstance(item,tuple):
            for layer in item: out[layer]=i
        else: out[item]=i
    return out

def evaluate_normative_relation(lower_layer:str,higher_layer:str,relation:str)->Dict[str,Any]:
    ranks=_rank_map()
    if lower_layer not in ranks or higher_layer not in ranks:
        return {"status":UNDETERMINED,"authorized":False,"required_response":"ABSTAIN","reason":"unknown_normative_layer"}
    rel=str(relation).strip().lower()
    if rel not in {"specify","strengthen","contradict","equal"}:
        return {"status":UNDETERMINED,"authorized":False,"required_response":"ABSTAIN","reason":"unknown_relation"}
    if rel=="contradict":
        return {"status":CONFLICT,"authorized":False,"required_response":"ESCALATE","reason":"normative_contradiction"}
    if ranks[lower_layer]>=ranks[higher_layer]:
        return {"status":PASS,"authorized":False,"required_response":"NONE","reason":"compatible_normative_relation"}
    return {"status":CONFLICT,"authorized":False,"required_response":"AUTHORIZED_REVIEW","reason":"reverse_normative_dependency"}

def evaluate_authority_claim(source:str,*,explicit_authority_ref:Optional[str])->Dict[str,Any]:
    if str(source).strip().lower() in NON_AUTHORITY_SOURCES:
        return {"status":FAIL,"authority_granted":False,"reason":"non_authority_property_cannot_create_constitutional_authority"}
    if explicit_authority_ref is None or not str(explicit_authority_ref).strip():
        return {"status":UNDETERMINED,"authority_granted":False,"reason":"missing_explicit_authority_reference"}
    if str(explicit_authority_ref).strip().upper()=="UNKNOWN":
        return {"status":UNDETERMINED,"authority_granted":False,"reason":"unknown_authority_is_not_authorized"}
    return {"status":PASS,"authority_granted":True,"reason":"explicit_authority_reference_present"}

def validate_act_chain(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        return {"status":FAIL,"execution_authorized":False,"errors":("record_not_mapping",)}
    fields=("recommendation_ref","decision_ref","authorization_ref","execution_ref")
    missing=tuple(f for f in fields if f not in record)
    if missing:
        return {"status":FAIL,"execution_authorized":False,"errors":("missing_fields:"+",".join(missing),)}
    values={f:record.get(f) for f in fields}
    for field,value in values.items():
        if value is not None and not isinstance(value,str):
            return {"status":FAIL,"execution_authorized":False,"errors":("invalid_"+field,)}
    auth=values["authorization_ref"]; execution=values["execution_ref"]
    if execution and not auth:
        return {"status":FAIL,"execution_authorized":False,"errors":("execution_without_authorization",)}
    if auth and auth.strip().upper()=="UNKNOWN":
        return {"status":UNDETERMINED,"execution_authorized":False,"errors":("authorization_undetermined",)}
    nonempty=[v.strip() for v in values.values() if isinstance(v,str) and v.strip()]
    if len(nonempty)!=len(set(nonempty)):
        return {"status":FAIL,"execution_authorized":False,"errors":("acts_must_have_distinct_evidence_references",)}
    return {"status":PASS,"execution_authorized":bool(execution and auth),"errors":()}

def fundamental_manifest()->Dict[str,Any]:
    return {"primitive":PRIMITIVE,"description":DESCRIPTION,"dependencies":tuple(DEPENDENCIES),
    "version":P088_VERSION,"schema_version":P088_SCHEMA_VERSION,"scope":P088_SCOPE,
    "normative_order":deepcopy(NORMATIVE_ORDER),"fundamental_relation_dimensions":FUNDAMENTAL_RELATION_DIMENSIONS,
    "distinct_acts":DISTINCT_ACTS,"non_authority_sources":NON_AUTHORITY_SOURCES,
    "boundaries":deepcopy(P088_BOUNDARIES),"transversal_referentials":deepcopy(TRANSVERSAL_REFERENTIALS),
    "reuse_articulations":deepcopy(REUSE_ARTICULATIONS),"p015_p024_reused_without_mutation":True,
    "p015_definition_version":minimal_dna.OCE_DNA_DEFINITION_VERSION,"p016_version":dna_stack.P016_VERSION,
    "p017_version":dna_registry.P017_VERSION,"p018_version":dna_rule_contract.P018_VERSION,
    "p019_version":dna_severity_model.P019_VERSION,"p020_version":dna_inheritance.P020_VERSION,
    "p021_version":dna_mutation_protocol.P021_VERSION,"p022_version":dna_versioning_lineage.P022_VERSION,
    "p023_version":dna_fitness_suite.P023_VERSION,"p024_version":dna_adversarial_regression.P024_VERSION,
    "functional_conclusion_only":True,"phenomenology_undetermined":True}
