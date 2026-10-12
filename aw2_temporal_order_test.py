from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False); x=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[{'interaction_id':'I','source_rf_id':'RF-A','target_rf_id':'RF-B','valid_from_utc':'2026-07-11T12:00:00Z','valid_until_utc':'2026-07-11T11:00:00Z'}]},persist=False); assert x['temporal_issue_count']==1 and not x['interaction_graph_ready']; print('AW2_TEMPORAL_ORDER_OK')
if __name__=='__main__': main()
