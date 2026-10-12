import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    manager = AceeLineageManager(root=root)
    manager.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    manager.step(inputs={"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":0.2}, persist=True)
    manager.step(inputs={"operation":"register_candidate","transaction_id":"T2","lineage_id":"L","generation_id":2,"architecture_id":"A1B","parent_id":"A0","mutation_id":"M1B","fitness_delta":0.15}, persist=True)
    manager.step(inputs={"operation":"apply_selection","transaction_id":"T3","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S1","selection_decision_ready":True,"decision":"accept"}}, persist=True)
    manager.step(inputs={"operation":"apply_selection","transaction_id":"T4","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S2","selection_decision_ready":True,"decision":"rollback"}}, persist=True)
    manager.step(inputs={"operation":"record_rollback","transaction_id":"T5","lineage_id":"L","generation_id":1,"rollback_result":{"transaction_id":"R1","rollback_status":"ACEE_ROLLBACK_ENGINE_READY","rollback_performed":True}}, persist=True)
    state = json.loads((root / "acee_runtime" / "ACEE13_acee_lineage_manager" / "lineages.json").read_text())
    generations = state["lineages"]["L"]["generations"]
    assert generations["2"]["architecture_id"] == "A1B"
    assert generations["2"]["status"] == "candidate"
    assert state["lineages"]["L"]["active_generation_id"] == 0
print("ACEE13_BRANCH_ROLLBACK_PRESERVATION_OK")
