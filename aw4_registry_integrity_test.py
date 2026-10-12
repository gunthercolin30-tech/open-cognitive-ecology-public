from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as A
from ontology.ontology_inventory import ONTOLOGY_INVENTORY as B
def main():
    assert A.count("coalition_detector")==1 and B.count("coalition_detector")==1
    deps=DEPENDENCY_REGISTRY["coalition_detector"]
    for name in ["ecology_blueprint","multi_rf_registry","interaction_graph","shared_reference_frame_detector"]: assert name in deps
    assert len(deps)==len(set(deps))
    print("AW4_REGISTRY_INTEGRITY_OK")
if __name__=="__main__": main()
