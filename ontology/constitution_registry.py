from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
from ontology import constitution_operational, dna_fundamental, normative_hierarchy

PRIMITIVE = "constitution_registry"
VERSION = "P092-v1"
SCHEMA_VERSION = "oce.p092.constitution_registry.v1"
SCOPE = "P092_ONLY"
PASS, FAIL, UNDETERMINED = "PASS", "FAIL", "UNDETERMINED"
EXECUTION_DEPENDENCIES = ("P091_CONSTITUTION_OPERATIONAL","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
REQUIRED_FIELDS = ("constitution_rule_id","source_DNA_F","scope","mandatory_mechanism","enforcement","tests","exception_policy","authority","version","provenance")
BOUNDARIES = {
 "registry_only":True,"does_not_define_p093_operational_invariants":True,
 "does_not_implement_p094_act_authorities":True,"does_not_create_p095_human_authority_registry":True,
 "does_not_resolve_p098_normative_conflicts":True,"does_not_implement_p099_non_circumvention":True,
 "does_not_persist_p104_decision_ledger":True,"does_not_claim_p155_p166_ccad_runtime_enforcement":True,
 "does_not_grant_execution_authority":True,"unknown_is_not_pass":True,
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
TRANSVERSAL_REFERENTIALS={"doctrines":("R20","R21"),"artifacts":("A-CANON",),"canonical_non_loss":("4B","4C","4D","4E"),"world_models_dependency":None}

def _rule(fid, scope, mechanisms):
    return {"constitution_rule_id":f"P092:{fid}:{'_'.join(mechanisms)}","source_DNA_F":fid,"scope":scope,
      "mandatory_mechanism":tuple(mechanisms),"enforcement":UNDETERMINED,
      "tests":("validation.p091_constitution_operational_test","validation.p092_constitution_registry_test"),
      "exception_policy":"NO_IMPLICIT_EXCEPTION","authority":"G2_DNA_FUNDAMENTAL",
      "version":VERSION,"provenance":f"ontology.constitution_operational:DNA_OPERATIONAL_BRIDGES[{fid}]"}

_CONSTITUTION_RULES=(
 _rule("F7","constitutional authority and permissions bridge",("authority","permissions")),
 _rule("F12","constitutional review and recourse bridge",("review","recourse")),
 _rule("F14","constitutional provenance bridge",("provenance",)),
 _rule("F16","constitutional rollback bridge",("rollback",)),
)

def registry_entries()->tuple[dict[str,Any],...]:
    return tuple(deepcopy(e) for e in _CONSTITUTION_RULES)

def find_rule(constitution_rule_id:str)->dict[str,Any]|None:
    key=str(constitution_rule_id).strip()
    for e in _CONSTITUTION_RULES:
        if e["constitution_rule_id"]==key: return deepcopy(e)
    return None

def rules_for_dna(source_dna_f:str)->tuple[dict[str,Any],...]:
    key=str(source_dna_f).strip().upper()
    return tuple(deepcopy(e) for e in _CONSTITUTION_RULES if e["source_DNA_F"]==key)

def _present(v:Any)->bool:
    return v is not None and str(v).strip() not in ("","UNKNOWN")

def validate_registry(entries:tuple[dict[str,Any],...]|None=None)->dict[str,Any]:
    records=registry_entries() if entries is None else tuple(deepcopy(entries))
    ids=[r.get("constitution_rule_id") for r in records if isinstance(r,Mapping)]
    unique=len(ids)==len(records)==len(set(ids))
    fields_ok=bool(records) and all(
      isinstance(r,Mapping) and all(f in r for f in REQUIRED_FIELDS)
      and _present(r.get("constitution_rule_id")) and _present(r.get("source_DNA_F")) and _present(r.get("scope"))
      and isinstance(r.get("mandatory_mechanism"),tuple) and bool(r.get("mandatory_mechanism"))
      and r.get("enforcement")==UNDETERMINED and isinstance(r.get("tests"),tuple) and bool(r.get("tests"))
      and r.get("exception_policy")=="NO_IMPLICIT_EXCEPTION" and _present(r.get("authority"))
      and _present(r.get("version")) and _present(r.get("provenance")) for r in records)
    bridge_ok=all(
      constitution_operational.operational_requirements_for_dna(r["source_DNA_F"]).get("status")==PASS
      and tuple(constitution_operational.operational_requirements_for_dna(r["source_DNA_F"]).get("control_domains",()))==tuple(r["mandatory_mechanism"])
      for r in records if isinstance(r,Mapping))
    hierarchy_ok=normative_hierarchy.validate_hierarchy().get("status")==PASS
    dna=dna_fundamental.fundamental_manifest()
    dna_ok=(dna.get("primitive")=="dna_fundamental"
      and dna.get("boundaries",{}).get("does_not_grant_runtime_authority") is True
      and dna.get("boundaries",{}).get("unknown_authority_is_not_authorized") is True)
    valid=bool(unique and fields_ok and bridge_ok and hierarchy_ok and dna_ok)
    return {"status":PASS if valid else FAIL,"valid":valid,"entry_count":len(records),"unique_rule_ids":unique,
      "required_fields_valid":fields_ok,"p091_bridge_compatible":bridge_ok,"p087_hierarchy_valid":hierarchy_ok,
      "g2_boundary_valid":dna_ok,"unknown_enforcement_preserved":all(isinstance(r,Mapping) and r.get("enforcement")==UNDETERMINED for r in records),
      "execution_authority_granted":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def registry_manifest()->dict[str,Any]:
    v=validate_registry()
    return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,
      "execution_dependencies":EXECUTION_DEPENDENCIES,"entry_count":len(_CONSTITUTION_RULES),"entries":_CONSTITUTION_RULES,
      "required_fields":REQUIRED_FIELDS,"boundaries":BOUNDARIES,"transversal_referentials":TRANSVERSAL_REFERENTIALS,
      "validation_status":v["status"],"functional_conclusion_only":True,"phenomenology_undetermined":True})
