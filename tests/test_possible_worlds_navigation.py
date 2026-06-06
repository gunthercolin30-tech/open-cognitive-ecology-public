from ontology.possible_worlds_navigation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    PossibleWorldsNavigation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "POSSIBLE_WORLDS_NAVIGATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = PossibleWorldsNavigation()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(
        result["possible_worlds_navigation_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = PossibleWorldsNavigation()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["counterfactual_exploration"] <= 1.0
    assert 0.0 <= result["trajectory_evaluation"] <= 1.0
    assert 0.0 <= result["constraint_compatibility"] <= 1.0
    assert (
        0.0
        <= result["possible_worlds_navigation_index"]
        <= 1.0
    )
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = PossibleWorldsNavigation()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(
        result["possible_worlds_navigation_index"] - 0.0
    ) < 1e-12


def test_bounding():
    primitive = PossibleWorldsNavigation()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert (
        0.0
        <= result["possible_worlds_navigation_index"]
        <= 1.0
    )


def test_step_consistency():
    primitive = PossibleWorldsNavigation()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["possible_worlds_navigation_index"]
        - b["possible_worlds_navigation_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = PossibleWorldsNavigation()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["possible_worlds_navigation_index"]
        - validation["possible_worlds_navigation_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
