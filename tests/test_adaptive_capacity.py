from ontology.adaptive_capacity import (
    AdaptiveCapacity,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "ADAPTIVE_CAPACITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = AdaptiveCapacity()
    result = primitive.evaluate({})
    assert abs(result["adaptive_capacity_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = AdaptiveCapacity()
    result = primitive.evaluate(
        {
            "learning_capacity": 0.8,
            "reconfiguration_flexibility": 0.7,
            "resource_mobilization": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["adaptive_capacity_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "adaptive"


def test_negative_case():
    primitive = AdaptiveCapacity()
    result = primitive.evaluate(
        {
            "learning_capacity": 0.1,
            "reconfiguration_flexibility": 0.2,
            "resource_mobilization": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "rigid"


def test_bounding():
    primitive = AdaptiveCapacity()
    result = primitive.evaluate(
        {
            "learning_capacity": 2.0,
            "reconfiguration_flexibility": -1.0,
            "resource_mobilization": 5.0,
        }
    )
    assert abs(result["learning_capacity"] - 1.0) < 1e-12
    assert abs(result["reconfiguration_flexibility"] - 0.0) < 1e-12
    assert abs(result["resource_mobilization"] - 1.0) < 1e-12
    assert 0.0 <= result["adaptive_capacity_index"] <= 1.0


def test_step_consistency():
    primitive = AdaptiveCapacity()
    inputs = {
        "learning_capacity": 0.6,
        "reconfiguration_flexibility": 0.6,
        "resource_mobilization": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = AdaptiveCapacity()
    inputs = {
        "learning_capacity": 0.4,
        "reconfiguration_flexibility": 0.5,
        "resource_mobilization": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["adaptive_capacity_index"]
            - evaluation["adaptive_capacity_index"]
        )
        < 1e-12
    )
