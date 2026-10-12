from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False); x=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[{'interaction_id':'V','source_rf_id':'RF-A','target_rf_id':'RF-B'},{'interaction_id':'O1','source_rf_id':'RF-X','target_rf_id':'RF-B'},{'interaction_id':'O2','source_rf_id':'RF-A','target_rf_id':'RF-Y'}]},persist=False); assert x['orphan_edge_count']==2 and x['edge_count']==1 and not x['interaction_graph_ready']; print('AW2_ORPHAN_EDGE_OK')
if __name__=='__main__': main()
