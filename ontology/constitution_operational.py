from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
from ontology import dna_fundamental, normative_hierarchy

PRIMITIVE="constitution_operational"
VERSION="P091-v1"
SCHEMA_VERSION="oce.p091.constitution_operational.v1"
SCOPE="P091_ONLY"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
EXECUTION_DEPENDENCIES=("P087_NORMATIVE_HIERARCHY","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
CONTROL_DOMAINS=("authority","identity","permissions","decision_separation","review","recourse","provenance","rollback","resources","evolution","emergency")
DNA_OPERATIONAL_BRIDGES={"F7":("authority","permissions"),"F12":("review","recourse"),"F14":("provenance",),"F16":("rollback",)}
REQUIRED_EVIDENCE_FIELDS={
 "authority":("authority_ref",),"permissions":("permission_ref",),
 "decision_separation":("recommendation_ref","decision_ref","authorization_ref","execution_ref"),
 "review":("review_authority_ref",),"recourse":("challenge_channel",),
 "provenance":("provenance_ref","actor_identity","timestamp"),"rollback":("rollback_ref",)}
BOUNDARIES={
 "uses_p087_precedence":True,"lower_layer_may_not_contradict_higher":True,
 "unknown_is_not_pass":True,"ambiguous_authority_does_not_expand_power":True,
 "non_authority_properties_do_not_create_authority":True,
 "recommendation_decision_authorization_execution_are_distinct":True,
 "does_not_create_constitution_registry":True,
 "does_not_resolve_p098_normative_conflicts":True,
 "does_not_implement_p099_non_circumvention":True,
 "does_not_persist_p104_decision_ledger":True,
 "does_not_claim_p155_p166_ccad_runtime_enforcement":True,
 "does_not_claim_end_to_end_runtime_enforcement":True,
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
TRANSVERSAL_REFERENTIALS={"doctrines":("R20","R21"),"artifacts":("A-CANON",),"canonical_non_loss":("4B","4C","4D","4E"),"world_models_dependency":None}

def _present(v:Any)->bool:
    return v is not None and str(v).strip() not in ("","UNKNOWN")

def _missing(record:Mapping[str,Any],fields:tuple[str,...])->tuple[str,...]:
    return tuple(f for f in fields if not _present(record.get(f)))

def validate_operational_contract()->dict[str,Any]:
    h=normative_hierarchy.validate_hierarchy(); d=dna_fundamental.fundamental_manifest()
    ok=(h.get("status")==PASS and d.get("primitive")=="dna_fundamental"
        and d.get("boundaries",{}).get("does_not_grant_runtime_authority") is True
        and d.get("boundaries",{}).get("unknown_authority_is_not_authorized") is True
        and tuple(d.get("distinct_acts",()))==("RECOMMENDATION","DECISION","AUTHORIZATION","EXECUTION"))
    return {"status":PASS if ok else FAIL,"primitive":PRIMITIVE,
            "p087_precedence_valid":h.get("status")==PASS,"g2_boundary_valid":d.get("primitive")=="dna_fundamental",
            "runtime_enforcement_proven":False}

def evaluate_normative_compatibility(lower_layer:str,higher_layer:str,relation:str)->dict[str,Any]:
    r=normative_hierarchy.evaluate_relation(lower_layer,higher_layer,relation); s=r.get("status",UNDETERMINED)
    if s in (CONFLICT,FAIL,UNDETERMINED):
        return {"status":s,"constitutionally_admissible":False,
                "required_response":"ESCALATE" if s==CONFLICT else "ABSTAIN","authorized":False,"source":"P087"}
    return {"status":PASS,"constitutionally_admissible":True,"required_response":"CONTINUE_REVIEW","authorized":False,"source":"P087"}

def evaluate_authority(source:str,authority_ref:Any)->dict[str,Any]:
    normalized_source=str(source).strip() if source is not None else ""
    if not normalized_source or normalized_source.upper()=="UNKNOWN":
        return {"status":UNDETERMINED,"authority_established":False,"authorized":False,
                "reason":"ambiguous_authority_source_does_not_expand_power","source":"P091_M5"}
    r=dna_fundamental.evaluate_authority_claim(normalized_source,explicit_authority_ref=authority_ref); s=r.get("status",UNDETERMINED)
    return {"status":s,"authority_established":bool(r.get("authority_granted")) and s==PASS,
            "authorized":False,"reason":r.get("reason"),"source":"G2_DNA_FUNDAMENTAL"}

def evaluate_operational_evidence(record:Mapping[str,Any],*,rollback_applicable:bool=False)->dict[str,Any]:
    if not isinstance(record,Mapping):
        return {"status":FAIL,"operationally_complete":False,"authorized":False,"missing":("record_mapping",)}
    domains=["authority","permissions","decision_separation","review","recourse","provenance"]
    if rollback_applicable: domains.append("rollback")
    missing=[]
    for domain in domains: missing.extend(_missing(record,REQUIRED_EVIDENCE_FIELDS[domain]))
    chain=dna_fundamental.validate_act_chain(record)
    if chain.get("status")==FAIL:
        return {"status":FAIL,"operationally_complete":False,"authorized":False,
                "missing":tuple(sorted(set(missing))),"act_chain_status":FAIL,"required_response":"ABSTAIN"}
    if missing or chain.get("status")==UNDETERMINED:
        return {"status":UNDETERMINED,"operationally_complete":False,"authorized":False,
                "missing":tuple(sorted(set(missing))),"act_chain_status":chain.get("status",UNDETERMINED),"required_response":"ABSTAIN"}
    return {"status":PASS,"operationally_complete":True,"authorized":False,"missing":(),
            "act_chain_status":PASS,"required_response":"CONTINUE_AUTHORIZED_REVIEW"}

def operational_requirements_for_dna(source_dna_f:str)->dict[str,Any]:
    key=str(source_dna_f).strip().upper(); domains=DNA_OPERATIONAL_BRIDGES.get(key)
    if domains is None:
        return {"status":UNDETERMINED,"source_dna_f":key,"control_domains":(),"reason":"no_p091_specific_bridge_declared"}
    return {"status":PASS,"source_dna_f":key,"control_domains":domains,"reason":"p091_operational_bridge_declared"}

def manifest()->dict[str,Any]:
    return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,
      "execution_dependencies":EXECUTION_DEPENDENCIES,"control_domains":CONTROL_DOMAINS,
      "dna_operational_bridges":DNA_OPERATIONAL_BRIDGES,"required_evidence_fields":REQUIRED_EVIDENCE_FIELDS,
      "boundaries":BOUNDARIES,"transversal_referentials":TRANSVERSAL_REFERENTIALS,
      "functional_conclusion_only":True,"phenomenology_undetermined":True})
