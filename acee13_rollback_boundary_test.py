from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    m=AceeLineageManager(root=Path(tmp))
    m.step({"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"},persist=True)
    m.step({"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":-0.2},persist=True)
    pending=m.step({"operation":"apply_selection","transaction_id":"T2","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S","selection_decision_ready":True,"decision":"rollback"}},persist=True)
    assert pending["generation_status"]=="rollback_pending" and pending["rollback_executed_by_lineage_manager"] is False
    blocked=m.step({"operation":"record_rollback","transaction_id":"T3","lineage_id":"L","generation_id":1,"rollback_result":{"transaction_id":"R1","rollback_status":"ACEE_ROLLBACK_BLOCKED","rollback_performed":False}},persist=True)
    assert blocked["generation_status"]=="rollback_blocked" and blocked["active_generation_id"]==0
print("ACEE13_ROLLBACK_BOUNDARY_OK")
