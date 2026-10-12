from ontology.dna_meta_rules import manifest
from ontology.dna_f1_f18 import manifest as p089_manifest
def main():
    m=manifest()
    assert m["upstream_p089_final_lock"]=="c8f571840fcb6656d9ffdc9bed613845ca1deb541d1a8bc8f4bceed18b660015"
    assert m["functional_conclusion_only"] is True
    assert m["phenomenology_undetermined"] is True
    assert p089_manifest()["scope"]=="P089_ONLY"
    assert any("P061-P086" in x and "not P090 execution prerequisites" in x for x in m["boundaries"])
    print("P090_NON_REGRESSION_OK")
if __name__=="__main__": main()
