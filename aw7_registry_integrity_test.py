
from pathlib import Path
def main():
    root=Path(__file__).resolve().parent
    assert (root/"ontology/reference_frame_fragmentation.py").exists()
    assert (root/"reference_frame_fragmentation_final_lock.py").exists()
    assert (root/"ontology_inventory.txt").read_text().splitlines().count("reference_frame_fragmentation")==1
    assert (root/"dependency_registry.py").read_text().count("# AW7 reference frame fragmentation dependency patch")==1
    print("AW7_REGISTRY_INTEGRITY_OK")
if __name__=="__main__": main()
