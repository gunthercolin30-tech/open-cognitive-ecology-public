from ontology.meta_cognition import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    MetaCognition,
)


def test_constants():
    assert PRIMITIVE_NAME == "META_COGNITION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MetaCognition()
    result = primitive.evaluate()

    assert abs(result["self_monitoring"] - 0.0) < 1e-12
    assert abs(result["strategy_evaluation"] - 0.0) < 1e-12
    assert abs(result["cognitive_regulation"] - 0.0) < 1e-12
    assert abs(result["meta_cognition_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = MetaCognition()
    result = primitive.evaluate(
        monitoring_signals=[1.0, 0.8],
        evaluation_signals=[1.0, 0.9],
        regulation_signals=[0.7, 1.0],
    )

    assert result["meta_cognition_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = MetaCognition()
    result = primitive.evaluate(
        monitoring_signals=[0.0],
        evaluation_signals=[0.0],
        regulation_signals=[0.0],
    )

    assert abs(result["meta_cognition_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = MetaCognition()
    result = primitive.evaluate(
        monitoring_signals=[10.0, -5.0],
        evaluation_signals=[2.0],
        regulation_signals=[3.0],
    )

    for key in (
        "self_monitoring",
        "strategy_evaluation",
        "cognitive_regulation",
        "meta_cognition_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = MetaCognition()
    kwargs = {
        "monitoring_signals": [1.0, 0.5],
        "evaluation_signals": [1.0],
        "regulation_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["meta_cognition_index"]
        - evaluation["meta_cognition_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = MetaCognition()
    kwargs = {
        "monitoring_signals": [1.0, 0.5],
        "evaluation_signals": [1.0],
        "regulation_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["meta_cognition_index"]
        - evaluation["meta_cognition_index"]
    ) < 1e-12
