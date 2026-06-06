"""
tests/test_homeostatic_regulation.py
"""

from ontology.homeostatic_regulation import (
    HomeostaticRegulation,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "HOMEOSTATIC_REGULATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = HomeostaticRegulation()
    result = primitive.evaluate()

    assert abs(result["deviation_detection"] - 0.0) < 1e-12
    assert abs(result["corrective_response"] - 0.0) < 1e-12
    assert abs(result["setpoint_stability"] - 0.0) < 1e-12
    assert abs(result["homeostatic_regulation_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = HomeostaticRegulation(
        deviation_detection=0.9,
        corrective_response=0.6,
        setpoint_stability=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(
        result["homeostatic_regulation_index"] - expected
    ) < 1e-12


def test_negative_case():
    primitive = HomeostaticRegulation(
        deviation_detection=-1.0,
        corrective_response=-2.0,
        setpoint_stability=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["homeostatic_regulation_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = HomeostaticRegulation(
        deviation_detection=2.0,
        corrective_response=1.5,
        setpoint_stability=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["deviation_detection"] - 1.0) < 1e-12
    assert abs(result["corrective_response"] - 1.0) < 1e-12
    assert abs(result["setpoint_stability"] - 1.0) < 1e-12
    assert abs(result["homeostatic_regulation_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = HomeostaticRegulation(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["homeostatic_regulation_index"]
        - result_step["homeostatic_regulation_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = HomeostaticRegulation(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["homeostatic_regulation_index"]
        - result["homeostatic_regulation_index"]
    ) < 1e-12
