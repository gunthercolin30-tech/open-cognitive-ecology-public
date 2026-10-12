from __future__ import annotations
import json
from pathlib import Path
from ontology.dna_stack import *
ROOT=Path.home()/"open-cognitive-ecology"
ORDER=("DNA-0","DNA-1","DNA-2","DNA-3","DNA-4","DNA-5","DNA-6","DNA-7","DNA-X")
NAMES=("Ontology","Epistemics","Cognition","Resources/Frugality","Governance","Individuals/Society","Evolution","Economics/Commons","Evidence/Provenance")
DOMAINS=("architectural","epistemic","cognitive","resources","governance","individuals","evolution","economics","evidence")
DOCTRINES=("R0","R1","R2","R4","R10","R11","R14","R15","R17","R18","R21")
ARTIFACTS=("A-CANON","A-R0R21","A-TRACE","A-NONLOSS")
def evaluate():
    m=stack_manifest()
    return {
      "scope":P016_SCOPE=="P016_ONLY","order":DNA_STACK_ORDER==ORDER,
      "names":tuple(DNA_STACK[k]["name"] for k in ORDER)==NAMES,
      "domains":tuple(DNA_STACK[k]["p015_domains"][0] for k in ORDER)==DOMAINS,
      "nine_layers":len(DNA_STACK)==9,
      "doctrines":P016_TRANSVERSAL_REFERENTIALS["doctrines"]==DOCTRINES,
      "artifacts":P016_TRANSVERSAL_REFERENTIALS["artifacts"]==ARTIFACTS,
      "no_wm":P016_TRANSVERSAL_REFERENTIALS["world_models_dependency_required"] is False,
      "composition_only":P016_BOUNDARIES["composition_only"] is True,
      "no_duplicate_logic":P016_BOUNDARIES["does_not_duplicate_domain_logic"] is True,
      "no_runtime_authority":P016_BOUNDARIES["does_not_grant_runtime_authority"] is True,
      "later_milestones_untouched":all(P016_BOUNDARIES[k] for k in (
        "does_not_define_registry","does_not_define_rule_contract","does_not_define_severity",
        "does_not_define_inheritance","does_not_define_mutation_protocol","does_not_define_lineage_versioning")),
      "enforcement_unknown":P016_BOUNDARIES["native_end_to_end_enforcement"]=="UNKNOWN",
      "no_enforcement_overclaim":P016_BOUNDARIES["does_not_claim_end_to_end_enforcement"] is True,
      "functional_only":P016_BOUNDARIES["functional_conclusion_only"] is True,
      "phenomenology_undetermined":P016_BOUNDARIES["phenomenology_undetermined"] is True,
      "self_validation":validate_stack()["valid"] is True,
      "defensive_copy":m["layers"] is not DNA_STACK,
    }
def main():
    checks=evaluate()
    report={"schema":"oce.p016.dna_stack.v1","milestone":"P016",
      "status":"PASS" if all(checks.values()) else "FAIL","scope":"P016_ONLY",
      "checks":checks,"functional_conclusion_only":True,
      "phenomenology_undetermined":True,"unknown_promotion":False}
    (ROOT/"p016_dna_stack_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if not all(checks.values()): raise SystemExit("P016_DNA_STACK_FAIL")
    print("P016_DNA_STACK_OK")
if __name__=="__main__": main()
