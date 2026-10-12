import tempfile
from pathlib import Path
from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False)
 with tempfile.TemporaryDirectory() as t:
  g=InteractionGraph(root=Path(t)); p=Path(t)/'rf_ecology/AW2_interaction_graph/latest_interaction_graph.json'; p.parent.mkdir(parents=True); p.write_text('{ bad'); x=g.step(inputs={'load_existing':True,'multi_rf_registry':r,'interactions':[{'interaction_id':'I','source_rf_id':'RF-A','target_rf_id':'RF-B'}]},persist=False); assert x['interaction_graph_ready'] and x['edge_count']==1
 print('AW2_CORRUPTION_FALLBACK_OK')
if __name__=='__main__': main()
