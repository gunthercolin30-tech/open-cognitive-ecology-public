from ontology.legitimacy import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Legitimacy,
)


def test_metadata():
    assert PRIMITIVE_NAME == "LEGITIMACY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Legitimacy()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["legitimacy_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = Legitimacy()

    result = primitive.evaluate(
        0.85,
        0.80,
        0.90,
    )

    assert 0.0 <= result["institutional_trust"] <= 1.0
    assert 0.0 <= result["reputational_support"] <= 1.0
    assert 0.0 <= result["normative_alignment"] <= 1.0
    assert 0.0 <= result["legitimacy_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = Legitimacy()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["legitimacy_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Legitimacy()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["legitimacy_index"] <= 1.0


def test_step_consistency():
    primitive = Legitimacy()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["legitimacy_index"] - b["legitimacy_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = Legitimacy()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["legitimacy_index"]
        - validation["legitimacy_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
