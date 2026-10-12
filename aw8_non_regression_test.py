from copy import deepcopy
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    context = build_context(); original = deepcopy(context)
    engine = CivilizationalMemoryEngine()
    a = engine.step(inputs=context, persist=False)
    b = engine.step(inputs=deepcopy(context), persist=False)
    assert context == original
    assert a["result_hash"] == b["result_hash"]
    assert a["memory_records"] == b["memory_records"]
    print("AW8_NON_REGRESSION_OK")
if __name__ == "__main__": main()
