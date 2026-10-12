from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
R=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False)
READY_OR_SYNTHETIC_CONTEXT={'multi_rf_registry':R,'interactions':[{'interaction_id':'I-AB','source_rf_id':'RF-A','target_rf_id':'RF-B'}]}
def main():
 x=InteractionGraph().step(inputs=READY_OR_SYNTHETIC_CONTEXT,persist=False); assert x['interaction_graph_status']=='RF_INTERACTION_GRAPH_READY' and x['node_count']==2 and x['edge_count']==1 and x['collective_consciousness_proven'] is False; print('AW2_FINAL_LOCK_OK')
if __name__=='__main__': main()
