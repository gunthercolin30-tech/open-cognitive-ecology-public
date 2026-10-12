from copy import deepcopy
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    context = deepcopy(build_context())
    context["memory_records"][0]["availability_score"] = float("nan")
    context["memory_records"][0]["loss_tolerance_score"] = float("inf")
    result = CivilizationalMemoryEngine().step(inputs=context, persist=False)
    assert 0.0 <= result["availability_score"] <= 1.0
    assert 0.0 <= result["loss_tolerance_score"] <= 1.0
    assert result["civilizational_memory_ready"] is False
    print("AW8_NUMERIC_ROBUSTNESS_OK")
if __name__ == "__main__": main()
