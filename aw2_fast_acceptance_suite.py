import json, py_compile, tempfile
from pathlib import Path
from ontology.interaction_graph import InteractionGraph
from ontology.multi_rf_registry import MultiRFRegistry
ROOT=Path.home()/"open-cognitive-ecology"
def context():
 r=MultiRFRegistry().step(inputs={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"},{"rf_id":"RF-C"}]},persist=False)
 return {"multi_rf_registry":r,"interactions":[{"interaction_id":"I-AB","source_rf_id":"RF-A","target_rf_id":"RF-B","directed":True},{"interaction_id":"I-BC","source_rf_id":"RF-B","target_rf_id":"RF-C","directed":False}]}
def main():
 for p in [ROOT/"ontology/interaction_graph.py",ROOT/"aw2_fast_acceptance_suite.py",ROOT/"interaction_graph_final_lock.py"]: py_compile.compile(str(p),cfile=str(Path('/private/tmp')/(p.name+'.aw2.pyc')),doraise=True)
 a=InteractionGraph().step(inputs=context(),persist=False); b=InteractionGraph().step(inputs=context(),persist=False)
 assert a['interaction_graph_status']=='RF_INTERACTION_GRAPH_READY' and a['node_count']==3 and a['edge_count']==2 and a['component_count']==1 and a['graph_hash']==b['graph_hash']
 with tempfile.TemporaryDirectory() as t:
  g=InteractionGraph(root=Path(t)); p=g.step(inputs=context(),persist=True); assert Path(p['output_path']).exists(); q=g.step(inputs={'load_existing':True,'multi_rf_registry':context()['multi_rf_registry']},persist=False); assert q['graph_hash']==p['graph_hash']
 assert a['functional_conclusion_only'] is True and a['collective_consciousness_proven'] is False
 print('AW2_FAST_ACCEPTANCE_OK')
if __name__=='__main__': main()
