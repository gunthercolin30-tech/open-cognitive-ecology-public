from pathlib import Path
from ontology.reference_frame_merging import ReferenceFrameMerging

def main():
    root=Path.home()/"open-cognitive-ecology"
    assert (root/"ontology/reference_frame_merging.py").exists()
    assert "reference_frame_merging" in (root/"ontology_inventory.txt").read_text().splitlines()
    assert "AW6 reference frame merging dependency patch" in (root/"dependency_registry.py").read_text()
    assert ReferenceFrameMerging.step_id=="AW6"
    print("AW6_REGISTRY_INTEGRITY_OK")
if __name__=="__main__": main()
