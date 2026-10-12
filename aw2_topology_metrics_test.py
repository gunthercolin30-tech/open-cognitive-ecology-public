from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'},{'rf_id':'RF-C'},{'rf_id':'RF-D'}]},persist=False); x=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[{'interaction_id':'AB','source_rf_id':'RF-A','target_rf_id':'RF-B','directed':True},{'interaction_id':'BC','source_rf_id':'RF-B','target_rf_id':'RF-C','directed':False}]},persist=False); assert x['component_count']==2 and x['isolated_node_ids']==['RF-D'] and x['density']==round(2/12,6); print('AW2_TOPOLOGY_METRICS_OK')
if __name__=='__main__': main()
