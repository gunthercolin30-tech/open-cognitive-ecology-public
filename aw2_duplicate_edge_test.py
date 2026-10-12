from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False); e={'interaction_id':'I','source_rf_id':'RF-A','target_rf_id':'RF-B'}; x=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[e,dict(e)]},persist=False); assert x['exact_duplicate_count']==1 and x['interaction_graph_ready']; y=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[e,{'interaction_id':'I','source_rf_id':'RF-B','target_rf_id':'RF-A'}]},persist=False); assert y['collision_count']==1 and not y['interaction_graph_ready']; print('AW2_DUPLICATE_AND_COLLISION_OK')
if __name__=='__main__': main()
