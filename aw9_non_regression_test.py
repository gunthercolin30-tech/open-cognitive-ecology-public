from copy import deepcopy
from aw9_context import build_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer


def main():
    analyzer = CollectiveConsciousnessAnalyzer()
    context = build_context()
    frozen = deepcopy(context)
    first = analyzer.step(inputs=context, persist=False)
    second_context = build_context()
    second_context["interaction_graph"]["edges"] = list(reversed(second_context["interaction_graph"].get("edges", [])))
    second = analyzer.step(inputs=second_context, persist=False)
    assert context == frozen
    assert first["analysis_hash"] == second["analysis_hash"]
    assert first["functional_collective_integration"] == second["functional_collective_integration"]
    assert first["member_rf_ids"] == sorted(first["member_rf_ids"])
    print("AW9_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
