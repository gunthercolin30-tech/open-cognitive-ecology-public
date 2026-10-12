from ontology.dna_registry import registry_entries,registry_manifest,find_entry,validate_registry
def main():
    entries=registry_entries()
    assert entries and registry_manifest()["entry_count"]==len(entries)
    assert find_entry("P015:epistemic_boundary")["layer"]=="DNA-1"
    assert find_entry("P016:canonical_stack_shape")["version"]=="P016-v1"
    assert find_entry("DOES-NOT-EXIST") is None
    assert validate_registry()["valid"] is True
    print("P017_FUNCTIONAL_TEST_OK")
if __name__=="__main__": main()
