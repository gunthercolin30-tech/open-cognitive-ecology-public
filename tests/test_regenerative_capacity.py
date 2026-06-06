from ontology.regenerative_capacity import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    RegenerativeCapacity,
)


def test_metadata():
    assert PRIMITIVE_NAME == "REGENERATIVE_CAPACITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = RegenerativeCapacity()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(
        result["regenerative_capacity_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = RegenerativeCapacity()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["resource_restoration"] <= 1.0
    assert 0.0 <= result["functional_recovery"] <= 1.0
    assert 0.0 <= result["renewal_sustainability"] <= 1.0
    assert 0.0 <= result["regenerative_capacity_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = RegenerativeCapacity()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(
        result["regenerative_capacity_index"] - 0.0
    ) < 1e-12


def test_bounding():
    primitive = RegenerativeCapacity()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert (
        0.0
        <= result["regenerative_capacity_index"]
        <= 1.0
    )


def test_step_consistency():
    primitive = RegenerativeCapacity()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["regenerative_capacity_index"]
        - b["regenerative_capacity_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = RegenerativeCapacity()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["regenerative_capacity_index"]
        - validation["regenerative_capacity_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
