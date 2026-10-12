
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def main():
    assert (ROOT/"ontology/conflict_detector.py").exists()
    assert (ROOT/"ontology_inventory.txt").read_text().splitlines().count("conflict_detector")==1
    assert (ROOT/"dependency_registry.py").read_text().count("AW5 conflict detector dependency patch")==1
    assert "ontology.conflict_detector" in (ROOT/"global_module_catalog.txt").read_text()
    print("AW5_REGISTRY_INTEGRITY_OK")
if __name__=="__main__": main()
