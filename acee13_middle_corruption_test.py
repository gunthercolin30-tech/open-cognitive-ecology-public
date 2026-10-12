import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    manager = AceeLineageManager(root=root)
    manager.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    manager.step(inputs={"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":0.1}, persist=True)
    manager.step(inputs={"operation":"apply_selection","transaction_id":"T2","lineage_id":"L","generation_id":1,"selection_decision":{"selection_id":"S1","selection_decision_ready":True,"decision":"accept"}}, persist=True)
    history = root / "acee_runtime" / "ACEE13_acee_lineage_manager" / "lineage_event_history.jsonl"
    lines = history.read_text().splitlines()
    middle = json.loads(lines[1])
    middle["event_type"] = "tampered"
    lines[1] = json.dumps(middle, sort_keys=True)
    history.write_text("\n".join(lines) + "\n")
    result = manager.step(inputs={"operation":"inspect","lineage_id":"L"}, persist=False)
    assert result["history_corrupted"] is True
    assert result["lineage_management_ready"] is False
    assert "persistence_corrupted" in result["blocking_reasons"]
print("ACEE13_MIDDLE_CORRUPTION_OK")
