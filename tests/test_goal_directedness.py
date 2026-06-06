"""
tests/test_goal_directedness.py
"""

from ontology.goal_directedness import (
    GoalDirectedness,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "GOAL_DIRECTEDNESS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = GoalDirectedness()
    result = primitive.evaluate()

    assert abs(result["target_specification"] - 0.0) < 1e-12
    assert abs(result["objective_persistence"] - 0.0) < 1e-12
    assert abs(result["trajectory_alignment"] - 0.0) < 1e-12
    assert abs(result["goal_directedness_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = GoalDirectedness(
        target_specification=0.9,
        objective_persistence=0.6,
        trajectory_alignment=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(
        result["goal_directedness_index"] - expected
    ) < 1e-12


def test_negative_case():
    primitive = GoalDirectedness(
        target_specification=-1.0,
        objective_persistence=-2.0,
        trajectory_alignment=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["goal_directedness_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = GoalDirectedness(
        target_specification=2.0,
        objective_persistence=1.5,
        trajectory_alignment=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["target_specification"] - 1.0) < 1e-12
    assert abs(result["objective_persistence"] - 1.0) < 1e-12
    assert abs(result["trajectory_alignment"] - 1.0) < 1e-12
    assert abs(result["goal_directedness_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = GoalDirectedness(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["goal_directedness_index"]
        - result_step["goal_directedness_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = GoalDirectedness(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["goal_directedness_index"]
        - result["goal_directedness_index"]
    ) < 1e-12
