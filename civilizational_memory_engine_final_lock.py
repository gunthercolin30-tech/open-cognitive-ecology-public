from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    result = CivilizationalMemoryEngine().step(inputs=build_context(), persist=False)
    assert result["status"] == "CIVILIZATIONAL_MEMORY_READY"
    assert result["civilizational_memory_ready"] is True
    assert result["quorum_status"] == "QUORUM_REACHED"
    assert result["consistency_status"] == "CONSISTENT"
    assert result["recovery_status"] == "RECOVERY_READY"
    assert result["functional_conclusion_only"] is True
    assert result["collective_consciousness_proven"] is False
    print("CIVILIZATIONAL_MEMORY_ENGINE_FINAL_LOCK_OK")
if __name__ == "__main__": main()
