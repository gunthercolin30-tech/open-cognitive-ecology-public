from ontology.irreversibility import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Irreversibility,
)


def test_metadata():
    assert PRIMITIVE_NAME == "IRREVERSIBILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Irreversibility()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["irreversibility_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = Irreversibility()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["entropy_production"] <= 1.0
    assert 0.0 <= result["historical_path_dependence"] <= 1.0
    assert 0.0 <= result["reversal_difficulty"] <= 1.0
    assert 0.0 <= result["irreversibility_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = Irreversibility()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["irreversibility_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Irreversibility()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["irreversibility_index"] <= 1.0


def test_step_consistency():
    primitive = Irreversibility()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["irreversibility_index"]
        - b["irreversibility_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = Irreversibility()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["irreversibility_index"]
        - validation["irreversibility_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
