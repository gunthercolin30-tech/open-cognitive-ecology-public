from __future__ import annotations
from copy import deepcopy
from ontology import constitution_operational
from ontology.constitution_registry import BOUNDARIES,PASS,FAIL,REQUIRED_FIELDS,SCHEMA_VERSION,SCOPE,VERSION,find_rule,registry_entries,registry_manifest,rules_for_dna,validate_registry

def main():
    entries=registry_entries(); m=registry_manifest(); bridges=constitution_operational.DNA_OPERATIONAL_BRIDGES
    checks={
      "scope":SCOPE=="P092_ONLY","schema":SCHEMA_VERSION=="oce.p092.constitution_registry.v1","version":VERSION=="P092-v1",
      "nonempty":len(entries)==4,"manifest_count":m["entry_count"]==len(entries),
      "unique_ids":len({e["constitution_rule_id"] for e in entries})==len(entries),
      "required_fields":all(all(f in e for f in REQUIRED_FIELDS) for e in entries),
      "exact_bridge_sources":{e["source_DNA_F"] for e in entries}==set(bridges),
      "exact_bridge_mechanisms":all(tuple(e["mandatory_mechanism"])==tuple(bridges[e["source_DNA_F"]]) for e in entries),
      "unknown_enforcement":all(e["enforcement"]=="UNDETERMINED" for e in entries),
      "no_implicit_exception":all(e["exception_policy"]=="NO_IMPLICIT_EXCEPTION" for e in entries),
      "lookup":find_rule("P092:F12:review_recourse")["source_DNA_F"]=="F12","missing_lookup":find_rule("UNKNOWN") is None,
      "dna_lookup":len(rules_for_dna("f14"))==1 and rules_for_dna("f14")[0]["source_DNA_F"]=="F14",
      "self_validation":validate_registry()["status"]==PASS,"registry_only":BOUNDARIES["registry_only"] is True,
      "no_p093":BOUNDARIES["does_not_define_p093_operational_invariants"] is True,
      "no_execution_authority":BOUNDARIES["does_not_grant_execution_authority"] is True,
      "functional_only":m["functional_conclusion_only"] is True,"phenomenology_undetermined":m["phenomenology_undetermined"] is True}
    duplicate=list(entries); duplicate.append(deepcopy(entries[0])); checks["duplicate_rejected"]=validate_registry(tuple(duplicate))["status"]==FAIL
    broken=list(entries); broken[0]["provenance"]=""; checks["missing_provenance_rejected"]=validate_registry(tuple(broken))["status"]==FAIL
    promoted=list(entries); promoted[0]["enforcement"]="PASS"; checks["enforcement_promotion_rejected"]=validate_registry(tuple(promoted))["status"]==FAIL
    incompatible=list(entries); incompatible[0]["mandatory_mechanism"]=("authority",); checks["bridge_drift_rejected"]=validate_registry(tuple(incompatible))["status"]==FAIL
    returned=registry_entries(); returned[0]["scope"]="MUTATED"; checks["non_mutation"]=registry_entries()[0]["scope"]!="MUTATED"
    assert all(checks.values()),{k:v for k,v in checks.items() if not v}
    print("P092_CONSTITUTION_REGISTRY_TEST_OK")
    print("status=PASSED"); print("entries=4"); print("unique_rule_ids=True"); print("p091_bridge_compatible=True")
    print("unknown_enforcement_preserved=True"); print("execution_authority_granted=False"); print("non_mutation=PASS")
    print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()
