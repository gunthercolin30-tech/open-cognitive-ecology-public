from copy import deepcopy
from ontology.dna_registry import registry_entries,validate_registry
def main():
    base=list(registry_entries())
    x=deepcopy(base); x[0].pop("provenance"); assert validate_registry(tuple(x))["valid"] is False
    x=deepcopy(base); x[0]["layer"]="DNA-UNKNOWN"; assert validate_registry(tuple(x))["valid"] is False
    x=deepcopy(base); x.append(deepcopy(x[0])); assert validate_registry(tuple(x))["valid"] is False
    x=deepcopy(base); x[0]["enforcement_status"]="PASS"; assert validate_registry(tuple(x))["valid"] is False
    print("P017_DEGRADATION_TEST_OK")
if __name__=="__main__": main()
