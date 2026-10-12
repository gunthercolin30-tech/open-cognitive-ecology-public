from ontology.dynamic_graph_constructor import DynamicGraphConstructor
from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={},persist=False); g=InteractionGraph().step(inputs={'multi_rf_registry':r},persist=False); l=DynamicGraphConstructor().step(inputs={'relations':[]},persist=False); assert r['primitive']=='MULTI_RF_REGISTRY' and g['primitive']=='INTERACTION_GRAPH' and l['primitive']=='DYNAMIC_GRAPH_CONSTRUCTOR'; print('AW2_NON_REGRESSION_OK')
if __name__=='__main__': main()
