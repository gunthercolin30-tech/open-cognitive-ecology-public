from ontology import dna_severity_model as s

def main():
    assert s.SEVERITY_LEVELS == ("ADVISORY", "STANDARD", "STRICT", "CONSTITUTIONAL")
    assert [s.severity_rank(x) for x in s.SEVERITY_LEVELS] == [0, 1, 2, 3]
    assert all(s.validate_severity(x)["valid"] for x in s.SEVERITY_LEVELS)
    print("P019_DNA_SEVERITY_MODEL_OK")

if __name__ == "__main__":
    main()
