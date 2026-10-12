from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as A
from ontology.ontology_inventory import ONTOLOGY_INVENTORY as B
def main():
 assert A.count('interaction_graph')==1 and B.count('interaction_graph')==1; d=DEPENDENCY_REGISTRY['interaction_graph']; assert 'multi_rf_registry' in d and 'dynamic_graph_constructor' in d and len(d)==len(set(d)); print('AW2_REGISTRY_INTEGRITY_OK')
if __name__=='__main__': main()
