from ontology.innovation_retention import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    InnovationRetention,
)


def test_metadata():
    assert PRIMITIVE_NAME == "INNOVATION_RETENTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = InnovationRetention()
    result = primitive.evaluate()

    assert abs(result["innovation_persistence"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "transient"


def test_nominal_case():
    primitive = InnovationRetention(
        stabilization_capacity=0.8,
        retention_probability=0.6,
        integration_strength=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["innovation_persistence"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "retained"


def test_negative_inputs_are_clamped():
    primitive = InnovationRetention(
        stabilization_capacity=-1.0,
        retention_probability=-2.0,
        integration_strength=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["innovation_persistence"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = InnovationRetention(
        stabilization_capacity=10.0,
        retention_probability=10.0,
        integration_strength=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "stabilization_capacity",
        "retention_probability",
        "integration_strength",
        "innovation_persistence",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = InnovationRetention(
        stabilization_capacity=0.4,
        retention_probability=0.5,
        integration_strength=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "stabilization_capacity",
        "retention_probability",
        "integration_strength",
        "innovation_persistence",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = InnovationRetention(
        stabilization_capacity=0.7,
        retention_probability=0.8,
        integration_strength=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["innovation_persistence"]
            - evaluation["innovation_persistence"]
        )
        < 1e-12
    )
