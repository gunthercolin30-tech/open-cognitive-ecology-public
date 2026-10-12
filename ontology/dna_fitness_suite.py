from __future__ import annotations
from copy import deepcopy
from typing import Any

PRIMITIVE="dna_fitness_suite"
DESCRIPTION="P023 thin deterministic DNA structural-invariant fitness suite with multi-scale composition."
DEPENDENCIES=["dna_versioning_lineage"]
P023_VERSION="P023-v1"
P023_SCHEMA_VERSION="oce.p023.dna_fitness_suite.v1"
P023_SCOPE="P023_ONLY"

PASS="PASS"; FAIL="FAIL"; UNDETERMINED="UNDETERMINED"
FITNESS_STATUSES=(PASS,FAIL,UNDETERMINED)
SCALES=("CIVILIZATION","INSTITUTION","ROLE","INDIVIDUAL","CRITICAL_COMPONENT")

P023_BOUNDARIES={
"fitness_evaluation_only":True,
"fitness_does_not_create_norms":True,
"fitness_does_not_grant_authority":True,
"local_pass_is_not_global_pass":True,
"undetermined_is_not_pass":True,
"multi_scale_composition_required_for_global_pass":True,
"does_not_replace_structural_conservation":True,
"does_not_replace_structural_continuity":True,
"does_not_replace_multi_scale_coupling":True,
"does_not_replace_hierarchical_integration":True,
"does_not_replace_invariant_propagation_monitor":True,
"does_not_define_p024_adversarial_campaign":True,
"does_not_claim_end_to_end_enforcement":True,
"functional_conclusion_only":True,
"phenomenology_undetermined":True,
}
P023_TRANSVERSAL_REFERENTIALS={
"doctrines":("R0","R10","R11","R15","R17","R20","R21"),
"artifacts":("A-CANON","A-COHERENCE","A-DNA-ADV","A-TRACE"),
"world_models_dependency":None,
}
REUSE_ARTICULATIONS={
"structural_conservation":"structural_conservation",
"structural_continuity":"structural_continuity",
"multi_scale_coupling":"multi_scale_coupling",
"hierarchical_integration":"hierarchical_integration",
"invariant_propagation":"invariant_propagation_monitor",
}

def _s(v,f):
    if not isinstance(v,str) or not v.strip(): raise ValueError("invalid_"+f)
def _status(v):
    if v not in FITNESS_STATUSES: raise ValueError("invalid_fitness_status")
def _exact(r,fields):
    if not isinstance(r,dict): raise ValueError("record_must_be_dict")
    if set(r)!=set(fields): raise ValueError("fitness_record_fields_mismatch")

def evaluate_scale(*,scale:str,required_invariants:tuple[str,...],observed_invariants:dict[str,Any],provenance:str)->dict[str,Any]:
    if scale not in SCALES: raise ValueError("invalid_scale")
    if not isinstance(required_invariants,tuple) or not required_invariants: raise ValueError("required_invariants_must_be_nonempty_tuple")
    if len(set(required_invariants))!=len(required_invariants): raise ValueError("duplicate_required_invariant")
    for x in required_invariants: _s(x,"required_invariant")
    if not isinstance(observed_invariants,dict): raise ValueError("observed_invariants_must_be_dict")
    _s(provenance,"provenance")
    missing=[]; unknown=[]; passed=[]
    for inv in required_invariants:
        if inv not in observed_invariants or observed_invariants[inv] is None or observed_invariants[inv]==UNDETERMINED:
            unknown.append(inv)
        elif observed_invariants[inv] is True or observed_invariants[inv]==PASS:
            passed.append(inv)
        elif observed_invariants[inv] is False or observed_invariants[inv]==FAIL:
            missing.append(inv)
        else:
            raise ValueError("invalid_invariant_observation:"+inv)
    status=FAIL if missing else (UNDETERMINED if unknown else PASS)
    return {"scale":scale,"status":status,"required_invariants":required_invariants,
            "passed_invariants":tuple(passed),"failed_invariants":tuple(missing),
            "undetermined_invariants":tuple(unknown),"provenance":provenance}

def validate_scale_result(r):
    fields=("scale","status","required_invariants","passed_invariants","failed_invariants","undetermined_invariants","provenance")
    _exact(r,fields)
    if r["scale"] not in SCALES: raise ValueError("invalid_scale")
    _status(r["status"]); _s(r["provenance"],"provenance")
    for f in ("required_invariants","passed_invariants","failed_invariants","undetermined_invariants"):
        if not isinstance(r[f],tuple): raise ValueError(f+"_must_be_tuple")
    req=set(r["required_invariants"]); p=set(r["passed_invariants"]); f=set(r["failed_invariants"]); u=set(r["undetermined_invariants"])
    if (p|f|u)!=req or (p&f) or (p&u) or (f&u): raise ValueError("invariant_partition_invalid")
    expected=FAIL if f else (UNDETERMINED if u else PASS)
    if r["status"]!=expected: raise ValueError("scale_status_inconsistent")
    return True

def compose_multiscale(results:tuple[dict[str,Any],...],*,required_scales:tuple[str,...],provenance:str)->dict[str,Any]:
    if not isinstance(results,tuple) or not results: raise ValueError("results_must_be_nonempty_tuple")
    if not isinstance(required_scales,tuple) or not required_scales: raise ValueError("required_scales_must_be_nonempty_tuple")
    if len(set(required_scales))!=len(required_scales): raise ValueError("duplicate_required_scale")
    for s in required_scales:
        if s not in SCALES: raise ValueError("invalid_required_scale")
    _s(provenance,"provenance")
    by={}
    for r in results:
        validate_scale_result(r)
        if r["scale"] in by: raise ValueError("duplicate_scale_result")
        by[r["scale"]]=r
    missing=tuple(s for s in required_scales if s not in by)
    considered=tuple(by[s] for s in required_scales if s in by)
    if missing: status=UNDETERMINED
    elif any(r["status"]==FAIL for r in considered): status=FAIL
    elif any(r["status"]==UNDETERMINED for r in considered): status=UNDETERMINED
    else: status=PASS
    return {"status":status,"required_scales":required_scales,"missing_scales":missing,
            "scale_statuses":tuple((r["scale"],r["status"]) for r in considered),
            "provenance":provenance}

def fitness_manifest():
    return deepcopy({"primitive":PRIMITIVE,"dependencies":tuple(DEPENDENCIES),"version":P023_VERSION,
    "schema_version":P023_SCHEMA_VERSION,"scope":P023_SCOPE,"statuses":FITNESS_STATUSES,"scales":SCALES,
    "boundaries":P023_BOUNDARIES,"transversal_referentials":P023_TRANSVERSAL_REFERENTIALS,
    "reuse_articulations":REUSE_ARTICULATIONS})

def validate_fitness_suite():
    assert FITNESS_STATUSES==(PASS,FAIL,UNDETERMINED)
    assert P023_BOUNDARIES["local_pass_is_not_global_pass"] is True
    assert P023_BOUNDARIES["undetermined_is_not_pass"] is True
    assert P023_BOUNDARIES["does_not_define_p024_adversarial_campaign"] is True
    assert P023_TRANSVERSAL_REFERENTIALS["world_models_dependency"] is None
    return True
