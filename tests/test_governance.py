from ontology.governance import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Governance,
)


def test_metadata():
    assert PRIMITIVE_NAME == "GOVERNANCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Governance()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["governance_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = Governance()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["coordination_capacity"] <= 1.0
    assert 0.0 <= result["normative_legitimacy"] <= 1.0
    assert 0.0 <= result["resource_management"] <= 1.0
    assert 0.0 <= result["governance_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = Governance()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["governance_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Governance()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["governance_index"] <= 1.0


def test_step_consistency():
    primitive = Governance()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["governance_index"] - b["governance_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = Governance()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["governance_index"]
        - validation["governance_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
