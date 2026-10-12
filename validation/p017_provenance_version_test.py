from ontology.dna_registry import registry_entries,P017_SCHEMA_VERSION,P017_VERSION
def main():
    assert P017_SCHEMA_VERSION=="oce.p017.dna_registry.v1" and P017_VERSION=="P017-v1"
    for e in registry_entries():
        assert e["provenance"].startswith("ontology.")
        assert e["version"] in ("P015-v3","P016-v1")
        assert e["test_coverage"] and e["enforcement_status"]=="UNKNOWN"
    print("P017_PROVENANCE_VERSION_TEST_OK")
if __name__=="__main__": main()
