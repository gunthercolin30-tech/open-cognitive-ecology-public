from copy import deepcopy
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    context = deepcopy(build_context())
    nominal = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert nominal["forgetting_status"] == "GOVERNED_FORGETTING_READY"
    context["memory_records"][0]["forgetting_policy"] = {"mode": "automatic", "authorized": True}
    bad = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert bad["forgetting_status"] == "FORGETTING_POLICY_INCOMPLETE"
    assert bad["civilizational_memory_ready"] is False
    print("AW8_GOVERNED_FORGETTING_OK")
if __name__ == "__main__": main()
