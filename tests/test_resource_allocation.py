from ontology.resource_allocation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ResourceAllocation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "RESOURCE_ALLOCATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ResourceAllocation()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["resource_allocation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = ResourceAllocation()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["resource_availability"] <= 1.0
    assert 0.0 <= result["allocation_efficiency"] <= 1.0
    assert 0.0 <= result["priority_satisfaction"] <= 1.0
    assert 0.0 <= result["resource_allocation_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = ResourceAllocation()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["resource_allocation_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = ResourceAllocation()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["resource_allocation_index"] <= 1.0


def test_step_consistency():
    primitive = ResourceAllocation()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["resource_allocation_index"]
        - b["resource_allocation_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ResourceAllocation()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["resource_allocation_index"]
        - validation["resource_allocation_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
