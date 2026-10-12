from ontology.dna_f1_f18 import get_rule, manifest
def main():
    f17=get_rule("F17"); f18=get_rule("F18")
    assert "humaine" in f17["definition"]
    assert "biodiversité" in f18["definition"]
    assert f17["status"] == "CANONICAL"
    assert f18["status"] == "CANONICAL"
    assert set(f17["reuse_interfaces"]) != set(f18["reuse_interfaces"])
    assert any("F17 and F18 remain distinct" in x for x in manifest()["boundaries"])
    print("P089_F17_F18_BOUNDARY_OK")
if __name__ == "__main__": main()
