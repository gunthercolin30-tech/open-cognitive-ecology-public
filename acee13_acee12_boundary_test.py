from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    manager = AceeLineageManager(root=Path(tmp))
    manager.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    result = manager.step(inputs={"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":0.1}, persist=True)
    event = result["genealogy_event"]
    assert event["target_primitive"] == "ACEE_ARCHITECTURE_GENEALOGY"
    assert result["genealogy_written_by_lineage_manager"] is False
    forbidden = {"topology", "continuity_score", "branch_analysis", "graph_metrics"}
    assert forbidden.isdisjoint(event)
print("ACEE13_ACEE12_BOUNDARY_OK")
