from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    m=AceeLineageManager(root=Path(tmp))
    m.step({"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"},persist=True)
    m.step({"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":0.1},persist=True)
    m.step({"operation":"apply_selection","transaction_id":"T2","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S1","selection_decision_ready":True,"decision":"accept"}},persist=True)
    m.step({"operation":"apply_selection","transaction_id":"T3","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S2","selection_decision_ready":True,"decision":"rollback"}},persist=True)
    done=m.step({"operation":"record_rollback","transaction_id":"T4","lineage_id":"L","generation_id":1,"rollback_result":{"transaction_id":"R1","rollback_status":"ACEE_ROLLBACK_ENGINE_READY","rollback_performed":True}},persist=True)
    assert done["generation_status"]=="rolled_back" and done["active_generation_id"]==0
print("ACEE13_ROLLBACK_COMPLETION_OK")
