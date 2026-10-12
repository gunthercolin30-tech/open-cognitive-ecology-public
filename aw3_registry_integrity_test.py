from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as A
from ontology.ontology_inventory import ONTOLOGY_INVENTORY as B

def main():
 assert A.count("shared_reference_frame_detector")==1 and B.count("shared_reference_frame_detector")==1
 deps=DEPENDENCY_REGISTRY["shared_reference_frame_detector"]
 assert "multi_rf_registry" in deps and "interaction_graph" in deps and len(deps)==len(set(deps))
 print("AW3_REGISTRY_INTEGRITY_OK")
if __name__=="__main__": main()
