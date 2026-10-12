from copy import deepcopy
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    context = deepcopy(build_context())
    divergent = deepcopy(context["memory_records"][1])
    divergent["version_id"] = "MEM-FOUNDATION-V2-B"
    divergent["content"] = {"axiom": "closure", "generation": 2}
    divergent["replica_ids"] = ["RF-A"]
    divergent["acknowledged_replica_ids"] = ["RF-A"]
    divergent["loss_tolerance_score"] = 0.0
    context["memory_records"].append(divergent)
    result = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert result["conflict_count"] == 1
    assert result["unresolved_conflict_count"] == 0
    assert result["reconciliation_status"] == "RECONCILIATION_COMPLETE"
    print("AW8_DIVERGENCE_RECONCILIATION_OK")
if __name__ == "__main__": main()
