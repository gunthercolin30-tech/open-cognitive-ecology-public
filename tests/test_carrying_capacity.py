from ontology.carrying_capacity import (
    CarryingCapacity,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "CARRYING_CAPACITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CarryingCapacity()
    result = primitive.evaluate({})
    expected = (0.0 + 0.0 + (1.0 - 0.0)) / 3.0
    assert abs(result["carrying_capacity_index"] - expected) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = CarryingCapacity()
    result = primitive.evaluate(
        {
            "resource_availability": 0.8,
            "regeneration_rate": 0.7,
            "population_pressure": 0.2,
        }
    )
    expected = (0.8 + 0.7 + 0.8) / 3.0
    assert abs(result["carrying_capacity_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "sustainable"


def test_negative_case():
    primitive = CarryingCapacity()
    result = primitive.evaluate(
        {
            "resource_availability": 0.1,
            "regeneration_rate": 0.2,
            "population_pressure": 0.9,
        }
    )
    assert result["diagnostics"]["status"] == "overshoot"


def test_bounding():
    primitive = CarryingCapacity()
    result = primitive.evaluate(
        {
            "resource_availability": 2.0,
            "regeneration_rate": -1.0,
            "population_pressure": 5.0,
        }
    )
    assert abs(result["resource_availability"] - 1.0) < 1e-12
    assert abs(result["regeneration_rate"] - 0.0) < 1e-12
    assert abs(result["population_pressure"] - 1.0) < 1e-12
    assert 0.0 <= result["carrying_capacity_index"] <= 1.0


def test_step_consistency():
    primitive = CarryingCapacity()
    inputs = {
        "resource_availability": 0.6,
        "regeneration_rate": 0.6,
        "population_pressure": 0.4,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = CarryingCapacity()
    inputs = {
        "resource_availability": 0.4,
        "regeneration_rate": 0.5,
        "population_pressure": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["carrying_capacity_index"]
            - evaluation["carrying_capacity_index"]
        )
        < 1e-12
    )
