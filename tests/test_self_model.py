from ontology.self_model import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    SelfModel,
)


def test_constants():
    assert PRIMITIVE_NAME == "SELF_MODEL"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SelfModel()
    result = primitive.evaluate()

    assert abs(
        result["self_representation_coherence"] - 0.0
    ) < 1e-12
    assert abs(result["capability_awareness"] - 0.0) < 1e-12
    assert abs(result["limitation_awareness"] - 0.0) < 1e-12
    assert abs(result["self_model_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = SelfModel()
    result = primitive.evaluate(
        representation_signals=[1.0, 0.8],
        capability_signals=[1.0, 0.9],
        limitation_signals=[0.7, 1.0],
    )

    assert result["self_model_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = SelfModel()
    result = primitive.evaluate(
        representation_signals=[0.0],
        capability_signals=[0.0],
        limitation_signals=[0.0],
    )

    assert abs(result["self_model_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = SelfModel()
    result = primitive.evaluate(
        representation_signals=[10.0, -5.0],
        capability_signals=[2.0],
        limitation_signals=[3.0],
    )

    for key in (
        "self_representation_coherence",
        "capability_awareness",
        "limitation_awareness",
        "self_model_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = SelfModel()
    kwargs = {
        "representation_signals": [1.0, 0.5],
        "capability_signals": [1.0],
        "limitation_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["self_model_index"]
        - evaluation["self_model_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = SelfModel()
    kwargs = {
        "representation_signals": [1.0, 0.5],
        "capability_signals": [1.0],
        "limitation_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["self_model_index"]
        - evaluation["self_model_index"]
    ) < 1e-12
