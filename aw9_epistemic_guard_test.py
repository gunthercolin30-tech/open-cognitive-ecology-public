from aw9_context import build_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer


def main():
    result = CollectiveConsciousnessAnalyzer().step(inputs=build_context(), persist=False)
    for key in ["collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven","consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"]:
        assert result[key] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["epistemic_scope"] == "functional_multi_rf_ecology_only"
    print("AW9_EPISTEMIC_GUARD_OK")


if __name__ == "__main__":
    main()
