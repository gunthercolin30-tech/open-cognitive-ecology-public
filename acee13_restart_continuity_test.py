from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    first = AceeLineageManager(root=root)
    first.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    first.step(inputs={"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":0.2}, persist=True)
    first.step(inputs={"operation":"apply_selection","transaction_id":"T2","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S1","selection_decision_ready":True,"decision":"accept"}}, persist=True)
    second = AceeLineageManager(root=root)
    inspected = second.step(inputs={"operation":"inspect","lineage_id":"L"}, persist=False)
    assert inspected["active_generation_id"] == 1
    assert inspected["history_corrupted"] is False
print("ACEE13_RESTART_CONTINUITY_OK")
