from ontology.counterfactual_simulation import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    CounterfactualSimulation,
)


def test_constants():
    assert PRIMITIVE_NAME == "COUNTERFACTUAL_SIMULATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CounterfactualSimulation()
    result = primitive.evaluate()

    assert abs(result["alternative_generation"] - 0.0) < 1e-12
    assert abs(result["counterfactual_consistency"] - 0.0) < 1e-12
    assert abs(result["intervention_comparison"] - 0.0) < 1e-12
    assert abs(result["counterfactual_simulation_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = CounterfactualSimulation()
    result = primitive.evaluate(
        alternatives=[1.0, 0.8],
        consistencies=[1.0, 0.9],
        comparisons=[0.7, 1.0],
    )

    assert result["counterfactual_simulation_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = CounterfactualSimulation()
    result = primitive.evaluate(
        alternatives=[0.0],
        consistencies=[0.0],
        comparisons=[0.0],
    )

    assert (
        abs(result["counterfactual_simulation_index"] - 0.0)
        < 1e-12
    )


def test_bounded_values():
    primitive = CounterfactualSimulation()
    result = primitive.evaluate(
        alternatives=[10.0, -5.0],
        consistencies=[2.0],
        comparisons=[3.0],
    )

    for key in (
        "alternative_generation",
        "counterfactual_consistency",
        "intervention_comparison",
        "counterfactual_simulation_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = CounterfactualSimulation()
    kwargs = {
        "alternatives": [1.0, 0.5],
        "consistencies": [1.0],
        "comparisons": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["counterfactual_simulation_index"]
            - evaluation["counterfactual_simulation_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = CounterfactualSimulation()
    kwargs = {
        "alternatives": [1.0, 0.5],
        "consistencies": [1.0],
        "comparisons": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["counterfactual_simulation_index"]
            - evaluation["counterfactual_simulation_index"]
        )
        < 1e-12
    )
