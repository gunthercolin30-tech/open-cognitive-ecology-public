from copy import deepcopy
from aw9_context import build_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer


def main():
    analyzer = CollectiveConsciousnessAnalyzer()
    aggregation = deepcopy(build_context())
    aggregation["interaction_graph"] = {"edges":[],"edge_count":0,"density":0.0}
    aggregation["shared_reference_frame_detection"] = {"detected_pair_count":0}
    aggregation["coalition_detection"] = {"coalitions":[]}
    result = analyzer.step(inputs=aggregation, persist=False)
    assert result["collective_rf_analysis_ready"] is False
    assert "INSUFFICIENT_OBSERVED_INTERACTION" in result["false_positive_blockers"]
    assert "NO_REPRODUCIBLE_SHARED_REFERENCE_FRAME" in result["false_positive_blockers"]
    print("AW9_FALSE_POSITIVE_BLOCKING_OK")


if __name__ == "__main__":
    main()
