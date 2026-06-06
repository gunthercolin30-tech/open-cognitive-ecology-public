"""
tests/test_feedback_sensitivity.py
"""

from ontology.feedback_sensitivity import (
    FeedbackSensitivity,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "FEEDBACK_SENSITIVITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = FeedbackSensitivity()
    result = primitive.evaluate()

    assert abs(result["signal_detection"] - 0.0) < 1e-12
    assert abs(result["response_gain"] - 0.0) < 1e-12
    assert abs(result["error_correction_efficiency"] - 0.0) < 1e-12
    assert abs(result["feedback_sensitivity_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = FeedbackSensitivity(
        signal_detection=0.9,
        response_gain=0.6,
        error_correction_efficiency=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(
        result["feedback_sensitivity_index"] - expected
    ) < 1e-12


def test_negative_case():
    primitive = FeedbackSensitivity(
        signal_detection=-1.0,
        response_gain=-2.0,
        error_correction_efficiency=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["feedback_sensitivity_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = FeedbackSensitivity(
        signal_detection=2.0,
        response_gain=1.5,
        error_correction_efficiency=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["signal_detection"] - 1.0) < 1e-12
    assert abs(result["response_gain"] - 1.0) < 1e-12
    assert abs(result["error_correction_efficiency"] - 1.0) < 1e-12
    assert abs(result["feedback_sensitivity_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = FeedbackSensitivity(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["feedback_sensitivity_index"]
        - result_step["feedback_sensitivity_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = FeedbackSensitivity(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["feedback_sensitivity_index"]
        - result["feedback_sensitivity_index"]
    ) < 1e-12
