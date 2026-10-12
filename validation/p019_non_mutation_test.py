from ontology import dna_severity_model as s

def main():
    m = s.severity_manifest()
    m["rank"]["ADVISORY"] = 99
    m["boundaries"]["does_not_grant_runtime_authority"] = False
    assert s.severity_manifest()["rank"]["ADVISORY"] == 0
    assert s.severity_manifest()["boundaries"]["does_not_grant_runtime_authority"] is True
    print("P019_NON_MUTATION_TEST_OK")

if __name__ == "__main__":
    main()
