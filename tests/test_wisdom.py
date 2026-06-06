from ontology.wisdom import (
    Wisdom,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "WISDOM"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Wisdom()
    result = primitive.evaluate({})
    assert abs(result["wisdom_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = Wisdom()
    result = primitive.evaluate(
        {
            "knowledge_integration": 0.8,
            "ethical_discernment": 0.7,
            "long_term_judgment": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["wisdom_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "wise"


def test_negative_case():
    primitive = Wisdom()
    result = primitive.evaluate(
        {
            "knowledge_integration": 0.1,
            "ethical_discernment": 0.2,
            "long_term_judgment": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "short_sighted"


def test_bounding():
    primitive = Wisdom()
    result = primitive.evaluate(
        {
            "knowledge_integration": 2.0,
            "ethical_discernment": -1.0,
            "long_term_judgment": 5.0,
        }
    )
    assert abs(result["knowledge_integration"] - 1.0) < 1e-12
    assert abs(result["ethical_discernment"] - 0.0) < 1e-12
    assert abs(result["long_term_judgment"] - 1.0) < 1e-12
    assert 0.0 <= result["wisdom_index"] <= 1.0


def test_step_consistency():
    primitive = Wisdom()
    inputs = {
        "knowledge_integration": 0.6,
        "ethical_discernment": 0.6,
        "long_term_judgment": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = Wisdom()
    inputs = {
        "knowledge_integration": 0.4,
        "ethical_discernment": 0.5,
        "long_term_judgment": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["wisdom_index"]
            - evaluation["wisdom_index"]
        )
        < 1e-12
    )
