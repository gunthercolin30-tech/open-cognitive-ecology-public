from ontology.trust import PRIMITIVE_NAME, MATURITY_LEVEL, Trust


def test_metadata():
    assert PRIMITIVE_NAME == "TRUST"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Trust()
    result = primitive.evaluate([], [], 0.0)

    assert abs(result["trust_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = Trust()

    result = primitive.evaluate(
        [1.0, 0.8, 0.6],
        [1.0, 0.7, 0.5],
        0.8,
    )

    assert 0.0 <= result["predictive_reliability"] <= 1.0
    assert 0.0 <= result["behavioral_consistency"] <= 1.0
    assert 0.0 <= result["institutional_confidence"] <= 1.0
    assert 0.0 <= result["trust_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = Trust()

    result = primitive.evaluate(
        [1.0, 1.0],
        [0.0, 0.0],
        0.0,
    )

    assert abs(result["trust_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Trust()

    result = primitive.evaluate(
        [2.0, -1.0],
        [3.0, -2.0],
        5.0,
    )

    assert 0.0 <= result["trust_index"] <= 1.0


def test_step_consistency():
    primitive = Trust()

    a = primitive.evaluate([0.9, 0.8], [0.8, 0.8], 0.6)
    b = primitive.step([0.9, 0.8], [0.8, 0.8], 0.6)

    assert abs(a["trust_index"] - b["trust_index"]) < 1e-12


def test_validate_consistency():
    primitive = Trust()

    evaluation = primitive.evaluate([0.9, 0.8], [0.8, 0.8], 0.6)
    validation = primitive.validate([0.9, 0.8], [0.8, 0.8], 0.6)

    assert abs(
        evaluation["trust_index"] - validation["trust_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
