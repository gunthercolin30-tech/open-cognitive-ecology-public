from ontology.error_correction import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    ErrorCorrection,
)


def test_constants():
    assert PRIMITIVE_NAME == "ERROR_CORRECTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ErrorCorrection()
    result = primitive.evaluate()

    assert abs(result["error_identification"] - 0.0) < 1e-12
    assert abs(result["correction_effectiveness"] - 0.0) < 1e-12
    assert abs(result["residual_error_reduction"] - 0.0) < 1e-12
    assert abs(result["error_correction_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = ErrorCorrection()
    result = primitive.evaluate(
        detected_errors=[1.0, 1.0],
        corrective_actions=[0.8, 1.0],
        residual_reductions=[0.9, 1.0],
    )

    assert result["error_correction_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = ErrorCorrection()
    result = primitive.evaluate(
        detected_errors=[0.0],
        corrective_actions=[0.0],
        residual_reductions=[0.0],
    )

    assert abs(result["error_correction_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = ErrorCorrection()
    result = primitive.evaluate(
        detected_errors=[10.0, -5.0],
        corrective_actions=[2.0],
        residual_reductions=[3.0],
    )

    for key in (
        "error_identification",
        "correction_effectiveness",
        "residual_error_reduction",
        "error_correction_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = ErrorCorrection()
    kwargs = {
        "detected_errors": [1.0, 0.5],
        "corrective_actions": [1.0],
        "residual_reductions": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["error_correction_index"]
            - evaluation["error_correction_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = ErrorCorrection()
    kwargs = {
        "detected_errors": [1.0, 0.5],
        "corrective_actions": [1.0],
        "residual_reductions": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["error_correction_index"]
            - evaluation["error_correction_index"]
        )
        < 1e-12
    )
