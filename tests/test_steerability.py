"""
tests/test_steerability.py
"""

from ontology.steerability import (
    Steerability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "STEERABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Steerability()
    result = primitive.evaluate()

    assert abs(result["directional_control"] - 0.0) < 1e-12
    assert abs(result["trajectory_reorientation"] - 0.0) < 1e-12
    assert (
        abs(result["constraint_responsive_steering"] - 0.0) < 1e-12
    )
    assert abs(result["steerability_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Steerability(
        directional_control=0.9,
        trajectory_reorientation=0.6,
        constraint_responsive_steering=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["steerability_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Steerability(
        directional_control=-1.0,
        trajectory_reorientation=-2.0,
        constraint_responsive_steering=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["steerability_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Steerability(
        directional_control=2.0,
        trajectory_reorientation=1.5,
        constraint_responsive_steering=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["directional_control"] - 1.0) < 1e-12
    assert abs(result["trajectory_reorientation"] - 1.0) < 1e-12
    assert (
        abs(result["constraint_responsive_steering"] - 1.0) < 1e-12
    )
    assert abs(result["steerability_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Steerability(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["steerability_index"]
        - result_step["steerability_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Steerability(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["steerability_index"]
        - result["steerability_index"]
    ) < 1e-12
