import json
from ontology.dna_registry import registry_manifest,registry_entries,find_entry
def canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def main():
    assert canonical(registry_manifest())==canonical(registry_manifest())
    entries=registry_entries(); entries[0]["scope"]="tampered"
    assert registry_entries()[0]["scope"]!="tampered"
    found=find_entry("P015:official_definition"); found["scope"]="tampered"
    assert find_entry("P015:official_definition")["scope"]!="tampered"
    print("P017_DETERMINISM_TEST_OK")
if __name__=="__main__": main()
