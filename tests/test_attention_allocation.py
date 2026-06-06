from ontology.attention_allocation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    AttentionAllocation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "ATTENTION_ALLOCATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = AttentionAllocation()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(result["attention_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = AttentionAllocation()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["salience_distribution"] <= 1.0
    assert 0.0 <= result["resource_focus"] <= 1.0
    assert 0.0 <= result["selective_priority"] <= 1.0
    assert 0.0 <= result["attention_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = AttentionAllocation()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(result["attention_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = AttentionAllocation()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["attention_index"] <= 1.0


def test_step_consistency():
    primitive = AttentionAllocation()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["attention_index"] - b["attention_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = AttentionAllocation()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["attention_index"]
        - validation["attention_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
