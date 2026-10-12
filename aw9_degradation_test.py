from copy import deepcopy
from aw9_context import build_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer


def main():
    analyzer = CollectiveConsciousnessAnalyzer()
    empty = analyzer.step(inputs={}, persist=False)
    assert empty["collective_rf_analysis_ready"] is False
    assert "INSUFFICIENT_MULTI_RF_POPULATION" in empty["false_positive_blockers"]

    centralized = deepcopy(build_context())
    centralized["interaction_graph"]["edges"] = [
        {"source_rf_id":"RF-A","target_rf_id":"RF-B"},
        {"source_rf_id":"RF-A","target_rf_id":"RF-C"},
    ]
    centralized["interaction_graph"]["edge_count"] = 2
    centralized["interaction_graph"]["density"] = 0.67
    centralized["thresholds"] = {"maximum_centralization_risk":0.45}
    result = analyzer.step(inputs=centralized, persist=False)
    assert result["collective_rf_analysis_ready"] is False
    assert "SINGLE_CONTROLLER_OR_CENTRALIZATION_RISK" in result["false_positive_blockers"]

    no_memory = deepcopy(build_context())
    no_memory["civilizational_memory"] = {}
    result = analyzer.step(inputs=no_memory, persist=False)
    assert result["collective_rf_analysis_ready"] is False
    assert "INSUFFICIENT_CIVILIZATIONAL_MEMORY_SHARING" in result["false_positive_blockers"]
    print("AW9_DEGRADATION_OK")


if __name__ == "__main__":
    main()
