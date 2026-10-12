from __future__ import annotations
from copy import deepcopy

PRIMITIVE = "dna_stack"
DESCRIPTION = "Canonical layered organization of OCE DNA (P016)."
DEPENDENCIES = ["minimal_architectural_dna"]
P016_VERSION = "P016-v1"
P016_SCOPE = "P016_ONLY"

DNA_STACK_ORDER = ("DNA-0","DNA-1","DNA-2","DNA-3","DNA-4","DNA-5","DNA-6","DNA-7","DNA-X")
DNA_STACK = {
 "DNA-0":{"name":"Ontology","p015_domains":("architectural",)},
 "DNA-1":{"name":"Epistemics","p015_domains":("epistemic",)},
 "DNA-2":{"name":"Cognition","p015_domains":("cognitive",)},
 "DNA-3":{"name":"Resources/Frugality","p015_domains":("resources",)},
 "DNA-4":{"name":"Governance","p015_domains":("governance",)},
 "DNA-5":{"name":"Individuals/Society","p015_domains":("individuals",)},
 "DNA-6":{"name":"Evolution","p015_domains":("evolution",)},
 "DNA-7":{"name":"Economics/Commons","p015_domains":("economics",)},
 "DNA-X":{"name":"Evidence/Provenance","p015_domains":("evidence",)},
}
P016_TRANSVERSAL_REFERENTIALS = {
 "doctrines":("R0","R1","R2","R4","R10","R11","R14","R15","R17","R18","R21"),
 "artifacts":("A-CANON","A-R0R21","A-TRACE","A-NONLOSS"),
 "world_models_dependency_required":False,
}
P016_BOUNDARIES = {
 "composition_only":True,
 "does_not_duplicate_domain_logic":True,
 "does_not_grant_runtime_authority":True,
 "does_not_define_registry":True,
 "does_not_define_rule_contract":True,
 "does_not_define_severity":True,
 "does_not_define_inheritance":True,
 "does_not_define_mutation_protocol":True,
 "does_not_define_lineage_versioning":True,
 "does_not_claim_end_to_end_enforcement":True,
 "native_end_to_end_enforcement":"UNKNOWN",
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
def stack_manifest():
    return {"primitive":PRIMITIVE,"version":P016_VERSION,"scope":P016_SCOPE,
            "order":DNA_STACK_ORDER,"layers":deepcopy(DNA_STACK),
            "transversal_referentials":deepcopy(P016_TRANSVERSAL_REFERENTIALS),
            "boundaries":deepcopy(P016_BOUNDARIES)}
def validate_stack():
    domains=tuple(DNA_STACK[k]["p015_domains"][0] for k in DNA_STACK_ORDER)
    valid=(tuple(DNA_STACK)==DNA_STACK_ORDER and domains==(
      "architectural","epistemic","cognitive","resources","governance",
      "individuals","evolution","economics","evidence")
      and P016_BOUNDARIES["composition_only"]
      and P016_BOUNDARIES["does_not_grant_runtime_authority"]
      and P016_BOUNDARIES["native_end_to_end_enforcement"]=="UNKNOWN")
    return {"primitive":PRIMITIVE,"valid":valid,"layer_count":len(DNA_STACK_ORDER),
            "scope":P016_SCOPE,"functional_conclusion_only":True,
            "phenomenology_undetermined":True}
