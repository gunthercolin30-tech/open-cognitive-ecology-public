from ontology.responsibility_attribution import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ResponsibilityAttribution,
)


def test_metadata():
    assert PRIMITIVE_NAME == "RESPONSIBILITY_ATTRIBUTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ResponsibilityAttribution()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["responsibility_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = ResponsibilityAttribution()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["causal_contribution"] <= 1.0
    assert 0.0 <= result["control_degree"] <= 1.0
    assert 0.0 <= result["intentional_involvement"] <= 1.0
    assert 0.0 <= result["responsibility_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = ResponsibilityAttribution()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["responsibility_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = ResponsibilityAttribution()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["responsibility_index"] <= 1.0


def test_step_consistency():
    primitive = ResponsibilityAttribution()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["responsibility_index"] - b["responsibility_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ResponsibilityAttribution()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["responsibility_index"]
        - validation["responsibility_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
