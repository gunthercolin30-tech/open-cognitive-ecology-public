from ontology.embodiment import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Embodiment,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EMBODIMENT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Embodiment()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["embodiment_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = Embodiment()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["sensorimotor_coupling"] <= 1.0
    assert 0.0 <= result["physical_constraint_integration"] <= 1.0
    assert 0.0 <= result["environmental_grounding"] <= 1.0
    assert 0.0 <= result["embodiment_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = Embodiment()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["embodiment_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Embodiment()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["embodiment_index"] <= 1.0


def test_step_consistency():
    primitive = Embodiment()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["embodiment_index"] - b["embodiment_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = Embodiment()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["embodiment_index"]
        - validation["embodiment_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
