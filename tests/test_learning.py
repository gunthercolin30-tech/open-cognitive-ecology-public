from ontology.learning import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Learning,
)


def test_constants():
    assert PRIMITIVE_NAME == "LEARNING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Learning()
    result = primitive.evaluate()

    assert abs(result["experience_integration"] - 0.0) < 1e-12
    assert abs(result["parameter_update"] - 0.0) < 1e-12
    assert abs(result["performance_improvement"] - 0.0) < 1e-12
    assert abs(result["learning_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Learning()
    result = primitive.evaluate(
        experiences=[1.0, 0.8],
        updates=[1.0, 0.9],
        improvements=[0.7, 1.0],
    )

    assert result["learning_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Learning()
    result = primitive.evaluate(
        experiences=[0.0],
        updates=[0.0],
        improvements=[0.0],
    )

    assert abs(result["learning_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Learning()
    result = primitive.evaluate(
        experiences=[10.0, -5.0],
        updates=[2.0],
        improvements=[3.0],
    )

    for key in (
        "experience_integration",
        "parameter_update",
        "performance_improvement",
        "learning_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Learning()
    kwargs = {
        "experiences": [1.0, 0.5],
        "updates": [1.0],
        "improvements": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(stepped["learning_index"] - evaluation["learning_index"]) < 1e-12


def test_validate_matches_evaluate():
    primitive = Learning()
    kwargs = {
        "experiences": [1.0, 0.5],
        "updates": [1.0],
        "improvements": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(validation["learning_index"] - evaluation["learning_index"]) < 1e-12
