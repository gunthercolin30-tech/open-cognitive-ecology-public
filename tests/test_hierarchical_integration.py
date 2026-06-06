from ontology.hierarchical_integration import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    HierarchicalIntegration,
)


def test_metadata():
    assert PRIMITIVE_NAME == "HIERARCHICAL_INTEGRATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = HierarchicalIntegration()
    result = primitive.evaluate()

    assert abs(result["hierarchical_coherence"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "flat"


def test_nominal_case():
    primitive = HierarchicalIntegration(
        level_differentiation=0.8,
        top_down_coordination=0.6,
        bottom_up_propagation=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["hierarchical_coherence"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "hierarchical"


def test_negative_inputs_are_clamped():
    primitive = HierarchicalIntegration(
        level_differentiation=-1.0,
        top_down_coordination=-2.0,
        bottom_up_propagation=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["hierarchical_coherence"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = HierarchicalIntegration(
        level_differentiation=10.0,
        top_down_coordination=10.0,
        bottom_up_propagation=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "level_differentiation",
        "top_down_coordination",
        "bottom_up_propagation",
        "hierarchical_coherence",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = HierarchicalIntegration(
        level_differentiation=0.4,
        top_down_coordination=0.5,
        bottom_up_propagation=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "level_differentiation",
        "top_down_coordination",
        "bottom_up_propagation",
        "hierarchical_coherence",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = HierarchicalIntegration(
        level_differentiation=0.7,
        top_down_coordination=0.8,
        bottom_up_propagation=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["hierarchical_coherence"]
            - evaluation["hierarchical_coherence"]
        )
        < 1e-12
    )
