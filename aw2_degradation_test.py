from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False)
 x=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[{'interaction_id':'I-X','source_rf_id':'RF-A','target_rf_id':'RF-X'}]},persist=True); assert not x['interaction_graph_ready'] and x['orphan_edge_count']==1 and not x['persisted']
 y=InteractionGraph().step(inputs={'multi_rf_registry':r,'interactions':[{'interaction_id':'I-BAD','source_rf_id':'RF-A','target_rf_id':'RF-B','weight':'nan','valid_from_utc':'2026-07-12T00:00:00Z','valid_until_utc':'2026-07-11T00:00:00Z'}]},persist=False); assert y['invalid_numeric_issue_count']==1 and y['temporal_issue_count']==1
 print('AW2_DEGRADATION_OK')
if __name__=='__main__': main()
