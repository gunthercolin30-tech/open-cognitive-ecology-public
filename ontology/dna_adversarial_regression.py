from __future__ import annotations
from copy import deepcopy
from typing import Any

PRIMITIVE="dna_adversarial_regression"
DESCRIPTION="P024 thin DNA-specific adversarial/regression orchestration contract."
DEPENDENCIES=["dna_fitness_suite"]
P024_VERSION="P024-v1"
P024_SCHEMA_VERSION="oce.p024.dna_adversarial_regression.v1"
P024_SCOPE="P024_ONLY"

PASS="PASS"; FAIL="FAIL"; UNDETERMINED="UNDETERMINED"
AUTHORIZED="AUTHORIZED"; UNAUTHORIZED="UNAUTHORIZED"
AUTHORIZATION_STATES=(AUTHORIZED,UNAUTHORIZED,UNDETERMINED)
BLOCK_REQUIRED="BLOCK_REQUIRED"; BLOCK_NOT_REQUIRED="BLOCK_NOT_REQUIRED"; BLOCK_UNDETERMINED="BLOCK_UNDETERMINED"

P024_BOUNDARIES={
"orchestration_only":True,
"does_not_create_new_norms":True,
"does_not_grant_authority":True,
"does_not_execute_mutation":True,
"does_not_execute_rollback":True,
"unauthorized_drift_requires_block":True,
"undetermined_authorization_is_not_authorized":True,
"tested_attacks_do_not_prove_absolute_security":True,
"preserves_p023_fitness_semantics":True,
"functional_conclusion_only":True,
"phenomenology_undetermined":True,
}
P024_TRANSVERSAL_REFERENTIALS={
"doctrines":("R0","R5","R21"),
"artifacts":("A-CANON","A-COHERENCE","A-DNA-ADV","A-NONLOSS"),
"world_models_dependency":None,
}
REUSE_ARTICULATIONS={
"rollback":"acee_rollback_engine",
"constitutional_gate":"constitutional_evolution_gate",
"self_modification":"constitutional_self_modification_protocol",
"evolution_orchestration":"controlled_evolution_orchestrator",
"external_amendment_gate":"external_governance_amendment_gate",
"sandbox":"evolution_sandbox",
"impact_before_after":"acee_impact_evaluator",
}

def _nonempty(v,name):
    if not isinstance(v,str) or not v.strip(): raise ValueError("invalid_"+name)

def canonical_snapshot(state:dict[str,Any])->tuple:
    if not isinstance(state,dict): raise ValueError("state_must_be_dict")
    # Recursive canonicalization without mutating input.
    def freeze(v):
        if isinstance(v,dict): return tuple((k,freeze(v[k])) for k in sorted(v))
        if isinstance(v,(list,tuple)): return tuple(freeze(x) for x in v)
        if isinstance(v,(str,int,float,bool,type(None))): return v
        raise ValueError("unsupported_state_value")
    return freeze(state)

def compare_dna(before:dict[str,Any],after:dict[str,Any])->dict[str,Any]:
    b=canonical_snapshot(before); a=canonical_snapshot(after)
    return {"changed":b!=a,"before":b,"after":a}

def assess(*,before:dict[str,Any],after:dict[str,Any],fitness_status:str,
           authorization_status:str,provenance:str,attack_class:str)->dict[str,Any]:
    _nonempty(provenance,"provenance"); _nonempty(attack_class,"attack_class")
    if fitness_status not in (PASS,FAIL,UNDETERMINED): raise ValueError("invalid_fitness_status")
    if authorization_status not in AUTHORIZATION_STATES: raise ValueError("invalid_authorization_status")
    delta=compare_dna(before,after)
    changed=delta["changed"]
    regression = changed and fitness_status==FAIL
    unresolved = changed and (fitness_status==UNDETERMINED or authorization_status==UNDETERMINED)
    unauthorized = changed and authorization_status==UNAUTHORIZED

    if unauthorized or regression:
        decision=BLOCK_REQUIRED
    elif unresolved:
        decision=BLOCK_UNDETERMINED
    else:
        decision=BLOCK_NOT_REQUIRED

    # "PASS" here means only that this assessed case yields no demonstrated
    # unauthorized/regressive drift. It is not a global security proof.
    if decision==BLOCK_REQUIRED:
        status=FAIL
    elif decision==BLOCK_UNDETERMINED:
        status=UNDETERMINED
    else:
        status=PASS

    return {
      "status":status,"block_decision":decision,"changed":changed,
      "regression_detected":regression,"authorization_status":authorization_status,
      "fitness_status":fitness_status,"attack_class":attack_class,
      "provenance":provenance,"delta":delta,
      "rollback_required":bool(decision==BLOCK_REQUIRED and changed),
    }

def validate_assessment(r):
    fields=("status","block_decision","changed","regression_detected","authorization_status",
            "fitness_status","attack_class","provenance","delta","rollback_required")
    if not isinstance(r,dict) or set(r)!=set(fields): raise ValueError("assessment_fields_mismatch")
    if r["status"] not in (PASS,FAIL,UNDETERMINED): raise ValueError("invalid_status")
    if r["block_decision"] not in (BLOCK_REQUIRED,BLOCK_NOT_REQUIRED,BLOCK_UNDETERMINED): raise ValueError("invalid_block_decision")
    if r["authorization_status"] not in AUTHORIZATION_STATES: raise ValueError("invalid_authorization_status")
    if r["fitness_status"] not in (PASS,FAIL,UNDETERMINED): raise ValueError("invalid_fitness_status")
    _nonempty(r["attack_class"],"attack_class"); _nonempty(r["provenance"],"provenance")
    if not isinstance(r["changed"],bool) or not isinstance(r["regression_detected"],bool) or not isinstance(r["rollback_required"],bool):
        raise ValueError("invalid_boolean_field")
    if r["authorization_status"]==UNAUTHORIZED and r["changed"] and r["block_decision"]!=BLOCK_REQUIRED:
        raise ValueError("unauthorized_drift_not_blocked")
    if r["regression_detected"] and r["block_decision"]!=BLOCK_REQUIRED:
        raise ValueError("regression_not_blocked")
    if r["authorization_status"]==UNDETERMINED and r["changed"] and r["block_decision"]==BLOCK_NOT_REQUIRED:
        raise ValueError("undetermined_promoted_to_authorized")
    return True

def adversarial_manifest():
    return deepcopy({"primitive":PRIMITIVE,"dependencies":tuple(DEPENDENCIES),"version":P024_VERSION,
      "schema_version":P024_SCHEMA_VERSION,"scope":P024_SCOPE,"boundaries":P024_BOUNDARIES,
      "transversal_referentials":P024_TRANSVERSAL_REFERENTIALS,"reuse_articulations":REUSE_ARTICULATIONS})

def validate_adversarial_regression():
    assert DEPENDENCIES==["dna_fitness_suite"]
    assert P024_BOUNDARIES["does_not_grant_authority"] is True
    assert P024_BOUNDARIES["unauthorized_drift_requires_block"] is True
    assert P024_BOUNDARIES["undetermined_authorization_is_not_authorized"] is True
    assert P024_TRANSVERSAL_REFERENTIALS["world_models_dependency"] is None
    return True
