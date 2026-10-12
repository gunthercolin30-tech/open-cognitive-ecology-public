from ontology import dna_severity_model as s

def main():
    m = s.severity_manifest()
    assert m["version"] == "P019-v1"
    assert m["schema_version"] == "oce.p019.dna_severity_model.v1"
    assert m["scope"] == "P019_ONLY"
    assert m["transversal_referentials"]["doctrines"] == ("R0", "R5", "R6", "R17", "R21")
    assert m["transversal_referentials"]["artifacts"] == ("A-CANON", "A-TRACE")
    assert m["transversal_referentials"]["world_models_dependency"] is None
    print("P019_PROVENANCE_VERSION_TEST_OK")

if __name__ == "__main__":
    main()
