from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    r = CivilizationalMemoryEngine().step(inputs=build_context(), persist=False)
    for key in ("collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven","consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"):
        assert r[key] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    print("AW8_EPISTEMIC_GUARD_OK")
if __name__ == "__main__": main()
