from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    manager = AceeLineageManager(root=Path(tmp))
    root_inputs = {
        "operation": "register_root",
        "transaction_id": "T0",
        "lineage_id": "L1",
        "architecture_id": "A0",
    }
    candidate_inputs = {
        "operation": "register_candidate",
        "transaction_id": "T1",
        "lineage_id": "L1",
        "generation_id": 1,
        "architecture_id": "A1",
        "parent_id": "A0",
        "mutation_id": "M1",
        "fitness_delta": 0.1,
    }
    selection_inputs = {
        "operation": "apply_selection",
        "transaction_id": "T2",
        "lineage_id": "L1",
        "generation_id": 1,
        "selection_decision": {
            "selection_id": "S1",
            "selection_decision_ready": True,
            "decision": "accept",
            "decision_reasons": ["gain"],
        },
    }
    root = manager.step(inputs=root_inputs, persist=True)
    candidate = manager.step(inputs=candidate_inputs, persist=True)
    active = manager.step(inputs=selection_inputs, persist=True)
    assert root["lineage_management_status"] == "ACEE_LINEAGE_MANAGEMENT_READY"
    assert candidate["generation_status"] == "candidate"
    assert active["generation_status"] == "active"
    assert active["active_generation_id"] == 1

print("ACEE13_FAST_ACCEPTANCE_OK")
