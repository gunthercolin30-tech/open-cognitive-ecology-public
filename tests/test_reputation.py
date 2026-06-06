from ontology.reputation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Reputation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "REPUTATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Reputation()
    result = primitive.evaluate([], [], 0.0)

    assert abs(result["reputation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = Reputation()

    result = primitive.evaluate(
        [0.9, 0.8, 1.0],
        [0.8, 0.9, 0.7],
        0.85,
    )

    assert 0.0 <= result["historical_reliability"] <= 1.0
    assert 0.0 <= result["social_consensus"] <= 1.0
    assert 0.0 <= result["reputation_stability"] <= 1.0
    assert 0.0 <= result["reputation_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = Reputation()

    result = primitive.evaluate(
        [0.0, 0.0],
        [0.0, 0.0],
        0.0,
    )

    assert abs(result["reputation_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Reputation()

    result = primitive.evaluate(
        [2.0, -1.0],
        [5.0, -2.0],
        3.0,
    )

    assert 0.0 <= result["reputation_index"] <= 1.0


def test_step_consistency():
    primitive = Reputation()

    a = primitive.evaluate(
        [0.9, 0.8],
        [0.7, 0.8],
        0.75,
    )
    b = primitive.step(
        [0.9, 0.8],
        [0.7, 0.8],
        0.75,
    )

    assert abs(
        a["reputation_index"] - b["reputation_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = Reputation()

    evaluation = primitive.evaluate(
        [0.9, 0.8],
        [0.7, 0.8],
        0.75,
    )
    validation = primitive.validate(
        [0.9, 0.8],
        [0.7, 0.8],
        0.75,
    )

    assert abs(
        evaluation["reputation_index"]
        - validation["reputation_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
