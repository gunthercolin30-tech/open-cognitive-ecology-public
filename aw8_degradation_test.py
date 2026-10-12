from copy import deepcopy
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    context = deepcopy(build_context())
    for record in context["memory_records"]:
        record["replica_ids"] = ["RF-A"]
        record["acknowledged_replica_ids"] = ["RF-A"]
        record["loss_tolerance_score"] = 0.0
    result = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert result["civilizational_memory_ready"] is False
    assert result["quorum_status"] == "QUORUM_NOT_REACHED"
    assert result["recovery_status"] == "RECOVERY_NOT_READY"
    print("AW8_DEGRADATION_OK")
if __name__ == "__main__": main()
