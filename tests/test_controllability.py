"""
tests/test_controllability.py
"""

from ontology.controllability import (
    Controllability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "CONTROLLABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Controllability()
    result = primitive.evaluate()

    assert abs(result["actuation_reach"] - 0.0) < 1e-12
    assert abs(result["state_accessibility"] - 0.0) < 1e-12
    assert abs(result["control_effectiveness"] - 0.0) < 1e-12
    assert abs(result["controllability_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Controllability(
        actuation_reach=0.9,
        state_accessibility=0.6,
        control_effectiveness=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["controllability_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Controllability(
        actuation_reach=-1.0,
        state_accessibility=-2.0,
        control_effectiveness=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["controllability_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Controllability(
        actuation_reach=2.0,
        state_accessibility=1.5,
        control_effectiveness=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["actuation_reach"] - 1.0) < 1e-12
    assert abs(result["state_accessibility"] - 1.0) < 1e-12
    assert abs(result["control_effectiveness"] - 1.0) < 1e-12
    assert abs(result["controllability_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Controllability(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["controllability_index"]
        - result_step["controllability_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Controllability(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["controllability_index"]
        - result["controllability_index"]
    ) < 1e-12
