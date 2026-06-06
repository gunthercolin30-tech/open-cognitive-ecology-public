from ontology.morphospace_exploration import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    MorphospaceExploration,
)


def test_metadata():
    assert PRIMITIVE_NAME == "MORPHOSPACE_EXPLORATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MorphospaceExploration()
    result = primitive.evaluate()

    assert abs(result["morphospace_coverage"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "localized"


def test_nominal_case():
    primitive = MorphospaceExploration(
        configuration_diversity=0.8,
        accessible_region_fraction=0.6,
        exploration_depth=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["morphospace_coverage"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "exploratory"


def test_negative_inputs_are_clamped():
    primitive = MorphospaceExploration(
        configuration_diversity=-1.0,
        accessible_region_fraction=-2.0,
        exploration_depth=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["morphospace_coverage"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = MorphospaceExploration(
        configuration_diversity=10.0,
        accessible_region_fraction=10.0,
        exploration_depth=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "configuration_diversity",
        "accessible_region_fraction",
        "exploration_depth",
        "morphospace_coverage",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = MorphospaceExploration(
        configuration_diversity=0.4,
        accessible_region_fraction=0.5,
        exploration_depth=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "configuration_diversity",
        "accessible_region_fraction",
        "exploration_depth",
        "morphospace_coverage",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = MorphospaceExploration(
        configuration_diversity=0.7,
        accessible_region_fraction=0.8,
        exploration_depth=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["morphospace_coverage"]
            - evaluation["morphospace_coverage"]
        )
        < 1e-12
    )
