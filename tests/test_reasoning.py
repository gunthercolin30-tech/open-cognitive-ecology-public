from ontology.reasoning import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Reasoning,
)


def test_constants():
    assert PRIMITIVE_NAME == "REASONING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Reasoning()
    result = primitive.evaluate()

    assert abs(result["inference_coherence"] - 0.0) < 1e-12
    assert abs(result["logical_consistency"] - 0.0) < 1e-12
    assert abs(result["conclusion_reliability"] - 0.0) < 1e-12
    assert abs(result["reasoning_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Reasoning()
    result = primitive.evaluate(
        inferences=[1.0, 0.8],
        consistencies=[1.0, 0.9],
        conclusions=[0.7, 1.0],
    )

    assert result["reasoning_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Reasoning()
    result = primitive.evaluate(
        inferences=[0.0],
        consistencies=[0.0],
        conclusions=[0.0],
    )

    assert abs(result["reasoning_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Reasoning()
    result = primitive.evaluate(
        inferences=[10.0, -5.0],
        consistencies=[2.0],
        conclusions=[3.0],
    )

    for key in (
        "inference_coherence",
        "logical_consistency",
        "conclusion_reliability",
        "reasoning_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Reasoning()
    kwargs = {
        "inferences": [1.0, 0.5],
        "consistencies": [1.0],
        "conclusions": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["reasoning_index"] - evaluation["reasoning_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Reasoning()
    kwargs = {
        "inferences": [1.0, 0.5],
        "consistencies": [1.0],
        "conclusions": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["reasoning_index"] - evaluation["reasoning_index"]
    ) < 1e-12
