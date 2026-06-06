"""
tests/test_navigability.py
"""

from ontology.navigability import (
    Navigability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "NAVIGABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Navigability()
    result = primitive.evaluate()

    assert abs(result["path_guidance"] - 0.0) < 1e-12
    assert abs(result["trajectory_stability"] - 0.0) < 1e-12
    assert abs(result["decision_resolution"] - 0.0) < 1e-12
    assert abs(result["navigability_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Navigability(
        path_guidance=0.9,
        trajectory_stability=0.6,
        decision_resolution=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["navigability_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Navigability(
        path_guidance=-1.0,
        trajectory_stability=-2.0,
        decision_resolution=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["navigability_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Navigability(
        path_guidance=2.0,
        trajectory_stability=1.5,
        decision_resolution=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["path_guidance"] - 1.0) < 1e-12
    assert abs(result["trajectory_stability"] - 1.0) < 1e-12
    assert abs(result["decision_resolution"] - 1.0) < 1e-12
    assert abs(result["navigability_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Navigability(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["navigability_index"]
        - result_step["navigability_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Navigability(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["navigability_index"]
        - result["navigability_index"]
    ) < 1e-12
