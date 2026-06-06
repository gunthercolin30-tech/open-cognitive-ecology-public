from ontology.phenotypic_plasticity import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    PhenotypicPlasticity,
)


def test_metadata():
    assert PRIMITIVE_NAME == "PHENOTYPIC_PLASTICITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = PhenotypicPlasticity()
    result = primitive.evaluate()

    assert abs(result["plasticity_strength"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "rigid"


def test_nominal_case():
    primitive = PhenotypicPlasticity(
        environmental_sensitivity=0.8,
        response_flexibility=0.6,
        reconfiguration_capacity=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["plasticity_strength"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "plastic"


def test_negative_inputs_are_clamped():
    primitive = PhenotypicPlasticity(
        environmental_sensitivity=-1.0,
        response_flexibility=-2.0,
        reconfiguration_capacity=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["plasticity_strength"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = PhenotypicPlasticity(
        environmental_sensitivity=10.0,
        response_flexibility=10.0,
        reconfiguration_capacity=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "environmental_sensitivity",
        "response_flexibility",
        "reconfiguration_capacity",
        "plasticity_strength",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = PhenotypicPlasticity(
        environmental_sensitivity=0.4,
        response_flexibility=0.5,
        reconfiguration_capacity=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "environmental_sensitivity",
        "response_flexibility",
        "reconfiguration_capacity",
        "plasticity_strength",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = PhenotypicPlasticity(
        environmental_sensitivity=0.7,
        response_flexibility=0.8,
        reconfiguration_capacity=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["plasticity_strength"]
            - evaluation["plasticity_strength"]
        )
        < 1e-12
    )
