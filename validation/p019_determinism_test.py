from ontology import dna_severity_model as s

def main():
    assert s.severity_manifest() == s.severity_manifest()
    for a in s.SEVERITY_LEVELS:
        for b in s.SEVERITY_LEVELS:
            assert s.compare_severity(a, b) == -s.compare_severity(b, a)
    print("P019_DETERMINISM_TEST_OK")

if __name__ == "__main__":
    main()
