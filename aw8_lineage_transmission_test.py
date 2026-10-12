from copy import deepcopy
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    context = deepcopy(build_context())
    result = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert result["lineage_preservation_score"] == 1.0
    assert result["transmission_status"] == "INTERGENERATIONAL_TRANSMISSION_READY"
    context["memory_records"][0]["transmission_chain"] = []
    degraded = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert degraded["transmission_status"] == "TRANSMISSION_INCOMPLETE"
    assert degraded["civilizational_memory_ready"] is False
    print("AW8_LINEAGE_TRANSMISSION_OK")
if __name__ == "__main__": main()
