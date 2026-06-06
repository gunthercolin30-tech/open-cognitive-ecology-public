from ontology.ecosystem_stability import (
    EcosystemStability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "ECOSYSTEM_STABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EcosystemStability()
    result = primitive.evaluate({})
    assert abs(result["ecosystem_stability_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = EcosystemStability()
    result = primitive.evaluate(
        {
            "functional_integrity": 0.8,
            "disturbance_resistance": 0.7,
            "recovery_capacity": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["ecosystem_stability_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "stable"


def test_negative_case():
    primitive = EcosystemStability()
    result = primitive.evaluate(
        {
            "functional_integrity": 0.1,
            "disturbance_resistance": 0.2,
            "recovery_capacity": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "unstable"


def test_bounding():
    primitive = EcosystemStability()
    result = primitive.evaluate(
        {
            "functional_integrity": 2.0,
            "disturbance_resistance": -1.0,
            "recovery_capacity": 5.0,
        }
    )
    assert abs(result["functional_integrity"] - 1.0) < 1e-12
    assert abs(result["disturbance_resistance"] - 0.0) < 1e-12
    assert abs(result["recovery_capacity"] - 1.0) < 1e-12
    assert 0.0 <= result["ecosystem_stability_index"] <= 1.0


def test_step_consistency():
    primitive = EcosystemStability()
    inputs = {
        "functional_integrity": 0.6,
        "disturbance_resistance": 0.6,
        "recovery_capacity": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = EcosystemStability()
    inputs = {
        "functional_integrity": 0.4,
        "disturbance_resistance": 0.5,
        "recovery_capacity": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["ecosystem_stability_index"]
            - evaluation["ecosystem_stability_index"]
        )
        < 1e-12
    )
