from ontology.causal_inference import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    CausalInference,
)


def test_constants():
    assert PRIMITIVE_NAME == "CAUSAL_INFERENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CausalInference()
    result = primitive.evaluate()

    assert abs(result["causal_discrimination"] - 0.0) < 1e-12
    assert abs(result["intervention_predictability"] - 0.0) < 1e-12
    assert abs(result["structural_consistency"] - 0.0) < 1e-12
    assert abs(result["causal_inference_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = CausalInference()
    result = primitive.evaluate(
        discriminations=[1.0, 0.8],
        intervention_predictions=[1.0, 0.9],
        structural_signals=[0.7, 1.0],
    )

    assert result["causal_inference_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = CausalInference()
    result = primitive.evaluate(
        discriminations=[0.0],
        intervention_predictions=[0.0],
        structural_signals=[0.0],
    )

    assert abs(result["causal_inference_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = CausalInference()
    result = primitive.evaluate(
        discriminations=[10.0, -5.0],
        intervention_predictions=[2.0],
        structural_signals=[3.0],
    )

    for key in (
        "causal_discrimination",
        "intervention_predictability",
        "structural_consistency",
        "causal_inference_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = CausalInference()
    kwargs = {
        "discriminations": [1.0, 0.5],
        "intervention_predictions": [1.0],
        "structural_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["causal_inference_index"]
            - evaluation["causal_inference_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = CausalInference()
    kwargs = {
        "discriminations": [1.0, 0.5],
        "intervention_predictions": [1.0],
        "structural_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["causal_inference_index"]
            - evaluation["causal_inference_index"]
        )
        < 1e-12
    )
