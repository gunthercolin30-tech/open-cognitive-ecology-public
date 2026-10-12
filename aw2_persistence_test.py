import json,tempfile
from pathlib import Path
from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
def main():
 r=MultiRFRegistry().step(inputs={'rf_records':[{'rf_id':'RF-A'},{'rf_id':'RF-B'}]},persist=False); c={'multi_rf_registry':r,'interactions':[{'interaction_id':'I','source_rf_id':'RF-A','target_rf_id':'RF-B'}]}
 with tempfile.TemporaryDirectory() as t:
  g=InteractionGraph(root=Path(t)); a=g.step(inputs=c,persist=True); b=g.step(inputs=c,persist=True); assert a['graph_hash']==b['graph_hash']; q=g.step(inputs={'load_existing':True,'multi_rf_registry':r},persist=False); assert q['graph_hash']==b['graph_hash']; assert json.loads(Path(b['output_path']).read_text())['graph_hash']==b['graph_hash']
 print('AW2_PERSISTENCE_AND_RESTART_OK')
if __name__=='__main__': main()
