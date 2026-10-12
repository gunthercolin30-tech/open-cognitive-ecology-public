from ontology import dna_severity_model as s

def main():
    for bad in (None, "", "advisory", "UNKNOWN", "CRITICAL", 0, False, (), [], {}):
        assert s.validate_severity(bad)["valid"] is False
        try:
            s.severity_rank(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid severity accepted")
    print("P019_DEGRADATION_TEST_OK")

if __name__ == "__main__":
    main()
