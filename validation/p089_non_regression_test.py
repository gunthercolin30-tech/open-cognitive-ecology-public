from ontology.dna_f1_f18 import manifest
from ontology.dna_fundamental import fundamental_manifest
def main():
    p89=manifest(); p88=fundamental_manifest()
    assert p89["upstream_p088_final_lock"] == "f1a7d4adf322378726d9c0f7f481c8c8fe820fac62e3d08e6b2094be2f9b9b59"
    assert p89["functional_conclusion_only"] is True
    assert p89["phenomenology_undetermined"] is True
    assert p88["functional_conclusion_only"] is True
    assert p88["phenomenology_undetermined"] is True
    print("P089_NON_REGRESSION_OK")
if __name__ == "__main__": main()
